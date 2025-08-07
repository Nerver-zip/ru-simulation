import csv
import statistics
import math
from scipy.stats import shapiro

# --- Configuração ---
ARQUIVO = "csv/resultados_dinheiro.csv"
ARQUIVO_SAIDA = "data/analise_dinheiro.txt"  
nivel_confianca = 0.95
z = 1.96  # z-score para 95% de confiança

# Listas para análise
clientes_atendidos = []

espera_media_geral = []
tempo_medio_sistema_geral = []

espera_media_dinheiro_ticket = []
tempo_medio_sistema_dinheiro_ticket = []

espera_media_pix = []
tempo_pagamento_pix_paralelo = []
tempo_medio_sistema_pix = []

clientes_prioritarios = []
clientes_ticket = []
clientes_com_erro = []
sem_troco = []
clientes_nao_atendidos = []

fila_pix_media = []
fila_pix_pico = []
fila_pix_final = []

# Leitura do CSV
with open(ARQUIVO, newline='') as csvfile:
    leitor = csv.DictReader(csvfile)
    for linha in leitor:
        clientes_atendidos.append(int(linha["clientes_atendidos"]))

        espera_media_geral.append(float(linha["espera_media_geral"]))
        tempo_medio_sistema_geral.append(float(linha["tempo_medio_sistema_geral"]))

        espera_media_dinheiro_ticket.append(float(linha["espera_media_dinheiro_ticket"]))
        tempo_medio_sistema_dinheiro_ticket.append(float(linha["tempo_medio_sistema_dinheiro_ticket"]))

        espera_media_pix.append(float(linha["espera_media_pix"]))
        tempo_pagamento_pix_paralelo.append(float(linha["tempo_pagamento_pix_paralelo"]))
        tempo_medio_sistema_pix.append(float(linha["tempo_medio_sistema_pix"]))

        clientes_prioritarios.append(int(linha["clientes_prioritarios"]))
        clientes_ticket.append(int(linha["clientes_ticket"]))
        clientes_com_erro.append(int(linha["clientes_com_erro"]))
        sem_troco.append(int(linha["sem_troco"]))
        clientes_nao_atendidos.append(int(linha["clientes_nao_atendidos"]))

        fila_pix_media.append(float(linha["fila_pix_media"]))
        fila_pix_pico.append(int(linha["fila_pix_pico"]))
        fila_pix_final.append(int(linha["fila_pix_final"]))


def analisar(nome, dados, f):
    n = len(dados)
    media = statistics.mean(dados)
    desvio = statistics.stdev(dados) if n > 1 else 0
    erro = z * desvio / math.sqrt(n) if n > 1 else 0
    ic_min = media - erro
    ic_max = media + erro
    cv = (desvio / media) * 100 if media != 0 else float('inf')

    stat, p = shapiro(dados) if n >= 3 else (None, None)
    normal = (p > 0.05) if p is not None else None

    print(f"\n--- {nome} ---", file=f)
    print(f"Média: {media:.4f}", file=f)
    print(f"Desvio padrão: {desvio:.4f}", file=f)
    print(f"Coeficiente de variação (CV): {cv:.2f}%", file=f)
    print(f"Intervalo de confiança 95%: [{ic_min:.4f}, {ic_max:.4f}]", file=f)
    print(f"Amostra: {n} execuções", file=f)
    if p is not None:
        print(f"Teste de Shapiro-Wilk: p = {p:.4f} → {'Distribuição normal' if normal else 'Não normal'}", file=f)
    else:
        print("Teste de Shapiro-Wilk: amostra insuficiente", file=f)

def proporcao_media(nome, campo, f):
    props = [v / c if c > 0 else 0 for v, c in zip(campo, clientes_atendidos)]
    media = statistics.mean(props)
    desvio = statistics.stdev(props) if len(props) > 1 else 0
    erro = z * desvio / math.sqrt(len(props)) if len(props) > 1 else 0
    cv = (desvio / media) * 100 if media != 0 else float('inf')

    print(f"\n--- Proporção média de {nome} ---", file=f)
    print(f"{media*100:.2f}% ± {erro*100:.2f}% (IC 95%)", file=f)
    print(f"Coeficiente de variação (CV): {cv:.2f}%", file=f)

with open(ARQUIVO_SAIDA, "w") as f:
    # Análises principais contínuas
    analisar("Tempo médio de espera geral (s)", espera_media_geral, f)
    analisar("Tempo médio total no sistema geral (s)", tempo_medio_sistema_geral, f)

    analisar("Tempo médio de espera dinheiro/ticket (s)", espera_media_dinheiro_ticket, f)
    analisar("Tempo médio no sistema dinheiro/ticket (s)", tempo_medio_sistema_dinheiro_ticket, f)

    analisar("Tempo médio de espera PIX (s)", espera_media_pix, f)
    analisar("Tempo médio pagamento PIX paralelo (s)", tempo_pagamento_pix_paralelo, f)
    analisar("Tempo médio no sistema PIX (s)", tempo_medio_sistema_pix, f)

    analisar("Tamanho médio da fila PIX", fila_pix_media, f)
    analisar("Pico da fila PIX", fila_pix_pico, f)
    analisar("Tamanho final da fila PIX", fila_pix_final, f)

    analisar("Clientes não atendidos", clientes_nao_atendidos, f)

    # Proporções
    proporcao_media("clientes prioritários", clientes_prioritarios, f)
    proporcao_media("clientes comprando tickets", clientes_ticket, f)
    proporcao_media("clientes com erro", clientes_com_erro, f)
    proporcao_media("clientes sem troco", sem_troco, f)
    proporcao_media("clientes não atendidos", clientes_nao_atendidos, f)
