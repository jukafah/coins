import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
DATABASE_NAME = os.getenv('DATABASE_NAME')
API_URL = os.getenv('BIRDEYE_API_URL')
HEADERS = {'X-API-KEY': os.getenv('BIRDEYE_API_KEY')}