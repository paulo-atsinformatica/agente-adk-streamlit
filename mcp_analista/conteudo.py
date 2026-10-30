"""Conteúdo servido pelo MCP local: conceitos, competências e um roteiro de estudos do Analista de IA."""

CONCEITOS = {
    "llm": "Modelo de linguagem de grande porte. Gera texto prevendo o próximo token, um pedaço de palavra por vez. Plausível não quer dizer verdadeiro.",
    "token": "Pedaço de texto que o modelo processa. Preço, velocidade e limite de contexto são medidos em tokens.",
    "janela de contexto": "Tudo o que o modelo enxerga numa chamada: instruções, histórico e documentos. O que fica de fora não existe para ele.",
    "prompt": "As instruções e o contexto enviados ao modelo. Bom prompt diz papel, objetivo, formato e o que fazer quando não souber.",
    "embedding": "Lista de números que representa o significado de um texto. Textos parecidos ficam com números próximos, o que permite buscar por sentido.",
    "rag": "Buscar trechos relevantes numa base e entregá-los no contexto antes de gerar a resposta. Dá ao modelo informação atual e permite citar a fonte.",
    "tool calling": "O modelo pede para chamar uma função (consultar um pedido, calcular algo) e a aplicação executa. Quem decide o que é permitido é o código, não o modelo.",
    "mcp": "Model Context Protocol: um padrão para ligar aplicações de IA a ferramentas e dados. Um servidor MCP serve a qualquer cliente compatível.",
    "agente": "Um modelo que escolhe os próximos passos e usa ferramentas em ciclo até cumprir um objetivo.",
    "harness": "Tudo o que envolve o modelo num agente: instruções, ferramentas, contexto, permissões, limites, verificação e registro.",
    "guardrail": "Verificação em volta do modelo que impede o agente de dizer ou fazer o que não deve. Pode ser regra, classificador ou outro modelo.",
    "eval": "Conjunto de casos com resultado esperado, rodado a cada mudança para saber se o agente melhorou ou piorou.",
    "precisão e recall": "Métricas de uma decisão de sim ou não. Precisão: dos que o sistema marcou, quantos estavam certos. Recall: dos que deviam ser marcados, quantos ele encontrou.",
    "observabilidade": "Registrar cada passo do agente (o trace) para entender por que ele respondeu o que respondeu e onde falhou.",
    "alucinação": "Resposta fluente e confiante, mas falsa ou sem base nas fontes. Reduz-se com fonte no contexto, citação e permissão para dizer não sei.",
}

COMPETENCIAS = {
    "técnicas": [
        "Explicar como um LLM funciona e onde ele erra",
        "Escrever prompts claros e versioná-los",
        "Montar um RAG e medir se a busca acha o trecho certo",
        "Ligar o modelo a sistemas com ferramentas e MCP, com permissões no código",
        "Criar evals e decidir com números",
        "Ler traces e investigar falhas",
        "Python suficiente para ler e ajustar código, Git e APIs",
    ],
    "de negócio": [
        "Entender o problema antes de escolher a ferramenta",
        "Definir escopo, métrica de sucesso e quando passar para um humano",
        "Estimar custo e valor de uma solução",
        "Explicar riscos e limites para quem decide, sem prometer mais do que os testes mostram",
    ],
    "de segurança e ética": [
        "Defender contra prompt injection em camadas",
        "Tratar dados pessoais com cuidado (LGPD) e nunca expor chaves",
        "Manter um humano no circuito nas ações com consequência",
    ],
}

ROTEIRO = [
    ("Fundamentos", "O que é IA, como um LLM gera texto, tokens, janela de contexto e prompt."),
    ("Conhecimento", "Embeddings, RAG e como medir se a busca funciona."),
    ("Ação", "Tool calling, agentes, harness e MCP."),
    ("Confiança", "Guardrails, evals, precisão e recall, observabilidade."),
    ("Operação", "Versões, segurança, LGPD e governança."),
    ("Ferramentas", "Python, Git, APIs, containers e um framework de agentes."),
    ("Projeto", "Construir um assistente pequeno, medir, melhorar e dizer se está pronto."),
]
