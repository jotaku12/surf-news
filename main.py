import requests
from jinja2 import Template
import datetime
import os
from urllib.parse import quote

def get_gnews_articles(query, max_results=5):
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        print("❌ GNEWS_API_KEY가 설정되지 않았습니다!")
        return []

    print(f"🔎 '{query}' 검색 중...")

    url = f"https://gnews.io/api/v4/search?q={quote(query)}&lang=en&max={max_results}&token={api_key}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ GNews API 요청 실패: {response.status_code}")
        return []

    data = response.json()
    articles = []

    for item in data.get("articles", []):
        title = item["title"]
        description = item.get("description", "") or ""
        link = item["url"]
        image = item.get("image")

        # 분류: 한국 / 발리 / 글로벌
        if "한국" in title or "Korea" in title or "한국" in description:
            category = "korea"
        elif "Bali" in title or "발리" in title or "Bali" in description:
            category = "bali"
        else:
            category = "global"

        articles.append({
            "title": title,
            "link": link,
            "type": category,
            "thumbnail": image
        })

    print(f"✅ '{query}' → {len(articles)}건 수집됨.")
    return articles

# 키워드
keywords = ["surfing", "surf", "서핑", "서프"]

raw_articles = []
for kw in keywords:
    raw_articles.extend(get_gnews_articles(kw))

print(f"📦 전체 기사 수: {len(raw_articles)}")

# 분류
korea_news = [a for a in raw_articles if a["type"] == "korea"]
bali_news = [a for a in raw_articles if a["type"] == "bali"]
global_news = [a for a in raw_articles if a["type"] == "global"]

print(f"🌏 분류 결과: 한국={len(korea_news)} / 발리={len(bali_news)} / 해외={len(global_news)}")

# 최대 5개씩만
articles = korea_news[:5] + bali_news[:5] + global_news[:5]

# 날짜
today = datetime.date.today().strftime("%Y년 %m월 %d일")

# 템플릿 렌더링
try:
    with open("template.html", "r", encoding="utf-8") as f:
        template = Template(f.read())
    html = template.render(articles=articles, date=today)
except Exception as e:
    print("❌ 템플릿 렌더링 오류:", e)
    html = "<h1>오류 발생!</h1>"

# 저장
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("🎉 index.html 생성 완료!")
