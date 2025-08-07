import simpy
import random
from .caixa import Caixa
from .cliente import gerar_cliente

# --- PARÂMETROS GERAIS ---
dia_semana = "quarta"            # [segunda, terca, quarta, quinta, sexta, sabado, domingo] Segunda e terça pode comprar ticket
tempo_base = 5                   # Tempo mínimo de atendimento em segundos
INTERVALO_CHEGADA = 10           # Média de tempo entre clientes

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
    "clientes_totais": 0,               # Total de clientes que chegaram

    # Para Dinheiro + Ticket
    "tempo_espera_dinheiro_ticket": 0.0,   # Soma dos tempos de espera na fila principal (dinheiro + ticket)
    "tempo_sistema_dinheiro_ticket": 0.0,  # Soma dos tempos totais no sistema (espera + atendimento) (dinheiro + ticket)
    "cont_dinheiro_ticket": 0,              # Contagem clientes dinheiro + ticket

    # Para PIX
    "tempo_espera_pix": 0.0,                # Soma do tempo de espera na fila principal para clientes PIX
    "tempo_pix_pagamento": 0.0,             # Soma do tempo gasto na fila paralela PIX (pagamento pós-atendimento)
    "tempo_sistema_pix": 0.0,               # Soma do tempo total no sistema (espera + atendimento + pagamento PIX)
    "cont_pix": 0,                          # Contagem clientes PIX

    # Total geral (todos clientes)
    "tempo_espera_total": 0.0,              # Soma dos tempos de espera para todos os clientes
    "tempo_sistema_total": 0.0,             # Soma dos tempos totais no sistema para todos os clientes
    "cont_total": 0,                        # Contagem geral clientes (mesmo que clientes_totais)

    "clientes_com_erro": 0,                 # Clientes que saíram sem atendimento
    "clientes_prioritarios": 0,             # Contagem de clientes prioritários
    "clientes_compra_ticket": 0,            # Quantos clientes compraram ticket
    "sem_troco": 0,                         # Quantos tiveram atraso por falta de troco
    "maior_espera": 0.0,                    # Maior tempo de espera individual
    "pico_fila": 0,                         # Maior tamanho da fila principal observado
    "soma_fila": 0,                         # Soma dos tamanhos da fila principal (para média)
    "instantes_fila": 0,                    # Número de amostras da fila principal

    # Métricas da fila paralela do PIX
    "fila_pix_momentos": [],                # Lista com o tamanho da fila PIX ao longo do tempo
    "fila_pix_pico": 0,                     # Maior número simultâneo de clientes no PIX
    "fila_pix_final": 0,                    # Quantos ainda estavam na fila do PIX ao fim da simulação
    "fila_pix_media": 0.0                   # Média do tamanho da fila paralela do PIX
}

def monitorar_fila(env, fila):
    while True:
        tamanho = len(fila.queue)
        estatisticas["soma_fila"] += tamanho
        estatisticas["instantes_fila"] += 1
        estatisticas["pico_fila"] = max(estatisticas["pico_fila"], tamanho)
        yield env.timeout(1)

# Simula o tempo do pagamento com PIX em segundo plano, sem travar o atendimento de outros clientes
def simular_pix(env, fila_pix):
    with fila_pix.request() as req:
        yield req

        # --- Registro do tamanho da fila PIX no início do atendimento ---
        tamanho_atual = len(fila_pix.queue) + 1  
        estatisticas["fila_pix_momentos"].append(tamanho_atual)
        estatisticas["fila_pix_pico"] = max(estatisticas["fila_pix_pico"], tamanho_atual)

        inicio_pix = env.now
        tempo_pix = random.uniform(*INTERVALO_PIX)
        yield env.timeout(tempo_pix)

        duracao_pix = env.now - inicio_pix
        estatisticas["tempo_pix_pagamento"] += duracao_pix
        estatisticas["tempo_sistema_total"] += duracao_pix
        estatisticas["tempo_sistema_pix"] += duracao_pix

