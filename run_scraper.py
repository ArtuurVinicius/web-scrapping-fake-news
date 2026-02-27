from scraper import scrape_boatos_saude
import time

if __name__ == '__main__':
    print('Iniciando scraper otimizado...')
    
    # Execute com configurações mais conservadoras
    scrape_boatos_saude(
        output='corpus.csv',
        max_articles=50,         # Mais artigos
        headless=True,           # Headless para melhor performance  
        load_existing=True,      # Carrega URLs existentes
        max_pages_per_query=2,   # Menos páginas para evitar timeouts
        use_sitemap=True         # Usa sitemap que já funcionou
    )
    
    print('Scraper finalizado!')