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
        genai.configure(api_key=api_key, transport="rest")
        model = genai.GenerativeModel("gemini-1.5-pro-latest")

        prompt = f"""\
# ANÁLISE SEPARADA DE FONTES - FORMATAÇÃO RIGOROSA

## INSTRUÇÕES GERAIS:
- **Acesse o link {main_link} e ANALISE CUIDADOSAMENTE o conteúdo principal do texto.**
- **Leia ATENTAMENTE o conteúdo do link {main_link} para identificar e extrair as informações solicitadas.**
- **EXTRAIA as informações EXATAS do link, SEM INTERPRETAR, RESUMIR ou PARAFRASEAR.**
- **MANTENHA o formato de saída EXATAMENTE como no exemplo fornecido, sem adicionar ou remover elementos.**
- **Acesse o link {daily_stoic_link} e EXAMINE o conteúdo, identificando a citação mais relevante do dia.**
- **A saída deve ser EXATAMENTE como o exemplo fornecido, sem qualquer alteração na estrutura ou formato.**
- **NÃO adicione informações extras ou faça suposições. Extraia APENAS o que é solicitado.**
- **A resposta deve ser SEMPRE em português**, independentemente do idioma original das fontes.
- **Mantenha o padrão visual exato**: títulos, bullets e separações devem ser respeitados.
- **Não interprete ou reformule informações**, apenas extraia das fontes fornecidas e formate.


---

## FORMATO OBRIGATÓRIO DA RESPOSTA:

<!-- TAREFA 1 - ANÁLISE PRINCIPAL -->

<!-- Acesse {main_link} e extraia do conteúdo principal do texto, o que se pede: -->

## Resumo:

<!-- Leia atentamente o conteúdo do link fornecido e:
- Explique o conceito do conteúdo de forma clara, precisa e fundamentada, sem inventar informações.
- Use definições bem estabelecidas e, se necessário, inclua exemplos concretos ou analogias para facilitar o entendimento.
- O nível de detalhamento deve ser adequado para alguém com conhecimento intermediário no assunto, garantindo profundidade sem ser excessivamente técnico.
- Caso existam diferentes abordagens ou interpretações, apresente-as de forma equilibrada, destacando os principais pontos de consenso e divergência.
- Evite simplificações excessivas e especulações. -->

## Pontos-chave:

- **[TÍTULO DO PONTO]:** [Descrição objetiva do ponto].
    - **Aplicação prática:** [Explicação de como aplicar(se necessário)].

- **[TÍTULO DO PONTO]:** [Descrição objetiva do ponto].
    - **Aplicação prática:** [Explicação de como aplicar(se necessário)].

- **[TÍTULO DO PONTO]:** [Descrição objetiva do ponto].
    - **Aplicação prática:** [Explicação de como aplicar(se necessário)].

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
A saída **deve ser exatamente** como o exemplo acima. O modelo **NÃO deve alterar a estrutura ou formato**.
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
