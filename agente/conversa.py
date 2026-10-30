"""Roda uma pergunta no agente e devolve a resposta com os passos (o "trace" da conversa)."""
from google.adk.runners import Runner
from google.adk.sessions import BaseSessionService
from google.genai import types

from .agent import criar_agente

APP = "assistente_analista_ia"


async def perguntar(sessoes: BaseSessionService, usuario: str, sessao_id: str, texto: str, modelo=None) -> dict:
    """Envia `texto` ao agente na sessão indicada. O histórico fica no serviço de sessões.

    O agente é montado a cada pergunta para que a conexão com o MCP viva no mesmo loop assíncrono
    da chamada (o Streamlit cria um loop novo a cada interação).
    """
    if await sessoes.get_session(app_name=APP, user_id=usuario, session_id=sessao_id) is None:
        await sessoes.create_session(app_name=APP, user_id=usuario, session_id=sessao_id)
    runner = Runner(app_name=APP, agent=criar_agente(modelo), session_service=sessoes)
    passos, resposta = [], ""
    try:
        mensagem = types.Content(role="user", parts=[types.Part(text=texto)])
        async for evento in runner.run_async(user_id=usuario, session_id=sessao_id, new_message=mensagem):
            for chamada in evento.get_function_calls():
                passos.append({"tipo": "chamada", "ferramenta": chamada.name, "argumentos": dict(chamada.args or {})})
            for retorno in evento.get_function_responses():
                passos.append({"tipo": "resultado", "ferramenta": retorno.name, "resultado": retorno.response})
            if evento.is_final_response() and evento.content and evento.content.parts:
                resposta = "".join(p.text or "" for p in evento.content.parts)
    finally:
        await runner.close()  # fecha também a conexão com o MCP
    return {"resposta": resposta, "passos": passos}
