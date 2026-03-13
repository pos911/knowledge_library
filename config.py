import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수 및 설정값
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
DB_PATH = os.environ.get("DB_PATH", "knowledge.db")

# 기타 설정
BLOGS_FILE_PATH = "blogs.txt"
