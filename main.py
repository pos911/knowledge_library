import time
import schedule
import os
import sys
import argparse
from datetime import datetime
from database import (
    init_db,
    insert_post,
    get_pending_posts,
    update_post_summary,
    get_summarized_posts,
    get_posts_by_links,
    mark_post_sent,
)
from scraper import scrape_recent_posts, scrape_latest_posts
from summarizer import summarize_post
from notifier import send_telegram_message, format_summary_message
from config import TELEGRAM_CHAT_ID


def run_pipeline():
    # GitHub Actions 등 일회성 실행 환경에서도 DB 초기화가 확실히 이루어지도록 파이프라인 시작 시 호출
    init_db()

    print("--- Pipeline Started ---")

    try:
        # 1. Scraping
        print("1. Scraping recent posts...")
        recent_posts = scrape_recent_posts()

        # 2. Add to DB
        print(f"Found {len(recent_posts)} posts from RSS. Adding to DB...")
        inserted_count = 0
        for post in recent_posts:
            if insert_post(post['title'], post['link'], post['published_date'], post['content']):
                inserted_count += 1
        print(f"Inserted {inserted_count} new posts to DB.")

        # 3. Summarize
        print("2. Summarizing pending posts...")
        pending_posts = get_pending_posts()
        for post in pending_posts:
            print(f"Summarizing: {post['title']}")
            summary = summarize_post(post['title'], post['content'])
            update_post_summary(post['id'], summary)
            print(f"Summarization complete for ID: {post['id']}")

        # 4. Notify
        print("3. Sending Telegram notifications...")
        summarized_posts = get_summarized_posts()
        sent_count = 0
        for post in summarized_posts:
            message = format_summary_message(post)
            if send_telegram_message(message):
                mark_post_sent(post['id'])
                sent_count += 1
                time.sleep(1)  # Rate limiting 방지

        print(f"Sent {sent_count} notifications.")
        print("--- Pipeline Ended ---")

    except Exception as e:
        print(f"[CRITICAL ERROR] Pipeline failed with exception: {e}", file=sys.stderr)
        raise


def run_latest_pipeline(limit):
    """전체 RSS에서 가장 최근 글만 골라 요약하고 미발송 항목을 전송한다."""
    init_db()
    print(f"--- Latest {limit} Pipeline Started ---")

    latest_posts = scrape_latest_posts(limit)
    if len(latest_posts) != limit:
        raise RuntimeError(f"Expected {limit} latest posts, found {len(latest_posts)}.")

    for post in latest_posts:
        insert_post(
            post['title'],
            post['link'],
            post['published_date'],
            post['content'],
        )

    selected_posts = get_posts_by_links([post['link'] for post in latest_posts])
    if len(selected_posts) != limit:
        raise RuntimeError(f"Expected {limit} database posts, found {len(selected_posts)}.")

    for post in selected_posts:
        if post['status'] != 'pending':
            continue

        print(f"Summarizing: {post['title']}")
        summary = summarize_post(post['title'], post['content'])
        if (
            not summary
            or summary.startswith("요약 중 에러 발생:")
            or summary in (
                "Gemini API 키가 설정되지 않았습니다.",
                "요약할 본문 내용이 부족합니다.",
            )
        ):
            raise RuntimeError(f"Summarization failed for '{post['title']}': {summary}")
        update_post_summary(post['id'], summary)

    selected_posts = get_posts_by_links([post['link'] for post in latest_posts])
    posts_to_send = [
        post for post in selected_posts
        if post['status'] == 'summarized'
    ]

    sent_count = 0
    for post in reversed(posts_to_send):
        print(f"Sending: {post['title']}")
        if not send_telegram_message(format_summary_message(post)):
            raise RuntimeError(f"Telegram send failed for '{post['title']}'.")
        mark_post_sent(post['id'])
        sent_count += 1
        time.sleep(1)

    print(f"Sent {sent_count} of the latest {limit} posts.")
    print(f"--- Latest {limit} Pipeline Ended ---")


def run_telegram_test():
    """Telegram 발송 단독 테스트 실행"""
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
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Knowledge Library Pipeline")
    parser.add_argument("--telegram-test", action="store_true", help="Run Telegram notification test only")
    parser.add_argument(
        "--latest-limit",
        type=int,
        help="Process and send only the newest N RSS posts",
    )
    args = parser.parse_args()

    init_db()

    if args.telegram_test:
        run_telegram_test()
        sys.exit(0)

    if args.latest_limit:
        run_latest_pipeline(args.latest_limit)
        sys.exit(0)

    # GitHub Actions 등 CI 환경에서는 스케줄러를 돌리지 않고 즉시 1회 실행 후 종료
    if os.getenv("GITHUB_ACTIONS") == "true":
        print("CI Environment detected. Running pipeline once and exiting...")
        try:
            run_pipeline()
        except Exception as e:
            print(f"[FATAL] Pipeline raised an exception in CI: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Scheduling pipeline to run at 07:00 AM (Mon-Fri) and 10:00 AM (Sat-Sun).")

        # 평일 오전 7시
        schedule.every().monday.at("07:00").do(run_pipeline)
        schedule.every().tuesday.at("07:00").do(run_pipeline)
        schedule.every().wednesday.at("07:00").do(run_pipeline)
        schedule.every().thursday.at("07:00").do(run_pipeline)
        schedule.every().friday.at("07:00").do(run_pipeline)

        # 주말 오전 10시
        schedule.every().saturday.at("10:00").do(run_pipeline)
        schedule.every().sunday.at("10:00").do(run_pipeline)

        while True:
            schedule.run_pending()
            time.sleep(60)
