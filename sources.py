from bs4 import BeautifulSoup
from typing import Dict, Optional
from urllib.parse import quote
import feedparser
import logging
import random
import requests

# Mapeamento de fallback para fontes
FALLBACK_MAP = {
    "wikipedia": ["pesquisa_fapesp", "jstor"],
    "science": ["wikipedia", "nautilus"],
    "jstor": ["science", "wikipedia"],
    "pesquisa_fapesp": ["science", "jstor"],
    "nautilus": ["pesquisa_fapesp", "wikipedia"],
}

TARGET_CATEGORIES = [
    "Aracnologia",
    "Astronomia",
    "Biologia",
    "Ciências naturais",
    "Cosmologia",
    "Cristianismo",
    "Física",
    "História antiga",
    "História da ciência",
    "História da Igreja",
    "História da religião",
    "Mitologia",
    "Paleontologia",
    "Reforma Protestante",
    "Sobrevivência",
    "Tecnologia",
    "Tolkien",
]


def get_with_fallback(source: str, max_fallbacks: int = 2) -> Dict[str, str]:
    """Tenta a fonte principal e fallbacks em caso de erro."""
    sources = [source] + FALLBACK_MAP.get(source, [])

    for attempt, current_source in enumerate(sources):
        try:
            content = globals()[f"get_{current_source}"]()
            if content:
                content = content
                break

            logging.warning(
                f"Conteúdo inválido de {current_source}. Tentando fallback..."
            )

        except Exception:
            logging.error(f"Falha em {current_source}", exc_info=True)
            if attempt >= max_fallbacks:
                break
    # Se não conseguir obter o conteúdo da fonte principal, usa fallback
    if not content:
        content = generate_fallback_note(sources)

    # Obtém o conteúdo do Daily Stoic
    daily_stoic_content = get_daily_stoic()

    # Retorna um dicionário com ambos os conteúdos
    return {
        "main": {
            "title": content.get("title", "Título não disponível"),
            "link": content.get("link", ""),
            "content": content.get("content", "Conteúdo não disponível"),
        },
        "daily_stoic": {
            "title": daily_stoic_content.get("title", "Daily Stoic"),
            "link": daily_stoic_content.get("link", ""),
            "content": daily_stoic_content.get(
                "content", "Conteúdo não disponível"
            ),
        },
    }


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
    """Obtém e valida feeds RSS/Atom."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        return feed if feed.entries else None
    except Exception as e:
        logging.error(f"Erro ao buscar feed: {str(e)}", exc_info=True)
        return None


def extract_content(entry: dict, max_length: int = 2000) -> str:
    """Extrai e sanitiza o conteúdo de um artigo."""
    soup = BeautifulSoup(entry.get("description", ""), "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return text[:max_length] if text else "Sem conteúdo disponível."


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
            f"https://pt.wikipedia.org/api/rest_v1/page/summary/{quote(title)}",
            params={"redirect": "true"},
            timeout=10,
        )
        article_response.raise_for_status()
        data = article_response.json()
        return {
            "title": data.get("title", "Artigo Desconhecido"),
            "link": data["content_urls"]["desktop"]["page"],
            "content": data.get("extract", "Sem resumo disponível."),
        }
    except Exception as e:
        logging.error(f"Erro Wikipedia: {str(e)}", exc_info=True)
        return generate_fallback_note(["Wikipedia"])


def get_jstor() -> Dict[str, str]:
    """Obtém artigo do JSTOR Daily."""
    return fetch_article_from_feed("https://daily.jstor.org/feed/", "JSTOR")


def get_pesquisa_fapesp() -> Dict[str, str]:
    """Obtém artigo da Pesquisa FAPESP via RSS."""
    return fetch_article_from_feed(
        "https://revistapesquisa.fapesp.br/feed/", "Pesquisa FAPESP"
    )


def get_nautilus() -> Dict[str, str]:
    """Obtém artigo do Nautilus via RSS."""
    return fetch_article_from_feed("https://nautil.us/feed/", "Nautilus")


def get_science() -> Dict[str, str]:
    """Obtém artigo do Nautilus via RSS."""
    return fetch_article_from_feed(
        "https://www.science.org/rss/news_current.xml", "Science"
    )


def get_daily_stoic() -> Dict[str, str]:
    """Obtém artigo do Daily Stoic via RSS."""
    return fetch_article_from_feed(
        "https://dailystoic.com/feed/", "Daily Stoic"
    )


def fetch_article_from_feed(feed_url: str, source_name: str) -> Dict[str, str]:
    """Busca e processa um artigo de um feed RSS."""
    feed = fetch_feed(feed_url)
    if not feed:
        return generate_fallback_note([source_name])

    entry = random.choice(feed.entries)
    return {
        "title": entry.get("title", f"Artigo {source_name}"),
        "link": entry.get("link", ""),
        "content": extract_content(entry),
    }
