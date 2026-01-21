from tunnl import Tunnl
import os
import random
import aiohttp
import asyncio
import logging
from helpers import create_env_for_import
from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(
    filename="tunnl_bot.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Also log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logging.getLogger().addHandler(console_handler)

async def main():
    auth_client = os.getenv("AUTH_CLIENT")
    user_agent = os.getenv("USER_AGENT")
    version = os.getenv("VERSION")
    platform = os.getenv("PLATFORM")
    
    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=15)
    )

    tunnl = Tunnl(
        auth_client=auth_client,
        user_agent=user_agent,
        version=version,
        platform=platform,
        session=session
    )
    count = 0
    try:
        
        if(create_env_for_import()):
            
            return 
        tunnl.set_twitter()

        await tunnl.twitter.get_cookies()
        await tunnl.connect_tunnl_via_twitter()
        logging.info("Connected to Tunnl via Twitter successfully.")
       
        while True:
            try:
                data = await tunnl.get_campaigns()

                if not data:
                    raise RuntimeError("Failed to fetch campaigns")

                campaigns = data.get("campaigns", [])
                logging.info(f"Processing {len(campaigns)} campaigns.")
                if campaigns:
                    count_camp = await tunnl.proceed_claims(campaigns)
                    logging.info(f"Campaigns clicked: {count_camp}")
                    await asyncio.sleep(random.uniform(0.2, .4))

            except aiohttp.ClientResponseError as e:
                if e.status in (401, 403):
                    count += 1
                    if count == 5:
                        return
                    logging.info("🔑 Token expired, reconnecting...")
                    await tunnl.connect_tunnl_via_twitter()
                else:
                    logging.info(f"HTTP error: {e}")

            except asyncio.TimeoutError:
                logging.info("⏱ Request timeout")

            except Exception as e:
                logging.info(f"Unexpected error: {e}")

            await asyncio.sleep(random.uniform(1.2, 2.0))

    finally:
        await session.close()
        
asyncio.run(main())