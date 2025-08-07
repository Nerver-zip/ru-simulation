import pandas as pd
import matplotlib.pyplot as plt

# Carregar os CSVs
pix = pd.read_csv('csv/resultados_pix.csv')
dinheiro = pd.read_csv('csv/resultados_dinheiro.csv')
ticket = pd.read_csv('csv/resultados_ticket.csv')

# Calcular clientes não atendidos reais (incluindo fila_pix_final)
pix_nao_atendidos = pix['clientes_nao_atendidos'] + pix['fila_pix_final']
dinheiro_nao_atendidos = dinheiro['clientes_nao_atendidos'] + dinheiro['fila_pix_final']
ticket_nao_atendidos = ticket['clientes_nao_atendidos'] + ticket['fila_pix_final']

# Criar DataFrame para plotar
data = {
    'PIX (60%)': pix_nao_atendidos,
    'DINHEIRO (60%)': dinheiro_nao_atendidos,
    'TICKET (60%)': ticket_nao_atendidos
}
df_nao_atendidos = pd.DataFrame(data)

# Plot boxplot
plt.figure(figsize=(10, 6))
box = plt.boxplot(df_nao_atendidos.values, tick_labels=df_nao_atendidos.columns, patch_artist=True, medianprops=dict(color='black'))

# Cores para as caixas
colors = ['lightblue', 'lightgreen', 'lightcoral']
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)

plt.title('Distribuição de Clientes Não Atendidos')
plt.ylabel('Número de Clientes Não Atendidos')
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()
