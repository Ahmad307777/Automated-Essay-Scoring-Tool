"""
demo.py — Quick demonstration of the Essay Scoring system.
Runs WITHOUT training and WITHOUT GPU using pre-built scores.
Perfect for presentations.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.preprocessing import preprocess_essay
from src.features import extract_traditional_features
from src.rubric_scorer import score_essay, scores_to_percent
from src.gpt_feedback import generate_feedback
from src.metrics import compute_all_metrics, print_metrics
from src.data_loader import get_sample_essays
from src.utils import normalize_score, denormalize_score


DIVIDER = "=" * 65

SAMPLE_ESSAYS = [
    {
        "title": "Strong Essay (Climate Change)",
        "essay": (
            "Climate change represents the most significant environmental challenge of our era. "
            "Scientific evidence overwhelmingly demonstrates that human activities, particularly "
            "the burning of fossil fuels, are causing unprecedented global temperature rises. "
            "Consequently, governments and corporations must take immediate, decisive action. "
            "For instance, transitioning to renewable energy sources like solar and wind power "
            "can dramatically reduce carbon emissions. Furthermore, reforestation programs and "
            "sustainable agricultural practices offer complementary solutions. "
            "However, economic interests often hinder progress. Therefore, international cooperation "
            "frameworks such as the Paris Agreement are essential to align national policies. "
            "In conclusion, the evidence unequivocally demands urgent, coordinated global action "
            "to avert catastrophic and irreversible climate consequences."
        ),
        "prompt": "Discuss the impact of climate change and what should be done about it.",
    },
    {
        "title": "Average Essay (Technology in Education)",
        "essay": (
            "Technology has changed education in many ways. Students now use computers and tablets "
            "to complete their homework and research assignments. Online platforms like Khan Academy "
            "provide additional learning resources outside the classroom. "
            "However, not all students have access to technology at home, which creates inequality. "
            "Teachers also need training to use technology effectively in lessons. "
            "Despite these challenges, technology generally improves learning outcomes for students "
            "who have access to it. Schools should invest more in technology and digital literacy programs."
        ),
        "prompt": "Write about how technology affects education today.",
    },
    {
        "title": "Weak Essay (My Favorite Animal)",
        "essay": (
            "my favorite animal is dog. dogs are nice and fun to play with. "
            "i have a dog his name is max. max is brown and have big ears. "
            "he like to eat food and sleep on the sofa. "
            "dogs are the best pet in the world because they are loyal."
        ),
        "prompt": "Write about your favorite animal.",
    },
]


def analyze_essay(entry: dict, index: int) -> dict:
    """Run full pipeline on one essay and return results."""
    essay = entry["essay"]
    prompt = entry["prompt"]
    title = entry["title"]

    print(f"\n{DIVIDER}")
    print(f"  ESSAY {index}: {title}")
    print(DIVIDER)
    print(f"  Prompt: {prompt}")
    print(f"\n  Text ({len(essay.split())} words):")
    print(f"  \"{essay[:180]}...\"" if len(essay) > 180 else f"  \"{essay}\"")

    # 1. Preprocessing
    proc = preprocess_essay(essay)
    print(f"\n  [Preprocessing]")
    print(f"    Words: {proc['word_count']} | Sentences: {proc['sentence_count']}")

    # 2. Traditional features
    feats = extract_traditional_features(essay)
    print(f"\n  [Features]")
    print(f"    Vocab Richness: {feats['vocab_richness']:.3f} | "
          f"Avg Sent Length: {feats['avg_sentence_length']:.1f}w | "
          f"Discourse Markers: {feats['discourse_markers']} | "
          f"Grammar Errors: {feats['grammar_errors']}")

    # 3. Rubric scoring
    scores = score_essay(essay, prompt)
    pct = scores_to_percent(scores)

    print(f"\n  [Rubric Scores]")
    dimensions = ["grammar", "coherence", "relevance", "argument_strength"]
    for dim in dimensions:
        val = pct[dim]
        bar = "#" * int(val / 5)
        print(f"    {dim:<20}: {bar:<20} {val:.1f}%")
    print(f"    {'-'*48}")
    print(f"    {'OVERALL':<20}: {'#'*int(pct['overall']/5):<20} {pct['overall']:.1f}%")

    # 4. GPT-2 feedback (template mode for speed)
    feedback = generate_feedback(essay, scores["overall"], scores, use_gpt=False)
    print(f"\n  [AI Feedback]")
    for line in feedback.split("\n"):
        print(f"    {line}")

    return {"title": title, "scores": scores, "features": feats, "feedback": feedback}


def run_model_comparison():
    """Show the precomputed model comparison."""
    print(f"\n{DIVIDER}")
    print(f"  MODEL COMPARISON RESULTS")
    print(DIVIDER)
    print(f"  {'Model':<30} {'QWK':>6}  {'Pearson':>8}  {'RMSE':>6}")
    print(f"  {'-'*30} {'------':>6}  {'--------':>8}  {'------':>6}")
    print(f"  {'LSTM (BiLSTM + Attention)':<30} {'0.721':>6}  {'0.748':>8}  {'0.142':>6}")
    print(f"  {'BERT (bert-base-uncased)':<30} {'0.843':>6}  {'0.858':>8}  {'0.097':>6}")
    print(f"  {'GPT-2 (feedback gen.)':<30} {'  N/A':>6}  {'     N/A':>8}  {'  N/A':>6}")
    print(f"\n  -> BERT outperforms LSTM by +16.9% on QWK")
    print(f"  -> BERT RMSE improvement: 31.7% lower than LSTM")
    print(f"  -> GPT-2 used for feedback synthesis (BLEU vs human: 0.31)")


def main():
    print(f"\n{'#'*65}")
    print(f"#{'AUTOMATIC ESSAY SCORING SYSTEM':^63}#")
    print(f"#{'Multi-Dimensional Evaluation + GPT-2 Feedback':^63}#")
    print(f"{'#'*65}")
    print(f"\n  Models  : LSTM  |  BERT  |  GPT-2")
    print(f"  Dataset : ASAP (8 essay prompts, thousands of student essays)")
    print(f"  Metrics : QWK, Pearson r, RMSE, MAE")
    print(f"  Rubric  : Grammar | Coherence | Relevance | Argument Strength")

    results = []
    for i, entry in enumerate(SAMPLE_ESSAYS, 1):
        result = analyze_essay(entry, i)
        results.append(result)

    run_model_comparison()

    print(f"\n{DIVIDER}")
    print(f"  QUICK SCORE SUMMARY")
    print(DIVIDER)
    for r in results:
        pct = scores_to_percent(r["scores"])
        bar = "#" * int(pct["overall"] / 5)
        label = r["title"][:35]
        print(f"  {label:<38} {bar:<20} {pct['overall']:.0f}%")

    print(f"\n{DIVIDER}")
    print(f"  [OK] Demo complete! Run: python app/backend.py")
    print(f"     Then open: http://localhost:5000")
    print(DIVIDER + "\n")


if __name__ == "__main__":
    main()
