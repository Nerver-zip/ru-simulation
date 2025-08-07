import random

contador_clientes = 0

def gerar_cliente(dia_simulado):
    """
    Gera um cliente com atributos aleatórios no dia atual da simulação, dependendo do dia, existe ou não a possibilidade
    da compra de tickets
    """
    global contador_clientes

    cliente = {}

    # ID único, útil para debug
    cliente["id"] = contador_clientes
    contador_clientes += 1

    # 1. Prioridade (0 = prioridade alta, 1 = normal)
    cliente["prioridade"] = 0 if random.random() < 0.03 else 1  # 3% dos clientes têm prioridade (idosos, gestantes, etc)

    # 2. Forma de pagamento: 20% dinheiro, 60% ticket, 20% pix
    r = random.random()
    if r < 0.20:
        cliente["forma_pagamento"] = "dinheiro"
    elif r < 0.80:
        cliente["forma_pagamento"] = "ticket"
    else:
        cliente["forma_pagamento"] = "pix"

    # 3. Valor pago (apenas para quem paga com dinheiro)
    if cliente["forma_pagamento"] == "dinheiro":
        opcoes = [2, 5, 10, 20, 50, 100]
        pesos = [0.43, 0.30, 0.15, 0.1, 0.015, 0.005]  # Pessoas tendem a pagar com notas menores
        cliente["valor_pago"] = random.choices(opcoes, weights=pesos)[0]
    else:
        cliente["valor_pago"] = None  # Não se aplica

    # 4. Valor da compra
    cliente["valor_compra"] = 2  # Preço fixo do RU

    # 5. Quer comprar tickets? Só segundas e terças. Para fins de simplificação, por enquanto entedende-se que tickets são ilimitados e 
    # sempre disponíveis para compra.
    if dia_simulado != "segunda" and dia_simulado != "terca":
        cliente["quer_ticket"] = False
    else:
        cliente["quer_ticket"] = random.random() < 0.05  # 5% pedem tickets
    # 6. Evento anormal?
    cliente["evento_anormal"] = random.random() < 0.01  # 1% dos clientes causam algum atraso
    
    #7. Comprando ticket e vai pagar em dinheiro? Entende-se que todo o valor pago será convertido em tickets.
    # Considera-se a compra de tickets usando notas num intervalo menor [10, 100].
    if cliente["quer_ticket"] and cliente["forma_pagamento"] == "dinheiro":
        opcoes = [10, 20, 50, 100]
        pesos = [0.05, 0.4, 0.5, 0.05]  # Pessoas tendem a pagar com notas maiores quando falamos em compra de tickets
        cliente["valor_pago"] = random.choices(opcoes, weights=pesos)[0]

    return cliente

if __name__ == "__main__":
    for _ in range(5):
        c = gerar_cliente(dia_simulado="segunda")
        print(c)
