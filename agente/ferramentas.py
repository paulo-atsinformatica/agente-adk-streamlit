"""Ferramentas próprias do agente. A docstring é o que o modelo lê para decidir quando usar cada uma."""


def estimar_custo(
    tokens_entrada: int,
    tokens_saida: int,
    preco_entrada_por_milhao: float,
    preco_saida_por_milhao: float,
    chamadas_por_dia: int = 1,
) -> dict:
    """Calcula quanto custam chamadas a um modelo de linguagem.

    Use quando a pessoa quiser saber o custo de uma chamada, de um dia ou de um mês de uso,
    a partir da quantidade de tokens e do preço do modelo (em dólares por milhão de tokens).

    Args:
        tokens_entrada: tokens enviados ao modelo em cada chamada (prompt e contexto).
        tokens_saida: tokens gerados pelo modelo em cada chamada (resposta).
        preco_entrada_por_milhao: preço em dólares por milhão de tokens de entrada.
        preco_saida_por_milhao: preço em dólares por milhão de tokens de saída.
        chamadas_por_dia: quantas chamadas são feitas por dia.

    Returns:
        O custo por chamada, por dia e por mês (30 dias), em dólares.
    """
    por_chamada = (tokens_entrada * preco_entrada_por_milhao + tokens_saida * preco_saida_por_milhao) / 1_000_000
    return {
        "custo_por_chamada_usd": round(por_chamada, 6),
        "custo_por_dia_usd": round(por_chamada * chamadas_por_dia, 4),
        "custo_por_mes_usd": round(por_chamada * chamadas_por_dia * 30, 2),
    }
