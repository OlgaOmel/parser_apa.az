# !pip install trafilatura
import time
import random
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import trafilatura

# парсер на одну статью
def parser(url):
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            return None

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # заголовок
        title_e = soup.select_one('h2.title_news.mb-site')
        title = title_e.get_text(strip=True) if title_e else None

        # дата
        article_date_e = soup.select_one('span.date')
        article_date = article_date_e.get_text(strip=True) if article_date_e else None

        # раздел
        section_e = soup.select_one('div.breadcrumb_row h1')
        section = section_e.get_text(strip=True) if section_e else None

        # автор и теги
        author = None
        tags = None

        tags_block = soup.select_one('div.tags.mt-site')
        if tags_block:
            # автор
            author_e = tags_block.select_one('div.logo span')
            author = author_e.get_text(strip=True) if author_e else None

            # теги
            tags_e = tags_block.select_one('div.links')
            if tags_e:
                tag_list = [a.get_text(strip=True) for a in tags_e.find_all('a')]
                tags = [t for t in tag_list if t] or None

        # текст через trafilatura
        article_text = None
        try:
            downloaded = trafilatura.fetch_url(url)
            article_text = trafilatura.extract(downloaded)
        except:
            pass

        # запасной вариант для текста через суп
        if not article_text:
            content_block = soup.select_one('div.news_content div.texts.mb-site[itemprop="articleBody"]')
            if content_block:
                paragraphs = [p.get_text(strip=True) for p in content_block.find_all('p')]
                article_text = '\n\n'.join(paragraphs)

        result = {
            "source": "https://apa.az/economy",
            "url": url,
            "title": title,
            "author": author,
            "parse_date": datetime.now().isoformat(),
            "article_date": article_date,
            "text": article_text,
            "section": section,
            "tags": tags
        }

        return result

    except Exception as e:
        print(f"ошибка {str(e)[:50]}")
        return None

# парсер на все статьи
def parse():
    with open('apa_economy_articles.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    urls = [article['url'] for article in data['articles']]

    print(f"всего статей {len(urls)}")

    all_articles = []
    failed_urls = []

    for i, url in enumerate(urls, 1):
        print(f"[{i:3d}/{len(urls)}] {url.split('/')[-1][:30]}...")

        article = parser(url)

        if article and article.get('text'):
            all_articles.append(article)
            text_len = len(article['text'])
            print(f"{text_len} символов")
        else:
            failed_urls.append(url)
            print(f"ошибка")
        # задержка в секундах
        if i < len(urls):
            sleep_time = 3 + random.random() * 2
            time.sleep(sleep_time)
        # автосохранение во врем. файл, сейчас стоит на каждые 20 статей
        if i % 20 == 0:
            with open('parsed_articles_partial.json', 'w', encoding='utf-8') as f:
                json.dump(all_articles, f, ensure_ascii=False, indent=2)
            print(f"автосохранение, ({i} статей)")
    print("готово")
 
    with open('parsed_articles_complete.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    # если неудачные URL или заглушки от джаваскрипта
    if failed_urls:
        with open('failed_urls.txt', 'w', encoding='utf-8') as f:
            for url in failed_urls:
                f.write(url + '\n')

    print(f"успешно: {len(all_articles)} статей")
    print(f"не успешно: {len(failed_urls)} статей")

parse()