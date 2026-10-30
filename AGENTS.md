# Instruções para agentes de código

Projeto de estudo: um agente com Google ADK, tela de chat em Streamlit, modelo da Groq (via LiteLLM), uma ferramenta própria, uma ferramenta MCP pública (DeepWiki) e guardrails. Quem usa este repositório está aprendendo; explique o que mudou e por quê, em português do Brasil.

## Comandos

- Instalar: `uv sync`
- Testes (sem chave, um deles acessa a internet): `uv run pytest -q`
- Teste de ponta a ponta com a Groq (precisa de `GROQ_API_KEY` no `.env`): `uv run python testar_groq.py`
- Tela de chat: `uv run streamlit run app.py`
- Interface do ADK: `uv run adk web` (na raiz; escolha o agente `agente`)

## Estrutura

- `agente/agent.py`: monta o agente (modelo, instruções, ferramentas, guardrails). `root_agent` é usado pelo `adk web`.
- `agente/ferramentas.py`: ferramentas próprias. A docstring é o que o modelo lê para decidir quando usar.
- `agente/guardrails.py`: `guardrail_entrada` (antes do modelo) e `guardrail_ferramenta` (antes da ferramenta).
- `agente/conversa.py`: roda uma pergunta e devolve a resposta e os passos (chamadas e resultados de ferramentas).
- `app.py`: tela de chat em Streamlit.
- `tests/`: testes com um modelo simulado, sem chave.

## Regras

- Nunca escreva chaves, senhas ou tokens no código, em testes ou em commits. A chave fica no `.env`, que está no `.gitignore`.
- Regra de segurança fica no código (guardrails, validação de argumentos), não só nas instruções do modelo.
- Ferramenta nova: docstring clara (o que faz, quando usar, cada argumento), validação no `guardrail_ferramenta` e um teste em `tests/`.
- Faça uma mudança por vez, rode `uv run pytest -q` antes de terminar e mostre o que mudou.
- Não adicione dependências sem explicar por quê.
- Mantenha os textos para o usuário em português do Brasil.
