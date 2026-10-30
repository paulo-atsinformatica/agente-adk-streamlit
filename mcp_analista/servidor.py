"""Servidor MCP local, em Python: informações sobre o trabalho do Analista de IA.

Por padrão roda por stdio: o próprio agente inicia este processo e conversa com ele pela entrada e saída.
Para subir como serviço HTTP e testar com outro cliente MCP:
    uv run python -m mcp_analista.servidor --http      (fica em http://127.0.0.1:8001/mcp)
"""
import sys
import unicodedata

from mcp.server.mcpserver import MCPServer

from .conteudo import COMPETENCIAS, CONCEITOS, ROTEIRO

servidor = MCPServer(
    name="analista-ia",
    instructions="Informações para quem está aprendendo a ser Analista de IA: conceitos, competências e roteiro de estudos.",
)


def _normalizar(texto: str) -> str:
    return unicodedata.normalize("NFD", texto.lower().strip()).encode("ascii", "ignore").decode()


@servidor.tool()
def consultar_glossario(termo: str) -> dict:
    """Explica um conceito de IA em linguagem simples (ex.: RAG, embedding, MCP, guardrail, eval).

    Use quando a pessoa perguntar o que é um termo. Se o termo não estiver na base, devolve a lista
    dos que estão, para o agente sugerir um deles em vez de inventar.
    """
    alvo = _normalizar(termo)
    for nome, definicao in CONCEITOS.items():
        if _normalizar(nome) == alvo or alvo in _normalizar(nome):
            return {"termo": nome, "explicacao": definicao}
    return {"erro": f"Não tenho o conceito '{termo}'.", "conceitos_disponiveis": sorted(CONCEITOS)}


@servidor.tool()
def competencias_analista_ia() -> dict:
    """Lista as competências esperadas de um Analista de IA, separadas em técnicas, de negócio e de segurança.

    Use quando a pessoa perguntar o que um Analista de IA faz ou precisa saber.
    """
    return COMPETENCIAS


@servidor.tool()
def roteiro_de_estudos(dias: int = 14) -> dict:
    """Monta um roteiro de estudos para virar Analista de IA, dividindo as etapas pelos dias disponíveis.

    Args:
        dias: em quantos dias a pessoa quer estudar (de 7 a 60).
    """
    dias = max(7, min(60, dias))
    por_etapa = dias / len(ROTEIRO)
    etapas, inicio = [], 1
    for i, (nome, conteudo) in enumerate(ROTEIRO, 1):
        fim = round(i * por_etapa)
        etapas.append({"dias": f"{inicio} a {max(inicio, fim)}", "etapa": nome, "conteudo": conteudo})
        inicio = max(inicio, fim) + 1
    return {"total_de_dias": dias, "etapas": etapas, "dica": "Constância vale mais que maratona: um pouco todo dia."}


if __name__ == "__main__":
    if "--http" in sys.argv:
        servidor.run(transport="streamable-http", host="127.0.0.1", port=8001)
    else:
        servidor.run()
