import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Arquivos CSV com dados dos 3 cenários
files = {
    'Dinheiro 60%': 'csv/resultados_dinheiro.csv',
    'PIX 60%': 'csv/resultados_pix.csv',
    'Ticket 60%': 'csv/resultados_ticket.csv'
}

# Carregar dados
data = {key: pd.read_csv(path) for key, path in files.items()}

# 1. Boxplot do tempo médio no sistema geral
plt.figure(figsize=(10,6))
times = [df['tempo_medio_sistema_geral'] for df in data.values()]
plt.boxplot(times, labels=data.keys(), patch_artist=True, medianprops=dict(color='black'))

colors = ['lightgreen', 'lightblue', 'lightcoral']
for patch, color in zip(plt.gca().artists, colors):
    patch.set_facecolor(color)

plt.title('Tempo Médio no Sistema Geral por Cenário')
plt.ylabel('Tempo Médio no Sistema (segundos)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()


labels = []
picos = []
medias = []

for key, df in data.items():
    labels.append(key)
    pico_pix = df['fila_pix_pico'].mean()
    media_pix = df['fila_pix_media'].mean()
    picos.append(pico_pix)
    medias.append(media_pix)

x = np.arange(len(labels))
width = 0.35

fig, ax = plt.subplots(figsize=(10,6))
rects1 = ax.bar(x - width/2, medias, width, label='Fila Média PIX', color='lightblue')
rects2 = ax.bar(x + width/2, picos, width, label='Pico da Fila PIX', color='steelblue')

ax.set_ylabel('Tamanho da Fila')
ax.set_title('Fila Média e Pico da Fila PIX por Cenário')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()

# 3. Clientes não atendidos
plt.figure(figsize=(10,6))
nao_atendidos = [df['clientes_nao_atendidos'].mean() for df in data.values()]
plt.bar(labels, nao_atendidos, color=['lightgreen', 'lightblue', 'lightcoral'])
plt.title('Média de Clientes Não Atendidos por Cenário')
plt.ylabel('Clientes Não Atendidos')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# 4. Falta de troco
plt.figure(figsize=(10,6))
sem_troco = [df['sem_troco'].mean() for df in data.values()]
plt.bar(labels, sem_troco, color=['lightgreen', 'lightblue', 'lightcoral'])
plt.title('Média de Ocorrências de Falta de Troco por Cenário')
plt.ylabel('Falta de Troco')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
