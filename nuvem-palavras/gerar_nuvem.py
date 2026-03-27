import argparse
import csv
import os
import re
from collections import Counter

import matplotlib.pyplot as plt
from wordcloud import WordCloud


# Stopwords em portugues e termos muito comuns que poluem a visualizacao.
STOPWORDS_PT = {
    "a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo", "as", "ate",
    "com", "como", "da", "das", "de", "dela", "dele", "deles", "demais", "depois", "do",
    "dos", "e", "ela", "elas", "ele", "eles", "em", "entre", "era", "eram", "essa", "essas",
    "esse", "esses", "esta", "estao", "estas", "estava", "este", "estes", "foi", "foram", "ha",
    "isso", "isto", "ja", "la", "lhe", "lhes", "mais", "mas", "me", "mesmo", "meu", "meus",
    "minha", "minhas", "muito", "na", "nao", "nas", "nem", "no", "nos", "nossa", "nossas",
    "nosso", "nossos", "num", "numa", "o", "os", "ou", "para", "pela", "pelas", "pelo", "pelos",
    "por", "porque", "quando", "que", "quem", "se", "sem", "seu", "seus", "so", "sua", "suas",
    "tambem", "te", "tem", "tendo", "tenho", "ter", "teve", "tinha", "tinham", "todo", "todos",
    "tu", "um", "uma", "umas", "uns", "vai", "vem", "ver", "vez", "voces", "boato", "boatos", "analise",
    "fake", "news", "org", "sobre", "ainda", "anos", "ano", "dia", "dias"
}


def carregar_texto(caminho_csv: str, coluna_texto: str) -> str:
    textos = []
    with open(caminho_csv, "r", encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            conteudo = (linha.get(coluna_texto) or "").strip()
            if conteudo:
                textos.append(conteudo)
    return "\n".join(textos)


def limpar_e_tokenizar(texto: str) -> list[str]:
    texto = texto.lower()
    tokens = re.findall(r"[a-zA-ZÀ-ÿ]{3,}", texto)
    return [token for token in tokens if token not in STOPWORDS_PT]


def exportar_top_frequencias(contador: Counter, caminho_saida_csv: str, top_n: int = 50) -> None:
    with open(caminho_saida_csv, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["palavra", "frequencia"])
        for palavra, frequencia in contador.most_common(top_n):
            escritor.writerow([palavra, frequencia])


def gerar_nuvem(contador: Counter, caminho_imagem: str) -> None:
    nuvem = WordCloud(
        width=1800,
        height=1000,
        background_color="white",
        collocations=False,
        colormap="viridis",
        max_words=300,
    ).generate_from_frequencies(contador)

    plt.figure(figsize=(16, 9))
    plt.imshow(nuvem, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(caminho_imagem, dpi=300)
    plt.close()


def main() -> None:
    pasta_script = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(
        description="Gera nuvem de palavras a partir de um corpus em CSV.")
    parser.add_argument(
        "--input",
        default=os.path.normpath(os.path.join(pasta_script, "..", "corpus.csv")),
        help="Caminho para o arquivo CSV de entrada.",
    )
    parser.add_argument(
        "--coluna",
        default="content",
        help="Nome da coluna de texto no CSV.",
    )
    parser.add_argument(
        "--output-image",
        default=os.path.join(pasta_script, "nuvem_palavras.png"),
        help="Caminho para salvar a imagem PNG da nuvem.",
    )
    parser.add_argument(
        "--output-top",
        default=os.path.join(pasta_script, "top_palavras.csv"),
        help="Caminho para salvar o CSV com as palavras mais frequentes.",
    )

    args = parser.parse_args()

    texto = carregar_texto(args.input, args.coluna)
    tokens = limpar_e_tokenizar(texto)
    contador = Counter(tokens)

    if not contador:
        raise ValueError("Nenhuma palavra valida foi encontrada. Verifique o CSV e a coluna informada.")

    exportar_top_frequencias(contador, args.output_top, top_n=50)
    gerar_nuvem(contador, args.output_image)

    print(f"Nuvem de palavras gerada em: {args.output_image}")
    print(f"Top palavras exportado em: {args.output_top}")


if __name__ == "__main__":
    main()
