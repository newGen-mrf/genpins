import os
import json
import base64
import requests

PINTEREST_ACCESS_TOKEN = os.getenv('PINTEREST_ACCESS_TOKEN')

def get_board_id(board_name: str) -> str:
    url = "https://api.pinterest.com/v5/boards"
    headers = {"Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch boards: {response.text}")
    
    boards = response.json().get("items", [])
    for board in boards:
        if board.get("name") == board_name:
            return board.get("id")
            
    raise Exception(f"Board '{board_name}' not found. Available boards: {[b.get('name') for b in boards]}")

async def upload_pin(image_path: str, title: str, description: str, link: str = '', board_name: str = 'AIProfitLabCash') -> dict:
    """
    Upload a single pin to Pinterest using the official API v5.
    Returns a dict with success flag and pin URL (if any).
    Note: kept async signature so main.py doesn't break.
    """
    result = {'success': False, 'url': None, 'error': None}
    
    if not PINTEREST_ACCESS_TOKEN:
        result['error'] = "PINTEREST_ACCESS_TOKEN is not set in environment variables."
        return result

    try:
        # 1. Fetch Board ID dynamically
        board_id = get_board_id(board_name)
        
        # 2. Convert JPG to Base64 string
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            
        # 3. Prepare payload for Pinterest v5 endpoint
        payload = {
            "board_id": board_id,
            "title": title[:100], # Max 100 chars
            "description": description[:500], # Max 500 chars (safe default)
            "media_source": {
                "source_type": "image_base64",
                "content_type": "image/jpeg",
                "data": encoded_string
            }
        }
        
        if link:
            payload["link"] = link
            
        # 4. Create Pin Request
        url = "https://api.pinterest.com/v5/pins"
        headers = {
            "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            pin_data = response.json()
            pin_id = pin_data.get("id")
            result['success'] = True
            result['url'] = f"https://www.pinterest.com/pin/{pin_id}/"
        else:
            result['error'] = f"API Error {response.status_code}: {response.text}"
            
    except Exception as e:
        result['error'] = str(e)
        
    return result

# Simple CLI for testing
if __name__ == '__main__':
    import argparse
    import asyncio
    parser = argparse.ArgumentParser(description='Upload a Pinterest pin via API')
    parser.add_argument('image', help='Path to image file (.jpg)')
    parser.add_argument('--title', required=True, help='Pin title')
    parser.add_argument('--desc', required=True, help='Pin description')
    parser.add_argument('--link', default='', help='Optional destination link')
    parser.add_argument('--board', default='AIProfitLabCash', help='Board name')
    args = parser.parse_args()
    
    res = asyncio.run(upload_pin(args.image, args.title, args.desc, args.link, args.board))
    print(json.dumps(res, indent=2))
