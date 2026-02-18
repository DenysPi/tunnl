import asyncio
import random
import json
class Captcha:
    def __init__(self, client_api_key, website_url, website_key, session, proxy=None):
        self.client_api_key = client_api_key
        self.website_url = website_url
        self.website_key = website_key
        self.session = session
        # self.proxy= proxy
    
    async def create_task(self):
        url = "https://api.2captcha.com/createTask"
        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "clientKey": self.client_api_key,
            "task": {
                "type": "RecaptchaV2EnterpriseTaskProxyless",
                "websiteURL": self.website_url,
                "websiteKey": self.website_key,
            }
        }
        
        response = await self.session.post(url, json=payload, headers=headers)
        
        text = await response.text()
        data = json.loads(text)
        if data.get("errorId") != 0:
            print("2captcha createTask error:", data.get("errorDescription"))
            return False
        return data.get("taskId")
    
    async def get_result(self, task_id):
        url = "https://api.2captcha.com/getTaskResult"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "clientKey": self.client_api_key,
            "taskId": task_id
        }
        i = 0
        while i !=100:
            response = await self.session.post(url, json=payload, headers=headers)
            
           
            
            text = await response.text()
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                print(f"2captcha bad response: {text[:80]}")
                i += 1
                await asyncio.sleep(1)
                continue
            if data.get("errorId") != 0:
                print(f"Captcha error: {data.get('errorCode')} - {data.get('errorDescription')}")
                return False
            if data.get("status") == "ready":
                print(f"Captcha claimed after {i} secondes")
                solution = data.get("solution", {})
                solution["createTime"] = data.get("createTime", 0)
                return solution
            i += 1
            
            await asyncio.sleep(1)
        return False