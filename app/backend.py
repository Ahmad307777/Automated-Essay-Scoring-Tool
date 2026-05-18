"""
backend.py — Flask REST API server for the Essay Scoring System.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import torch
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from src.preprocessing import preprocess_essay
from src.features import extract_traditional_features
from src.rubric_scorer import score_essay, scores_to_percent
from src.gpt_feedback import generate_feedback
from src.bert_model import BertScorer, predict_bert, load_bert_tokenizer
from compare_models import get_live_metrics

app = Flask(__name__)
CORS(app)

# ─── Load BERT Model at Startup ─────────────────────────────────────────────
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
BERT_MODEL_PATH = os.path.join(MODELS_DIR, "bert_set1.pt")
BERT_TOK_PATH = os.path.join(MODELS_DIR, "bert_tokenizer_set1")

_bert_model = None
_bert_tokenizer = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_models():
    global _bert_model, _bert_tokenizer
    if os.path.exists(BERT_MODEL_PATH):
        try:
            print(f"[Backend] Loading BERT model from {BERT_MODEL_PATH}...")
            _bert_tokenizer = load_bert_tokenizer("bert-base-uncased") # Fallback to base
            _bert_model = BertScorer()
            _bert_model.load_state_dict(torch.load(BERT_MODEL_PATH, map_location=_device))
            _bert_model.to(_device)
            _bert_model.eval()
            print("[Backend] BERT model loaded successfully.")
        except Exception as e:
            print(f"[Backend] Error loading BERT: {e}")

load_models()

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/score", methods=["POST"])
def score():
    """
    POST /score
    Body: { "essay": "...", "prompt": "..." (optional), "use_gpt": true/false }
    Returns: { scores, features, feedback, preprocessing }
    """
    data = request.get_json(force=True)
    essay = (data.get("essay") or "").strip()
    prompt = (data.get("prompt") or "").strip()
    use_gpt = bool(data.get("use_gpt", False))

    if not essay or len(essay.split()) < 5:
        return jsonify({"error": "Essay is too short. Please enter at least 5 words."}), 400

    try:
        # 1. Rubric Pipeline (Heuristic Feedback)
        proc = preprocess_essay(essay)
        feats = extract_traditional_features(essay)
        dimension_scores = score_essay(essay, prompt)
        pct_rubric = scores_to_percent(dimension_scores)

        # 2. Deep Learning Model (Holistic Prediction)
        if _bert_model is not None:
            # Predict using the fine-tuned BERT model
            pred_norm = predict_bert(_bert_model, [essay], _bert_tokenizer, device=_device)[0]
            holistic_score = round(pred_norm * 100, 1)
            source = "BERT AI Model"
        else:
            # Fallback to weighted rubric if model not trained yet
            holistic_score = round(dimension_scores["overall"] * 100, 1)
            source = "Formulaic Weighted Average (Heuristic)"

        # 3. Feedback Generation
        feedback = generate_feedback(essay, holistic_score / 100.0, dimension_scores, use_gpt=use_gpt)

        # Stars out of 5
        stars = min(5, max(1, round(holistic_score / 20)))

        return jsonify({
            "holistic_score": holistic_score,
            "scoring_source": source,
            "stars": stars,
            "rubric_scores": pct_rubric,
            "features": {
                "word_count": feats["word_count"],
                "sentence_count": feats["sentence_count"],
                "avg_sentence_length": feats["avg_sentence_length"],
                "vocab_richness": feats["vocab_richness"],
                "discourse_markers": feats["discourse_markers"],
                "grammar_errors": feats["grammar_errors"],
                "grammar_error_list": feats["grammar_error_list"],
            },
            "feedback": feedback,
            "word_count": proc["word_count"],
            "sentence_count": proc["sentence_count"],
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/compare")
def compare():
    """GET /compare — Return live model comparison data."""
    table = []
    live_results = get_live_metrics()
    for model_name, metrics in live_results.items():
        table.append({
            "model": model_name,
            "QWK": metrics["QWK"],
            "Pearson_r": metrics["Pearson_r"],
            "RMSE": metrics["RMSE"],
            "MAE": metrics["MAE"],
            "speed": metrics["Speed_secs_per_essay"],
            "params_M": metrics["Parameters_M"],
            "notes": metrics["notes"],
        })
    return jsonify(table)


@app.route("/health")
def health():
    return jsonify({
        "status": "ok", 
        "service": "Essay Scoring API v1.1",
        "bert_loaded": _bert_model is not None
    })


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  [OK] Automatic Essay Scoring System")
    print("  Starting Flask server on http://localhost:5000")
    print("=" * 55 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
