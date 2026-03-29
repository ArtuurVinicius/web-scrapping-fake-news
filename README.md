# Web Crawler para Construção de Corpus em Saúde (Boatos.org)

## 1. Contexto e propósito acadêmico

Este repositório contém o código utilizado na construção de um corpus textual a partir de páginas do portal Boatos.org, com foco temático em saúde. O projeto foi desenvolvido como base empírica para pesquisa acadêmica, com ênfase em coleta reprodutível de dados textuais para análises em Processamento de Linguagem Natural (PLN), desinformação e estudos correlatos.

O sistema implementa um web crawler que identifica URLs candidatas, extrai conteúdo textual de artigos e consolida os registros em formato tabular.

## 2. Artefato principal do projeto

O corpus principal deste projeto é o arquivo:

- `corpus.csv`

Esse arquivo representa a base textual consolidada para uso no trabalho científico.

Estrutura base esperada (colunas):

- `url`: endereço da página coletada;
- `title`: título do artigo;
- `date`: data publicada/extraída da página;
- `content`: texto principal do artigo;
- `source`: fonte do conteúdo (boatos.org).

Observação: dependendo de etapas posteriores de transformação, podem existir colunas adicionais (por exemplo, `lang`).

## 3. Estratégia de coleta (crawler)

O fluxo de coleta foi implementado em `scraper.py` com Playwright e Requests, seguindo uma estratégia híbrida:

1. Coleta de URLs por sitemap do domínio.
2. Coleta complementar por busca paginada com termos relacionados à saúde.
3. Visita de cada URL candidata com renderização via navegador automatizado.
4. Extração de metadados (`title`, `date`) e texto (`content`).
5. Filtros de qualidade/relevância:
	- remoção de textos muito curtos;
	- manutenção de conteúdos com aderência temática em saúde.
6. Deduplicação por registro e escrita incremental no CSV.

Esse desenho visa maximizar cobertura com controle de qualidade textual, respeitando limites de coleta definidos nos scripts.

## 4. Organização do repositório

- `main.py`: ponto de entrada padrão para coleta, com saída em `corpus.csv`.
- `scraper.py`: implementação do crawler e funções de extração.
- `run_scraper.py`: execução com parâmetros mais conservadores (útil para rodadas controladas).
- `debug_scraper.py`: execução de depuração (modo visual do navegador).
- `corpus-transformation/dataTransform.py`: filtragem por idioma e geração de `corpus-pt.csv`.
- `corpus-transformation/remove-scrapped-at.py`: utilitário para remover coluna `scraped_at` quando presente.
- `nuvem-palavras/gerar_nuvem.py`: análise lexical exploratória (nuvem de palavras e top termos).

Arquivos auxiliares de análise (já existentes no projeto), como `analise_tamanho_textos.txt` e `contagem_palavras_por_registro.csv`, documentam estatísticas descritivas do corpus.

## 5. Requisitos

- Python 3.10+
- Dependências Python listadas em `requirements.txt`
- Navegador do Playwright instalado

## 6. Configuração do ambiente (Windows)

No PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install
```

Alternativa no Prompt de Comando (cmd):

```bat
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python -m playwright install
```

## 7. Execução

### 7.1 Coleta principal (gera/atualiza o corpus)

```powershell
python main.py
```

Saída principal: `corpus.csv`.

### 7.2 Execução com parâmetros conservadores

```powershell
python run_scraper.py
```

### 7.3 Execução para depuração

```powershell
python debug_scraper.py
```

## 8. Pós-processamento e análises auxiliares

Filtragem por idioma (português):

```powershell
python corpus-transformation/dataTransform.py
```

Geração de nuvem de palavras:

```powershell
python nuvem-palavras/gerar_nuvem.py
```

## 9. Reprodutibilidade e observações metodológicas

- O crawler utiliza deduplicação para evitar repetição de registros em execuções sucessivas.
- A coleta depende do estado corrente do site (estrutura HTML, disponibilidade de URLs e conteúdo online).
- Resultados podem variar ao longo do tempo devido a atualizações do portal de origem.

## 10. Uso acadêmico e citação

Este repositório foi produzido para fins acadêmicos e pode ser referenciado como material de apoio metodológico para a construção do corpus.

Ao citar o projeto no artigo, recomenda-se mencionar:

- finalidade do crawler;
- fonte dos dados (Boatos.org);
- período de coleta da sua execução experimental;
- arquivo de corpus utilizado na análise (`corpus.csv`).
