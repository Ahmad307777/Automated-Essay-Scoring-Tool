"""
generate_synthetic_data.py - Generate synthetic essay dataset for training
"""
import pandas as pd
import random
import os

# Essay templates by quality level
STRONG_ESSAYS = [
    "Climate change represents one of the most pressing challenges facing humanity today. "
    "Scientific evidence overwhelmingly demonstrates that human activities, particularly the burning of fossil fuels, "
    "are causing unprecedented global temperature rises. Consequently, governments and corporations must take immediate action. "
    "For instance, transitioning to renewable energy sources can dramatically reduce carbon emissions. "
    "Furthermore, international cooperation frameworks are essential to align national policies. "
    "In conclusion, the evidence demands urgent, coordinated global action to avert catastrophic consequences.",
    
    "Technology has fundamentally transformed modern education in profound ways. "
    "Digital tools provide unprecedented access to information and interactive learning experiences. "
    "Research demonstrates that technology enhances student engagement and motivation significantly. "
    "However, critics argue that excessive screen time may hinder social development. "
    "Therefore, educators must strike a careful balance between technological integration and traditional instruction. "
    "Ultimately, when implemented thoughtfully, technology serves as a powerful catalyst for educational innovation.",
    
    "The importance of critical thinking skills cannot be overstated in today's complex world. "
    "Students must learn to analyze information, evaluate sources, and construct logical arguments. "
    "Moreover, critical thinking enables individuals to navigate misinformation and make informed decisions. "
    "Educational institutions should prioritize teaching these essential skills across all disciplines. "
    "By fostering critical thinking, we prepare students for success in both academic and professional contexts. "
    "In summary, critical thinking represents a cornerstone of effective education.",
]

AVERAGE_ESSAYS = [
    "Technology has changed education in many ways. Students now use computers and tablets for homework. "
    "Online platforms provide additional learning resources outside the classroom. "
    "However, not all students have access to technology at home, which creates inequality. "
    "Teachers also need training to use technology effectively. "
    "Despite these challenges, technology generally improves learning outcomes. "
    "Schools should invest more in technology and digital literacy programs.",
    
    "Social media affects teenagers in both positive and negative ways. "
    "It helps them stay connected with friends and family. "
    "However, spending too much time on social media can be harmful. "
    "Some studies show it can lead to anxiety and depression. "
    "Parents should monitor their children's social media use. "
    "Overall, social media is a tool that needs to be used responsibly.",
    
    "Reading books is important for many reasons. "
    "It improves vocabulary and language skills. "
    "Books also help develop imagination and creativity. "
    "Many successful people say they read regularly. "
    "Schools should encourage students to read more. "
    "In conclusion, reading is a valuable habit everyone should develop.",
]

WEAK_ESSAYS = [
    "my favorite subject is math. i like math because its fun. "
    "we learn about numbers and shapes. my teacher is nice. "
    "sometimes math is hard but i try my best. "
    "i want to be good at math when i grow up.",
    
    "computers are good. they help us do things. "
    "i use computer for games and homework. "
    "my mom use computer for work. computers are everywhere now. "
    "everyone should learn how to use computers.",
    
    "i think school is okay. some classes are boring and some are fun. "
    "i like lunch time and recess. homework is too much sometimes. "
    "my friends make school better. teachers are nice most of the time.",
]

PROMPTS = [
    "Discuss the impact of climate change and what should be done about it.",
    "Write about how technology affects education today.",
    "Explain the importance of critical thinking skills.",
    "Discuss the effects of social media on teenagers.",
    "Write about the benefits of reading books.",
    "Describe your favorite subject and why you like it.",
    "Discuss the role of computers in modern life.",
    "Write about your experience in school.",
]

def generate_variation(base_text, variation_level=0.3):
    """Add slight variations to base text"""
    words = base_text.split()
    if random.random() < variation_level:
        # Add filler words
        fillers = ["actually", "basically", "really", "very", "quite", "somewhat"]
        insert_pos = random.randint(0, len(words))
        words.insert(insert_pos, random.choice(fillers))
    return " ".join(words)

def generate_dataset(num_samples=500):
    """Generate synthetic essay dataset"""
    data = []
    essay_id = 1
    
    for _ in range(num_samples):
        # Randomly select quality level
        quality = random.choices(
            ['strong', 'average', 'weak'],
            weights=[0.2, 0.5, 0.3]  # More average essays
        )[0]
        
        if quality == 'strong':
            base_essay = random.choice(STRONG_ESSAYS)
            score = random.randint(9, 12)
        elif quality == 'average':
            base_essay = random.choice(AVERAGE_ESSAYS)
            score = random.randint(5, 8)
        else:
            base_essay = random.choice(WEAK_ESSAYS)
            score = random.randint(2, 4)
        
        # Add variation
        essay = generate_variation(base_essay)
        prompt = random.choice(PROMPTS)
        essay_set = random.randint(1, 3)
        
        data.append({
            'essay_id': essay_id,
            'essay_set': essay_set,
            'essay': essay,
            'domain1_score': score,
            'rater1_domain1': score,
            'rater2_domain1': score,
        })
        essay_id += 1
    
    return pd.DataFrame(data)

def main():
    print("Generating synthetic essay dataset...")
    
    # Generate dataset
    df = generate_dataset(num_samples=500)
    
    # Save to data folder
    os.makedirs('data', exist_ok=True)
    output_path = 'data/training_set_rel3.tsv'
    df.to_csv(output_path, sep='\t', index=False)
    
    print(f"\n✓ Generated {len(df)} synthetic essays")
    print(f"✓ Saved to: {output_path}")
    print(f"\nScore distribution:")
    print(df['domain1_score'].value_counts().sort_index())
    print(f"\nEssay set distribution:")
    print(df['essay_set'].value_counts().sort_index())
    print("\nYou can now run:")
    print("  python train_lstm.py --essay_set 1 --epochs 10")
    print("  python train_bert.py --essay_set 1 --epochs 3")

if __name__ == "__main__":
    main()
