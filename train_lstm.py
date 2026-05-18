"""
train_lstm.py — CLI script to train the BiLSTM essay scoring model on ASAP data.

Usage:
    python train_lstm.py --essay_set 1 --epochs 15 --lr 0.001
"""

import os
import sys
import argparse
import pickle
import numpy as np
import torch
from torch.utils.data import DataLoader
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import load_asap, split_dataset, get_sample_essays
from src.preprocessing import preprocess_essay
from src.lstm_model import BiLSTMScorer, EssayDataset, train_lstm, predict_lstm
from src.metrics import compute_all_metrics, print_metrics
from src.utils import set_seed, get_device, save_json, denormalize_score

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")


def build_vocab(texts, min_freq: int = 2) -> dict:
    """Build a word-to-index vocabulary from a list of texts."""
    counter = Counter()
    for text in texts:
        counter.update(text.lower().split())
    vocab = {"<PAD>": 0, "<UNK>": 1}
    for word, freq in counter.items():
        if freq >= min_freq:
            vocab[word] = len(vocab)
    return vocab


def main():
    parser = argparse.ArgumentParser(description="Train BiLSTM Essay Scorer")
    parser.add_argument("--essay_set", type=int, default=1, help="ASAP essay set (1-8)")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--embed_dim", type=int, default=100)
    parser.add_argument("--hidden_dim", type=int, default=256)
    parser.add_argument("--max_len", type=int, default=512)
    parser.add_argument("--dropout", type=float, default=0.3)
    parser.add_argument("--use_sample", action="store_true",
                        help="Use built-in 5 sample essays (demo mode, no ASAP download needed)")
    args = parser.parse_args()

    set_seed(42)
    device = get_device()

    print(f"\n{'='*55}")
    print(f"  Training BiLSTM Scorer - Essay Set {args.essay_set}")
    print(f"{'='*55}\n")

    # ── Load data ──
    if args.use_sample:
        print("[Demo] Using built-in sample essays (5 essays).")
        samples = get_sample_essays()
        texts = [s[0] for s in samples]
        norm_scores = [s[1] / 12.0 for s in samples]  # Normalize to [0,1]
        # Minimal train/val split
        train_texts, val_texts = texts[:4], texts[4:]
        train_scores, val_scores = norm_scores[:4], norm_scores[4:]
    else:
        print(f"[Data] Loading ASAP essay set {args.essay_set}...")
        df = load_asap(args.essay_set)
        train_df, val_df, test_df = split_dataset(df)
        train_texts = train_df["essay"].tolist()
        val_texts   = val_df["essay"].tolist()
        train_scores = train_df["norm_score"].tolist()
        val_scores   = val_df["norm_score"].tolist()
        test_texts   = test_df["essay"].tolist()
        test_scores  = test_df["norm_score"].tolist()

    # ── Build vocab ──
    print("[Vocab] Building vocabulary...")
    vocab = build_vocab(train_texts, min_freq=2)
    print(f"  Vocabulary size: {len(vocab):,} tokens")

    # ── Datasets & Loaders ──
    train_ds = EssayDataset(train_texts, train_scores, vocab, args.max_len)
    val_ds   = EssayDataset(val_texts,   val_scores,   vocab, args.max_len)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch_size)

    # ── Model ──
    model = BiLSTMScorer(
        vocab_size=len(vocab),
        embed_dim=args.embed_dim,
        hidden_dim=args.hidden_dim,
        num_layers=2,
        dropout=args.dropout,
    )
    total_params = sum(p.numel() for p in model.parameters())
    print(f"[Model] BiLSTMScorer | Parameters: {total_params:,}")

    # ── Train ──
    history = train_lstm(model, train_loader, val_loader,
                         epochs=args.epochs, lr=args.lr, device=device)

    # ── Evaluate (if ASAP data) ──
    if not args.use_sample:
        print("\n[Evaluation] Running on test set...")
        preds_norm = predict_lstm(model, test_texts, vocab, args.max_len, device)
        metrics = compute_all_metrics(test_scores, preds_norm)
        print_metrics(metrics, "BiLSTM Scorer")
    else:
        preds_norm = predict_lstm(model, train_texts, vocab, args.max_len, device)
        metrics = compute_all_metrics(train_scores, preds_norm)
        print_metrics(metrics, "BiLSTM Scorer (Sample)")

    # ── Save ──
    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, f"lstm_set{args.essay_set}.pt")
    vocab_path = os.path.join(MODELS_DIR, f"vocab_set{args.essay_set}.pkl")
    torch.save(model.state_dict(), model_path)
    with open(vocab_path, "wb") as f:
        pickle.dump(vocab, f)
    save_json(metrics, os.path.join(MODELS_DIR, f"lstm_metrics_set{args.essay_set}.json"))
    print(f"\n[Saved] Model -> {model_path}")
    print(f"[Saved] Vocab  -> {vocab_path}")


if __name__ == "__main__":
    main()
