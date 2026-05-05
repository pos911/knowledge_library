# Knowledge Library

블로그 글을 수집하고 AI로 요약하여 Telegram으로 발송하는 자동화 도구입니다.

## Telegram 채널 발송 설정

Telegram 채널로 메시지를 발송하려면 다음 설정을 확인하세요.

- **발송 대상 설정**:
  - 공개 채널: `TELEGRAM_CHAT_ID`에 `@채널아이디`를 입력합니다. (예: `@invest_blog_kr`)
  - 비공개 채널: `-100`으로 시작하는 숫자 ID를 입력합니다.
  - 개인/그룹: 숫자 ID를 입력합니다.
- **봇 권한**:
  - 봇을 채널 관리자로 추가해야 합니다.
  - 봇에게 '메시지 게시' 권한이 있어야 합니다.
- **환경 변수**:
  - `TELEGRAM_TOKEN`: Telegram Bot API 토큰
  - `TELEGRAM_CHAT_ID`: 발송 대상 ID 또는 username

### Telegram 발송 테스트

설정이 올바른지 확인하기 위해 다음 명령어를 실행할 수 있습니다.

**로컬 실행:**
```bash
# 방법 1: 전용 스크립트 실행
python scripts/test_telegram.py

# 방법 2: main.py의 테스트 플래그 사용
python main.py --telegram-test
```

**GitHub Actions:**
- `Actions` 탭에서 `Daily AI Investment Summary` 워크플로우를 선택합니다.
- `Run workflow` 클릭 후 `Execution mode`를 `telegram-test`로 설정하여 실행합니다.

### 오류별 조치 가이드

- **400 Bad Request (chat not found)**:
  - `TELEGRAM_CHAT_ID`가 올바른지 확인하세요.
  - 봇이 해당 채널/그룹에 추가되어 있는지 확인하세요.
  - 공개 채널의 경우 `@`를 포함했는지 확인하세요.
- **403 Forbidden**:
  - 봇이 채널 관리자로 등록되어 있고 메시지 게시 권한이 있는지 확인하세요.
- **401 Unauthorized**:
  - `TELEGRAM_TOKEN`이 올바른지 확인하세요.
- **429 Too Many Requests**:
  - 과도한 메시지 발송으로 인해 Telegram API 제한에 걸린 상태입니다. 잠시 후 다시 시도하세요.

## 설정값 검증 (ENV_JSON)

GitHub Actions에서 `ENV_JSON`을 사용하는 경우 다음 키가 포함되어야 합니다. **특히 `TELEGRAM_CHAT_ID`를 반드시 `@invest_blog_kr` (또는 실제 채널 ID)로 업데이트했는지 확인하세요.**

```json
{
  "TELEGRAM_TOKEN": "...",
  "TELEGRAM_CHAT_ID": "@invest_blog_kr",
  "GEMINI_API_KEY": "...",
  "NAVER_CLIENT_ID": "...",
  "NAVER_CLIENT_SECRET": "...",
  "DB_PATH": "knowledge.db",
  "GH_PAT": "..."
}
```
*주의: 실제 Secret 값은 로그에 노출되지 않도록 주의하세요.*
