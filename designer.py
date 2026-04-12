import os
import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import urllib.parse

def fetch_background_image(prompt, size=(1000, 1500)):
    """
    Fetches a background image from Pollinations.ai based on a prompt.
    """
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={size[0]}&height={size[1]}&model=flux&nologo=true"
    
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs("assets", exist_ok=True)
        path = os.path.join("assets", "bg_base.jpg")
        with open(path, "wb") as f:
            f.write(response.content)
        return path
    else:
        raise Exception(f"Failed to fetch image: {response.status_code}")

def get_font(size):
    """
    Attempts to find a suitable bold font on the system.
    """
    possible_fonts = [
        "C:\\Windows\\Fonts\\impact.ttf",
        "C:\\Windows\\Fonts\\ariblk.ttf",
        "C:\\Windows\\Fonts\\segoeuib.ttf",
        "arial.ttf"
    ]
    for font_path in possible_fonts:
        try:
            return ImageFont.truetype(font_path, size)
        except:
            continue
    return ImageFont.load_default()

def create_pin_design(bg_path, text, output_path):
    """
    Adds text overlay and darkens background for mobile-readability.
    """
    img = Image.open(bg_path)
    
    # 1. Darken image slightly for better text contrast
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.6) # 60% brightness
    
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # 2. Add BIG text
    # Split text into lines if too long
    words = text.split()
    lines = []
    if len(words) > 3:
        lines = [" ".join(words[:2]), " ".join(words[2:])]
    else:
        lines = [text]
    
    font_size = 120
    font = get_font(font_size)
    
    # Calculate starting Y to center text vertically or place in top/middle
    total_text_height = sum([draw.textbbox((0, 0), line, font=font)[3] for line in lines])
    current_y = (height - total_text_height) // 2
    
    for line in lines:
        line = line.upper() # Design rule: BIG text often looks better in caps
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        # Add a subtle shadow/glow for extra pop
        shadow_offset = 5
        draw.text(((width - text_w) // 2 + shadow_offset, current_y + shadow_offset), line, font=font, fill=(0, 0, 0))
        
        # Main text (White or Vibrant Yellow)
        draw.text(((width - text_w) // 2, current_y), line, font=font, fill=(255, 255, 255))
        current_y += text_h + 20
        
    img.save(output_path, quality=95)
    return output_path

if __name__ == "__main__":
    # Test Design
    bg = fetch_background_image("modern dark workspace with glowing laptop and money on desk")
    create_pin_design(bg, "AI MAKES MONEY", "assets/test_pin.jpg")
    print("Test pin saved to assets/test_pin.jpg")
