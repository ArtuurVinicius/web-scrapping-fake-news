import json
import time
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright


def _extract_text(page):
    selectors = ['.entry-content', '.post-content', 'article', '#content', '.content']
    for sel in selectors:
        elem = page.query_selector(sel)
        if elem:
            ps = elem.query_selector_all('p')
            if ps:
                return '\n\n'.join([p.inner_text().strip() for p in ps if p.inner_text().strip()])
            txt = elem.inner_text().strip()
            if txt:
                return txt
    # fallback: whole page
    try:
        return page.inner_text()
    except Exception:
        return ''


def _extract_title(page):
    for sel in ['h1.entry-title', 'h1.post-title', 'h1']:
        t = page.query_selector(sel)
        if t:
            return t.inner_text().strip()
    return page.title().strip()


def _extract_date(page):
    time_elem = page.query_selector('time')
    if time_elem:
        try:
            return time_elem.get_attribute('datetime') or time_elem.inner_text().strip()
        except Exception:
            return time_elem.inner_text().strip()
    return ''


def _collect_links_from_search(page, query):
    url = f'https://www.boatos.org/?s={query}'
    page.goto(url)
    page.wait_for_timeout(800)
    links = set()
    # common WP structures
    for a in page.query_selector_all('.entry-title a'):
        href = a.get_attribute('href')
        if href:
            links.add(href.split('#')[0])
    # fallback: any anchor with year-like path
    for a in page.query_selector_all('a'):
        href = a.get_attribute('href')
        if href and 'boatos.org' in href and '/202' in href:
            links.add(href.split('#')[0])
    return links


def scrape_boatos_saude(output='corpus.jsonl', max_articles=200, headless=True):
    queries = ['saúde', 'saude', 'vacina', 'vacinas', 'covid', 'coronavírus', 'coronavirus', 'medicamento', 'hospital', 'tratamento', 'doença', 'doenca']
    seen = set()
    count = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        with open(output, 'a', encoding='utf-8') as fout:
            for q in queries:
                links = _collect_links_from_search(page, q)
                for link in links:
                    if link in seen:
                        continue
                    if count >= max_articles:
                        break
                    try:
                        page.goto(link, timeout=30000)
                        page.wait_for_timeout(500)
                        title = _extract_title(page)
                        date = _extract_date(page)
                        content = _extract_text(page)
                        if not content or len(content.split()) < 30:
                            # skip very short pages
                            seen.add(link)
                            continue
                        record = {
                            'url': link,
                            'title': title,
                            'date': date,
                            'content': content,
                            'source': 'boatos.org',
                            'scraped_at': time.strftime('%Y-%m-%dT%H:%M:%S')
                        }
                        fout.write(json.dumps(record, ensure_ascii=False) + '\n')
                        seen.add(link)
                        count += 1
                    except Exception:
                        # ignore and continue
                        continue
                if count >= max_articles:
                    break
        browser.close()
    print(f'Scraped {count} articles to {output}')


if __name__ == '__main__':
    scrape_boatos_saude()
