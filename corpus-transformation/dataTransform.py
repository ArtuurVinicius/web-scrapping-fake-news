
import pandas as pd
from langdetect import detect, LangDetectException


# Carregar o dataset
df = pd.read_csv('corpus.csv')


# Detectar idioma do texto principal (content)
def detect_lang(text):
	try:
		return detect(str(text))
	except LangDetectException:
		return 'unknown'

# Adiciona coluna com idioma detectado
df['lang'] = df['content'].apply(detect_lang)

# Filtra apenas registros em português
df = df[df['lang'] == 'pt']

echo = '\n'
print('Primeiras linhas do dataset (apenas português):')
print(df.head())


# Informações gerais sobre o dataset
print(f'{echo}Informações gerais:')
print(df.info())


# Contagem de valores nulos por coluna
print(f'{echo}Valores nulos por coluna:')
print(df.isnull().sum())



# Estatísticas básicas das colunas
print(f'{echo}Estatísticas básicas:')
print(df.describe(include='all'))

# Salvar resultado filtrado em novo arquivo
df.to_csv('corpus-pt.csv', index=False)
print(f'{echo}Arquivo corpus-pt.csv salvo com os registros em português.')
