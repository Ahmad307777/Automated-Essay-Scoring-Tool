"""
train_bert.py — CLI script to fine-tune BERT for essay score regression.

Usage:
    python train_bert.py --essay_set 1 --epochs 5 --lr 2e-5
"""

import os
import sys
import argparse
import numpy as np
import torch
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import load_asap, split_dataset, get_sample_essays
from src.bert_model import (BertScorer, BertEssayDataset,
                             train_bert, predict_bert, load_bert_tokenizer)
from src.metrics import compute_all_metrics, print_metrics
from src.utils import set_seed, get_device, save_json

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")


def main():
    parser = argparse.ArgumentParser(description="Fine-tune BERT Essay Scorer")
    parser.add_argument("--essay_set", type=int, default=1)
    parser.add_argument("--model_name", type=str, default="bert-base-uncased")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--max_len", type=int, default=512)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--use_sample", action="store_true",
                        help="Use built-in 5 sample essays (demo mode)")
    args = parser.parse_args()

    set_seed(42)
    device = get_device()

    print(f"\n{'='*55}")
    print(f"  Fine-tuning BERT Scorer - Essay Set {args.essay_set}")
    print(f"  Model: {args.model_name}")
    print(f"{'='*55}\n")

    # ── Load tokenizer ──
    print("[Tokenizer] Loading BERT tokenizer...")
    tokenizer = load_bert_tokenizer(args.model_name)

    # ── Load data ──
    if args.use_sample:
        print("[Demo] Using built-in sample essays (5 essays).")
        samples = get_sample_essays()
        texts  = [s[0] for s in samples]
        scores = [s[1] / 12.0 for s in samples]
        train_texts, val_texts   = texts[:4], texts[4:]
        train_scores, val_scores = scores[:4], scores[4:]
        test_texts, test_scores  = texts[4:], scores[4:]
    else:
        print(f"[Data] Loading ASAP essay set {args.essay_set}...")
        df = load_asap(args.essay_set)
        train_df, val_df, test_df = split_dataset(df)
        train_texts  = train_df["essay"].tolist()
        val_texts    = val_df["essay"].tolist()
        test_texts   = test_df["essay"].tolist()
        train_scores = train_df["norm_score"].tolist()
        val_scores   = val_df["norm_score"].tolist()
        test_scores  = test_df["norm_score"].tolist()

    print(f"  Train: {len(train_texts)} | Val: {len(val_texts)} | Test: {len(test_texts)}")

    # ── Datasets & Loaders ──
    train_ds = BertEssayDataset(train_texts, train_scores, tokenizer, args.max_len)
    val_ds   = BertEssayDataset(val_texts,   val_scores,   tokenizer, args.max_len)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch_size)

    # ── Model ──
    model = BertScorer(model_name=args.model_name, dropout=args.dropout)
    total_params = sum(p.numel() for p in model.parameters()) / 1e6
    print(f"[Model] BertScorer | Parameters: {total_params:.1f}M")

    # ── Train ──
    history = train_bert(
        model, train_loader, val_loader,
        epochs=args.epochs, lr=args.lr, device=device
    )

    # ── Evaluate ──
    print("\n[Evaluation] Running on test set...")
    preds = predict_bert(model, test_texts, tokenizer, args.max_len, device)
    metrics = compute_all_metrics(test_scores, preds)
    print_metrics(metrics, "BERT Scorer")

    # ── Save ──
    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, f"bert_set{args.essay_set}.pt")
    tok_path   = os.path.join(MODELS_DIR, f"bert_tokenizer_set{args.essay_set}")
    torch.save(model.state_dict(), model_path)
    tokenizer.save_pretrained(tok_path)
    save_json(metrics, os.path.join(MODELS_DIR, f"bert_metrics_set{args.essay_set}.json"))
    print(f"\n[Saved] Model      -> {model_path}")
    print(f"[Saved] Tokenizer  -> {tok_path}")


if __name__ == "__main__":
    main()
