from typing import Final
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN: Final = os.getenv("TELEGRAM_TOKEN")
BOT_USERNAME: Final = os.getenv("BOT_USERNAME")