import pandas as pd
import matplotlib.pyplot as plt

pix_csv = 'csv/resultados_pix.csv'
dinheiro_csv = 'csv/resultados_dinheiro.csv'
ticket_csv = 'csv/resultados_ticket.csv'

# Leitura dos dados
pix = pd.read_csv(pix_csv)
dinheiro = pd.read_csv(dinheiro_csv)
ticket = pd.read_csv(ticket_csv)

data = [
    pix['tempo_medio_sistema_geral'],
    dinheiro['tempo_medio_sistema_geral'],
    ticket['tempo_medio_sistema_geral']
]

labels = ['PIX (60%)', 'DINHEIRO (60%)', 'TICKET (60%)']

plt.figure(figsize=(10, 6))
box = plt.boxplot(data, patch_artist=True, medianprops=dict(color='black'))

# Cores customizadas para cada caixa
colors = ['lightblue', 'lightgreen', 'lightcoral']
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)

plt.xticks([1, 2, 3], labels)
plt.title('Comparação do Tempo Médio no Sistema Geral por Tipo de Pagamento')
plt.ylabel('Tempo Médio no Sistema (segundos)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
