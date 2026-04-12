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
    email_input = page.locator('input[type="email"], input[name="email"], input[id="email"], input[autocomplete="username"]').first
    await email_input.fill(PINTEREST_EMAIL)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(2000)
    password_input = page.locator('input[type="password"], input[name="password"], input[id="password"], input[autocomplete="current-password"]').first
    await password_input.fill(PINTEREST_PASSWORD)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(5000)
    try:
        await page.wait_for_url('**/pinterest.com/**', timeout=15000)
    except:
        await page.screenshot(path="output/v2/login_debug.png")
        current_url = page.url
        print(f"Login didn't redirect. Current URL: {current_url}")
        raise

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
            await page.wait_for_timeout(2000)
            await page.set_input_files('input[type="file"]', image_path)
            await page.wait_for_timeout(3000)
            title_field = page.locator('textarea').first
            await title_field.fill(title)
            desc_field = page.locator('textarea').nth(1)
            await desc_field.fill(description)
            if link:
                link_field = page.locator('input[type="url"], input[placeholder*="destination"], input[placeholder*="link"]').first
                await link_field.fill(link)
            board_btn = page.locator('div[role="combobox"], div[data-test-id="board-select-button"], button:has-text("Board")').first
            await board_btn.click(force=True)
            await page.wait_for_timeout(1000)
            board_option = page.locator(f'text="{board_name}", div[role="option"]:has-text("{board_name}")').first
            await board_option.click()
            await page.wait_for_timeout(1000)
            save_btn = page.locator('button[type="submit"], button:has-text("Save"), button[data-test-id="pin-create-save-button"]').first
            await save_btn.click()
            await page.wait_for_timeout(5000)
            pin_url = page.url
            result['success'] = True
            result['url'] = pin_url
            await browser.close()
    except Exception as e:
        result['error'] = str(e)
        try:
            if 'page' in locals():
                await page.screenshot(path="output/v2/error_screenshot.png")
                print(f"Saved error screenshot to output/v2/error_screenshot.png. Current URL: {page.url}")
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
