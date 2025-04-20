import requests
from jinja2 import Template
import datetime
import os
from urllib.parse import quote

# ✅ GNews API로 뉴스 가져오기
def get_gnews_articles(query, max_results=10):
    api_key = os.getenv("GNEWS_API_KEY")
    url = f"https://gnews.io/api/v4/search?q={quote(query)}&lang=en&max={max_results}&token={api_key}"
    res = requests.get(url)
    if res.status_code != 200:
        print("❌ GNews API 오류:", res.status_code)
        return []
    data = res.json()
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
    return articles

# ✅ 검색 키워드: 국내는 한글, 글로벌은 영어
keywords = ["surfing", "surf", "서핑", "서프"]

raw_articles = []
for kw in keywords:
    raw_articles.extend(get_gnews_articles(kw, max_results=5))

# ✅ 분류 정리
korea_news = [a for a in raw_articles if a["type"] == "korea"]
bali_news = [a for a in raw_articles if a["type"] == "bali"]
global_news = [a for a in raw_articles if a["type"] == "global"]

# ✅ 최대 5개씩 추출
articles = korea_news[:5] + bali_news[:5] + global_news[:5]
print(f"✅ 뉴스 수집 완료: 한국 {len(korea_news)}, 발리 {len(bali_news)}, 해외 {len(global_news)}")

# ✅ 날짜 포맷
today = datetime.date.today().strftime("%Y년 %m월 %d일")

# ✅ 템플릿 렌더링
with open("template.html", "r", encoding="utf-8") as f:
    template = Template(f.read())
html = template.render(articles=articles, date=today)

# ✅ index.html 저장
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ index.html 생성 완료!")
