# What is this project?

This is an AI Essay Scoring System. You give it a student essay, it reads it and gives a score out of 100 — just like a teacher, but in seconds. It also tells you what was good and what needs improvement.

It uses 3 AI models:
- BERT — the main model that gives the final score
- LSTM — an older, faster model (also trained, used for comparison)
- GPT-2 — only used to write feedback text, not for scoring

---

# The Big Picture — What happens when you submit an essay?

You open the website, type your essay, click Score Essay. Behind the scenes, 5 things happen one by one. At the end you get a score, a chart, and feedback. That's it.

---

# Step 1 — Cleaning the essay (preprocessing.py)

Before anything, the essay text gets cleaned up.

It converts everything to lowercase. It removes weird characters and extra spaces. Then it splits the essay into individual words (tokens) and into sentences. It also removes common words like "the", "is", "a" and converts words to their root form — so "running" becomes "run", "better" becomes "good".

After this step we have a clean list of words and a list of sentences ready for analysis.

---

# Step 2 — Counting things (features.py)

Now it counts measurable things from the essay:

Word count — how many words total.
Sentence count — how many sentences.
Average sentence length — words divided by sentences.
Vocab richness — how many unique words out of total words. If you use the same 10 words 100 times, richness is low. If you use many different words, richness is high.
Discourse markers — it counts words like "however", "therefore", "furthermore", "in conclusion". These show the essay is well structured.
Grammar errors — it checks simple rules like: did you write "i" instead of "I"? Did you repeat a word twice like "the the"? Is there a missing space after a comma?

These numbers are shown on the screen as the "Extracted Features" section.

---

# Step 3 — Rubric scoring (rubric_scorer.py)

This gives 4 separate scores, each between 0 and 100.

Grammar score — based on how many grammar errors were found. Zero errors = 100%. More errors = lower score.

Coherence score — checks if the essay flows well. It compares each sentence to the next one. If they share similar words and ideas, the essay is coherent. It also gives bonus points for discourse markers like "however" and "therefore".

Relevance score — if you gave a prompt/question, it checks how related the essay is to that question. If no prompt was given, it gives a default middle score.

Argument strength — checks if the essay uses strong argument words like "because", "evidence", "research shows", "in conclusion". Also considers vocab richness and essay length.

Then it combines all 4 into one overall rubric score:
Grammar 25% + Coherence 30% + Relevance 20% + Argument 25%

These 4 scores are shown as the progress bars and radar chart on screen.

---

# Step 4 — BERT gives the final score (bert_model.py)

This is the main AI model. It was trained on 12,000 real student essays from the ASAP Kaggle dataset, where each essay already had a teacher's score.

It takes the essay text and converts it into numbers using a tokenizer. Then it passes those numbers through BERT — a powerful model with 110 million parameters that understands context and meaning of words. BERT produces a 768-number summary of the whole essay. That summary goes through a small neural network that outputs one number between 0 and 1. Multiply by 100 and you get the final score.

This score is what you see as the big number on screen — the Holistic Score.

If BERT is not loaded for some reason, it falls back to using the rubric overall score instead.

---

# Step 5 — Writing feedback (gpt_feedback.py)

After scoring, the system writes a feedback paragraph.

If GPT-2 toggle is OFF — it uses pre-written templates. It picks a template based on the score level (high, medium, or low) and adds specific tips if any dimension scored badly. This is fast and instant.

If GPT-2 toggle is ON — it loads the GPT-2 model (about 500MB, slow on first load). It builds a prompt that includes the score and a piece of the essay, then GPT-2 generates a feedback paragraph from that. This feels more natural but takes longer.

---

# Where does the training data come from?

The file data/training_set_rel3.tsv is the ASAP dataset from Kaggle. It has real student essays written for 8 different prompts. Each essay has a score given by a human teacher.

The scores in the dataset have different ranges for different essay sets. Set 1 goes from 2 to 12. Set 7 goes from 0 to 30. So before training, all scores are converted to a 0 to 1 scale so the model can learn consistently.

The data is split into 80% for training, 10% for validation, 10% for testing.

---

# How were the models trained?

train_bert.py loads the ASAP data, creates a BERT model, and fine-tunes it for 5 epochs using MSE loss. It saves the trained model to models/bert_set1.pt.

