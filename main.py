import time
import schedule
from database import init_db, insert_post, get_pending_posts, update_post_summary, get_summarized_posts, mark_post_sent
from scraper import scrape_recent_posts
from summarizer import summarize_post
from notifier import send_telegram_message, format_summary_message

def run_pipeline():
    print("--- Pipeline Started ---")
    
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
            time.sleep(1) # Rate limiting 방지
            
    print(f"Sent {sent_count} notifications.")
    print("--- Pipeline Ended ---")

if __name__ == "__main__":
    print("Initializing Database...")
    init_db()
    
    # 즉시 1회 실행 (테스트용)
    # run_pipeline()
    
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
