import os
import json
import asyncio
from playwright.async_api import async_playwright

try:
    from playwright_stealth import stealth_async
except ImportError:
    try:
        from playwright_stealth import stealth_sync as stealth_async
    except ImportError:
        # Fallback dummy stealth function if library is broken
        async def stealth_async(page):
            pass


# Environment variables for credentials
PINTEREST_EMAIL = os.getenv('PINTEREST_EMAIL')
PINTEREST_PASSWORD = os.getenv('PINTEREST_PASSWORD')

async def _login(page):
    await page.goto('https://www.pinterest.com/login/')
    await page.wait_for_timeout(2000)
    await page.wait_for_selector('input[name="id"]')
    await page.fill('input[name="id"]', PINTEREST_EMAIL)
    await page.keyboard.press('Enter')
    # Wait for password field
    await page.wait_for_timeout(1000)
    await page.wait_for_selector('input[name="password"]')
    await page.fill('input[name="password"]', PINTEREST_PASSWORD)
    await page.keyboard.press('Enter')
    # Wait for home page to load
    await page.wait_for_selector('div[data-test-id="homepage-feed"]', timeout=20000)

async def upload_pin(image_path: str, title: str, description: str, link: str = '', board_name: str = 'AIProfitLabCash') -> dict:
    """Upload a single pin to Pinterest.
    Returns a dict with success flag and pin URL (if any)."""
    result = {'success': False, 'url': None, 'error': None}
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            try:
                await stealth_async(page)
            except Exception as e:
                print(f"Stealth application failed, proceeding without it: {e}")
            await _login(page)
            # Skip homepage clutters and navigate directly to the Pin Builder
            await page.wait_for_timeout(2000)
            await page.goto('https://www.pinterest.com/pin-creation/tool/')
            # Upload image
            await page.set_input_files('input[type="file"]', image_path)
            # Fill title and description
            await page.fill('textarea[data-test-id="pin-create-title"]', title)
            await page.fill('textarea[data-test-id="pin-create-description"]', description)
            if link:
                await page.fill('input[data-test-id="pin-create-destination-url"]', link)
            # Select board
            await page.click('div[data-test-id="board-select-button"]', force=True)
            await page.wait_for_selector(f'div[role="listbox"] div:has-text("{board_name}")')
            await page.click(f'div[role="listbox"] div:has-text("{board_name}")', force=True)
            # Publish
            await page.click('button[data-test-id="pin-create-save-button"]', force=True)
            # Wait for pin to appear and capture URL
            await page.wait_for_selector('a[data-test-id="pin-link"]', timeout=15000)
            pin_url = await page.get_attribute('a[data-test-id="pin-link"]', 'href')
            result['success'] = True
            result['url'] = pin_url
            await browser.close()
    except Exception as e:
        result['error'] = str(e)
        try:
            if 'page' in locals():
                await page.screenshot(path="output/v2/error_screenshot.png")
                print("Saved error screenshot to output/v2/error_screenshot.png")
        except:
            pass
    return result

# Simple CLI for testing
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Upload a Pinterest pin')
    parser.add_argument('image', help='Path to image file')
    parser.add_argument('--title', required=True, help='Pin title')
    parser.add_argument('--desc', required=True, help='Pin description')
    parser.add_argument('--link', default='', help='Optional destination link')
    parser.add_argument('--board', default='AIProfitLabCash', help='Board name')
    args = parser.parse_args()
    res = asyncio.run(upload_pin(args.image, args.title, args.desc, args.link, args.board))
    print(json.dumps(res, indent=2))
