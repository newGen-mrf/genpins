import os
import requests
import asyncio
from playwright.async_api import async_playwright
import urllib.parse

# Style 1: Glassmorphism (Modern, Tech)
TEMPLATE_GLASS = """
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@800&family=Playfair+Display:wght@900&display=swap" rel="stylesheet">
<style>
    body, html {{
        margin: 0; padding: 0;
        width: 1000px; height: 1500px;
        overflow: hidden;
        font-family: 'Montserrat', sans-serif;
    }}
    .container {{
        width: 1000px; height: 1500px;
        background: url('{bg_url}') center/cover no-repeat;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        position: relative;
    }}
    .overlay {{
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.4);
    }}
    .glass-card {{
        position: relative;
        z-index: 10;
        width: 80%;
        padding: 50px 30px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 40px;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
        text-align: center;
    }}
    h1 {{
        margin: 0;
        font-size: 85px;
        color: #FFFFFF;
        text-transform: uppercase;
        letter-spacing: -2px;
        line-height: 1.1;
    }}
    .divider {{
        width: 100px; height: 8px;
        background: #FFD700;
        margin: 30px auto;
        border-radius: 4px;
    }}
</style>
</head>
<body>
    <div class="container">
        <div class="overlay"></div>
        <div class="glass-card">
            <h1>{main_text}</h1>
            <div class="divider"></div>
        </div>
    </div>
</body>
</html>
"""

# Style 2: Minimalist Luxury (Serif, Clean)
TEMPLATE_MINIMALIST = """
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Montserrat:wght@400&display=swap" rel="stylesheet">
<style>
    body, html {{
        margin: 0; padding: 0;
        width: 1000px; height: 1500px;
        overflow: hidden;
        background: #F4F1EA;
        font-family: 'Playfair Display', serif;
    }}
    .container {{
        width: 1000px; height: 1500px;
        display: flex; flex-direction: column;
        align-items: center; justify-content: flex-start;
        position: relative;
    }}
    .image-frame {{
        width: 100%; height: 60%;
        background: url('{bg_url}') center/cover no-repeat;
    }}
    .content {{
        width: 100%; height: 40%;
        padding: 60px 80px;
        box-sizing: border-box;
        display: flex; flex-direction: column;
        align-items: flex-start;
        background: #FFF;
    }}
    .tag {{
        font-family: 'Montserrat', sans-serif;
        font-size: 24px; color: #888;
        letter-spacing: 4px; margin-bottom: 20px;
        text-transform: uppercase;
    }}
    h1 {{
        margin: 0; font-size: 72px; color: #1a1a1a;
        line-height: 1.2; font-weight: 700;
    }}
</style>
</head>
<body>
    <div class="container">
        <div class="image-frame"></div>
        <div class="content">
            <div class="tag">AI STRATEGY</div>
            <h1>{main_text}</h1>
        </div>
    </div>
</body>
</html>
"""

# Style 3: Viral Bold (High Contrast, Yellow/Black)
TEMPLATE_BOLD = """
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&display=swap" rel="stylesheet">
<style>
    body, html {{
        margin: 0; padding: 0;
        width: 1000px; height: 1500px;
        overflow: hidden;
        background: #FFD700;
        font-family: 'Archivo Black', sans-serif;
    }}
    .container {{
        width: 1000px; height: 1500px;
        display: flex; flex-direction: column;
        align-items: center; justify-content: flex-end;
    }}
    .image-circle {{
        width: 1200px; height: 1200px;
        border-radius: 50%;
        background: url('{bg_url}') center/cover no-repeat;
        position: absolute; top: -200px;
        border: 20px solid #000;
    }}
    .text-box {{
        width: 100%;
        padding: 100px 50px;
        background: #000;
        color: #FFD700;
        text-align: center;
        z-index: 10;
    }}
    h1 {{
        margin: 0; font-size: 110px;
        line-height: 1.0; text-transform: uppercase;
    }}
</style>
</head>
<body>
    <div class="container">
        <div class="image-circle"></div>
        <div class="text-box">
            <h1>{main_text}</h1>
        </div>
    </div>
</body>
</html>
"""

async def render_pin(html_content, output_path):
    """
    Renders HTML content to a high-quality JPEG using Playwright.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1000, "height": 1500})
        
        # Set content and wait for fonts/images to load
        await page.set_content(html_content, wait_until="networkidle")
        
        # Capture screenshot
        await page.screenshot(path=output_path, type="jpeg", quality=95)
        await browser.close()
        return output_path

def generate_premium_pin(bg_url, text, output_path, style="glass"):
    """
    Synchronous wrapper to generate the pin design with style selection.
    """
    # Clean/Format text for HTML
    formatted_text = text.upper()
    
    # Choose template
    templates = {
        "glass": TEMPLATE_GLASS,
        "minimalist": TEMPLATE_MINIMALIST,
        "bold": TEMPLATE_BOLD
    }
    
    html = templates.get(style, TEMPLATE_GLASS).format(
        bg_url=bg_url,
        main_text=formatted_text
    )
    
    # Run async renderer
    asyncio.run(render_pin(html, output_path))
    return output_path

def get_pollinations_url(prompt, size=(1000, 1500)):
    """
    Returns a Pollinations.ai image URL for a given prompt.
    """
    encoded_prompt = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={size[0]}&height={size[1]}&model=flux&nologo=true"

if __name__ == "__main__":
    # Test Premium Design
    test_prompt = "modern dark workspace with glowing laptop and money on desk"
    test_bg = get_pollinations_url(test_prompt)
    generate_premium_pin(test_bg, "AI MAKES MONEY", "assets/premium_test.jpg")
    print("Premium test pin saved to assets/premium_test.jpg")
