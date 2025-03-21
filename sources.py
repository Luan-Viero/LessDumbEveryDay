from bs4 import BeautifulSoup
from typing import Dict, Optional
from urllib.parse import quote
import feedparser
import logging
import random
import requests

TARGET_CATEGORIES = [
    "Aracnologia",
    "Arqueologia",
    "Astronomia",
    "Biologia",
    "Ciências naturais",
    "Cosmologia",
    "Cristianismo",
    "Ética",
    "Evolução",
    "Filosofia medieval",
    "Filosofia",
    "Física",
    "História Antiga",
    "História da ciência",
    "História da Igreja",
    "História da religião",
    "Mitologia",
    "Neurociência",
    "Paleontologia",
    "Reforma Protestante",
    "Sobrevivência",
    "Tecnologia",
    "Tolkien",
]


def get_content(source: str) -> Dict[str, str]:
    """
    Obtém o conteúdo de uma fonte específica e o formata em um dicionário.

    Esta função tenta obter conteúdo de uma fonte especificada, realiza
    validações e retorna um dicionário formatado com o conteúdo principal e um
    conteúdo adicional do Daily Stoic.

    Args:
        source (str): O nome da fonte de conteúdo a ser consultada.

    Returns:
        Dict[str, str]: Um dicionário contendo:
            - 'main': Um dicionário com 'title' e 'link' do conteúdo principal.
            - 'daily_stoic': O conteúdo obtido do Daily Stoic.

    Raises:
        ValueError: Se o conteúdo obtido estiver incompleto.
        Exception: Para qualquer outro erro durante a obtenção ou processamento
            do conteúdo.

    Note:
        - A função usa `globals()` para chamar dinamicamente a função de
            obtenção específica para a fonte fornecida.
        - Erros são registrados usando o módulo `logging`.
    """

    try:
        content = globals()[f"get_{source}"]()

        # Validação rigorosa
        if not content.get("link") or not content.get("title"):
            raise ValueError(f"Conteúdo incompleto de {source}")

        # return content
        return {
            "main": {
                "title": content.get("title", "Título não disponível"),
                "link": content.get("link", ""),
            },
            "daily_stoic": get_daily_stoic(),
        }

    except Exception as e:
        logging.error(f"Falha em '{source}': {str(e)}", exc_info=True)


def generate_fallback_note(failed_sources: list) -> Dict[str, str]:
    """Gera nota de fallback padronizada."""
    return {
        "title": "Falha na Geração Automática",
        "link": "",
        "content": f"""
        **Fontes tentadas:** {", ".join(failed_sources)}

        ## Instruções:
        1. Acesse manualmente: [Wikipedia](https://wikipedia.org)
        2. Escolha um conceito relevante
        3. Adicione seus insights abaixo
        """,
    }


def fetch_feed(url: str, timeout: int = 10) -> Optional[dict]:
    """Obtém e valida feeds RSS/Atom a partir de uma URL.

    Esta função faz uma requisição HTTP para a URL fornecida, tenta obter o
    conteúdo do feed e analisá-lo usando a biblioteca `feedparser`. Se o feed
    for válido e contiver entradas, ele é retornado como um dicionário.
    Caso contrário, retorna `None`.

    Args:
        url (str): A URL do feed RSS/Atom a ser buscado.
        timeout (int, opcional): Tempo limite da requisição em segundos.
            Padrão é 10 segundos.

    Returns:
        Optional[dict]: Um dicionário contendo o feed analisado se houver
        entradas válidas, ou `None` caso contrário.

    Raises:
        requests.RequestException: Se houver erro na requisição HTTP.
        feedparser.FeedParserError: Se houver erro ao processar o feed.
        Exception: Para quaisquer outros erros inesperados.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        return feed if feed.entries else None
    except Exception as e:
        logging.error(f"Erro ao buscar feed: {str(e)}", exc_info=True)
        return None


def fetch_article_from_feed(feed_url: str, source_name: str) -> Dict[str, str]:
    """Busca e processa um artigo aleatório de um feed RSS.

    Esta função obtém um feed RSS/Atom a partir da URL fornecida e seleciona
    aleatoriamente um dos artigos disponíveis. Se o feed não puder ser obtido
    ou estiver vazio, é gerada uma nota alternativa.

    Args:
        feed_url (str): A URL do feed RSS/Atom de onde o artigo será extraído.
        source_name (str): O nome da fonte do feed, usado para personalizar
            mensagens em caso de fallback.

    Returns:
        Dict[str, str]: Um dicionário contendo o título e o link do artigo
            selecionado.
        Se não houver artigos disponíveis, um fallback adequado é retornado.
    """
    feed = fetch_feed(feed_url)
    if not feed:
        return generate_fallback_note([source_name])

    entry = random.choice(feed.entries)
    return {
        "title": entry.get("title", f"Artigo {source_name}"),
        "link": entry.get("link", ""),
    }


def get_wikipedia() -> Dict[str, str]:
    """Obtém artigo aleatório da Wikipedia dentro das categorias-alvo."""
    try:
        category = random.choice(TARGET_CATEGORIES)
        response = requests.get(
            "https://pt.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Categoria:{category}",
                "cmtype": "page",
                "cmlimit": 50,
                "format": "json",
            },
            timeout=10,
        )
        response.raise_for_status()
        pages = response.json().get("query", {}).get("categorymembers", [])
        if not pages:
            return generate_fallback_note(["Wikipedia"])

        title = random.choice(pages)["title"]
        article_response = requests.get(
            f"https://pt.wikipedia.org/api/rest_v1/page/summary/"
            f"{quote(title)}",
            params={"redirect": "true"},
            timeout=10,
        )
        article_response.raise_for_status()
        data = article_response.json()
        return {
            "title": data.get("title", "Artigo Desconhecido"),
            "link": data["content_urls"]["desktop"]["page"],
        }
    except Exception as e:
        logging.error(f"Erro Wikipedia: {str(e)}", exc_info=True)
        return generate_fallback_note(["Wikipedia"])


def get_jstor() -> Dict[str, str]:
    """Obtém artigo do JSTOR Daily."""
    return fetch_article_from_feed("https://daily.jstor.org/feed/", "JSTOR")


def get_plato() -> Dict[str, str]:
    """Obtém verbete aleatório da Stanford Encyclopedia of Philosophy"""
    try:
        response = requests.get(
            "https://plato.stanford.edu/cgi-bin/encyclopedia/random"
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Extrai o título da entrada (está em um <h1>)
        title_element = soup.find("h1")
        if not title_element:
            raise ValueError("Título não encontrado na página")

        title = title_element.text.strip()

        # Usa a URL final após o redirecionamento como link
        return {"title": title, "link": response.url}

    except Exception as e:
        # Em caso de erro, retorna uma entrada de fallback
        print(f"Erro: {e}")
        return generate_fallback_note(["Stanford Philosophy"])


def get_daily_stoic() -> Dict[str, str]:
    """Obtém artigo do Daily Stoic via RSS."""
    return fetch_article_from_feed(
        "https://dailystoic.com/feed/", "Daily Stoic"
    )
