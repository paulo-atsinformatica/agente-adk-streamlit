"""O agente: modelo da Groq (via LiteLLM), uma ferramenta própria, um MCP local, um MCP público e guardrails.

Funciona com a tela em Streamlit (app.py) e também com a interface do ADK (`adk web`).
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams, StreamableHTTPConnectionParams
from mcp import StdioServerParameters

from .ferramentas import estimar_custo
from .guardrails import guardrail_entrada, guardrail_ferramenta

load_dotenv()
RAIZ = Path(__file__).resolve().parent.parent

# Modelo da Groq com suporte a ferramentas. Troque em GROQ_MODEL, no arquivo .env
# (lista em https://console.groq.com/docs/models; use o prefixo "groq/").
MODELO = os.getenv("GROQ_MODEL", "groq/openai/gpt-oss-20b")
# Modelos de raciocínio devolvem o "pensamento" junto da resposta, e a Groq recusa recebê-lo de volta
# no turno seguinte (depois de uma ferramenta). "hidden" pede para não devolver. Deixe vazio em
# GROQ_REASONING_FORMAT se usar um modelo sem raciocínio.
FORMATO_RACIOCINIO = os.getenv("GROQ_REASONING_FORMAT", "hidden")

# MCP público e sem login: o DeepWiki responde perguntas sobre repositórios do GitHub.
URL_MCP = os.getenv("MCP_URL", "https://mcp.deepwiki.com/mcp")

INSTRUCOES = """Você é o assistente de estudos de quem está aprendendo a ser Analista de IA.
Responda em português do Brasil, de forma curta e direta.

Ao se apresentar, diga em uma frase que ajuda a estudar para ser Analista de IA. Não liste nomes de
ferramentas nem detalhes técnicos de como você funciona, a menos que a pessoa pergunte.

Como responder:
- Conceitos de IA (o que é RAG, embedding, MCP, guardrail...): use consultar_glossario.
- O que um Analista de IA faz ou precisa saber: use competencias_analista_ia.
- Como e em quanto tempo estudar: use roteiro_de_estudos.
- Custo de chamadas a um modelo: use estimar_custo. Nunca faça a conta de cabeça.
- Dúvidas sobre um repositório público do GitHub ("dono/repositorio", por exemplo google/adk-python):
  use ask_wiki_question ou read_wiki_structure.

Regras:
- Se não souber e nenhuma ferramenta ajudar, diga que não sabe. Não invente.
- Quando usar uma ferramenta, baseie a resposta no que ela devolveu.
- Nunca peça chaves de API, senhas ou dados pessoais.
"""


def criar_modelo() -> LiteLlm:
    extra = {"extra_body": {"reasoning_format": FORMATO_RACIOCINIO}} if FORMATO_RACIOCINIO else {}
    return LiteLlm(model=MODELO, **extra)


def criar_mcp_local() -> McpToolset:
    """MCP local, em Python (mcp_analista/servidor.py): o agente inicia o processo e conversa por stdio."""
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(command=sys.executable, args=["-m", "mcp_analista.servidor"], cwd=str(RAIZ)),
            timeout=30,
        ),
    )


def criar_mcp_publico() -> McpToolset:
    """MCP público por HTTP. tool_filter libera só as ferramentas de leitura que o agente precisa (menor privilégio)."""
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=URL_MCP, timeout=30),
        tool_filter=["ask_wiki_question", "read_wiki_structure"],
    )


def criar_agente(modelo=None) -> Agent:
    """Monta o agente. `modelo` permite trocar o LLM nos testes (por exemplo, por uma resposta simulada)."""
    return Agent(
        name="assistente_analista_ia",
        description="Assistente de estudos para quem está aprendendo a ser Analista de IA.",
        model=modelo or criar_modelo(),
        instruction=INSTRUCOES,
        tools=[estimar_custo, criar_mcp_local(), criar_mcp_publico()],
        before_model_callback=guardrail_entrada,
        before_tool_callback=guardrail_ferramenta,
    )


# O `adk web` procura uma variável chamada root_agent.
root_agent = criar_agente()
