"""
data_loader.py — ASAP dataset loading and train/val/test splitting.
The ASAP dataset (TSV format) is loaded from data/ folder.
Download from: https://www.kaggle.com/c/asap-aes/data
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from src.utils import normalize_score, ASAP_SCORE_RANGES


DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "training_set_rel3.tsv")


def load_asap(essay_set: int = 1, path: str = None) -> pd.DataFrame:
    """
    Load the ASAP dataset for a specific essay set.

    Args:
        essay_set: Integer 1-8 (ASAP has 8 prompts)
        path: Custom path to the TSV file

    Returns:
        DataFrame with columns: essay_id, essay_set, essay, domain1_score, norm_score
    """
    filepath = path or DATASET_PATH
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"ASAP dataset not found at: {filepath}\n"
            "Please download from: https://www.kaggle.com/c/asap-aes/data\n"
            "and place 'training_set_rel3.tsv' in the data/ folder."
        )

    # Try multiple encodings
    try:
        df = pd.read_csv(filepath, sep="\t", encoding="utf-8")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(filepath, sep="\t", encoding="windows-1252")
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, sep="\t", encoding="latin-1")
    df.columns = [c.lower().strip() for c in df.columns]

    # Filter to essay set
    df = df[df["essay_set"] == essay_set].copy()
    df = df.dropna(subset=["essay", "domain1_score"])
    df["essay"] = df["essay"].astype(str)

    # Normalize score to [0, 1]
    df["norm_score"] = df["domain1_score"].apply(
        lambda s: normalize_score(s, essay_set)
    )

    return df[["essay_id", "essay_set", "essay", "domain1_score", "norm_score"]]


def load_all_sets(path: str = None) -> pd.DataFrame:
    """Load all 8 essay sets combined."""
    frames = []
    for es in range(1, 9):
        try:
            frames.append(load_asap(es, path))
        except Exception as e:
            print(f"Warning: could not load essay set {es}: {e}")
    if not frames:
        raise RuntimeError("No essay sets could be loaded.")
    return pd.concat(frames, ignore_index=True)


def split_dataset(df: pd.DataFrame, val_size: float = 0.1, test_size: float = 0.1,
                  random_state: int = 42):
    """
    Split DataFrame into train / val / test sets (stratified on rounded score).
    Returns: (train_df, val_df, test_df)
    """
    # Stratify bucket
    df = df.copy()
    df["score_bucket"] = (df["norm_score"] * 5).round().astype(int)

    train_df, temp_df = train_test_split(
        df, test_size=(val_size + test_size), random_state=random_state,
        stratify=df["score_bucket"]
    )
    relative_test = test_size / (val_size + test_size)
    val_df, test_df = train_test_split(
        temp_df, test_size=relative_test, random_state=random_state,
        stratify=temp_df["score_bucket"]
    )

    for split, name in [(train_df, "Train"), (val_df, "Val"), (test_df, "Test")]:
        print(f"{name}: {len(split)} samples | "
              f"Score mean: {split['norm_score'].mean():.3f} ± {split['norm_score'].std():.3f}")

    return train_df.drop("score_bucket", axis=1), \
           val_df.drop("score_bucket", axis=1), \
           test_df.drop("score_bucket", axis=1)


def get_sample_essays() -> list:
    """
    Return 5 hand-crafted sample essays for demo/testing when ASAP is unavailable.
    Each item is (essay_text, raw_score, essay_set).
    """
    return [
        (
            "Dear local newspaper, I think effects computers have on people are great learning "
            "skills/affects in our society. "
            "Computers and the internet help us to gain knowledge in life and to use "
            "computers and internet technology as people. "
            "It's great for kids because they need to learn about what's going out in the world. "
            "However, people shouldn't rely too much on computers and the internet because it can "
            "make them lazy, unfit, and forget important social skills.",
            9, 1
        ),
        (
            "The article 'The Challenge of Exploring Venus' presents scientists as explorers and "
            "highlights the difficulties in space exploration. "
            "The author emphasizes that Venus is the closest planet to Earth and yet "
            "one of the least explored due to its extremely hostile environment. "
            "Temperatures on Venus can reach 465°C, and its atmosphere is composed mainly of "
            "carbon dioxide and sulfuric acid clouds. "
            "Despite these challenges, scientists remain determined to explore Venus using "
            "advanced robotic spacecraft. "
            "The author concludes that the scientific rewards of exploring Venus justify the "
            "risks and expenses involved.",
            10, 1
        ),
        (
            "i think computors are good because you can lean stuff on them. "
            "they help you with homewrk and stuff. "
            "my mom uses the computor for her job. "
            "computors are fun to use. i like playing games and watching videos.",
            3, 1
        ),
        (
            "The advent of technology has profoundly transformed modern education, "
            "fundamentally altering how students acquire, process, and retain knowledge. "
            "Digital tools such as computers, tablets, and educational platforms provide "
            "unprecedented access to information and interactive learning experiences. "
            "Consequently, traditional pedagogical methods are being supplemented or replaced "
            "by technology-driven approaches. Furthermore, research demonstrates that technology "
            "enhances student engagement and motivation. However, critics argue that excessive "
            "screen time may hinder social development and critical thinking skills. "
            "Therefore, educators must strike a careful balance between technological integration "
            "and traditional instruction to optimize student outcomes.",
            11, 1
        ),
        (
            "Technology affects our daily lives significantly. "
            "We use phones and computers every day. "
            "Some people think this is bad for society because we depend on machines too much. "
            "Others believe technology makes everything easier and faster. "
            "I think both sides have good points, but overall technology is beneficial. "
            "We should use it wisely and not let it control us completely.",
            7, 1
        ),
    ]


if __name__ == "__main__":
    print("=== Sample Essays (Demo Mode) ===")
    for i, (essay, score, es) in enumerate(get_sample_essays(), 1):
        norm = normalize_score(score, es)
        print(f"\n[Essay {i}] Score: {score}/12 (norm: {norm:.2f})")
        print(f"  {essay[:100]}...")
