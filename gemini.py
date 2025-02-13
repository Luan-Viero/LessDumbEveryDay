from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()
api_key = os.getenv("API_KEY")


def generate_summary(
    main_link: str,
    daily_stoic_link: str,
) -> str:
    """
    Gera resumo, pontos-chave e citação para a nota no formato especificado
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")

        prompt = f"""\
# ANÁLISE SEPARADA DE FONTES - FORMATAÇÃO RIGOROSA

## INSTRUÇÕES GERAIS:
- **Siga estritamente o formato exigido** abaixo, sem adicionar ou remover \
    elementos estruturais.
- **Não misture informações** de `{main_link}` com `{daily_stoic_link}`.
- **A resposta deve ser sempre em português**, independentemente do idioma \
    original das fontes.
- **Mantenha o padrão visual exato**: títulos, bullets e separações devem ser \
    respeitados.
- **Não interprete ou reformule informações**, apenas extraia e formate.

---

## FORMATO OBRIGATÓRIO DA RESPOSTA:

<!-- TAREFA 1 - ANÁLISE PRINCIPAL -->

<!-- Link: {main_link} -->

## Resumo:

<!-- Aplicar princípio 80/20: 1 parágrafo denso com os 20% de conceitos que \
    entregam 80% do valor -->

## Pontos-chave:

- **[TÍTULO DO PONTO]:** [Descrição objetiva do ponto].
    - **Aplicação prática:** [Explicação de como aplicar].

- **[TÍTULO DO PONTO]:** [Descrição objetiva do ponto].
    - **Aplicação prática:** [Explicação de como aplicar].

- **[TÍTULO DO PONTO]:** [Descrição objetiva do ponto].
    - **Aplicação prática:** [Explicação de como aplicar].

- *(Opcional: até 5 pontos no total)*

---

<!-- TAREFA 2 - DAILY STOIC -->

<!-- Link: {daily_stoic_link} -->

## Citação do dia:

> "[Texto EXATO da citação mais relevante do Daily Stoic]"
- [Autor da citação] (se identificado)

---

## EXEMPLO DE SAÍDA ESPERADA:

```markdown
## Resumo:

Resumo do link principal.

## Pontos-chave:

- **Título:** Descrição.
    - **Aplicação prática:** Explicação.

- **Título:** Descrição.
    - **Aplicação prática:** Explicação.

- **Título:** Descrição.
    - **Aplicação prática:** Explicação.

---

## Citação do dia:

> "Citação."
- Autor

---
```

**IMPORTANTE:**
A saída **deve ser exatamente** como o exemplo acima. O modelo **NÃO deve \
    alterar a estrutura ou formato**.
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
