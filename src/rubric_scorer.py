"""
rubric_scorer.py — Multi-dimensional essay scoring: Grammar, Coherence, Relevance, Argument Strength.
All scores are returned in [0.0, 1.0] range.
"""

import re
import numpy as np
from src.preprocessing import split_sentences, clean_text
from src.features import (
    count_discourse_markers,
    detect_grammar_errors_detailed,
    vocab_richness,
    cosine_similarity,
)


# ─── Grammar Score ───────────────────────────────────────────────────────────

def score_grammar(text: str) -> float:
    """
    Grammar score based on heuristic error detection.
    Fewer errors -> higher score.
    Scale: max ~20 errors -> 0.0 score, 0 errors -> 1.0 score.
    """
    errors = detect_grammar_errors_detailed(text)
    error_count = len(errors)
    # Normalize: assume >20 errors is very bad
    penalty = min(error_count / 20.0, 1.0)
    return round(1.0 - penalty, 3)


# ─── Coherence Score ─────────────────────────────────────────────────────────

def _get_tokens_for_sim(text: str) -> list:
    """Helper to get clean, lowercase tokens for similarity comparison."""
    # Basic cleaning and tokenization
    text = re.sub(r'[^\w\s]', '', text.lower())
    tokens = text.split()
    # Filter out very common short stop words to focus on content
    stops = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with'}
    return [t for t in tokens if t not in stops and len(t) > 2]


def _simple_sentence_vector(sentence: str) -> np.ndarray:
    """
    Stable bag-of-words sentence vector using character hashing (zlib) to 512-dim.
    zlib.adler32 is stable across Python processes, unlike hash().
    """
    import zlib
    tokens = _get_tokens_for_sim(sentence)
    vec = np.zeros(512, dtype=np.float32)
    for t in tokens:
        # Use a stable hash to map to 512 buckets
        idx = zlib.adler32(t.encode()) % 512
        vec[idx] += 1.0
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


def score_coherence(text: str) -> float:
    """
    Coherence score based on inter-sentence similarity and discourse markers.
    Improved to be more generous to academic-style transitions.
    """
    sentences = split_sentences(text)
    if len(sentences) < 2:
        return 0.5

    vecs = [_simple_sentence_vector(s) for s in sentences]
    similarities = []
    for i in range(len(vecs) - 1):
        sim = cosine_similarity(vecs[i], vecs[i + 1])
        similarities.append(sim)
    
    # Average similarity with a slight 'academic boost' (0.1) as 
    # dense academic texts often use synonyms rather than direct repeats.
    avg_sim = float(np.mean(similarities)) if similarities else 0.5
    
    # Discourse marker bonus: 0.04 per marker, max 0.3
    dm_count = count_discourse_markers(text)
    dm_bonus = min(dm_count * 0.04, 0.3)

    return round(min(avg_sim + 0.15 + dm_bonus, 1.0), 3)


# ─── Relevance Score ─────────────────────────────────────────────────────────

def score_relevance(essay: str, prompt: str) -> float:
    """
    Relevance score: cosine similarity between essay and prompt.
    Increased sensitivity to main keywords.
    """
    if not prompt or not prompt.strip():
        return 0.5
        
    v_essay = _simple_sentence_vector(clean_text(essay))
    v_prompt = _simple_sentence_vector(clean_text(prompt))
    sim = cosine_similarity(v_essay, v_prompt)
    
    # Relevance Boost: If similarity is non-zero, it gets a significant multiplier
    # because even partial overlap of key topics indicates high relevance.
    boosted_sim = sim * 1.5 if sim > 0 else 0
    
    return round(max(min(boosted_sim + 0.2, 1.0), 0.0), 3)


# ─── Argument Strength Score ─────────────────────────────────────────────────

ARGUMENT_KEYWORDS = [
    "because", "therefore", "thus", "hence", "consequently", "proves",
    "demonstrates", "evidence", "research shows", "studies", "data",
    "example", "for instance", "illustrates", "supports", "argument",
    "claim", "assert", "contend", "conclude", "in summary", "in conclusion",
    "position", "perspective", "viewpoint", "opinion", "believe", "suggests",
]


def score_argument_strength(text: str) -> float:
    """
    Argument strength based on:
      1. Presence of logical connectors and claim keywords
      2. Vocabulary richness (broader vocab → stronger argument)
      3. Essay length (very short essays are penalized)
    """
    text_lower = text.lower()
    words = text_lower.split()

    # Keyword density
    keyword_hits = sum(1 for kw in ARGUMENT_KEYWORDS if kw in text_lower)
    keyword_score = min(keyword_hits / 10.0, 1.0)  # 10+ keywords → full score

    # Vocabulary richness
    alpha_words = [w for w in words if w.isalpha()]
    vr = vocab_richness(alpha_words)

    # Length penalty for very short essays (< 50 words)
    length_penalty = min(len(alpha_words) / 50.0, 1.0)

    score = 0.4 * keyword_score + 0.3 * vr + 0.3 * length_penalty
    return round(max(min(score, 1.0), 0.0), 3)


# ─── Combined Rubric Scorer ──────────────────────────────────────────────────

def score_essay(text: str, prompt: str = "") -> dict:
    """
    Full multi-dimensional rubric scoring of an essay.

    Returns dict with keys:
      grammar, coherence, relevance, argument_strength, overall
    All values are in [0.0, 1.0].
    """
    grammar = score_grammar(text)
    coherence = score_coherence(text)
    relevance = score_relevance(text, prompt)
    argument = score_argument_strength(text)

    # Weighted average: argument and coherence matter most
    overall = round(
        0.25 * grammar +
        0.30 * coherence +
        0.20 * relevance +
        0.25 * argument,
        3
    )

    return {
        "grammar": grammar,
        "coherence": coherence,
        "relevance": relevance,
        "argument_strength": argument,
        "overall": overall,
    }


def scores_to_percent(scores: dict) -> dict:
    """Convert [0,1] scores to percentage (0-100) for display."""
    return {k: round(v * 100, 1) for k, v in scores.items()}


if __name__ == "__main__":
    sample_essay = (
        "Climate change is one of the most critical challenges of the 21st century. "
        "Scientists have provided ample evidence that global temperatures are rising due to "
        "greenhouse gas emissions. Therefore, governments must implement strict policies to "
        "reduce carbon footprints. For example, investing in renewable energy like solar and wind "
        "power can significantly decrease reliance on fossil fuels. However, economic interests "
        "often prevent meaningful action. Consequently, a balance between growth and sustainability "
        "is essential. In conclusion, the evidence strongly supports immediate climate action."
    )
    prompt = "Write an essay discussing the impact of climate change and what should be done."

    scores = score_essay(sample_essay, prompt)
    print("=== Rubric Scores ===")
    for k, v in scores.items():
        bar = "█" * int(v * 20)
        print(f"  {k:<20}: {v:.3f} [{bar:<20}] {v*100:.1f}%")
