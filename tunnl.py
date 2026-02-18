
from twitter_client import TwitterClient
from captcha import Captcha
from helpers import *
from config import *
import logging
import asyncio
import time
import config

class Tunnl:
    def __init__(self, auth_client: str, user_agent: str, version: int, platform: str, captcha_key: str, session, proxy):
        self.auth_client = auth_client
        self.user_agent = user_agent
        self.version = version
        self.platform = platform
        self.captcha_key = captcha_key
        self.session = session
        
        self.twitter = None
        self.bearer = None
        
        self.ranks = ["PURPLE", "BRONZE_1", "BRONZE_2", "BRONZE_3", "SILVER_1", "SILVER_2", "SILVER_3"]
        self.my_rank = None
        self.campaign_ids_cliked = []
        
        self.captcha = Captcha(
            client_api_key=captcha_key,
            website_url="https://app.tunnl.io",
            website_key="6LdWAF8sAAAAAFLZSh3ttweah9XLSPG_df3wzCGT",
            session=session,
            # proxy=proxy
        )
        self.captcha_solution = None
        self.captcha_timestamp = 0
        self.captcha_ttl = 60

    async def refresh_captcha_loop(self):
        while True:
            try:
                now = time.time()
                if not self.captcha_solution or (now - self.captcha_timestamp) >= self.captcha_ttl:
                    logging.info("Pre-solving captcha...")
                    for _ in range(3):
                        task_id = await self.captcha.create_task()
                        if not task_id:
                            logging.warning("Failed to create captcha task, retrying...")
                            continue
                        solution = await self.captcha.get_result(task_id)
                        if solution:
                            self.captcha_solution = solution
                            self.captcha_timestamp = solution["createTime"] / 1000
                            logging.info("Captcha ready to use")
                            break
                    else:
                        logging.error("Failed to pre-solve captcha")
            except Exception as e:
                logging.error(f"Captcha loop error: {e}")
            await asyncio.sleep(10)

    def consume_captcha(self):
        solution = self.captcha_solution
        self.captcha_solution = None
        self.captcha_timestamp = 0
        return solution

    async def  get_my_rank(self):
        url = "https://api-tunnl-mainnet-6l3nt.ondigitalocean.app/profile/me"
        headers = { 
            'Authorization': f'Bearer {self.bearer}',
            "User-Agent": self.user_agent   
        }
        response =  await self.session.get(url, headers=headers )
        data = await response.json()  
        
        return data.get("tier")
        
    async def get_auth_token(self, identity_token, token):
        url = "https://api-tunnl-mainnet-6l3nt.ondigitalocean.app/auth/authenticate"
        headers = {
            "User-Agent": self.user_agent
        }
        payload = {
            "identityToken": identity_token,
            "token": token,
            
        }
        
        response =  await self.session.post(url, headers=headers, json=payload )
        data = await response.json()  
        return data.get("token")
        
        
    def set_twitter(self):
        self.twitter = TwitterClient(
            auth_token=self.auth_client,
            user_agent=self.user_agent,
            version=self.version,
            platform=self.platform,
            session=self.session
        )
    
    async def connect_tunnl_via_twitter(self):
    
        

        status, data = await self.twitter.start_connect_twitter()
        if status:
            token = data.get("token")
            identity_token = data.get("identity_token")
            self.bearer = await self.get_auth_token(identity_token, token)
            return True
            
        
        return None
    
    # async def valid_session(self):
    #     url = "https://privy.tunnl.io/api/v1/sessions"
    #     cookies = get_cookies_from_json(FILE_PATH)
        
    #     response = await self.session.get(url, )
        
    async def get_campaigns(self):
        url = "https://api-tunnl-mainnet-6l3nt.ondigitalocean.app/campaigns"
        params  = {
            "sort_by": "created_at",
            "order": "desc",
            "page": 1,
            "page_size": 4
        }
        headers = {
            'Authorization': f'Bearer {self.bearer}',
            "User-Agent": self.user_agent
        }
        
        
        
        response =  await self.session.get(url, headers=headers, params=params )
        if response.status == 200:
            data = await response.json()  
            return data
            
        else: 
            return False
    
    async def get_campaign_rank_req(self, id_campaign):
        url = f"https://api-tunnl-mainnet-6l3nt.ondigitalocean.app/campaigns/{id_campaign}"
        headers = {

            'Authorization': f'Bearer {self.bearer}',
            "User-Agent": self.user_agent
        }

        response = await self.session.get(url, headers=headers)
        if response.status != 200:
            logging.warning(f"Campaign {id_campaign} rank req failed with status {response.status}")
            return None
        data = await response.json()
        return data.get("min_tier")
        
        
    
    async def proceed_claims(self, data):
        count = 0
        for campaign in data:
            campaign_id = campaign["id"]
            remaining_budget = campaign["remaining_budget"]
            if not self.my_rank:
                self.my_rank = await self.get_my_rank()
            rank_req = await self.get_campaign_rank_req(campaign_id)
            if rank_req is None:
                continue

            if campaign["status"] == "ACTIVE" and campaign["id"] not in self.campaign_ids_cliked and self.ranks.index(self.my_rank) >= self.ranks.index(rank_req) and remaining_budget is not None:
                logging.info(f"Campaign ID: {campaign['id']} | Required Rank: {rank_req} | My Rank: {self.my_rank}")
                logging.info(f"Campaign ID: {campaign['id']} | Claiming")
                
                
                
                solution_data = self.consume_captcha()
                if not solution_data:
                    logging.warning(f"Campaign ID: {campaign_id} | Captcha not ready yet, skipping")
                    continue
                captcha_token = solution_data.get("gRecaptchaResponse")
                if not captcha_token:
                    logging.warning(f"Campaign ID: {campaign_id} | Captcha token missing")
                    continue

                success, error = await self.claim_campaign(campaign_id, captcha_token)
                if success:
                    count +=1
                    self.campaign_ids_cliked.append(campaign_id)
                    logging.info(f"Campaign ID: {campaign_id} | Claimed")
                else:
                    logging.error(f"Campaign ID: {campaign_id} | Claim failed: {campaign.get('name', campaign_id)} - {error}")
                
        return count
        
    
    async def claim_campaign(self, id_campaign, captcha_solution):
        url = "https://api-tunnl-mainnet-6l3nt.ondigitalocean.app/offers/claim-faucet"
        
        headers = {
            'Authorization': f'Bearer {self.bearer}',
            "User-Agent": self.user_agent
        }
        
        payload = {
            "campaignId": id_campaign,
            "captcha": captcha_solution
        }
        
        response =  await self.session.post(url, headers=headers, json=payload )
        text = await response.text()
        if response.status == 200:
              
            return True, None
        return False, text
        
        
        
        