import os
from dotenv import load_dotenv
import json

class Config:
    def __init__(self):
        load_dotenv()
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        self.ADMINS = set(json.loads(os.getenv("ADMINS")))
