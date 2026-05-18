"""
gpt_feedback.py — Constructive essay feedback generation using GPT-2 (HuggingFace).
Runs fully locally — no API key required.
"""

import re
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer


# ─── Pre-built Template Feedback (fast fallback) ─────────────────────────────

FEEDBACK_TEMPLATES = {
    "high": [
        "Excellent essay! Your argument is well-structured and clearly supported by evidence. "
        "Your use of transitions enhances coherence throughout the piece. "
        "To further strengthen your work, consider adding more varied examples and deepening your analysis of counterarguments.",

        "Outstanding work! The essay demonstrates strong command of language and logical reasoning. "
        "Your introduction effectively sets up the discussion, and the conclusion nicely ties everything together. "
        "A minor suggestion: explore alternative perspectives to make your argument even more persuasive.",
    ],
    "medium": [
        "Your essay shows a good understanding of the topic, but there is room for improvement. "
        "The main argument is present but could benefit from stronger supporting evidence. "
        "Work on improving transitions between paragraphs to enhance the overall flow and coherence. "
        "Consider expanding your vocabulary and varying sentence structure for better readability.",

        "The essay demonstrates potential but needs refinement. Your ideas are on the right track, "
        "however the argument lacks depth in several places. "
        "Focus on providing concrete examples and data to support your claims. "
        "Also, review grammatical correctness and ensure consistent paragraph structure throughout.",
    ],
    "low": [
        "Your essay needs significant improvement. The argument is unclear and the essay lacks "
        "proper structure. Begin by organizing your thoughts with a clear introduction, body paragraphs, "
        "and conclusion. Each paragraph should have one main idea supported by evidence. "
        "Pay attention to grammar, spelling, and punctuation. Consider using discourse markers "
        "like 'however', 'therefore', and 'furthermore' to improve coherence.",

        "The essay requires considerable revision. Start by clearly defining your main argument in "
        "the introduction. Body paragraphs should each develop one idea with supporting evidence. "
        "The writing lacks coherence — use transition words to connect ideas logically. "
        "Please proofread carefully for grammatical errors before submission.",
    ],
}


def _get_template_feedback(score_normalized: float, dimension_scores: dict) -> str:
    """Return a template-based feedback string based on performance level."""
    import random

    # Choose level
    if score_normalized >= 0.7:
        level = "high"
    elif score_normalized >= 0.4:
        level = "medium"
    else:
        level = "low"

    base = random.choice(FEEDBACK_TEMPLATES[level])

    # Append dimension-specific tips
    tips = []
    if dimension_scores.get("grammar", 1.0) < 0.6:
        tips.append("[!] Grammar: Multiple grammatical errors detected. Review subject-verb agreement and punctuation.")
    if dimension_scores.get("coherence", 1.0) < 0.5:
        tips.append("[!] Coherence: Paragraphs feel disconnected. Add transition sentences between ideas.")
    if dimension_scores.get("relevance", 1.0) < 0.5:
        tips.append("[!] Relevance: Some sections drift off-topic. Keep your writing focused on the essay prompt.")
    if dimension_scores.get("argument_strength", 1.0) < 0.5:
        tips.append("[!] Argument: Claims need stronger evidence. Use research, statistics, or examples to support your points.")

    if tips:
        base += "\n\n**Specific Suggestions:**\n" + "\n".join(tips)

    return base


# ─── GPT-2 Model Wrapper ──────────────────────────────────────────────────────

