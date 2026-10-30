# Agente de exemplo: Google ADK + Streamlit + Groq + MCP

Um projeto pequeno e completo para estudar como se monta um agente de IA de verdade: uma tela de chat, um modelo de linguagem, uma **ferramenta própria**, uma **ferramenta MCP pública** e **guardrails** em código. Tudo com plano gratuito.

```text
Você (tela em Streamlit)
   │
   ▼
Runner do Google ADK ──► guardrail de entrada ──► (barra chave, senha, cartão, CPF: não chega ao modelo)
   │
   ▼
Modelo da Groq (via LiteLLM) ◄──► ferramentas
                                    ├─ estimar_custo (própria) ◄── guardrail de ferramenta valida os argumentos
                                    └─ DeepWiki (MCP público): perguntas sobre repositórios do GitHub
   │
   ▼
Resposta + "passos do agente" (cada chamada de ferramenta e o resultado)
```

## O que você vai ver funcionando

| Peça | Onde está | Tema |
|---|---|---|
| Agente com instruções e ferramentas | `agente/agent.py` | agentes e harness |
| Ferramenta própria, descrita pela docstring | `agente/ferramentas.py` | tool calling |
| Ferramenta MCP pública, com só as ferramentas de leitura liberadas | `criar_mcp()` em `agente/agent.py` | MCP e menor privilégio |
| Guardrail de entrada e guardrail de ferramenta | `agente/guardrails.py` | guardrails |
| Passos do agente na tela | `agente/conversa.py` e `app.py` | observabilidade |
| Testes com modelo simulado | `tests/` | evals |

## Antes de começar

