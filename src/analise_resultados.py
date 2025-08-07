import csv
import statistics
import math
from scipy.stats import shapiro

# --- Configuração ---
ARQUIVO = "csv/resultados_pix.csv"
ARQUIVO_SAIDA = "data/analise_pix.txt"  
nivel_confianca = 0.95
z = 1.96  # z-score para 95% de confiança

# Listas para análise
esperas = []
totais = []
prioritarios = []
ticket = []
com_erro = []
sem_troco = []
nao_atendidos = []

fila_pix_media = []
fila_pix_pico = []
fila_pix_final = []

clientes = []

# Leitura do CSV
with open(ARQUIVO, newline='') as csvfile:
    leitor = csv.DictReader(csvfile)
    for linha in leitor:
        clientes.append(int(linha["clientes"]))

        esperas.append(float(linha["espera_media"]))
        totais.append(float(linha["tempo_total_medio"]))

        prioritarios.append(int(linha["clientes_prioritarios"]))
        ticket.append(int(linha["clientes_ticket"]))
        com_erro.append(int(linha["clientes_com_erro"]))
        sem_troco.append(int(linha["sem_troco"]))
        nao_atendidos.append(int(linha["nao_atendidos"]))

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
    props = [v / c if c > 0 else 0 for v, c in zip(campo, clientes)]
    media = statistics.mean(props)
    desvio = statistics.stdev(props) if len(props) > 1 else 0
    erro = z * desvio / math.sqrt(len(props)) if len(props) > 1 else 0
    cv = (desvio / media) * 100 if media != 0 else float('inf')

    print(f"\n--- Proporção média de {nome} ---", file=f)
    print(f"{media*100:.2f}% ± {erro*100:.2f}% (IC 95%)", file=f)
    print(f"Coeficiente de variação (CV): {cv:.2f}%", file=f)

with open(ARQUIVO_SAIDA, "w") as f:
    # Análises principais contínuas
    analisar("Tempo médio de espera (s)", esperas, f)
    analisar("Tempo total no sistema (s)", totais, f)
    analisar("Tamanho médio da fila PIX", fila_pix_media, f)
    analisar("Pico da fila PIX", fila_pix_pico, f)
    analisar("Tamanho final da fila PIX", fila_pix_final, f)
    analisar("Clientes não atendidos", nao_atendidos, f)

    # Proporções
    proporcao_media("clientes prioritários", prioritarios, f)
    proporcao_media("clientes comprando tickets", ticket, f)
    proporcao_media("clientes com erro", com_erro, f)
    proporcao_media("clientes sem troco", sem_troco, f)
    proporcao_media("clientes não atendidos", nao_atendidos, f)

