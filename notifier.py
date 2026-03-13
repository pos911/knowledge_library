import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message):
    """
    지정된 Telegram 챗봇과 Chat ID로 메시지를 전송한다.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID or TELEGRAM_BOT_TOKEN == 'your_telegram_bot_token_here':
        print("Warning: Telegram credentials are not set.")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML" # HTML 태그 지원
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        print(f"Error sending to Telegram: {e} - Response: {response.text}")
        return False
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return False

def format_summary_message(post):
    """
    정보지 포맷으로 메시지를 가공한다.
    """
    title = post['title']
    link = post['link']
    summary = post['summary']
    
    # HTML escape (if needed, though Telegram HTML parsing is basic)
    title = title.replace('<', '&lt;').replace('>', '&gt;')
    summary = summary.replace('<', '&lt;').replace('>', '&gt;')
    
    message = f"<b>[오늘의 투자 인사이트 리포트]</b>\n\n"
    message += f"<b>제목:</b> {title}\n\n"
    message += f"<b>요약/인사이트:\n</b>{summary}\n\n"
    message += f"<a href='{link}'>원문 읽기</a>"
    
    return message
