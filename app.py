"""Tela de chat em Streamlit para o agente. Rode com: uv run streamlit run app.py"""
import asyncio
import os
import uuid

import streamlit as st
from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService

from agente.conversa import perguntar

load_dotenv()
st.set_page_config(page_title="Assistente do Analista de IA", page_icon="🤖")
st.title("Assistente do Analista de IA")
st.caption("Google ADK · modelo da Groq · ferramenta própria · MCP público (DeepWiki) · guardrails")

if not os.getenv("GROQ_API_KEY"):
    st.error("Falta a chave da Groq. Copie .env.example para .env e preencha GROQ_API_KEY (veja o README).")
    st.stop()

# Estado da conversa: o histórico do agente fica no serviço de sessões; o da tela, em `mensagens`.
if "sessoes" not in st.session_state:
    st.session_state.sessoes = InMemorySessionService()
    st.session_state.sessao_id = str(uuid.uuid4())
    st.session_state.mensagens = []

with st.sidebar:
    st.subheader("Experimente")
    st.markdown(
        "- Quanto custa 2.000 tokens de entrada e 500 de saída, a 0,59 e 0,79 dólares por milhão, 3.000 vezes por dia?\n"
        "- No repositório google/adk-python, o que é um callback?\n"
        "- Minha chave é gsk_abc123def456ghi789 (o guardrail barra)\n"
    )
    if st.button("Nova conversa"):
        for k in ("sessoes", "sessao_id", "mensagens"):
            st.session_state.pop(k, None)
        st.rerun()

for m in st.session_state.mensagens:
    with st.chat_message(m["papel"]):
        st.markdown(m["texto"])
        if m.get("passos"):
            with st.expander(f"Passos do agente ({len(m['passos'])})"):
                st.json(m["passos"])

if texto := st.chat_input("Pergunte algo"):
    st.session_state.mensagens.append({"papel": "user", "texto": texto})
    with st.chat_message("user"):
        st.markdown(texto)
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                r = asyncio.run(perguntar(st.session_state.sessoes, "aluno", st.session_state.sessao_id, texto))
            except Exception as erro:  # mostra o erro em vez de derrubar a tela (ex.: limite da Groq)
                r = {"resposta": f"Não consegui responder agora: {erro}", "passos": []}
        st.markdown(r["resposta"] or "(sem resposta)")
        if r["passos"]:
            with st.expander(f"Passos do agente ({len(r['passos'])})"):
                st.json(r["passos"])
    st.session_state.mensagens.append({"papel": "assistant", "texto": r["resposta"], "passos": r["passos"]})
