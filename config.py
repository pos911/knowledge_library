import os
import json
import sys
from dotenv import load_dotenv

IS_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


def _fail_config(message):
    print(f"[CONFIG ERROR] {message}", file=sys.stderr)
    raise SystemExit(1)


def _looks_like_env_file(value):
    stripped = value.lstrip()
    if not stripped:
        return False
    if stripped.startswith("#"):
        return True
    first_line = stripped.splitlines()[0]
    return "=" in first_line and not first_line.startswith("{")


config = {}
env_json_str = os.environ.get("ENV_JSON")

if IS_GITHUB_ACTIONS:
    # GitHub Actions에서는 .env fallback을 허용하지 않는다.
    # 반드시 GitHub Secrets의 ENV_JSON만 신뢰한다.
    if not env_json_str:
        _fail_config(
            "GitHub Actions requires secrets.ENV_JSON. "
            "Local .env fallback is disabled in CI."
        )

    if _looks_like_env_file(env_json_str):
        _fail_config(
            "GitHub Actions requires secrets.ENV_JSON to be valid JSON. "
            "Do not use .env KEY=VALUE format or comments."
        )

    try:
        config = json.loads(env_json_str)
        if not isinstance(config, dict):
            _fail_config("ENV_JSON must be a JSON object.")
        print("Loaded configuration from GitHub Actions ENV_JSON.")
    except json.JSONDecodeError as e:
        _fail_config(
            "GitHub Actions requires secrets.ENV_JSON to be valid JSON. "
            f"JSON parse error: {e}. "
            "Do not use .env KEY=VALUE format or comments."
        )
else:
    # 로컬에서는 ENV_JSON이 있으면 우선 사용하고, 없으면 .env를 로드한다.
    if env_json_str:
        try:
            config = json.loads(env_json_str)
            if not isinstance(config, dict):
                print("[WARNING] ENV_JSON is not a JSON object. Falling back to .env/system environment.")
                config = {}
            else:
                print("Loaded configuration from local ENV_JSON.")
        except json.JSONDecodeError as e:
            print(f"[WARNING] Error parsing local ENV_JSON: {e}. Falling back to .env/system environment.")
            load_dotenv()
    else:
        load_dotenv()


def get_config_value(key, default=None):
    return config.get(key) or os.environ.get(key, default)


GEMINI_API_KEY = get_config_value("GEMINI_API_KEY")
GEMINI_MODEL = get_config_value("GEMINI_MODEL", "gemini-2.5-flash")
TELEGRAM_BOT_TOKEN = get_config_value("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = get_config_value("TELEGRAM_CHAT_ID")
DB_PATH = get_config_value("DB_PATH", "knowledge.db")


def validate_required_config(mode="run"):
    """실행 모드별 필수 설정을 검증한다."""
    if mode == "telegram-test":
        required_keys = ["TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID"]
    else:
        required_keys = ["GEMINI_API_KEY", "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID"]

    missing = [key for key in required_keys if not get_config_value(key)]
    if missing:
        _fail_config(f"Missing required configuration: {', '.join(missing)}")


# Telegram 설정 검증 로그는 값 노출 없이 상태만 출력한다.
if not TELEGRAM_BOT_TOKEN:
    print("[WARNING] TELEGRAM_TOKEN is not set.")
if not TELEGRAM_CHAT_ID:
    print("[WARNING] TELEGRAM_CHAT_ID is not set.")
else:
    print("Configured Telegram target is set.")

# 기타 설정
BLOGS_FILE_PATH = "blogs.txt"
