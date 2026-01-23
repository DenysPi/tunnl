
from twitter_client import TwitterClient
from helpers import *
from config import *
import logging 
import config
class Tunnl:
    def __init__(self, auth_client: str, user_agent: str, version: int, platform: str, session):
        self.auth_client = auth_client
        self.user_agent = user_agent
        self.version = version
        self.platform = platform
        self.session = session
        
        self.twitter = None
        self.bearer = None
        
        self.ranks = ["PURPLE", "BRONZE_1", "BRONZE_2", "BRONZE_3", "SILVER_1", "SILVER_2", "SILVER_3"]
        self.my_rank = None
        
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
        
        response =  await self.session.get(url, headers=headers )
        data = await response.json()  
        return data.get("min_tier")
        
        
    
    async def proceed_claims(self, data):
        count = 0
        for campaign in data:
            if not self.my_rank:
                self.my_rank = await self.get_my_rank()
            rank_req = await self.get_campaign_rank_req(campaign["id"])
            
            
            
            if campaign["status"] == "ACTIVE" and self.ranks.index(self.my_rank) >= self.ranks.index(rank_req):
                logging.info(f"Campaign ID: {campaign['id']} | Required Rank: {rank_req} | My Rank: {self.my_rank}")
                logging.info(f"Campaign ID: {campaign['id']} | Claiming")
                id = campaign["id"]
                
                claim = await self.claim_campaign(id)
                if (claim != False):
                    count +=1
                    logging.info(f"Campaign ID: {campaign['id']} | Claimed")
        return count
        
    
    async def claim_campaign(self, id_campaign):
        url = "https://api-tunnl-mainnet-6l3nt.ondigitalocean.app/offers/claim-faucet"
        
        headers = {
            'Authorization': f'Bearer {self.bearer}',
            "User-Agent": self.user_agent
        }
        
        payload = {
            "campaignId": id_campaign
        }
        
        response =  await self.session.post(url, headers=headers, json=payload )
        if response.status == 200:
            data = await response.json()  
            return data
        return False
        
        
        
        