import logging

logging.basicConfig(
    filename="tunnl_bot.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


FILE_PATH = "cookies.json"
FILE_PATH_AUTH = "auth.txt"