def atendimento(env, cliente, caixa, fila, fila_pix):
    chegada = env.now

    with fila.request(priority=cliente["prioridade"]) as req:
        yield req

        inicio_servico = env.now
        espera = inicio_servico - chegada

        # Atualiza métricas gerais e específicas
        estatisticas["clientes_totais"] += 1
        estatisticas["tempo_espera_total"] += espera
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

                estatisticas["tempo_sistema_total"] += tempo_sistema
                estatisticas["cont_total"] += 1

                if cliente["prioridade"] == 0:
                    estatisticas["clientes_prioritarios"] += 1
                return

            # Nenhum troco necessário, valor é convertido em tickets. Assim, usuários compram tickets de 
            # maneira gananciosa e sempre com notas pares 
            elif cliente["forma_pagamento"] == "dinheiro":
                valor_pago = cliente["valor_pago"]
                caixa.receber_pagamento(valor_pago)

                yield env.timeout(tempo_atendimento)
                fim_servico = env.now
                tempo_sistema = fim_servico - chegada

                # Atualiza métricas para dinheiro + ticket
                estatisticas["tempo_espera_dinheiro_ticket"] += espera
                estatisticas["tempo_sistema_dinheiro_ticket"] += tempo_sistema
                estatisticas["cont_dinheiro_ticket"] += 1

                # Atualiza métricas gerais
                estatisticas["tempo_espera_total"] += 0  # já somou acima
                estatisticas["tempo_sistema_total"] += tempo_sistema
                estatisticas["cont_total"] += 1

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
            tempo_sistema_parcial = fim_servico - chegada

            # Inicia pagamento PIX paralelo e não bloqueia a fila principal
            env.process(simular_pix(env, fila_pix))

            # Atualiza métricas PIX para o atendimento parcial
            estatisticas["tempo_espera_pix"] += espera
            estatisticas["tempo_sistema_pix"] += tempo_sistema_parcial
            estatisticas["cont_pix"] += 1

            # Atualiza métricas gerais
            estatisticas["tempo_espera_total"] += 0  # já somou acima
            estatisticas["tempo_sistema_total"] += tempo_sistema_parcial
            estatisticas["cont_total"] += 1

            if cliente["prioridade"] == 0:
                estatisticas["clientes_prioritarios"] += 1

            return

        elif cliente["forma_pagamento"] == "ticket":
            tempo_pagamento = random.uniform(*INTERVALO_PAGAMENTO_TICKET)
            yield env.timeout(tempo_atendimento + tempo_pagamento)
            fim_servico = env.now
            tempo_sistema = fim_servico - chegada

            # Atualiza métricas dinheiro + ticket
            estatisticas["tempo_espera_dinheiro_ticket"] += espera
            estatisticas["tempo_sistema_dinheiro_ticket"] += tempo_sistema
            estatisticas["cont_dinheiro_ticket"] += 1

            # Atualiza métricas gerais
            estatisticas["tempo_espera_total"] += 0  # já somou acima
            estatisticas["tempo_sistema_total"] += tempo_sistema
            estatisticas["cont_total"] += 1

            if cliente["prioridade"] == 0:
                estatisticas["clientes_prioritarios"] += 1

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

            # Atualiza métricas dinheiro + ticket
            estatisticas["tempo_espera_dinheiro_ticket"] += espera
            estatisticas["tempo_sistema_dinheiro_ticket"] += tempo_sistema
            estatisticas["cont_dinheiro_ticket"] += 1

            # Atualiza métricas gerais
            estatisticas["tempo_espera_total"] += 0  # já somou acima
            estatisticas["tempo_sistema_total"] += tempo_sistema
            estatisticas["cont_total"] += 1

            if cliente["prioridade"] == 0:
                estatisticas["clientes_prioritarios"] += 1

def gerar_clientes(env, caixa, fila, fila_pix):
    while True:
        cliente = gerar_cliente(dia_semana)
        env.process(atendimento(env, cliente, caixa, fila, fila_pix))
        yield env.timeout(random.expovariate(1.0 / INTERVALO_CHEGADA))

