from scraper import scrape_boatos_saude


if __name__ == '__main__':
	print('Iniciando scrapping')
	scrape_boatos_saude(output='corpus.csv')

