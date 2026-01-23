import uuid
import aiohttp
import hashlib
import os
import base64, secrets
import json
from urllib.parse import urlparse, parse_qs

from helpers import *
from config import *
class TwitterClient:
    def __init__(self, auth_token, user_agent, version, platform, session: aiohttp.ClientSession | None = None):
        self.auth_token = auth_token
        self.user_agent = user_agent
        self.version = version
        self.platform = platform
        
        self.session = session
        self.code_verifier = None
        self.state_code = None
    @staticmethod
    def generate_client_transaction_id():
        random_bytes = secrets.token_bytes(70)  
        transaction_id = base64.b64encode(random_bytes).decode('ascii').rstrip('=')  
        return transaction_id
    
    @staticmethod
    def generate_client_uuid():
            return str(uuid.uuid4())
    
    
    async def get_cookies(self):
        if   os.path.exists(FILE_PATH):
            print("Cookies already existing")
            return True
        params = {
            "variables": json.dumps({"withCommunitiesMemberships": True}),
            "features": json.dumps({
                "subscriptions_upsells_api_enabled": True,
                "profile_label_improvements_pcf_label_in_post_enabled": True,
                "responsive_web_profile_redirect_enabled": False,
                "rweb_tipjar_consumption_enabled": True,
                "verified_phone_label_enabled": False,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "responsive_web_graphql_timeline_navigation_enabled": True
            }),
            "fieldToggles": json.dumps({
                "isDelegate": False,
                "withAuxiliaryUserLabels": True
            })
        }
        headers = {
            "Authorization": f"Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Cookie": "auth_token=8778fb4379ae255111c0c187201bda48b3157072"
        }
        url = "https://api.x.com/graphql/178EtFdhcGqmoyzKL4muaA/Viewer"
        
        async with self.session.get(url, headers=headers, params=params) as response:
            raw_cookies = response.headers.getall("Set-Cookie", [])
            cookies_dict = {}

            for cookie_str in raw_cookies:
                parts = cookie_str.split(";")
                if len(parts) > 0:
                    key_value = parts[0].strip().split("=", 1)
                    if len(key_value) == 2:
                        key, value = key_value
                        cookies_dict[key] = value  
                        
            cookies_dict["auth_token"] = self.auth_token
            load_cookies_to_json(cookies_dict)
            
            
            
            print("Cookies saved to cookies.json")
            
    async def startOauth2(self, params):
        
        cookies = get_cookies_from_json(FILE_PATH)
        
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'priority': 'u=1, i',
            'referer': "https://x.com/i/oauth2/authorize?",
            'sec-ch-ua': f'"Not A(Brand";v="8", "Chromium";v="{self.version}", "Google Chrome";v="{self.version}"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': f'"{self.platform}"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.user_agent,
            'x-client-transaction-id': self.generate_client_transaction_id(),
            'x-csrf-token': cookies["ct0"],
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'en',
        }

        
        
        response = await self.session.get('https://twitter.com/i/api/2/oauth2/authorize', params=params, cookies=cookies, headers=headers)
        if response.status == 200:
            data = await response.json()  
            auth_code = data.get('auth_code')
            if auth_code:
                return auth_code
            
    async def confirm_oauth2(self, auth_code):
        
        cookies = get_cookies_from_json(FILE_PATH)

        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'priority': 'u=1, i',
            'referer': "https://x.com/i/oauth2/authorize?",
            'sec-ch-ua': f'"Not A(Brand";v="8", "Chromium";v="{self.version}", "Google Chrome";v="{self.version}"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': f'"{self.platform}"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.user_agent,
            'x-client-transaction-id': self.generate_client_transaction_id(),
            'x-csrf-token': cookies["ct0"],
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'en',
        }
        
        data = {
            'approval': 'true',
            'code': auth_code,
        }

        response = await self.session.post('https://twitter.com/i/api/2/oauth2/authorize', cookies=cookies, headers=headers, data=data)
        
        if response.status == 200:
            redirect_uri =  await response.json()
            redirect_uri = redirect_uri.get('redirect_uri')
            if redirect_uri:
                
                return True, redirect_uri
            
        return False, f'Не смог сделать twitter confirm_oauth2 | status code: {response.status} | ответ сервера: {response.text}'
    
    async def start_connect_twitter(self):
        url_data = await self.get_connect_twitter_url()
        print(url_data)
        if url_data:
            oauth_url = url_data.get("url")
            
            
            parsed_url = urlparse(oauth_url)
            params = parse_qs(parsed_url.query)
            params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
            
            
            auth_code = await self.startOauth2(params=params)
            print(auth_code)
            if auth_code: 
                status, redirect_url = await self.confirm_oauth2(auth_code=auth_code)
                print(redirect_url)
                if status:
             
                    async with self.session.get(redirect_url, allow_redirects=False) as callback_response:
                       
                        
                        if callback_response.status in [301, 302, 303, 307, 308]:
                            
                            final_redirect = callback_response.headers.get('Location')
                           
                            
                            if final_redirect:
                                
                                parsed_final = urlparse(final_redirect)
                                final_params = parse_qs(parsed_final.query)
                                authorization_code = final_params.get('privy_oauth_code', [None])[0]
                                print(authorization_code)
                                if authorization_code:
                                    success, result = await self.authenticate_with_privy(authorization_code)
                                    print(result)
                                    if success:

                                        return True, result
                                    else:
                                        print(f"✗ Failed to authenticate with Privy: {result}")
                                        return False, ""
                else:
                    print(f"Error: {redirect_url}")
                    return False, ""
        return False, ""
        
                

        
    
    async def authenticate_with_privy(self, authorization_code):
        """
        Send the Twitter authorization code to Privy's authenticate endpoint.
        This is the step that exchanges the Twitter code for Privy tokens.
        """
        url = "https://privy.tunnl.io/api/v1/oauth/authenticate"
        
        payload = {
            "authorization_code": authorization_code,
            "code_verifier": self.code_verifier,
            
            "mode": "login-or-sign-up",
            "state_code": self.state_code
        }
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json',
            'Origin': 'https://app.tunnl.io',
            'Referer': 'https://app.tunnl.io/',
            'Sec-Ch-Ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': self.user_agent,
            'Privy-App-Id': 'cmcmf870100hxjx0m4k296bn0',
            'Privy-Client': 'react-auth:3.8.0',
            'Privy-Ui': 't'
        }
        
        try:
            response = await self.session.post(url, json=payload, headers=headers)
            if response.status == 200:
                data = await response.json()
                
                
                return True, data
            else:
                text = await response.text()
                print(f"Authentication failed: {text}")
                return False, text
                
        except Exception as e:
            print(f"Error during authentication: {e}")
            return False, str(e)
    
    async def get_connect_twitter_url(self):
   
        try:
    
            self.code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
            code_challenge_bytes = hashlib.sha256(self.code_verifier.encode('utf-8')).digest()
            code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).decode('utf-8').rstrip('=')
        
            
            self.state_code = base64.urlsafe_b64encode(secrets.token_bytes(36)).decode('utf-8').rstrip('=')
            
        
            
        
            url = "https://privy.tunnl.io/api/v1/oauth/init"
        
            payload = {
                "provider": "twitter",
                "redirect_to": "https://app.tunnl.io/login",
                "code_challenge": code_challenge,  
                "state_code": self.state_code          
            }
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Content-Type': 'application/json',
                'Origin': 'https://app.tunnl.io',
                'Referer': 'https://app.tunnl.io/',
                'Referrer-Policy': 'strict-origin-when-cross-origin',
                'Sec-Ch-Ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            
                'Privy-App-Id': 'cmcmf870100hxjx0m4k296bn0',
                
                'Privy-Client':
                'react-auth:3.8.0',
                'Privy-Ui': 't'
            }
            response = await self.session.post(
                url,
                json=payload,
                headers=headers,
            
            )
            
            
            
            if response.status == 200:
                
                data = await response.json()
                return data
                
        except Exception as e:
            return False
            
    