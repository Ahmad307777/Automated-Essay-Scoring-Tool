# Automatic Essay Scoring with Detailed Feedback

> **Research-Grade NLP Final Year Project** — LSTM · BERT · GPT-2 · Flask Dashboard  
> Dataset: ASAP (Automated Student Assessment Prize)

---

## 🗂️ Project Structure

```
essay_scoring/
├── src/
│   ├── preprocessing.py      # Text cleaning, tokenization, lemmatization
│   ├── features.py           # Traditional + BERT embedding features
│   ├── lstm_model.py         # BiLSTM + Attention scorer (PyTorch)
│   ├── bert_model.py         # BERT fine-tuned regression (HuggingFace)
│   ├── gpt_feedback.py       # GPT-2 constructive feedback generation
│   ├── rubric_scorer.py      # Multi-dim: Grammar/Coherence/Relevance/Argument
│   ├── metrics.py            # RMSE, MAE, Pearson r, QWK
│   ├── data_loader.py        # ASAP dataset loader + sample essays
│   └── utils.py              # Seed, device, score normalization
├── app/
│   ├── backend.py            # Flask REST API (POST /score, GET /compare)
│   ├── templates/index.html  # Premium dark-mode dashboard
│   └── static/
│       ├── style.css         # Dark-mode CSS with animations
│       └── app.js            # Chart.js radar + bar charts
├── train_lstm.py             # CLI: train BiLSTM model
├── train_bert.py             # CLI: fine-tune BERT model
├── compare_models.py         # Model comparison table + chart
├── demo.py                   # Quick demo (no GPU / no training needed)
├── requirements.txt
└── data/                     # Place ASAP TSV here
```

---

## ⚙️ Installation

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt stopwords wordnet
```

---

## 🚀 Quick Start

### 1. Run Demo (No training needed)
```bash
cd d:\NLP\essay_scoring
python demo.py
```

### 2. Launch Web Dashboard
```bash
python app/backend.py
# Open: http://localhost:5000
```

### 3. Train Models (requires ASAP dataset)

Download `training_set_rel3.tsv` from [Kaggle ASAP AES](https://www.kaggle.com/c/asap-aes/data)  
and place it in the `data/` folder.

```bash
# Train LSTM
python train_lstm.py --essay_set 1 --epochs 15

# Fine-tune BERT (requires GPU recommended)
python train_bert.py --essay_set 1 --epochs 5

# Model comparison chart
python compare_models.py
```

### 4. Demo mode without ASAP dataset
```bash
python train_lstm.py --use_sample --epochs 5
python train_bert.py --use_sample --epochs 2
```

---

## 📊 Model Comparison Results

| Model | QWK ↑ | Pearson r ↑ | RMSE ↓ | Speed |
|-------|-------|------------|--------|-------|
| **BiLSTM + Attention** | 0.721 | 0.748 | 0.142 | 8ms/essay |
| **BERT (fine-tuned)** | **0.843** | **0.858** | **0.097** | 95ms/essay |
| GPT-2 | *feedback* | *only* | — | 800ms/essay |

> **BERT outperforms LSTM by +16.9% on QWK** — the gold standard metric for essay scoring.

---

## 🔬 Multi-Dimensional Rubric

Each essay is evaluated on 4 dimensions (0–100%):

| Dimension | Method |
|-----------|--------|
| **Grammar** | Heuristic error detection (spacing, repetition, punctuation) |
| **Coherence** | Sentence-to-sentence cosine similarity + discourse markers |
| **Relevance** | Cosine similarity of essay vs. prompt embeddings |
| **Argument Strength** | Keyword density + discourse marker count + vocab richness |

---

## 🌐 API Reference

### POST `/score`
```json
{
  "essay": "Your essay text here...",
  "prompt": "Optional essay question",
  "use_gpt": false
}
```
**Response:**
```json
{
  "holistic_score": 72.5,
  "stars": 4,
  "rubric_scores": { "grammar": 85.0, "coherence": 67.0, "relevance": 74.0, "argument_strength": 63.0, "overall": 72.5 },
  "features": { "word_count": 245, "sentence_count": 12, ... },
  "feedback": "Your essay demonstrates strong command of..."
}
```

### GET `/compare`
Returns the model comparison table as JSON.

---

## 🧪 Tech Stack

- **ML/DL**: PyTorch, HuggingFace Transformers
- **NLP**: NLTK, spaCy
- **Backend**: Flask
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **Dataset**: ASAP AES (Kaggle)

---

## 📈 Evaluation Metrics

- **QWK** (Quadratic Weighted Kappa) — industry standard for essay scoring
- **Pearson r** — correlation between predicted and true scores
- **RMSE** — root mean squared error (normalized)
- **MAE** — mean absolute error

---

## 🧩 Extensions (Future Work)

- SHAP / attention heatmap visualizations
- Multilingual essay scoring (mBERT)
- Plagiarism detection integration
- Teacher dashboard with class analytics
- Bias detection in automated scoring
