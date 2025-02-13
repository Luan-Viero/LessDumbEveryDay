from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from sources import get_with_fallback
from gemini import generate_summary
from urllib.parse import quote
import logging
import os
import webbrowser
import re


load_dotenv()
obsidian_vault_name = os.getenv("OBSIDIAN_VAULT_NAME")
vault_path = Path(os.getenv("VAULT_PATH", "./vault"))

# Cria o diretório se não existir
vault_path.mkdir(parents=True, exist_ok=True)

# Configurar logging
logging.basicConfig(
    filename=vault_path / "knowledge_drop_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)


def create_daily_note(
    title: str, link: str, category: str, daily_stoic_link: str
) -> str:
    # Validação essencial
    if not all([title, link, category]):
        logging.error(
            "Dados essenciais faltando: title=%s, link=%s, category=%s",
            title,
            link,
            category,
        )
        raise ValueError("Dados incompletos para criação da nota")

    try:
        sections = {
            "resumo": "⚠️ Falha ao gerar conteúdo. Leia o artigo original.",
            "pontos_chave": "- Ponto 1\n- Ponto 2",
            "citacao": "> Citação não disponível",
        }

        # Gerar análise do Gemini apenas com link e título
        try:
            gemini_response = generate_summary(link, daily_stoic_link)
        except Exception as e:
            logging.error(f"Erro no Gemini: {str(e)}")
            gemini_response = ""  # Fallback para resposta vazia

        # Extrair seções da resposta
        if gemini_response:
            try:
                # Resumo: Captura tudo entre 'Resumo:' e 'Pontos-chave'
                resumo_match = re.search(
                    r"## Resumo:?(.*?)(?=## Pontos-chave|###|$)",
                    gemini_response,
                    re.IGNORECASE | re.DOTALL,
                )
                if resumo_match:
                    sections["resumo"] = resumo_match.group(1).strip()

                # Pontos-chave: Captura tudo entre 'Pontos-chave' e 'Citação'
                pontos_match = re.search(
                    r"## Pontos-chave:?(.*?)(?=## Citação|###|$)",
                    gemini_response,
                    re.IGNORECASE | re.DOTALL,
                )
                if pontos_match:
                    sections["pontos_chave"] = pontos_match.group(1).strip()

                # Citação: Captura o bloco completo
                citacao_match = re.search(
                    r"## Citação do dia:?(.*?)(?=##|\Z)",
                    gemini_response,
                    re.IGNORECASE | re.DOTALL,
                )
                if citacao_match:
                    sections["citacao"] = citacao_match.group(1).strip()

            except Exception as e:
                logging.error(f"Erro ao processar resposta Gemini: {str(e)}")

        # Gerar ID único
        note_id = datetime.now().strftime("%Y%m%d%H%M")

        # Criar template
        return f"""---
tags: [{category}]
date: {datetime.now().strftime('%Y-%m-%d')}
source: "{category}"
---

# {title}

## Metadata
- **Id:** {note_id}

## Referência
- Fonte: [{category.capitalize()}]({link})

## Resumo
{sections['resumo']}

## Pontos-chave
{sections['pontos_chave']}

## Citação do dia
{sections['citacao']}
"""

    except Exception as e:
        logging.critical(f"Falha crítica: {str(e)}", exc_info=True)
        webbrowser.open(f"obsidian://vault/{quote(obsidian_vault_name)}")
        return ""


if __name__ == "__main__":
    try:
        # Criar pasta se não existir
        vault_path.mkdir(parents=True, exist_ok=True)

        # Determinar fonte do dia
        day = datetime.today().weekday()
        fonts = [
            "wikipedia",
            "science",
            "jstor",
            "nautilus",
            "pesquisa_fapesp",
        ]
        daily_font = fonts[day] if day < 5 else "wikipedia"  # Seg-Sex

        # Obter conteúdo estruturado
        content_data = get_with_fallback(daily_font)

        # Validação reforçada
        if not content_data.get("main") or not content_data.get("daily_stoic"):
            raise ValueError("Dados incompletos das fontes")

        # Extrair componentes da fonte principal
        content = content_data["main"]
        daily_stoic = content_data["daily_stoic"]

        # Extrair componentes
        title = content["title"]
        link = content["link"]
        category = daily_font.capitalize()  # Fallback para fonte do dia

        # Salvar arquivo
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title)[
            :50
        ]  # Remove caracteres inválidos
        file_path = (
            vault_path
            / f"{safe_title} - {datetime.now().strftime('%Y%m%d')}.md"
        )
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(
                create_daily_note(
                    title=title,
                    link=link,
                    category=category,
                    daily_stoic_link=daily_stoic["link"],
                )
            )

        # Após salvar o arquivo:
        if file_path.exists():
            obsidian_url = (
                f"obsidian://open?vault={quote(obsidian_vault_name)}"
                f"&file=Inbox/{quote(file_path.name)}"
            )
            webbrowser.open(obsidian_url)
        else:
            logging.error("Falha ao criar arquivo")
            webbrowser.open(
                f"obsidian://vault/{quote(obsidian_vault_name)}"
            )  # Abre só o vault

    except Exception as e:
        logging.error(f"Erro fatal: {str(e)}")
        webbrowser.open(
            f"obsidian://new?vault={obsidian_vault_name}"
            f"&name=ERRO-{datetime.now().strftime('%Y-%m-%d')}"
        )
