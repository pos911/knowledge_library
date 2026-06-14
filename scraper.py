import feedparser
import requests
from bs4 import BeautifulSoup
import datetime
from config import BLOGS_FILE_PATH


def get_blog_urls():
    urls = []
    try:
        with open(BLOGS_FILE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url:
                    urls.append(url)
    except FileNotFoundError:
        print(f"Error: {BLOGS_FILE_PATH} not found.")
    return urls

def extract_naver_id(url):
    # url formats could be:
    # https://blog.naver.com/id
    # blog.naver.com/id
    url = url.split('?')[0] # remove query params
    parts = url.rstrip('/').split('/')
    if parts[-1]:
        return parts[-1]
    return None

def fetch_rss(naver_id):
    rss_url = f"https://rss.blog.naver.com/{naver_id}.xml"
    feed = feedparser.parse(rss_url)
    return feed

def scrape_naver_blog_content(post_link):
    """
    네이버 블로그 링크(예: https://blog.naver.com/아이디/글번호)에서
    iframe 안의 실제 본문 주소를 찾아 텍스트를 파싱한다.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 1. 원본 링크에서 iframe src 추출
        response = requests.get(post_link, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        iframe = soup.select_one('iframe#mainFrame')
        if not iframe:
            return "본문을 찾을 수 없습니다."
            
        real_post_url = "https://blog.naver.com" + iframe['src']
        
        # 2. 실제 본문 페이지 스크래핑
        real_response = requests.get(real_post_url, headers=headers)
        real_response.raise_for_status()
        real_soup = BeautifulSoup(real_response.text, 'html.parser')
        
        # 네이버 블로그 스마트에디터 ONE (se-main-container) 
        # 혹은 구버전 (postViewArea) 본문 찾기
        content_area = real_soup.select_one('.se-main-container, #postViewArea')
        
        if content_area:
            # 불필요한 태그 제거 및 텍스트만 추출
            text = content_area.get_text(separator='\n', strip=True)
            return text
        else:
            return "본문 영역을 인식하지 못했습니다."
            
    except Exception as e:
        print(f"Error scraping {post_link}: {e}")
        return f"스크래핑 에러: {e}"

def scrape_recent_posts():
    """
    blogs.txt의 모든 블로그를 순회하며 지난 24시간 이내의 게시물을 수집.
    """
    urls = get_blog_urls()
    recent_posts = []
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    
    for url in urls:
        naver_id = extract_naver_id(url)
        if not naver_id:
            continue
            
        print(f"Fetching RSS for: {naver_id}")
        feed = fetch_rss(naver_id)
        
        for entry in feed.entries:
            try:
                # RSS published date parsing
                # example format: Tue, 04 Jun 2024 10:20:30 +0900
                import email.utils
                parsed_date = email.utils.parsedate_to_datetime(entry.published)
                
                # Check if it's within 24 hours (naive compare or timezone aware compare)
                # Ensure published date is handled correctly with timezones
                if parsed_date.tzinfo is not None:
                    # make now aware
                    import pytz
                    local_tz = pytz.timezone('Asia/Seoul')
                    now_aware = local_tz.localize(now)
                    yesterday_aware = now_aware - datetime.timedelta(days=1)
                    is_recent = parsed_date >= yesterday_aware
                else:
                    is_recent = parsed_date >= yesterday
                
                if is_recent:
                    link = entry.link
                    title = entry.title
                    date_str = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                    
                    print(f"Found new post: {title}")
                    content = scrape_naver_blog_content(link)
                    
                    recent_posts.append({
                        'title': title,
                        'link': link,
                        'published_date': date_str,
                        'content': content
                    })
            except Exception as e:
                print(f"Error parsing date for {entry.link}: {e}")
                
    return recent_posts


def scrape_latest_posts(limit=10):
    """
    모든 RSS 항목을 게시 시각순으로 정렬한 뒤 최신 항목만 본문까지 수집한다.
    """
    candidates = []
    seen_links = set()

    for url in get_blog_urls():
        naver_id = extract_naver_id(url)
        if not naver_id:
            continue

        print(f"Fetching RSS for: {naver_id}")
        feed = fetch_rss(naver_id)

        for entry in feed.entries:
            try:
                import email.utils

                parsed_date = email.utils.parsedate_to_datetime(entry.published)
                link = entry.link
                if link in seen_links:
                    continue

                seen_links.add(link)
                candidates.append({
                    'title': entry.title,
                    'link': link,
                    'published_date': parsed_date.strftime("%Y-%m-%d %H:%M:%S"),
                    '_published_at': parsed_date,
                })
            except Exception as e:
                print(f"Error parsing date for {getattr(entry, 'link', 'unknown')}: {e}")

    candidates.sort(key=lambda post: post['_published_at'], reverse=True)
    selected_posts = candidates[:limit]

    for post in selected_posts:
        print(f"Scraping selected post: {post['title']}")
        post['content'] = scrape_naver_blog_content(post['link'])
        del post['_published_at']

    return selected_posts