train_lstm.py does the same but with a Bidirectional LSTM model — 2 layers, with attention. It trains for 10 epochs and saves to models/lstm_set1.pt.

BERT gets a QWK score of 0.843 (higher is better). LSTM gets 0.721. So BERT is more accurate but uses 110M parameters vs LSTM's 4.2M.

---

# How does the website work?

When you run python app/backend.py, a Flask server starts on localhost:5000. It loads the BERT model into memory right away.

The website (index.html) is what you see in the browser. When you click Score Essay, the JavaScript in app.js sends your essay to the server using a POST request. The server runs all 5 steps above and sends back a JSON response with the score, rubric scores, features, and feedback. The JavaScript then draws the score ring, fills the progress bars, draws the radar chart, and shows the feedback.

There is also a /compare page that shows a table comparing BERT vs LSTM performance.

---

# Now a real example — follow one essay through every step

Essay submitted:
"Technology has changed education in many ways. Students can now access information easily using computers and the internet. However, some teachers believe that too much screen time is harmful for children. Therefore, schools must balance technology use with traditional teaching methods. Furthermore, research shows that interactive digital tools improve student engagement. In conclusion, technology is beneficial for education when used wisely."

Prompt given: "Write about the effects of technology on education."

---

Step 1 — Cleaning:

The text becomes lowercase. It gets split into 6 sentences. Words like "has", "can", "the", "in" are removed. "changed" stays, "using" becomes "use", "harmful" stays. We end up with a clean word list and 6 sentences ready for analysis.

---

Step 2 — Counting:

Word count = 72
Sentence count = 6
Average sentence length = 72 divided by 6 = 12 words per sentence
Vocab richness = about 58 unique words out of 72 total = 80%
Discourse markers found = "however", "therefore", "furthermore", "research shows", "in conclusion" = 5 markers
Grammar errors = 0 (no repeated words, no missing capitals, no lowercase i)

---

Step 3 — Rubric scores:

Grammar: 0 errors, so score = 100%

Coherence: Each sentence pair shares related words (education, technology, schools). Average similarity is around 0.33. Add academic boost of 0.15. Add discourse marker bonus of 5 times 0.04 = 0.20. Final coherence = 0.33 + 0.15 + 0.20 = 0.68 = 68%

Relevance: The essay talks about technology and education, same as the prompt. Similarity is high. Score = 100%

Argument strength: Found keywords — "however", "therefore", "research shows", "in conclusion", "believe", "beneficial" = 6 keywords. Score = 0.4 times 0.6 + 0.3 times 0.80 + 0.3 times 1.0 = 0.78 = 78%

Overall rubric = 0.25 times 100 + 0.30 times 68 + 0.20 times 100 + 0.25 times 78 = 25 + 20.4 + 20 + 19.5 = 84.9%

---

Step 4 — BERT score:

The essay goes into BERT tokenizer. It becomes a sequence of token IDs starting with [CLS]. BERT processes all 12 transformer layers. The [CLS] token comes out as a 768-number vector representing the whole essay's meaning. The regressor network takes that and outputs 0.82. Multiply by 100 = 82 out of 100.

Stars = round(82 divided by 20) = 4 stars
Grade = "Good" (between 70 and 85)

---

Step 5 — Feedback:

GPT-2 is OFF. Score is 0.82 which is above 0.70, so level = "high". Template selected:

"Excellent essay! Your argument is well-structured and clearly supported by evidence. Your use of transitions enhances coherence throughout the piece. To further strengthen your work, consider adding more varied examples and deepening your analysis of counterarguments."

All 4 dimension scores are above 0.5, so no extra warning tips are added.

---

Final result on screen:

Score ring shows 82.0 out of 100, animating from 0.
4 stars appear.
"Good" label in blue.
Grammar bar fills to 100%.
Coherence bar fills to 68%.
Relevance bar fills to 100%.
Argument bar fills to 78%.
Radar chart draws a shape across all 4 dimensions.
Feature tiles show: 72 words, 6 sentences, 12.0 avg length, 80% vocab, 5 discourse markers, 0 errors.
Feedback paragraph appears below.

That is the complete journey of one essay through this system.