1. **Python 3.12 e uv.** Instale o [uv](https://docs.astral.sh/uv/getting-started/installation/); ele baixa o Python certo sozinho.
2. **Chave gratuita da Groq.** Crie em [console.groq.com/keys](https://console.groq.com/keys). Trate como senha: não cole em chat, issue, print nem commit.

## Como rodar

```bash
git clone https://github.com/paulo-atsinformatica/agente-adk-streamlit.git
cd agente-adk-streamlit
uv sync
cp .env.example .env        # no Windows (PowerShell): copy .env.example .env
```

Abra o `.env` e preencha `GROQ_API_KEY`. Depois:

```bash
uv run streamlit run app.py
```

Abra o endereço que aparecer (normalmente http://localhost:8501) e experimente as perguntas da barra lateral:

- *Quanto custa 2.000 tokens de entrada e 500 de saída, a 0,59 e 0,79 dólares por milhão, 3.000 vezes por dia?* → usa a ferramenta própria.
- *No repositório google/adk-python, o que é um callback?* → usa o MCP do DeepWiki.
- *Minha chave é gsk_abc123...* → o guardrail barra antes de chegar ao modelo.

Abra "Passos do agente" embaixo de cada resposta para ver quais ferramentas ele chamou e o que voltou.

**Alternativa:** a interface do próprio ADK, com o rastro detalhado de cada evento: `uv run adk web` e escolha o agente `agente`.

## Testes

```bash
uv run pytest -q              # sem chave: ferramenta, guardrails e o agente com um modelo simulado
uv run python testar_groq.py  # com a chave: três perguntas de ponta a ponta no modelo de verdade
```

O teste do agente usa um **modelo simulado**: um "LLM de mentira" que pede a ferramenta e depois responde. Assim dá para testar o fluxo inteiro sem gastar nada. Ele acessa a internet para listar as ferramentas do MCP.

## Como cada peça funciona

- **Modelo.** O ADK fala com a Groq pelo LiteLLM (`LiteLlm(model="groq/...")`). Trocar de fornecedor é trocar esse texto. O modelo padrão é `groq/openai/gpt-oss-20b`; os modelos da Groq mudam com o tempo, então confira a [lista](https://console.groq.com/docs/models) e ajuste `GROQ_MODEL` no `.env`.
- **Raciocínio escondido.** Modelos de raciocínio devolvem o "pensamento" junto da resposta, e a Groq recusa receber esse pensamento de volta no turno depois de uma ferramenta. Por isso o projeto pede `reasoning_format: hidden`. Se usar um modelo sem raciocínio, deixe `GROQ_REASONING_FORMAT` vazio.
- **Ferramenta própria.** Uma função Python comum. O modelo não lê o código: lê o nome, a docstring e os tipos dos argumentos para decidir quando usar.
- **MCP.** O agente se conecta ao servidor MCP público do DeepWiki por HTTP. `tool_filter` libera só duas ferramentas de leitura, mesmo que o servidor ofereça mais.
- **Guardrails.** `guardrail_entrada` roda antes de cada chamada ao modelo: se a mensagem tiver chave, senha, cartão ou CPF, devolve uma resposta pronta e o modelo nem é chamado. `guardrail_ferramenta` roda antes da ferramenta e recusa argumentos inválidos. São regras em código: valem mesmo que o modelo seja enganado.

## Limites do plano gratuito

A Groq limita requisições e tokens por minuto. Se aparecer erro de limite (*rate limit*), espere um pouco ou troque para um modelo menor. Respostas longas e muitas chamadas de ferramenta seguidas consomem o limite mais rápido.

## Use um agente de código para ir além

Este repositório foi preparado para você trabalhar junto com um agente de código, como **Google Antigravity**, **Claude Code** ou **OpenAI Codex**. O arquivo `AGENTS.md` (lido pelo Codex e pelo Antigravity; o `CLAUDE.md` aponta para ele) já explica ao agente os comandos, a estrutura e as regras.

Como trabalhar bem com ele:

1. Abra a pasta do projeto no agente e peça primeiro para ele **explicar** o código: *"Leia o projeto e me explique, em poucas linhas, o caminho de uma mensagem do chat até a resposta."*
2. Peça **uma mudança por vez**, com critério de pronto: *"Adicione uma ferramenta que converte dólar para real com uma taxa fixa, com validação no guardrail e um teste. Rode os testes no final."*
3. **Leia o diff** antes de aceitar. Você precisa conseguir explicar cada linha.
4. Rode `uv run pytest -q` e teste na tela.
5. **Nunca cole a sua chave no chat do agente.** Ela fica só no `.env`.

## Exercícios

Do mais simples ao mais desafiador:

1. **Nova ferramenta.** Crie `converter_moeda(valor_usd, cotacao)` com docstring clara, validação no guardrail e um teste.
2. **Falso positivo no guardrail.** Mande *"meu pedido é 12345678901234"*. O guardrail barra como se fosse cartão? Ajuste a regra sem deixar passar cartões de verdade e escreva os testes dos dois casos (pense em precisão e recall).
3. **Guardrail de saída.** Use `after_model_callback` para conferir se a resposta cita a fonte quando usou o DeepWiki; se não citar, acrescente um aviso.
4. **Outro MCP.** Troque ou some outro servidor MCP público (HTTP). Use `tool_filter` para liberar só o necessário.
5. **Evals.** Escreva dez perguntas com o resultado esperado (que ferramenta deveria chamar e o que a resposta deve conter) e um script que rode todas e mostre quantas passaram.
6. **Memória.** Troque `InMemorySessionService` por `DatabaseSessionService` (SQLite) para a conversa sobreviver a um reinício.

## Segurança

- A chave fica no `.env`, que está no `.gitignore`. Nunca a coloque no código.
- Se uma chave vazar, revogue em [console.groq.com/keys](https://console.groq.com/keys) e crie outra; apagar o arquivo não basta, porque o histórico do Git guarda tudo.
- Os guardrails deste projeto são didáticos. Num sistema real, combine regras, classificadores e revisão humana.

## Licença

MIT. Use, copie e adapte à vontade.
