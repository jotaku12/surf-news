import requests
from jinja2 import Template
import datetime
import os
from urllib.parse import quote

def get_articles(keyword, lang="en", max_results=10):
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        print("❌ GNEWS_API_KEY 환경 변수가 설정되지 않았습니다.")
        return []

    url = f"https://gnews.io/api/v4/search?q={quote(keyword)}&lang={lang}&max={max_results}&token={api_key}"
    resp = requests.get(url)

    if resp.status_code != 200:
        print(f"❌ API 요청 실패: {resp.status_code}")
        return []

    results = []
    for a in resp.json().get("articles", []):
        results.append({
            "title": a["title"],
            "link": a["url"],
            "thumbnail": a.get("image"),
            "type": None,  # 이후 분류
        })
    print(f"🔍 '{keyword}' → {len(results)}건 수집됨")
    return results

# 📥 수집: 세 범주로 분리
print("📡 GNews API로 서핑 뉴스 수집 중...\n")
korea_articles = get_articles("서핑", lang="ko", max_results=10)
bali_articles = get_articles("surf Bali", lang="en", max_results=10)
global_articles = get_articles("surfing OR surf", lang="en", max_results=20)

# 📂 태그 분류
for a in korea_articles:
    a["type"] = "korea"
for a in bali_articles:
    a["type"] = "bali"
for a in global_articles:
    a["type"] = "global"

# 🧹 중복 제거 (링크 기준)
all_articles = korea_articles + bali_articles + global_articles
unique_articles = []
seen = set()
for a in all_articles:
    if a["link"] not in seen:
        seen.add(a["link"])
        unique_articles.append(a)

print(f"\n📦 최종 수집된 뉴스: {len(unique_articles)}개")

# 📅 날짜 표시용
today = datetime.date.today().strftime("%Y년 %m월 %d일")

# 🎨 템플릿 렌더링
try:
    with open("template.html", "r", encoding="utf-8") as f:
        template = Template(f.read())
    html = template.render(articles=unique_articles, date=today)
except Exception as e:
    print("❌ 템플릿 렌더링 실패:", e)
    html = "<h1>오류 발생!</h1>"

# 💾 저장
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n✅ index.html 생성 완료!")
