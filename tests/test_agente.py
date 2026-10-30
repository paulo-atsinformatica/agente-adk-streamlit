"""Testes que rodam sem chave da Groq: a ferramenta, os guardrails e o agente com um modelo simulado.

Os testes marcados com `mcp` sobem o MCP local e um deles acessa a internet (o MCP público do DeepWiki).
"""
import asyncio

import pytest
from google.adk.models import BaseLlm, LlmResponse
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agente.conversa import perguntar
from agente.ferramentas import estimar_custo
from agente.guardrails import encontrar_dado_sensivel, guardrail_ferramenta
from mcp_analista.servidor import competencias_analista_ia, consultar_glossario, roteiro_de_estudos


class ModeloSimulado(BaseLlm):
    """Finge ser o LLM: na primeira chamada pede a ferramenta de custo; depois, responde com o resultado."""

    model: str = "simulado"
    chamadas: int = 0

    async def generate_content_async(self, llm_request, stream=False):
        self.chamadas += 1
        ultimo = llm_request.contents[-1]
        retorno = next((p.function_response for p in ultimo.parts if p.function_response), None)
        if retorno is None:
            pedido = types.FunctionCall(name="estimar_custo", args={
                "tokens_entrada": 2000, "tokens_saida": 500, "preco_entrada_por_milhao": 0.59,
                "preco_saida_por_milhao": 0.79, "chamadas_por_dia": 3000})
            yield LlmResponse(content=types.Content(role="model", parts=[types.Part(function_call=pedido)]))
        else:
            mes = retorno.response.get("custo_por_mes_usd", retorno.response)
            yield LlmResponse(content=types.Content(role="model", parts=[types.Part(text=f"Custo por mês: {mes} dólares.")]))


def test_estimar_custo():
    r = estimar_custo(2000, 500, 0.59, 0.79, chamadas_por_dia=3000)
    assert r["custo_por_chamada_usd"] == pytest.approx(0.001575)
    assert r["custo_por_mes_usd"] == pytest.approx(141.75)


@pytest.mark.parametrize("texto,esperado", [
    ("minha chave é gsk_abcdefghijklmnop123", "chave de API"),
    ("o cartão 4111 1111 1111 1111 venceu", "número de cartão"),
    ("meu CPF é 123.456.789-09", "CPF"),
    ("senha: 1234", "senha"),
    ("quanto custa 2000 tokens a 0,59 por milhão?", None),
])
def test_dado_sensivel(texto, esperado):
    assert encontrar_dado_sensivel(texto) == esperado


def test_guardrail_ferramenta():
    class Ferramenta:
        name = "estimar_custo"
    assert "erro" in guardrail_ferramenta(Ferramenta(), {"tokens_entrada": -5, "tokens_saida": 1}, None)
    assert guardrail_ferramenta(Ferramenta(), {"tokens_entrada": 5, "tokens_saida": 1}, None) is None


@pytest.mark.mcp
def test_agente_chama_ferramenta_e_guardrail_barra():
    async def rodar():
        sessoes, modelo = InMemorySessionService(), ModeloSimulado()
        ok = await perguntar(sessoes, "aluno", "s1", "Quanto custa por mês?", modelo=modelo)
        barrado = await perguntar(sessoes, "aluno", "s1", "minha chave é gsk_abcdefghijklmnop123", modelo=modelo)
        return ok, barrado, modelo.chamadas

    ok, barrado, chamadas = asyncio.run(rodar())
    assert ok["resposta"] == "Custo por mês: 141.75 dólares."
    assert [p["tipo"] for p in ok["passos"]] == ["chamada", "resultado"]
    assert "não foi enviada ao modelo" in barrado["resposta"]
    assert chamadas == 2  # a mensagem com a chave não chegou ao modelo


def test_mcp_local_funcoes():
    assert consultar_glossario("rag")["termo"] == "rag"
    assert consultar_glossario("Alucinacao")["termo"] == "alucinação"  # sem acento também acha
    assert "conceitos_disponiveis" in consultar_glossario("blockchain")
    assert "técnicas" in competencias_analista_ia()
    r = roteiro_de_estudos(3)  # abaixo do mínimo vira 7
    assert r["total_de_dias"] == 7 and len(r["etapas"]) == 7


@pytest.mark.mcp
def test_mcp_local_por_stdio():
    """O agente sobe o servidor local como processo e enxerga as três ferramentas."""
    from agente.agent import criar_mcp_local

    async def listar():
        ts = criar_mcp_local()
        try:
            return sorted(t.name for t in await ts.get_tools())
        finally:
            await ts.close()

    assert asyncio.run(listar()) == ["competencias_analista_ia", "consultar_glossario", "roteiro_de_estudos"]
