"""O agente: modelo da Groq (via LiteLLM), uma ferramenta própria, uma ferramenta MCP pública e guardrails.

Funciona com a tela em Streamlit (app.py) e também com a interface do ADK (`adk web`).
"""
import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

from .ferramentas import estimar_custo
from .guardrails import guardrail_entrada, guardrail_ferramenta

load_dotenv()

# Modelo da Groq com suporte a ferramentas. Troque em GROQ_MODEL, no arquivo .env
# (lista em https://console.groq.com/docs/models; use o prefixo "groq/").
MODELO = os.getenv("GROQ_MODEL", "groq/openai/gpt-oss-20b")
# Modelos de raciocínio devolvem o "pensamento" junto da resposta, e a Groq recusa recebê-lo de volta
# no turno seguinte (depois de uma ferramenta). "hidden" pede para não devolver. Deixe vazio em
# GROQ_REASONING_FORMAT se usar um modelo sem raciocínio.
FORMATO_RACIOCINIO = os.getenv("GROQ_REASONING_FORMAT", "hidden")

# MCP público e sem login: o DeepWiki responde perguntas sobre repositórios do GitHub.
# tool_filter deixa só as ferramentas de leitura que o agente precisa (menor privilégio).
URL_MCP = os.getenv("MCP_URL", "https://mcp.deepwiki.com/mcp")

INSTRUCOES = """Você é o assistente de estudos de quem está aprendendo a ser Analista de IA.
Responda em português do Brasil, de forma curta e direta.

Ferramentas:
- estimar_custo: para calcular o custo de chamadas a um modelo. Nunca faça a conta de cabeça.
- ask_wiki_question / read_wiki_structure (DeepWiki): para dúvidas sobre um repositório público do GitHub,
  informado como "dono/repositorio" (por exemplo, google/adk-python).

Regras:
- Se não souber e nenhuma ferramenta ajudar, diga que não sabe. Não invente.
- Cite de onde veio a informação (a ferramenta ou o repositório consultado).
- Nunca peça chaves de API, senhas ou dados pessoais.
"""


def criar_modelo() -> LiteLlm:
    extra = {"extra_body": {"reasoning_format": FORMATO_RACIOCINIO}} if FORMATO_RACIOCINIO else {}
    return LiteLlm(model=MODELO, **extra)


def criar_mcp() -> McpToolset:
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=URL_MCP, timeout=30),
        tool_filter=["ask_wiki_question", "read_wiki_structure"],
    )


def criar_agente(modelo=None) -> Agent:
    """Monta o agente. `modelo` permite trocar o LLM nos testes (por exemplo, por uma resposta simulada)."""
    return Agent(
        name="assistente_analista_ia",
        description="Assistente de estudos com uma ferramenta de custo e o MCP público do DeepWiki.",
        model=modelo or criar_modelo(),
        instruction=INSTRUCOES,
        tools=[estimar_custo, criar_mcp()],
        before_model_callback=guardrail_entrada,
        before_tool_callback=guardrail_ferramenta,
    )


# O `adk web` procura uma variável chamada root_agent.
root_agent = criar_agente()
