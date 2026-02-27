from scraper import scrape_boatos_saude

if __name__ == '__main__':
    print('Iniciando debug do scraper...')
    # Execute com menos artigos para debug mais rápido
    # headless=False para ver o browser em ação
    scrape_boatos_saude(
        output='corpus.csv',
        max_articles=10,  # Só 10 artigos para debug rápido
        headless=False,   # Mostrar browser para debug
        load_existing=True,
        max_pages_per_query=5,  # Menos páginas por query
        use_sitemap=True
    )