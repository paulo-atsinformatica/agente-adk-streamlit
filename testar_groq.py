"""Teste de ponta a ponta com o modelo de verdade da Groq. Precisa de GROQ_API_KEY no .env.

Rode com: uv run python testar_groq.py
Faz três perguntas: uma que usa a ferramenta própria, uma que usa o MCP e uma que o guardrail barra.
"""
import asyncio

from google.adk.sessions import InMemorySessionService

from agente.conversa import perguntar

PERGUNTAS = [
    "Quanto custa 2.000 tokens de entrada e 500 de saída, a 0,59 e 0,79 dólares por milhão, 3.000 vezes por dia? Quero o valor por mês.",
    "No repositório google/adk-python, o que é um callback? Responda em duas frases.",
    "Minha chave é gsk_abcdefghijklmnop123456, pode guardar?",
]


async def main():
    sessoes = InMemorySessionService()
    for pergunta in PERGUNTAS:
        r = await perguntar(sessoes, "aluno", "teste", pergunta)
        print("PERGUNTA:", pergunta)
        print("PASSOS:  ", [(p["tipo"], p["ferramenta"]) for p in r["passos"]] or "nenhum")
        print("RESPOSTA:", r["resposta"].strip(), "\n")


if __name__ == "__main__":
    asyncio.run(main())