class GPTFeedbackGenerator:
    """
    Generates constructive essay feedback using GPT-2.
    Falls back to template-based feedback if GPU is unavailable or model fails.
    """

    def __init__(self, model_name: str = "gpt2", max_new_tokens: int = 200):
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cpu")  # GPT-2 runs on CPU for small scale
        self._loaded = False

    def load(self):
        """Lazily load GPT-2 model and tokenizer."""
        if self._loaded:
            return
        try:
            print(f"\n[GPT-2] Loading '{self.model_name}'...")
            print("[GPT-2] Note: If this is the first time, it will download ~500MB from Hugging Face.")
            print("[GPT-2] This may take 2-5 minutes depending on your internet speed.")
            self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model = GPT2LMHeadModel.from_pretrained(self.model_name)
            self.model.eval().to(self.device)
            self._loaded = True
            print("[GPT-2] Model loaded successfully [OK]")
        except Exception as e:
            print(f"[GPT-2] Warning: could not load model: {e}")
            self._loaded = False

    def _build_prompt(self, essay_excerpt: str, overall_score: float,
                      dimension_scores: dict) -> str:
        """Build a structured prompt for GPT-2 to generate useful feedback."""
        score_pct = int(overall_score * 100)
        grammar_pct = int(dimension_scores.get("grammar", 0.5) * 100)
        coherence_pct = int(dimension_scores.get("coherence", 0.5) * 100)
        relevance_pct = int(dimension_scores.get("relevance", 0.5) * 100)
        argument_pct = int(dimension_scores.get("argument_strength", 0.5) * 100)

        prompt = (
            f"Essay feedback report:\n"
            f"Overall Score: {score_pct}/100 | Grammar: {grammar_pct}% | "
            f"Coherence: {coherence_pct}% | Relevance: {relevance_pct}% | "
            f"Argument: {argument_pct}%\n\n"
            f"Essay excerpt: \"{essay_excerpt[:300]}...\"\n\n"
            f"Detailed teacher feedback: The essay"
        )
        return prompt

    def generate(self, essay: str, overall_score: float,
                 dimension_scores: dict, use_gpt: bool = True) -> str:
        """
        Generate feedback for an essay.

        Args:
            essay: Full essay text
            overall_score: Normalized [0,1] overall score
            dimension_scores: Dict with grammar, coherence, relevance, argument_strength
            use_gpt: If True, try to use GPT-2; else use template

        Returns:
            str: Constructive feedback paragraph
        """
        if use_gpt:
            self.load()

        if use_gpt and self._loaded:
            try:
                prompt = self._build_prompt(essay, overall_score, dimension_scores)
                inputs = self.tokenizer(
                    prompt, return_tensors="pt",
                    truncation=True, max_length=400
                ).to(self.device)

                with torch.no_grad():
                    output_ids = self.model.generate(
                        **inputs,
                        max_new_tokens=self.max_new_tokens,
                        do_sample=True,
                        temperature=0.8,
                        top_p=0.9,
                        pad_token_id=self.tokenizer.eos_token_id,
                        repetition_penalty=1.3,
                    )

                full_text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
                # Extract only the generated part after the prompt
                generated = full_text[len(prompt):].strip()
                # Clean and truncate at sentence boundary
                sentences = re.split(r"(?<=[.!?])\s+", generated)
                feedback = " ".join(sentences[:5]).strip()
                if feedback:
                    return "The essay " + feedback
            except Exception as e:
                print(f"[GPT-2] Generation error: {e}. Falling back to template.")

        # Fallback: rich template-based feedback
        return _get_template_feedback(overall_score, dimension_scores)


# ─── Singleton Instance ───────────────────────────────────────────────────────

_feedback_generator = None


def get_feedback_generator() -> GPTFeedbackGenerator:
    global _feedback_generator
    if _feedback_generator is None:
        _feedback_generator = GPTFeedbackGenerator()
    return _feedback_generator


def generate_feedback(essay: str, overall_score: float,
                      dimension_scores: dict, use_gpt: bool = True) -> str:
    """Top-level convenience function for generating feedback."""
    gen = get_feedback_generator()
    return gen.generate(essay, overall_score, dimension_scores, use_gpt=use_gpt)


if __name__ == "__main__":
    sample_essay = (
        "Climate change threatens our planet. Many scientists agree on this. "
        "We should do something about it. Governments are too slow. "
        "People can help by recycling and using less plastic."
    )
    dim_scores = {"grammar": 0.75, "coherence": 0.45, "relevance": 0.6, "argument_strength": 0.35}
    feedback = generate_feedback(sample_essay, 0.45, dim_scores, use_gpt=False)
    print("=== Generated Feedback ===\n")
    print(feedback)
