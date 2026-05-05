import sys
import os
from datetime import datetime

# 프로젝트 루트 경로를 sys.path에 추가하여 config, notifier 등을 불러올 수 있게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notifier import send_telegram_message
from config import TELEGRAM_CHAT_ID

def run_test():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target = TELEGRAM_CHAT_ID or "Unknown"
    
    test_message = (
        f"<b>[Telegram 발송 테스트]</b>\n"
        f"knowledge_library 채널 발송 테스트입니다.\n"
        f"대상: {target}\n"
        f"시간: {now} KST"
    )
    
    print(f"Starting Telegram test to {target}...")
    
    if send_telegram_message(test_message):
        print(f"SUCCESS: Telegram test message sent successfully to {target}")
    else:
        print(f"FAILED: Telegram test failed. Check the logs above for details.")

if __name__ == "__main__":
    run_test()
