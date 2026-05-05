import requests
import html
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message, parse_mode="HTML"):
    """
    지정된 Telegram 챗봇과 Chat ID로 메시지를 전송한다.
    4096자 제한을 처리하고, HTML 파싱 오류 시 fallback을 시도한다.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERROR] Telegram credentials are not set.")
        return False
        
    # 메시지 길이 제한 처리 (4096자)
    MAX_LENGTH = 4096
    messages = [message[i:i+MAX_LENGTH] for i in range(0, len(message), MAX_LENGTH)]
    
    success = True
    for msg in messages:
        if not _send_request(msg, parse_mode):
            # HTML 파싱 에러 등으로 실패했을 경우 fallback 시도
            if parse_mode == "HTML":
                print("[INFO] Retrying without HTML parse_mode...")
                if not _send_request(msg, parse_mode=None):
                    success = False
            else:
                success = False
    
    return success

def _send_request(text, parse_mode):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
        
    try:
        response = requests.post(url, json=payload, timeout=15)
        result = response.json()
        
        if response.status_code == 200 and result.get("ok"):
            return True
        else:
            status_code = response.status_code
            description = result.get("description", "No description")
            error_code = result.get("error_code")
            
            print(f"[ERROR] Telegram API failed (Status: {status_code}): {description}")
            
            # 상세 에러 가이드
            if status_code == 400:
                print("  -> Check if TELEGRAM_CHAT_ID is correct or if the bot is in the channel.")
            elif status_code == 401:
                print("  -> Check if TELEGRAM_TOKEN is valid.")
            elif status_code == 403:
                print("  -> Check if the bot has permission to post in the channel.")
            elif status_code == 429:
                print("  -> Too many requests. Please wait.")
                
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Connection error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

def format_summary_message(post):
    """
    정보지 포맷으로 메시지를 가공한다.
    """
    title = post['title']
    link = post['link']
    summary = post['summary']
    
    # HTML escape
    safe_title = html.escape(title)
    safe_summary = html.escape(summary)
    
    message = f"<b>[오늘의 투자 인사이트 리포트]</b>\n\n"
    message += f"<b>제목:</b> {safe_title}\n\n"
    message += f"<b>요약/인사이트:\n</b>{safe_summary}\n\n"
    message += f"<a href='{link}'>원문 읽기</a>"
    
    return message
