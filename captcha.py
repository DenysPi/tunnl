import asyncio
import random
class Captcha:
    def __init__(self, client_api_key, website_url, website_key, session):
        self.client_api_key = client_api_key
        self.website_url = website_url
        self.website_key = website_key
        self.session = session
    
    async def create_task(self):
        url = "https://api.rucaptcha.com/createTask"
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
        
        data = await response.json()
        return data.get("taskId")
    
    async def get_result(self, task_id):
        url = "https://api.rucaptcha.com/getTaskResult"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "clientKey": self.client_api_key,
            "taskId": task_id
        }
        
        while True:
            print(f"Checking captcha result for task ID: {task_id}")
            response = await self.session.post(url, json=payload, headers=headers)
            
            data = await response.json()
            if data.get("status") == "ready":
                return data.get("solution", {}).get("gRecaptchaResponse")
            await asyncio.sleep(random.uniform(0.3, .7))