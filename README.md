# Automated Essay Scoring with Detailed Feedback

> **NLP Final Year Project** — BiLSTM · BERT · Multi-Dimensional Rubric · Flask Dashboard  
> Dataset: ASAP (Automated Student Assessment Prize)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Project Overview

An AI-powered automated essay scoring system that evaluates student essays using deep learning models and provides detailed multi-dimensional feedback. The system achieves **QWK of 0.782** on the ASAP benchmark dataset, demonstrating near-human-level performance.

### Key Features
- 🤖 **Dual Model Architecture**: BiLSTM + Attention and Fine-tuned BERT
- 📊 **Multi-Dimensional Scoring**: Grammar, Coherence, Relevance, Argument Strength
- 🌐 **Web Dashboard**: Real-time scoring with interactive visualizations
- 📈 **Research-Grade Performance**: QWK 0.782 (BERT), competitive with published papers
- 💬 **Feedback Generation**: GPT-2 based constructive feedback

## 📊 Performance Results

| Model | QWK ↑ | Pearson r ↑ | RMSE ↓ | Inference Speed |
|-------|-------|------------|--------|-----------------|
| **BiLSTM + Attention** | 0.721 | 0.853 | 0.313 | 8ms/essay |
| **BERT (fine-tuned)** | **0.782** | **0.853** | **0.071** | 95ms/essay |

**Key Achievement**: 77% error reduction using BERT vs BiLSTM baseline

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Ahmad307777/Automated-Essay-Scoring-Tool.git
cd Automated-Essay-Scoring-Tool

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -m nltk.downloader punkt stopwords wordnet

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Run Web Application

```bash
python app/backend.py
# Open http://localhost:5000 in your browser
```

### Train Models

```bash
# Train BiLSTM model
python train_lstm.py --essay_set 1 --epochs 15

# Fine-tune BERT model (GPU recommended)
python train_bert.py --essay_set 1 --epochs 5

# Compare models
python compare_models.py
```

## 📁 Project Structure

```
essay_scoring/
├── src/                          # Core modules
│   ├── preprocessing.py          # Text cleaning & tokenization
│   ├── features.py               # Feature extraction
│   ├── lstm_model.py             # BiLSTM + Attention
│   ├── bert_model.py             # BERT regression
│   ├── rubric_scorer.py          # Multi-dimensional scoring
│   ├── gpt_feedback.py           # Feedback generation
│   └── metrics.py                # Evaluation metrics
├── app/                          # Web application
│   ├── backend.py                # Flask REST API
│   ├── templates/index.html      # Frontend
│   └── static/                   # CSS, JS, assets
├── models/                       # Trained models
│   ├── bert_set1.pt              # BERT model
│   ├── lstm_set1.pt              # LSTM model
│   └── *_metrics_set1.json       # Performance metrics
├── train_lstm.py                 # LSTM training script
├── train_bert.py                 # BERT training script
├── compare_models.py             # Model comparison
└── requirements.txt              # Dependencies
```

## 🔬 Technical Details

### Architecture

**BiLSTM Model (4.2M parameters)**
- 100-dim word embeddings
- 2-layer Bidirectional LSTM (256 hidden units)
- Attention mechanism
- Regression head with sigmoid output

**BERT Model (110M parameters)**
- bert-base-uncased (pretrained)
- [CLS] token embedding (768-dim)
- Custom regression head (768 → 256 → 1)
- Fine-tuned on ASAP dataset

### Multi-Dimensional Rubric
- **Grammar**: Heuristic error detection
- **Coherence**: Sentence similarity + discourse markers
- **Relevance**: Essay-prompt cosine similarity
- **Argument Strength**: Keyword density + vocabulary richness

### Evaluation Metrics
- **QWK** (Quadratic Weighted Kappa): Gold standard for AES
- **Pearson r**: Linear correlation
- **RMSE/MAE**: Prediction error

## 📊 Dataset

**ASAP (Automated Student Assessment Prize)**
- Source: Kaggle / Hewlett Foundation
- Size: 12,976 essays across 8 prompts
- Used: Essay Set 1 (1,783 essays)
- Scores: 2-12 point scale
- Split: 80% train / 10% val / 10% test

[Download Dataset](https://www.kaggle.com/c/asap-aes/data)

## 🌐 Web Application

### Features
- Real-time essay scoring
- Interactive score visualization (radar chart, progress bars)
- Feature extraction display
- Multi-dimensional rubric breakdown
- Constructive feedback generation
- Model comparison view

### API Endpoints

**POST /score**
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
  "rubric_scores": {
    "grammar": 85.0,
    "coherence": 67.0,
    "relevance": 74.0,
    "argument_strength": 63.0
  },
  "features": {
    "word_count": 245,
    "sentence_count": 12,
    "vocab_richness": 0.68
  },
  "feedback": "Your essay demonstrates..."
}
```

## 🎓 Academic Use

This project was developed as part of a Natural Language Processing course assignment. 

### Group Members
- **Ahmad Mustafa** - BiLSTM implementation, dataset analysis
- **Aqeel Abbas Khan** - BERT implementation, web application

### Citations
If you use this code in your research, please cite:
```bibtex
@misc{essay_scoring_2026,
  title={Automated Essay Scoring with Multi-Dimensional Feedback},
  author={Mustafa, Ahmad and Khan, Aqeel Abbas},
  year={2026},
  publisher={GitHub},
  url={https://github.com/Ahmad307777/Automated-Essay-Scoring-Tool}
}
```

## 🔧 Requirements

- Python 3.10+
- PyTorch 2.0+
- HuggingFace Transformers 4.30+
- Flask 2.3+
- NLTK, spaCy
- CUDA 11.8+ (optional, for GPU training)

See [requirements.txt](requirements.txt) for complete list.

## 🚧 Future Work

- [ ] Cross-prompt generalization (train on all 8 essay sets)
- [ ] Explainable AI (SHAP analysis, attention visualization)
- [ ] Multilingual support (mBERT, XLM-RoBERTa)
- [ ] Bias detection and mitigation
- [ ] Sentence-level feedback
- [ ] Plagiarism detection integration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- ASAP Dataset: The Hewlett Foundation
- BERT: Google Research
- PyTorch & HuggingFace: Open source community

## 📞 Contact

- Ahmad Mustafa - [GitHub](https://github.com/Ahmad307777)
- Aqeel Abbas Khan - [GitHub](https://github.com/AqeelAbbasKhan)

---

**⭐ Star this repo if you find it helpful!**
