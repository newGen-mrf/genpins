import os
import json
from generator import generate_pin_content
from designer_v2 import get_pollinations_url, generate_premium_pin
from dotenv import load_dotenv

load_dotenv()

def run_premium_demo(count=3):
    """
    Runs a full generation cycle for premium test pins.
    """
    print(f"💎 Starting Premium Demo Generation ({count} pins)...")
    
    os.makedirs("output/v2", exist_ok=True)
    
    samples = []
    
    styles = ["glass", "minimalist", "bold"]
    
    for i in range(count):
        print(f"\n--- Generating Premium Pin #{i+1} ({styles[i % len(styles)]}) ---")
        try:
            # 1. Generate content via Gemini (or Pollinations fallback)
            content = generate_pin_content()
            if not content:
                print("Skipping due to generation error.")
                continue
                
            print(f"Hook: {content['image_text']}")
            
            # 2. Get Pollinations background URL
            bg_url = get_pollinations_url(content['image_prompt'])
            
            # 3. Render HTML to Image via Playwright
            style = styles[i % len(styles)]
            out_path = f"output/v2/premium_pin_{i+1}_{style}.jpg"
            generate_premium_pin(bg_url, content['image_text'], out_path, style=style)
            
            # 4. Save metadata
            samples.append({
                "pin_number": i+1,
                "image_path": out_path,
                "title": content['title'],
                "description": content['description'],
                "tags": content.get('hashtags', [])
            })
            
            print(f"✅ Success! Saved to {out_path}")
            
        except Exception as e:
            print(f"❌ Error in premium pin #{i+1}: {e}")
            
    # Save a summary report
    with open("output/v2/demo_summary.json", "w") as f:
        json.dump(samples, f, indent=4)
        
    print("\n" + "="*30)
    print("Premium Demo Generation Complete!")
    print("Check the 'output/v2/' folder for results.")

if __name__ == "__main__":
    run_premium_demo()
