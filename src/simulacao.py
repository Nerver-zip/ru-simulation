import simpy
import random
from .caixa import Caixa
from .cliente import gerar_cliente

# --- PARÂMETROS GERAIS ---
dia_semana = "quarta"             # [segunda, terca, quarta, quinta, sexta, sabado, domingo] Segunda e terça pode comprar ticket
tempo_base = 5                    # Tempo mínimo de atendimento em segundos
INTERVALO_CHEGADA = 10            # Média de tempo entre clientes
                                  # Tempo total da simulação, por padrão 2.5h em dias de semana e 1.5h em finais de semana
TEMPO_SIMULACAO = 3600 * 2.5 if dia_semana != "sabado" and dia_semana != "domingo" else 3600 * 1.5

# --- ESTADO INICIAL DO CAIXA ---
CAIXA_INICIAL = {1: 30, 2: 30, 5: 15, 10: 8, 20: 3, 50: 1}

# --- ESTADO DE REPOSIÇÃO DO CAIXA ---
CAIXA_REPOSICAO = {1: 20, 2: 20, 5: 10, 10: 8, 20: 3, 50: 1}

# --- TEMPOS DE OPERAÇÃO (em segundos) ---
TEMPOS_TROCO = {
    2:  (2, 5),
    5:  (5, 10),
    10: (5, 15),
    20: (5, 20),
    50: (10, 20),
    100: (10, 25)
}
INTERVALO_PIX = (20, 60)
INTERVALO_TICKET = (30, 90)
INTERVALO_PAGAMENTO_TICKET = (2, 5)
INTERVALO_FALTA_TROCO = (30, 90)
INTERVALO_EVENTO_ANORMAL = (5, 100)

# --- MÉTRICAS ---
estatisticas = {
    "clientes_totais": 0,
    "tempo_total_espera": 0.0,
    "tempo_total_sistema": 0.0,
    "clientes_com_erro": 0,
    "clientes_prioritarios": 0,
    "clientes_compra_ticket": 0,
    "sem_troco": 0,
    "maior_espera": 0.0,
    "pico_fila": 0,
    "soma_fila": 0,
    "instantes_fila": 0,
}

def monitorar_fila(env, fila):
    while True:
        tamanho = len(fila.queue)
        estatisticas["soma_fila"] += tamanho
        estatisticas["instantes_fila"] += 1
        estatisticas["pico_fila"] = max(estatisticas["pico_fila"], tamanho)
        yield env.timeout(1)

# Simula o tempo do pagamento com PIX em segundo plano, sem travar o atendimento de outros clientes
def simular_pix(env):
    tempo_pix = random.uniform(*INTERVALO_PIX)
    yield env.timeout(tempo_pix)

