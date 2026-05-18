"""
preprocessing.py — Text cleaning, tokenization, lemmatization, and sentence splitting.
"""

import re
import string
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data (runs once)
def download_nltk_resources():
    resources = [
        "punkt", "punkt_tab", "stopwords", "wordnet",
        "averaged_perceptron_tagger", "omw-1.4"
    ]
    for r in resources:
        try:
            nltk.download(r, quiet=True)
        except Exception:
            pass

download_nltk_resources()

_lemmatizer = WordNetLemmatizer()
_stop_words = set(stopwords.words("english"))


def clean_text(text: str) -> str:
    """Basic cleaning: lowercase, remove extra whitespace and special chars."""
    if not isinstance(text, str):
        text = str(text)
    text = text.lower()
    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)
    # Remove non-ASCII
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list:
    """Word-level tokenization."""
    try:
        return word_tokenize(text)
    except Exception:
        return text.split()


def remove_stopwords(tokens: list) -> list:
    """Remove common English stopwords."""
    return [t for t in tokens if t not in _stop_words and t not in string.punctuation]


def lemmatize(tokens: list) -> list:
    """Lemmatize a list of word tokens."""
    return [_lemmatizer.lemmatize(t) for t in tokens]


def split_sentences(text: str) -> list:
    """Split text into sentences."""
    try:
        return sent_tokenize(text)
    except Exception:
        return [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]


def preprocess_essay(text: str, remove_stops: bool = False) -> dict:
    """
    Full preprocessing pipeline for a single essay.

    Returns a dict with:
      - original: raw text
      - cleaned: lowercased, normalized text
      - tokens: word tokens (with stopwords)
      - tokens_filtered: without stopwords, lemmatized
      - sentences: list of sentence strings
      - word_count: integer
      - sentence_count: integer
    """
    cleaned = clean_text(text)
    tokens = tokenize(cleaned)
    tokens_no_stop = remove_stopwords(tokens)
    tokens_lemma = lemmatize(tokens_no_stop)
    sentences = split_sentences(text)  # use original for better sentence splitting

    return {
        "original": text,
        "cleaned": cleaned,
        "tokens": tokens,
        "tokens_filtered": tokens_lemma,
        "sentences": sentences,
        "word_count": len([t for t in tokens if t.isalpha()]),
        "sentence_count": len(sentences),
    }


if __name__ == "__main__":
    sample = (
        "The quick brown fox jumps over the lazy dog. "
        "This is an excellent example of a well-formed sentence. "
        "However, some essays lack proper structure and coherence."
    )
    result = preprocess_essay(sample)
    print("=== Preprocessing Demo ===")
    for k, v in result.items():
        print(f"{k}: {v}")