def rodar_simulacao():
    env = simpy.Environment()
    fila = simpy.PriorityResource(env, capacity=1)
    fila_pix = simpy.Resource(env, capacity=1)
    caixa = Caixa(CAIXA_INICIAL)

    env.process(gerar_clientes(env, caixa, fila, fila_pix))
    env.process(monitorar_fila(env, fila))
    env.run(until=TEMPO_SIMULACAO)

    clientes_nao_atendidos = len(fila.queue)

    estatisticas["fila_pix_final"] = len(fila_pix.queue)
    estatisticas["fila_pix_media"] = (
        sum(estatisticas["fila_pix_momentos"]) / len(estatisticas["fila_pix_momentos"])
        if estatisticas["fila_pix_momentos"] else 0
    )

    # --- RESULTADOS ---
    total = estatisticas["cont_total"]
    print("\n--- Resultados ---")
    if total > 0:
        print(f"Clientes atendidos: {total}")
        print(f"Clientes não atendidos: {clientes_nao_atendidos}")
        print(f"Tempo médio de espera (dinheiro + ticket): {estatisticas['tempo_espera_dinheiro_ticket'] / estatisticas['cont_dinheiro_ticket']:.2f}s")
        print(f"Tempo médio no sistema (dinheiro + ticket): {estatisticas['tempo_sistema_dinheiro_ticket'] / estatisticas['cont_dinheiro_ticket']:.2f}s")
        print(f"Tempo médio de espera (PIX): {estatisticas['tempo_espera_pix'] / estatisticas['cont_pix']:.2f}s")
        print(f"Tempo médio no sistema (PIX): {estatisticas['tempo_sistema_pix'] / estatisticas['cont_pix']:.2f}s")
        print(f"Tempo médio de espera (geral): {estatisticas['tempo_espera_total'] / total:.2f}s")
        print(f"Tempo médio no sistema (geral): {estatisticas['tempo_sistema_total'] / total:.2f}s")
        print(f"Maior espera observada: {estatisticas['maior_espera']:.2f}s")
        print(f"Tamanho médio da fila: {estatisticas['soma_fila'] / estatisticas['instantes_fila']:.2f}")
        print(f"Pico de fila: {estatisticas['pico_fila']}")
        print(f"Clientes prioritários: {estatisticas['clientes_prioritarios']}")
        print(f"Clientes comprando ticket: {estatisticas['clientes_compra_ticket']}")
        print(f"Clientes com erro: {estatisticas['clientes_com_erro']}")
        print(f"Sem troco: {estatisticas['sem_troco']}")
        print(f"Tamanho médio da fila PIX: {estatisticas['fila_pix_media']:.2f}")
        print(f"Pico da fila PIX: {estatisticas['fila_pix_pico']}")
        print(f"Tamanho final da fila PIX: {estatisticas['fila_pix_final']}")

        # Coleta CSV 
        print(f"\nCSV,"
              f"{total}," 
              f"{estatisticas['tempo_espera_total'] / total:.2f},"  
              f"{estatisticas['tempo_sistema_total'] / total:.2f},"  
              f"{estatisticas['tempo_espera_dinheiro_ticket'] / estatisticas['cont_dinheiro_ticket']:.2f}," 
              f"{estatisticas['tempo_sistema_dinheiro_ticket'] / estatisticas['cont_dinheiro_ticket']:.2f},"  
              f"{estatisticas['tempo_espera_pix'] / estatisticas['cont_pix']:.2f}," 
              f"{estatisticas['tempo_pix_pagamento'] / estatisticas['cont_pix']:.2f}," 
              f"{estatisticas['tempo_sistema_pix'] / estatisticas['cont_pix']:.2f},"  
              f"{estatisticas['clientes_prioritarios']},"
              f"{estatisticas['clientes_compra_ticket']},"
              f"{estatisticas['clientes_com_erro']},"
              f"{estatisticas['sem_troco']},"
              f"{clientes_nao_atendidos},"
              f"{estatisticas['fila_pix_media']:.2f},"
              f"{estatisticas['fila_pix_pico']},"
              f"{estatisticas['fila_pix_final']}"
              )

if __name__ == "__main__":
    rodar_simulacao()
