import os
import json
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수를 담을 기본 딕셔너리
config = {}

# GitHub Actions의 단일 ENV_JSON Secret 우선 처리
env_json_str = os.environ.get("ENV_JSON")
if env_json_str:
    try:
        config = json.loads(env_json_str)
        print("Loaded configuration from ENV_JSON.")
    except json.JSONDecodeError as e:
        print(f"Error parsing ENV_JSON: {e}")

# ENV_JSON에 없는 값들은 로컬 .env 또는 일반 시스템 환경변수에서 가져오기
def get_config_value(key, default=None):
    return config.get(key) or os.environ.get(key, default)

GEMINI_API_KEY = get_config_value("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = get_config_value("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = get_config_value("TELEGRAM_CHAT_ID")
DB_PATH = get_config_value("DB_PATH", "knowledge.db")


# 기타 설정
BLOGS_FILE_PATH = "blogs.txt"
