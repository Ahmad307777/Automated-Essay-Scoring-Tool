"""
bert_model.py — Fine-tuned BERT for essay score regression (HuggingFace).
"""

import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import Dataset, DataLoader
from transformers import (
    BertTokenizer,
    BertModel,
    get_linear_schedule_with_warmup,
)


# ─── Dataset ────────────────────────────────────────────────────────────────

class BertEssayDataset(Dataset):
    """Tokenizes essays for BERT input."""

    def __init__(self, texts, scores, tokenizer, max_len=512):
        self.texts = texts
        self.scores = scores
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            truncation=True,
            max_length=self.max_len,
            padding="max_length",
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "score": torch.tensor(self.scores[idx], dtype=torch.float),
        }


# ─── Model ───────────────────────────────────────────────────────────────────

class BertScorer(nn.Module):
    """
    BERT-based regression model for essay scoring.
    Architecture:
      BERT (bert-base-uncased) -> [CLS] embedding -> Dropout -> Linear -> Score
    """

    def __init__(self, model_name: str = "bert-base-uncased", dropout: float = 0.1):
        super().__init__()
        self.bert = BertModel.from_pretrained(model_name)
        hidden_size = self.bert.config.hidden_size  # 768

        self.regressor = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, 1),
            nn.Sigmoid(),  # Normalized score in [0, 1]
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        cls_output = outputs.last_hidden_state[:, 0, :]  # (B, 768)
        score = self.regressor(cls_output)               # (B, 1)
        return score.squeeze(-1)                         # (B,)


# ─── Training ────────────────────────────────────────────────────────────────

def train_bert(model, train_loader, val_loader, epochs=5,
               lr=2e-5, device=None):
    """Fine-tune BertScorer with MSE loss and linear warmup scheduler."""
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    total_steps = len(train_loader) * epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(0.1 * total_steps),
        num_training_steps=total_steps,
    )
    criterion = nn.MSELoss()
    history = {"train_loss": [], "val_loss": []}

    for epoch in range(1, epochs + 1):
        model.train()
        train_losses = []
        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            targets = batch["score"].to(device)

            optimizer.zero_grad()
            preds = model(input_ids, attention_mask)
            loss = criterion(preds, targets)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            train_losses.append(loss.item())

        model.eval()
        val_losses = []
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                targets = batch["score"].to(device)
                preds = model(input_ids, attention_mask)
                val_losses.append(criterion(preds, targets).item())

        train_loss = np.mean(train_losses)
        val_loss = np.mean(val_losses)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        print(f"Epoch {epoch:02d}/{epochs} | "
              f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")

    return history


def predict_bert(model, texts, tokenizer, max_len=512, device=None):
    """Run inference on a list of essay texts, return normalized scores [0,1]."""
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval().to(device)
    dummy_scores = [0.0] * len(texts)
    dataset = BertEssayDataset(texts, dummy_scores, tokenizer, max_len)
    loader = DataLoader(dataset, batch_size=8)
    preds = []
    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            out = model(input_ids, attention_mask)
            preds.extend(out.cpu().numpy().tolist())
    return preds


def load_bert_tokenizer(model_name: str = "bert-base-uncased"):
    return BertTokenizer.from_pretrained(model_name)


if __name__ == "__main__":
    print("BertScorer module loaded successfully [OK]")
    print("To train: instantiate BertScorer(), prepare BertEssayDataset, call train_bert()")
