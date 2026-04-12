import os
import json
import google.generativeai as genai
import requests
from dotenv import load_dotenv

load_dotenv()

def call_pollinations(prompt):
    """Uses Pollinations AI's OpenAI-compatible text endpoint. Completely free, no keys."""
    url = "https://text.pollinations.ai/openai"
    payload = {
        "model": "openai",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85,
        "max_tokens": 1000
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Pollinations AI failed: {e}")
        return None

def generate_pin_content(pillar=None):
    """
    Generates viral Pinterest pin content using Gemini API.
    Pillars: AI Money Methods, AI Tools, Passive Income Ideas
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    selected_pillar = pillar or "💰 AI Money Methods (How to make money with AI)"
    
    prompt = f"""
    You are a viral Pinterest marketing expert. Generate a high-converting Pinterest pin idea for the pillar: {selected_pillar}
    
    Follow these strict rules from the strategy plan:
    1. TITLE: Use Formula: [Number] + [Keyword] + [Curiosity]. 
    2. IMAGE TEXT: Exactly 3-6 words, high-impact hook.
    3. DESCRIPTION: Keyword-rich, SEO optimized (include 3-5 keywords).
    4. HASHTAGS: Exactly 5 relevant hashtags.
    
    Output ONLY a JSON object with these keys:
    - image_text
    - title
    - description
    - hashtags (as a list)
    - image_prompt (detailed prompt for an image generator, cinematic lighting, 1000x1500)
    """

    # Try Gemini 2.0 Flash first (as used in GenVid)
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            return parse_ai_json(response.text)
        except Exception as e:
            print(f"Gemini 2.0 Flash failed: {e}. Trying Pollinations...")

    # Fallback to Pollinations AI (100% Free)
    res_text = call_pollinations(prompt)
    if res_text:
        print(f"Pollinations Raw Text: {res_text[:200]}...")
        return parse_ai_json(res_text)
    
    return None

def parse_ai_json(text):
    try:
        result_text = text.strip()
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        
        # Sometimes AI adds extra text before or after JSON
        if "{" in result_text and "}" in result_text:
            result_text = result_text[result_text.find("{"):result_text.rfind("}")+1]
            
        return json.loads(result_text)
    except Exception as e:
        print(f"Error parsing AI JSON: {e}")
        print(f"Attempted to parse: {text[:500]}")
        return None

if __name__ == "__main__":
    # Test generation
    print("Testing Pin Generation...")
    content = generate_pin_content()
    print(json.dumps(content, indent=4))
