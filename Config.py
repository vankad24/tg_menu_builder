import os
from dotenv import load_dotenv
import json

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BOT_ADMINS = set(json.loads(os.getenv("BOT_ADMINS")))
    
