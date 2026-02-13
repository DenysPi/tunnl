import asyncio
import random
import json
class Captcha:
    def __init__(self, client_api_key, website_url, website_key, session, proxy):
        self.client_api_key = client_api_key
        self.website_url = website_url
        self.website_key = website_key
        self.session = session
        self.proxy= proxy
    
    async def create_task(self):
        url = "https://api.capsolver.com/createTask"
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "clientKey": self.client_api_key,
            "task": {
                "type": "ReCaptchaV2EnterpriseTask",
                "websiteURL": self.website_url,
                "websiteKey": self.website_key,
                "proxyType": "http",
                "proxyAddress": self.proxy[0],
                "proxyPort": int(self.proxy[1]),
                "proxyLogin": self.proxy[2],
                "proxyPassword": self.proxy[3]
                
            }
        }
        
        response = await self.session.post(url, json=payload, headers=headers)
        
        text = await response.text()
        data = json.loads(text)
        if data.get("errorId") != 0:
            print("CapMonster createTask error:", data)
            return False
        return data.get("taskId")
    
    async def get_result(self, task_id):
        url = "https://api.capsolver.com/getTaskResult"
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
            data = json.loads(text)
            if data.get("errorId") != 0:
                print(f"Captcha error: {data.get('errorCode')} - {data.get('errorDescription')}")
                return False
            if data.get("status") == "ready":
                print(f"Captcha claimed after {i} secondes")
                return data.get("solution", {}).get("gRecaptchaResponse")
            i += 1
            
            await asyncio.sleep(1)
        return False