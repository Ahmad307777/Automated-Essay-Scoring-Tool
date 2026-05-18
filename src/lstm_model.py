"""
lstm_model.py — Bidirectional LSTM model for essay score regression using PyTorch.
"""

import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import Dataset, DataLoader


# ─── Dataset ────────────────────────────────────────────────────────────────

class EssayDataset(Dataset):
    """Simple dataset of (padded_token_ids, score) pairs."""

    def __init__(self, texts, scores, vocab, max_len=512):
        self.max_len = max_len
        self.vocab = vocab
        self.data = []
        for text, score in zip(texts, scores):
            ids = self._encode(text)
            self.data.append((ids, float(score)))

    def _encode(self, text: str) -> torch.Tensor:
        tokens = text.lower().split()
        ids = [self.vocab.get(t, 1) for t in tokens]  # 1 = UNK
        if len(ids) > self.max_len:
            ids = ids[:self.max_len]
        else:
            ids = ids + [0] * (self.max_len - len(ids))  # PAD = 0
        return torch.tensor(ids, dtype=torch.long)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        ids, score = self.data[idx]
        return ids, torch.tensor(score, dtype=torch.float)


# ─── Model ───────────────────────────────────────────────────────────────────

class BiLSTMScorer(nn.Module):
    """
    Bidirectional 2-layer LSTM for essay score regression.
    Architecture:
      Embedding → BiLSTM (2 layers) → Attention Pooling → FC → Score
    """

    def __init__(self, vocab_size: int, embed_dim: int = 100,
                 hidden_dim: int = 256, num_layers: int = 2,
                 dropout: float = 0.3, pretrained_embeddings=None):
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        if pretrained_embeddings is not None:
            self.embedding.weight = nn.Parameter(
                torch.tensor(pretrained_embeddings, dtype=torch.float)
            )

        self.lstm = nn.LSTM(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0,
        )

        self.attention = nn.Linear(hidden_dim * 2, 1)
        self.dropout = nn.Dropout(dropout)

        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 1),
            nn.Sigmoid(),  # Output in [0, 1] -> denormalize later
        )

    def forward(self, x):
        # x: (batch, seq_len)
        embedded = self.dropout(self.embedding(x))           # (B, L, E)
        lstm_out, _ = self.lstm(embedded)                    # (B, L, 2H)

        # Attention over time steps
        attn_weights = torch.softmax(self.attention(lstm_out), dim=1)  # (B, L, 1)
        context = (attn_weights * lstm_out).sum(dim=1)      # (B, 2H)

        out = self.fc(context)                               # (B, 1)
        return out.squeeze(-1)                               # (B,)


# ─── Training ────────────────────────────────────────────────────────────────

def train_lstm(model, train_loader, val_loader, epochs=10,
               lr=1e-3, device=None):
    """Train the BiLSTM model with MSE loss."""
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, patience=2, factor=0.5
    )

    history = {"train_loss": [], "val_loss": []}

    for epoch in range(1, epochs + 1):
        model.train()
        train_losses = []
        for ids, targets in train_loader:
            ids, targets = ids.to(device), targets.to(device)
            optimizer.zero_grad()
            preds = model(ids)
            loss = criterion(preds, targets)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_losses.append(loss.item())

        model.eval()
        val_losses = []
        with torch.no_grad():
            for ids, targets in val_loader:
                ids, targets = ids.to(device), targets.to(device)
                preds = model(ids)
                val_losses.append(criterion(preds, targets).item())

        train_loss = np.mean(train_losses)
        val_loss = np.mean(val_losses)
        scheduler.step(val_loss)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        print(f"Epoch {epoch:02d}/{epochs} | "
              f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")

    return history


def predict_lstm(model, texts, vocab, max_len=512, device=None):
    """Run inference on a list of essay texts, return normalized scores [0,1]."""
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval().to(device)
    dummy_scores = [0.0] * len(texts)
    dataset = EssayDataset(texts, dummy_scores, vocab, max_len)
    loader = DataLoader(dataset, batch_size=16)
    preds = []
    with torch.no_grad():
        for ids, _ in loader:
            ids = ids.to(device)
            out = model(ids)
            preds.extend(out.cpu().numpy().tolist())
    return preds


if __name__ == "__main__":
    # Quick smoke test with dummy data
    vocab = {"the": 2, "quick": 3, "brown": 4, "fox": 5}
    texts = ["the quick brown fox"] * 20
    scores = [0.7, 0.5, 0.8, 0.6, 0.9] * 4
    dataset = EssayDataset(texts, scores, vocab, max_len=64)
    loader = DataLoader(dataset, batch_size=4)
    model = BiLSTMScorer(vocab_size=10, embed_dim=16, hidden_dim=32, num_layers=2)
    history = train_lstm(model, loader, loader, epochs=3)
    print("LSTM smoke test passed ✓")
