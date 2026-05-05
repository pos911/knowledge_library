import os
from google import genai
from config import GEMINI_API_KEY

def summarize_post(title, content):
    """
    Gemini API를 호출하여 블로그 본문을 요약한다.
    """
    if not content or len(content.strip()) < 10:
        print(f"Skipping summary for '{title}': Content is too short or empty.")
        return "요약할 본문 내용이 부족합니다."

    if not GEMINI_API_KEY or GEMINI_API_KEY == 'your_gemini_api_key_here':
        print("Warning: GEMINI_API_KEY is not set.")
        return "Gemini API 키가 설정되지 않았습니다."
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # 사용할 모델 설정 (gemini-2.5-flash -> gemini-2.0-flash 로 수정)
    MODEL_ID = 'gemini-2.0-flash'
    
    prompt = f"""
당신은 전문적인 금융/투자 애널리스트입니다.
다음은 네이버 블로그의 투자 관련 게시글 본문입니다.
이 글을 읽고 아래 지침에 따라 요약해 주세요.

[게시글 제목]: {title}
[본문 내용 시작]
{content[:8000]} # 토큰 제한을 고려하여 앞부분만 절단
[본문 내용 끝]

가이드라인:
1. 이 글이 다루는 핵심 자산(종목, 산업, 매크로 지표 등)을 식별할 것.
2. 글쓴이의 핵심 논거와 최종 결론을 3줄 이내로 요약할 것.
3. 투자자가 주목해야 할 '기회'와 '리스크' 요인을 각각 하나씩 뽑을 것.

아래와 같은 포맷으로 결과를 출력해 주세요 (마크다운 없이 일반 텍스트 포맷 유지):
핵심 자산: [자산명]
요약:
- [요약 1]
- [요약 2]
- [요약 3]

기회 요인: [내용]
리스크 요인: [내용]
"""

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error in Gemini summarization: {e}")
        return f"요약 중 에러 발생: {e}"
