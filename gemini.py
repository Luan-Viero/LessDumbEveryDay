from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()
api_key = os.getenv("API_KEY")
api_model = os.getenv("API_MODEL")


def generate_summary(
    main_link: str,
    daily_stoic_link: str,
) -> str:
    """
    Gera resumo, pontos-chave e citação para a nota no formato especificado
    """
    try:
        genai.configure(api_key=api_key, transport="rest")
        model = genai.GenerativeModel(api_model)

        prompt = f"""\
# TAREFA DE ANÁLISE ESTRUTURADA PARA OBSIDIAN

## FUNÇÃO:
Você é um assistente de pesquisa acadêmica especializado em extração e formatação rigorosa.

## INSTRUÇÕES:
1. Acesse e analise SEPARADAMENTE:
    - Conteúdo principal: '{main_link}'
    - Daily Stoic: '{daily_stoic_link}'

2. Para o conteúdo principal:
    a. RESUMO: 3-5 parágrafos técnicos com definições precisas e contexto epistemológico
    b. PONTOS-CHAVE: 3-5 elementos com:
        - Título conciso (max 7 palavras)
        - Descrição objetiva (1 frase)
        - Aplicação prática (1 exemplo concreto)

3. Para o Daily Stoic:
    a. Extraia a citação COMPLETA do dia
    b. Traduza literalmente para português entre > e -
    c. Retorne a citação traduzida mantendo a formatação exata do exemplo

## FORMATO OBRIGATÓRIO:
```markdown
## Resumo:
[Conteúdo analítico sem markdown. Inclua referências a escolas de pensamento e contexto histórico quando aplicável.]

## Pontos-chave:
- **Título 1:** Descrição objetiva.
    - **Aplicação prática:** Exemplo específico.

(Repetir para 3-5 pontos)

---

## Citação do dia:
> "[Tradução literal]"
- [Autor]```
"""

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"""## Resumo:
Erro na análise. Leia o artigo manualmente.

## Pontos-chave:
- {str(e)}

## Citação do dia:
> Citação não disponível"""
