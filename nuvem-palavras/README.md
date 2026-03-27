# Nuvem de palavras do corpus

Este diretório contém o script para gerar uma nuvem de palavras a partir do arquivo `../corpus.csv`.

## Arquivos

- `gerar_nuvem.py`: script principal.
- `nuvem_palavras.png`: imagem gerada (saida).
- `top_palavras.csv`: top 50 palavras mais frequentes (saida).

## Como executar

Na raiz do projeto:

```bash
python nuvem-palavras/gerar_nuvem.py
```

Com parametros opcionais:

```bash
python nuvem-palavras/gerar_nuvem.py --input corpus.csv --coluna content
```

## Saidas

- Gera a imagem em `nuvem-palavras/nuvem_palavras.png`.
- Gera o ranking em `nuvem-palavras/top_palavras.csv`.
