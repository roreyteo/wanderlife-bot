import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="/home/krikri/wanderlife-bot/.env", override=True)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
