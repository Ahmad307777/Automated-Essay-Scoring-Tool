"""
test_api.py - Direct API test to verify backend is working
"""
import requests
import json

API_URL = "http://localhost:5000/score"

# Test essay
essay = """Climate change represents one of the most pressing challenges facing humanity today. Scientific evidence overwhelmingly demonstrates that human activities, particularly the burning of fossil fuels, are causing unprecedented global temperature rises. The consequences of inaction are dire, including rising sea levels, extreme weather events, and ecosystem collapse.

Governments and corporations must take immediate, decisive action to address this crisis. For instance, transitioning to renewable energy sources like solar and wind power can dramatically reduce carbon emissions. Furthermore, reforestation programs and sustainable agricultural practices offer complementary solutions that can help absorb existing carbon dioxide from the atmosphere.

However, economic interests often hinder progress toward meaningful climate action. Therefore, international cooperation frameworks such as the Paris Agreement are essential to align national policies and ensure accountability. Developed nations must also provide financial and technological support to developing countries to facilitate their transition to clean energy.

In conclusion, the scientific evidence unequivocally demands urgent, coordinated global action to avert catastrophic and irreversible climate consequences. The time for debate has passed; now is the time for action."""

prompt = "Discuss the impact of climate change and what should be done about it."

print("=" * 70)
print("TESTING ESSAY SCORING API")
print("=" * 70)

# Test 1: Without GPT
print("\n[TEST 1] Scoring without GPT-2 feedback...")
response = requests.post(API_URL, json={
    "essay": essay,
    "prompt": prompt,
    "use_gpt": False
})

if response.status_code == 200:
    result = response.json()
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Holistic Score: {result['holistic_score']}/100")
    print(f"✓ Stars: {'⭐' * result['stars']}")
    print(f"✓ Scoring Source: {result.get('scoring_source', 'N/A')}")
    print(f"\n✓ Rubric Scores:")
    for key, val in result['rubric_scores'].items():
        print(f"  - {key}: {val:.1f}%")
    print(f"\n✓ Features:")
    print(f"  - Words: {result['features']['word_count']}")
    print(f"  - Sentences: {result['features']['sentence_count']}")
    print(f"  - Vocab Richness: {result['features']['vocab_richness']:.3f}")
    print(f"  - Grammar Errors: {result['features']['grammar_errors']}")
    print(f"\n✓ Feedback (first 200 chars):")
    print(f"  {result['feedback'][:200]}...")
else:
    print(f"✗ Error: {response.status_code}")
    print(f"  {response.text}")

# Test 2: With GPT
print("\n" + "=" * 70)
print("[TEST 2] Scoring WITH GPT-2 feedback (slower)...")
response2 = requests.post(API_URL, json={
    "essay": essay,
    "prompt": prompt,
    "use_gpt": True
})

if response2.status_code == 200:
    result2 = response2.json()
    print(f"✓ Status: {response2.status_code}")
    print(f"✓ Holistic Score: {result2['holistic_score']}/100")
    print(f"\n✓ GPT-2 Feedback:")
    print(f"  {result2['feedback']}")
else:
    print(f"✗ Error: {response2.status_code}")
    print(f"  {response2.text}")

print("\n" + "=" * 70)
print("API TEST COMPLETE")
print("=" * 70)
print("\nIf both tests passed, the backend is working correctly!")
print("If the web interface isn't showing results, it's a frontend issue.")
