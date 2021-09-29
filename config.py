import os
from dotenv import load_dotenv
load_dotenv()


def keys():
    keys.TOKEN = os.getenv('TOKEN')
    keys.CLIENT_ID = os.getenv('CLIENT_ID')
    keys.SECRET = os.getenv('SECRET')
    keys.TOTAL_GUILDS_API_URI = os.getenv('TOTAL_GUILDS_API_URI')
    keys.MONGODB_URL = os.getenv('MONGODB_URL')
    keys.PREFIX = os.getenv('PREFIX')


def cogs():
    cogs.UNLOADED = ["Utilities.py", "Help.py"]