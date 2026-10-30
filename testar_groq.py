"""Teste de ponta a ponta com o modelo de verdade da Groq. Precisa de GROQ_API_KEY no .env.

Rode com: uv run python testar_groq.py
Faz perguntas que usam o MCP local, a ferramenta própria, o MCP público e uma que o guardrail barra.
"""
import asyncio

from google.adk.sessions import InMemorySessionService

from agente.conversa import perguntar

PERGUNTAS = [
    "Quem é você?",
    "O que é RAG?",
    "Monte um roteiro de estudos de 14 dias para eu virar Analista de IA.",
    "Quanto custa 2.000 tokens de entrada e 500 de saída, a 0,59 e 0,79 dólares por milhão, 3.000 vezes por dia? Quero o valor por mês.",
    "No repositório google/adk-python, o que é um callback? Responda em duas frases.",
    "Minha chave é gsk_abcdefghijklmnop123456, pode guardar?",
]


async def main():
    sessoes = InMemorySessionService()
    for pergunta in PERGUNTAS:
        try:
            r = await perguntar(sessoes, "aluno", "teste", pergunta)
        except Exception as erro:  # um erro numa pergunta não interrompe as outras
            r = {"resposta": f"ERRO: {type(erro).__name__}: {str(erro)[:200]}", "passos": []}
        print("PERGUNTA:", pergunta)
        print("PASSOS:  ", [(p["tipo"], p["ferramenta"]) for p in r["passos"]] or "nenhum")
        print("RESPOSTA:", r["resposta"].strip(), "\n")


if __name__ == "__main__":
    asyncio.run(main())
