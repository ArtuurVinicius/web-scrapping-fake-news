import json
import os
import time
import requests
import xml.etree.ElementTree as ET
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
    # single-page search collector (kept for compatibility)
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


def _collect_links_from_search_paginated(page, query, max_pages=20):
    """Collect links from multiple search result pages for a query."""
    links = set()
    for p in range(1, max_pages + 1):
        # Try common WP search pagination patterns
        urls_to_try = [f'https://www.boatos.org/page/{p}/?s={query}', f'https://www.boatos.org/?s={query}&paged={p}']
        success = False
        for url in urls_to_try:
            try:
                page.goto(url, timeout=30000, wait_until='domcontentloaded')
                page.wait_for_timeout(1000)
                # if page contains no results, break
                items = page.query_selector_all('.entry-title a')
                if not items:
                    # try scanning anchors for year-like links as fallback
                    anchors = page.query_selector_all('a')
                    found = False
                    for a in anchors:
                        href = a.get_attribute('href')
                        if href and 'boatos.org' in href and '/202' in href:
                            links.add(href.split('#')[0])
                            found = True
                    if not found:
                        success = False
                        continue
                for a in items:
                    href = a.get_attribute('href')
                    if href:
                        links.add(href.split('#')[0])
                success = True
                break
            except Exception as e:
                print(f"Erro ao acessar {url}: {e}")
                time.sleep(2)  # Espera antes de tentar próxima URL
                continue
        if not success:
            print(f"Falha ao obter resultados da página {p} para '{query}'")
            break
        time.sleep(1)  # Pausa entre páginas
    return links


def _collect_links_from_sitemap(sitemap_url='https://www.boatos.org/sitemap.xml'):
    """Fetch sitemap(s) and return all URLs found."""
    urls = set()
    try:
        resp = requests.get(sitemap_url, timeout=10)
        if resp.status_code != 200:
            return urls
        root = ET.fromstring(resp.content)
        # handle both sitemapindex and urlset
        for elem in root.iter():
            if elem.tag.endswith('loc') and elem.text:
                urls.add(elem.text.strip())
        # if sitemap contained sitemap entries (pointing to other sitemaps), fetch them
        # heurstic: if any child is a sitemap (contains '/sitemap' in url), fetch those
        child_sitemaps = [u for u in urls if '/sitemap' in u and u.endswith('.xml')]
        all_urls = set(urls)
        for sm in child_sitemaps:
            try:
                r2 = requests.get(sm, timeout=10)
                if r2.status_code != 200:
                    continue
                root2 = ET.fromstring(r2.content)
                for elem in root2.iter():
                    if elem.tag.endswith('loc') and elem.text:
                        all_urls.add(elem.text.strip())
            except Exception:
                continue
        return all_urls
    except Exception:
        return urls


def scrape_boatos_saude(output='corpus.jsonl', max_articles=2000, headless=True, load_existing=True, max_pages_per_query=50, use_sitemap=True):
    queries = [
        'saúde', 'saude', 'vacina', 'vacinas', 'covid', 'coronavírus', 'coronavirus', 'medicamento', 'hospital',
        'tratamento', 'doença', 'doenca', 'sintoma', 'epidemia', 'pandemia', 'febre', 'gripe', 'dengue',
        'zika', 'chikungunya', 'h1n1', 'sarampo', 'câncer', 'cancer', 'aids', 'hiv', 'oms', 'anvisa',
        'sus', 'infecção', 'infectado', 'cura', 'remédio', 'remedios', 'farmácia', 'farmacia', 'enfermidade',
        'prevenção', 'prevencao', 'imunização', 'imunizacao', 'mutação', 'mutacao', 'vírus', 'virus', 'bactéria', 'bacteria'
    ]
    health_keywords = [q.lower() for q in queries]
    seen = set()
    
    count = 0
    skipped_existing = 0
    # Garante criação do arquivo CSV com cabeçalho
    import csv
    fieldnames = ['url', 'title', 'date', 'content', 'source']
    if not os.path.exists(output):
        with open(output, 'w', encoding='utf-8', newline='') as fout:
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()

    # Load existing URLs from output CSV file to avoid duplicates across runs
    if load_existing and os.path.exists(output):
        try:
            with open(output, 'r', encoding='utf-8', newline='') as fin:
                reader = csv.DictReader(fin)
                for row in reader:
                    key = tuple(row.get(f) for f in fieldnames)
                    seen.add(key)
        except Exception:
            pass
    print(f"Iniciando scraper... URLs já coletadas: {len(seen)}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        # Prioriza busca no boatos.org
        print("Coletando URLs do boatos.org...")
        candidates = set()
        try:
            sitemap_urls = _collect_links_from_sitemap()
            for u in sitemap_urls:
                lu = u.lower()
                if any(k in lu for k in health_keywords):
                    candidates.add(u)
            print(f"URLs relevantes de saúde no boatos.org: {len(candidates)}")
        except Exception as e:
            print(f"Erro ao coletar sitemap: {e}")

        # Fallback: search for each query
        for q in queries:
            try:
                links = _collect_links_from_search_paginated(page, q, max_pages=max_pages_per_query)
                print(f"URLs encontradas para '{q}': {len(links)}")
                candidates.update(links)
            except Exception as e:
                print(f"Erro ao buscar '{q}': {e}")
                try:
                    page.close()
                    page = browser.new_page()
                except:
                    pass
                continue

        # Process all collected candidates
        processed = 0
        with open(output, 'a', encoding='utf-8', newline='') as fout:
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            for link in sorted(candidates):
                processed += 1
                if processed % 10 == 0:
                    print(f"Processando URL {processed}/{len(candidates)} - Coletados: {count}")
                if count >= max_articles:
                    print(f"Limite de {max_articles} artigos atingido")
                    break
                print(f"Processando: {link}")
                try:
                    page.goto(link, timeout=30000, wait_until='domcontentloaded')
                    page.wait_for_timeout(1000)
                    title = _extract_title(page)
                    date = _extract_date(page)
                    content = _extract_text(page)
                    if not content or len(content.split()) < 30:
                        print(f"  Pulando: conteúdo muito curto ({len(content.split()) if content else 0} palavras)")
                        continue
                    # filter by content keywords to ensure relevance
                    lc = content.lower()
                    if not any(k in lc for k in health_keywords) and not any(k in link.lower() for k in health_keywords):
                        print(f"  Pulando: não relevante para saúde")
                        continue
                    record = {
                        'url': link,
                        'title': title,
                        'date': date,
                        'content': content,
                        'source': 'boatos.org'
                    }
                    key = tuple(record[f] for f in fieldnames)
                    if key in seen:
                        skipped_existing += 1
                        continue
                    writer.writerow(record)
                    fout.flush()  # Force write to disk
                    seen.add(key)
                    count += 1
                    print(f"  ✓ Coletado: {title[:50]}...")
                    # brief pause to be polite to the site
                    time.sleep(0.2)
                except Exception as e:
                    print(f"  Erro ao processar {link}: {e}")
                    continue

        browser.close()
    print(f'Scraped {count} articles to {output} (skipped {skipped_existing} already-collected URLs)')


if __name__ == '__main__':
    scrape_boatos_saude()
