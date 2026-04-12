import os
import json
import argparse
import subprocess
import asyncio
from datetime import datetime, date

# Import generation function (assumes generate_demo_v2 provides a function)
from generate_demo_v2 import run_premium_demo

# Import uploader
from uploader import upload_pin

STATE_FILE = os.path.join('db', 'state.json')

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"last_run_date": "1970-01-01", "pins_posted_today": 0, "day_counter": 0}
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def allowed_pins(state):
    # Determine day number since start
    today_str = date.today().isoformat()
    if state["last_run_date"] != today_str:
        # new day, reset counter and increment day_counter
        state["last_run_date"] = today_str
        state["pins_posted_today"] = 0
        state["day_counter"] += 1
    # First two days: 5 pins, thereafter 10
    return 5 if state["day_counter"] < 2 else 10

def main(generate: bool = False, post: bool = False):
    state = load_state()
    if generate:
        # Run generation demo (creates pins in output/v2)
        print("Generating premium pins...")
        run_premium_demo(count=allowed_pins(state))
    if post:
        # Find generated pins
        pin_dir = os.path.join('output', 'v2')
        pins = [os.path.join(pin_dir, f) for f in os.listdir(pin_dir) if f.lower().endswith('.jpg')]
        # Sort to ensure deterministic order
        pins.sort()
        posted = 0
        for pin_path in pins:
            if posted >= allowed_pins(state) - state["pins_posted_today"]:
                break
            title = os.path.splitext(os.path.basename(pin_path))[0]
            description = f"Automated pin generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            print(f"Uploading: {pin_path}...")
            result = asyncio.run(upload_pin(pin_path, title, description))
            
            if result.get('success'):
                posted += 1
                print(f"Posted: {result.get('url')}")
            else:
                print(f"Failed to post {pin_path}: {result.get('error')}")
        # Update state
        state["pins_posted_today"] += posted
        save_state(state)
        print(f"Posted {posted} pins this run. Total today: {state['pins_posted_today']}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pinterest automation pipeline')
    parser.add_argument('--generate', action='store_true', help='Run generation step')
    parser.add_argument('--post', action='store_true', help='Run posting step')
    args = parser.parse_args()
    main(generate=args.generate, post=args.post)
