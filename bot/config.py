import os
from datetime import timedelta, timezone

from dotenv import load_dotenv

# =========================
# .env
# =========================
load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))


# セバスチャン応答（Gemini）
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")


# =========================
# JST
# =========================
JST = timezone(timedelta(hours=9))
