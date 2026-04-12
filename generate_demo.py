import os
import json
import time
from generator import generate_pin_content
from designer import fetch_background_image, create_pin_design
from dotenv import load_dotenv

load_dotenv()

def run_demo(count=2):
    """
    Runs a full generation cycle for test pins.
    """
    print(f"🚀 Starting Demo Generation ({count} pins)...")
    
    os.makedirs("output", exist_ok=True)
    
    samples = []
    
    for i in range(count):
        print(f"\n--- Generating Pin #{i+1} ---")
        try:
            # 1. Generate content via Gemini
            content = generate_pin_content()
            if not content:
                print("Skipping due to generation error.")
                continue
                
            print(f"Hook: {content['image_text']}")
            
            # 2. Fetch background image
            bg_path = fetch_background_image(content['image_prompt'])
            
            # 3. Design output
            out_path = f"output/demo_pin_{i+1}.jpg"
            create_pin_design(bg_path, content['image_text'], out_path)
            
            # 4. Save metadata for user review
            samples.append({
                "pin_number": i+1,
                "image_path": out_path,
                "title": content['title'],
                "description": content['description'],
                "tags": content.get('hashtags', [])
            })
            
            print(f"✅ Success! Saved to {out_path}")
            
        except Exception as e:
            print(f"❌ Error in pin #{i+1}: {e}")
            
    # Save a summary report
    with open("output/demo_summary.json", "w") as f:
        json.dump(samples, f, indent=4)
        
    print("\n" + "="*30)
    print("Demo Generation Complete!")
    print("Check the 'output/' folder for results.")

if __name__ == "__main__":
    run_demo()
