import json
import os


def get_cookies_from_json(FILE_PATH: str):
    with open(FILE_PATH, "r") as f:
        cookies = json.load(f)
    return cookies
        
def load_cookies_to_json(cookies_dict: dict):
    with open("cookies.json", "w") as f:
        f.write(json.dumps(cookies_dict, indent=4))
        
def update_cookies(FILE_PATH: str, cookies_to_add: dict):
    cookies = get_cookies_from_json(FILE_PATH)
    for key, item in cookies_to_add.items():
        cookies[key] = item
    load_cookies_to_json(cookies)
    
def create_env_for_import():
    if not os.path.exists(".env"):
        with open(".env", "w", encoding="utf-8"):
            pass
        print("File created: .env")
        return True
    else:
        print("File already exists: .env")
        return False
    