def atendimento(env, cliente, caixa, fila):
    chegada = env.now

    with fila.request(priority=cliente["prioridade"]) as req:
        yield req

        inicio_servico = env.now
        espera = inicio_servico - chegada

        estatisticas["clientes_totais"] += 1
        estatisticas["tempo_total_espera"] += espera
        estatisticas["maior_espera"] = max(estatisticas["maior_espera"], espera)

        tempo_atendimento = tempo_base
        
        # TICKET: Aqui o processamento é especial
        if cliente["quer_ticket"]:
            tempo_ticket = random.uniform(*INTERVALO_TICKET)
            tempo_atendimento += tempo_ticket
            estatisticas["clientes_compra_ticket"] += 1
            
            # Overhead adicional de um pagamento via PIX já está incluso no tempo_ticket, ao se entender que essa operação 
            # interrompe a fila normal e não cria uma fila paralela como no caso do PIX sem querer tickets.
            if cliente["forma_pagamento"] == "pix":
                yield env.timeout(tempo_atendimento)
                fim_servico = env.now
                tempo_sistema = fim_servico - chegada
                estatisticas["tempo_total_sistema"] += tempo_sistema
                if cliente["prioridade"] == 0:
                    estatisticas["clientes_prioritarios"] += 1
                return
            
            # Nenhum troco necessário, valor é convertido em tickets. Assimindo usuários compram tickets de 
            # maneira gananciosa e sempre com notas pares 
            elif cliente["forma_pagamento"] == "dinheiro":
                valor_pago = cliente["valor_pago"]
                caixa.receber_pagamento(valor_pago)

                yield env.timeout(tempo_atendimento)
                fim_servico = env.now
                tempo_sistema = fim_servico - chegada
                estatisticas["tempo_total_sistema"] += tempo_sistema
                if cliente["prioridade"] == 0:
                    estatisticas["clientes_prioritarios"] += 1
                return
        
        # Nos demais casos, mais convencionais onde não há compra de tickets:
        # EVENTO ANORMAL
        if cliente["evento_anormal"]:
            tempo_extra = random.uniform(*INTERVALO_EVENTO_ANORMAL)
            tempo_atendimento += tempo_extra
            estatisticas["clientes_com_erro"] += 1

        # PAGAMENTO: 
        # Para PIX cria-se uma fila paralela pós atendimento inicial, para não trancar fila para outros usuários
        if cliente["forma_pagamento"] == "pix":
            yield env.timeout(tempo_atendimento)
            fim_servico = env.now
            tempo_sistema = fim_servico - chegada
            estatisticas["tempo_total_sistema"] += tempo_sistema
            env.process(simular_pix(env)) # Pagamento em paralelo, fora da fila 

        elif cliente["forma_pagamento"] == "ticket":
            tempo_pagamento = random.uniform(*INTERVALO_PAGAMENTO_TICKET)
            yield env.timeout(tempo_atendimento + tempo_pagamento)
            fim_servico = env.now
        
        else:
            valor_pago = cliente["valor_pago"]
            troco = valor_pago - cliente["valor_compra"]

            tempo_dinheiro = random.uniform(*TEMPOS_TROCO[valor_pago]) 
            tempo_total = tempo_atendimento + tempo_dinheiro

            caixa.receber_pagamento(valor_pago)
            sucesso = caixa.dar_troco(troco) if troco > 0 else True

            if not sucesso:
                estatisticas["sem_troco"] += 1
                caixa.repor(CAIXA_REPOSICAO)
                tempo_total += random.uniform(*INTERVALO_FALTA_TROCO)

            yield env.timeout(tempo_total)
            fim_servico = env.now

        tempo_sistema = fim_servico - chegada
        estatisticas["tempo_total_sistema"] += tempo_sistema

        if cliente["prioridade"] == 0:
            estatisticas["clientes_prioritarios"] += 1

def gerar_clientes(env, caixa, fila):
    while True:
        cliente = gerar_cliente(dia_semana)
        env.process(atendimento(env, cliente, caixa, fila))
        yield env.timeout(random.expovariate(1.0 / INTERVALO_CHEGADA))

def rodar_simulacao():
    env = simpy.Environment()
    fila = simpy.PriorityResource(env, capacity=1)
    caixa = Caixa(CAIXA_INICIAL)

    env.process(gerar_clientes(env, caixa, fila))
    env.process(monitorar_fila(env, fila))
    env.run(until=TEMPO_SIMULACAO)

    clientes_nao_atendidos = len(fila.queue)

    # --- RESULTADOS ---
    total = estatisticas["clientes_totais"]
    print("\n--- Resultados ---")
    if total > 0:
        print(f"Clientes atendidos: {total}")
        print(f"Clientes não atendidos: {clientes_nao_atendidos}")
        print(f"Tempo médio de espera: {estatisticas['tempo_total_espera'] / total:.2f}s")
        print(f"Tempo médio no sistema: {estatisticas['tempo_total_sistema'] / total:.2f}s")
        print(f"Maior espera observada: {estatisticas['maior_espera']:.2f}s")
        print(f"Tamanho médio da fila: {estatisticas['soma_fila'] / estatisticas['instantes_fila']:.2f}")
        print(f"Pico de fila: {estatisticas['pico_fila']}")
        print(f"Clientes prioritários: {estatisticas['clientes_prioritarios']}")
        print(f"Clientes comprando ticket: {estatisticas['clientes_compra_ticket']}")
        print(f"Clientes com erro: {estatisticas['clientes_com_erro']}")
        print(f"Sem troco: {estatisticas['sem_troco']}")

        # Coleta CSV
        print(f"\nCSV,{total},{estatisticas['tempo_total_espera'] / total:.2f},"
              f"{estatisticas['tempo_total_sistema'] / total:.2f},"
              f"{estatisticas['clientes_prioritarios']},"
              f"{estatisticas['clientes_compra_ticket']},"
              f"{estatisticas['clientes_com_erro']},"
              f"{estatisticas['sem_troco']},{clientes_nao_atendidos}")


if __name__ == "__main__":
    rodar_simulacao()
