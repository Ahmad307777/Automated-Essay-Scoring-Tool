"""
test_essay.py - Quick command-line essay scoring test
Usage: python test_essay.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.rubric_scorer import score_essay, scores_to_percent
from src.gpt_feedback import generate_feedback

# Sample essays
ESSAYS = {
    "1": {
        "title": "Strong Essay - Climate Change",
        "text": """Climate change represents one of the most pressing challenges facing humanity today. Scientific evidence overwhelmingly demonstrates that human activities, particularly the burning of fossil fuels, are causing unprecedented global temperature rises. The consequences of inaction are dire, including rising sea levels, extreme weather events, and ecosystem collapse.

Governments and corporations must take immediate, decisive action to address this crisis. For instance, transitioning to renewable energy sources like solar and wind power can dramatically reduce carbon emissions. Furthermore, reforestation programs and sustainable agricultural practices offer complementary solutions that can help absorb existing carbon dioxide from the atmosphere.

However, economic interests often hinder progress toward meaningful climate action. Therefore, international cooperation frameworks such as the Paris Agreement are essential to align national policies and ensure accountability. Developed nations must also provide financial and technological support to developing countries to facilitate their transition to clean energy.

In conclusion, the scientific evidence unequivocally demands urgent, coordinated global action to avert catastrophic and irreversible climate consequences. The time for debate has passed; now is the time for action.""",
        "prompt": "Discuss the impact of climate change and what should be done about it."
    },
    "2": {
        "title": "Average Essay - Technology in Education",
        "text": """Technology has changed education in many ways. Students now use computers and tablets to complete their homework and research assignments. Online platforms like Khan Academy provide additional learning resources outside the classroom.

However, not all students have access to technology at home, which creates inequality. Some families cannot afford computers or internet connections. Teachers also need training to use technology effectively in their lessons.

Despite these challenges, technology generally improves learning outcomes for students who have access to it. Schools should invest more in technology and digital literacy programs. They should also provide devices to students who need them.""",
        "prompt": "Write about how technology affects education today."
    },
    "3": {
        "title": "Weak Essay - My Favorite Animal",
        "text": """my favorite animal is dog. dogs are nice and fun to play with. i have a dog his name is max. max is brown and have big ears. he like to eat food and sleep on the sofa. dogs are the best pet in the world because they are loyal. everyone should have a dog.""",
        "prompt": "Write about your favorite animal."
    }
}

def score_and_display(essay_data):
    """Score an essay and display results"""
    print("\n" + "="*70)
    print(f"  {essay_data['title']}")
    print("="*70)
    
    essay = essay_data['text']
    prompt = essay_data['prompt']
    
    print(f"\nPrompt: {prompt}")
    print(f"\nEssay ({len(essay.split())} words):")
    print(f"{essay[:200]}..." if len(essay) > 200 else essay)
    
    # Score the essay
    scores = score_essay(essay, prompt)
    pct = scores_to_percent(scores)
    
    # Display rubric scores
    print("\n" + "-"*70)
    print("RUBRIC SCORES:")
    print("-"*70)
    
    dimensions = [
        ("Grammar", pct['grammar']),
        ("Coherence", pct['coherence']),
        ("Relevance", pct['relevance']),
        ("Argument Strength", pct['argument_strength']),
    ]
    
    for dim, score in dimensions:
        bar = "█" * int(score / 5)
        print(f"  {dim:<20}: {bar:<20} {score:.1f}%")
    
    print("-"*70)
    overall_bar = "█" * int(pct['overall'] / 5)
    stars = "⭐" * int((pct['overall'] / 100) * 5)
    print(f"  {'OVERALL SCORE':<20}: {overall_bar:<20} {pct['overall']:.1f}%")
    print(f"  {'STAR RATING':<20}: {stars}")
    
    # Generate feedback
    feedback = generate_feedback(essay, scores['overall'], scores, use_gpt=False)
    print("\n" + "-"*70)
    print("AI FEEDBACK:")
    print("-"*70)
    print(feedback)
    print()

def main():
    print("\n" + "="*70)
    print("  AUTOMATIC ESSAY SCORING - COMMAND LINE TEST")
    print("="*70)
    print("\nAvailable Essays:")
    for key, data in ESSAYS.items():
        print(f"  [{key}] {data['title']}")
    
    print("\n[0] Score all essays")
    print("[q] Quit")
    
    while True:
        choice = input("\nSelect essay number (0-3, q to quit): ").strip()
        
        if choice.lower() == 'q':
            print("\nGoodbye!")
            break
        elif choice == '0':
            for key in sorted(ESSAYS.keys()):
                score_and_display(ESSAYS[key])
            break
        elif choice in ESSAYS:
            score_and_display(ESSAYS[choice])
            break
        else:
            print("Invalid choice. Please enter 0, 1, 2, 3, or q")

if __name__ == "__main__":
    main()
