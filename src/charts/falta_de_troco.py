import pandas as pd
import matplotlib.pyplot as plt

# Carregar os CSVs
pix = pd.read_csv('csv/resultados_pix.csv')
dinheiro = pd.read_csv('csv/resultados_dinheiro.csv')
ticket = pd.read_csv('csv/resultados_ticket.csv')

# Extrair a coluna sem_troco
pix_falta_troco = pix['sem_troco']
dinheiro_falta_troco = dinheiro['sem_troco']
ticket_falta_troco = ticket['sem_troco']

# Criar DataFrame para plotar
data = {
    'PIX (60%)': pix_falta_troco,
    'DINHEIRO (60%)': dinheiro_falta_troco,
    'TICKET (60%)': ticket_falta_troco
}
df_falta_troco = pd.DataFrame(data)

# Plot boxplot
plt.figure(figsize=(10, 6))
box = plt.boxplot(df_falta_troco.values, tick_labels=df_falta_troco.columns, patch_artist=True, medianprops=dict(color='black'))

# Cores para as caixas
colors = ['lightblue', 'lightgreen', 'lightcoral']
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)

plt.title('Ocorrência de Falta de Troco em cada cenário')
plt.ylabel('Número de vezes em que faltou troco')
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()
