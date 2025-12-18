# все ссылки на статьи
import requests
from bs4 import BeautifulSoup
import json
import time
import random

def all_links():
    all_articles = []
    base_url = "https://apa.az/economy?page="

    for page in range(1, 44):
        url = f"{base_url}{page}"
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                print(f"страница {page}, ошибка {response.status_code}")
                break
            soup = BeautifulSoup(response.text, 'html.parser')
            container = soup.select_one('div.four_columns_block')

            if not container:
                print(f"страница {page}, ошибка")
                break

            links = container.find_all('a', href=True)

            page_articles = []
            for link in links:
                href = link.get('href', '')
                if href.startswith('/'):
                    href = f"https://apa.az{href}"

                article_data = {
                    "url": href,
                    "title": link.get_text(strip=True)[:100] if link.get_text(strip=True) else "",
                    "page": page,
                    "position": len(page_articles) + 1
                }
                page_articles.append(article_data)

            all_articles.extend(page_articles)

            print(f"страница {page:2d},  найдено {len(page_articles)} статей (всего: {len(all_articles)})")

            if page < 43:
                delay = random.uniform(2, 4)
                time.sleep(delay)

        except Exception as e:
            print(f"страница {page}  ошибка - {str(e)[:50]}")
            time.sleep(5) 
            continue

    output_data = {
        "source": "apa.az/economy",
        "total_articles": len(all_articles),
        "total_pages": min(page, 43),
        "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "articles": all_articles
    }

    filename = f"apa_economy_articles.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"собрано: {len(all_articles)} статей")

    return all_articles

all_links()