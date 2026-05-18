"""
features.py — Traditional and deep feature extraction for essay scoring.
"""

import re
import math
import numpy as np
from src.preprocessing import preprocess_essay, split_sentences, tokenize


# ─── Traditional / Handcrafted Features ─────────────────────────────────────

def vocab_richness(tokens: list) -> float:
    """Type-Token Ratio (TTR) — measure of vocabulary diversity."""
    if not tokens:
        return 0.0
    unique = set(tokens)
    return len(unique) / len(tokens)


def avg_word_length(tokens: list) -> float:
    """Average word length in characters."""
    words = [t for t in tokens if t.isalpha()]
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)


def avg_sentence_length(sentences: list) -> float:
    """Average number of words per sentence."""
    if not sentences:
        return 0.0
    total_words = sum(len(tokenize(s)) for s in sentences)
    return total_words / len(sentences)


def count_discourse_markers(text: str) -> int:
    """Count discourse/cohesion markers (however, therefore, furthermore, etc.)."""
    markers = [
        "however", "therefore", "furthermore", "moreover", "consequently",
        "in addition", "on the other hand", "as a result", "in conclusion",
        "for example", "for instance", "in contrast", "although", "despite",
        "because", "since", "thus", "hence", "subsequently", "nevertheless"
    ]
    text_lower = text.lower()
    return sum(text_lower.count(m) for m in markers)


def detect_grammar_errors_detailed(text: str) -> list:
    """
    Heuristic grammar error detector.
    Returns a list of descriptive error strings.
    """
    errors = []
    # Repeated words
    repeated = re.findall(r"\b(\w+)\s+\1\b", text, re.IGNORECASE)
    for word in repeated:
        errors.append(f"Repeated word: '{word}'")
    
    # No space after comma
    no_space_comma = re.findall(r",(?!\s)", text)
    if no_space_comma:
        errors.append(f"Missing space after comma ({len(no_space_comma)} instances)")
    
    # Missing capital after period
    missing_cap = re.findall(r"\.\s+[a-z]", text)
    for match in missing_cap:
        errors.append(f"Missing capitalization after period: '{match}'")
    
    # Double spaces
    double_spaces = re.findall(r"  +", text)
    if double_spaces:
        errors.append(f"Unnecessary double spacing detected ({len(double_spaces)} instances)")
    
    # Lowercase 'i' as pronoun
    lowercase_i = re.findall(r"\bi\b", text)
    if lowercase_i:
        errors.append(f"Lowercase pronoun 'i' detected ({len(lowercase_i)} instances)")

    return errors


def extract_traditional_features(text: str) -> dict:
    """Extract all traditional handcrafted features from an essay."""
    proc = preprocess_essay(text)
    tokens = proc["tokens"]
    sentences = proc["sentences"]
    word_count = proc["word_count"]
    sentence_count = proc["sentence_count"]

    grammar_err_list = detect_grammar_errors_detailed(text)

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_word_length": round(avg_word_length(tokens), 3),
        "avg_sentence_length": round(avg_sentence_length(sentences), 3),
        "vocab_richness": round(vocab_richness([t for t in tokens if t.isalpha()]), 3),
        "discourse_markers": count_discourse_markers(text),
        "grammar_errors": len(grammar_err_list),
        "grammar_error_list": grammar_err_list,
        "char_count": len(text),
    }


# ─── Deep / Embedding Features ───────────────────────────────────────────────

def get_bert_embedding(text: str, model=None, tokenizer=None) -> np.ndarray:
    """
    Extract [CLS] token embedding from BERT.
    Pass in a pre-loaded model and tokenizer to avoid re-loading.
    Returns a 768-dim numpy array.
    """
    import torch
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True,
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    cls_embedding = outputs.last_hidden_state[:, 0, :].squeeze().cpu().numpy()
    return cls_embedding


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


if __name__ == "__main__":
    sample = (
        "Climate change is one of the most pressing issues of our time. "
        "Governments must act immediately to reduce carbon emissions. "
        "However, economic concerns often delay meaningful action. "
        "Therefore, we need both policy changes and technological innovation."
    )
    feats = extract_traditional_features(sample)
    print("=== Traditional Features ===")
    for k, v in feats.items():
        print(f"  {k}: {v}")
