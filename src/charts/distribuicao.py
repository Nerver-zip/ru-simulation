import pandas as pd
import matplotlib.pyplot as plt

# Caminhos dos arquivos CSV
dinheiro_csv = 'csv/resultados_dinheiro.csv'
ticket_csv = 'csv/resultados_ticket.csv'

# Leitura dos dados
dinheiro = pd.read_csv(dinheiro_csv)
ticket = pd.read_csv(ticket_csv)

# Extrair a coluna de interesse
dinheiro_tempo = dinheiro['tempo_medio_sistema_geral']
ticket_tempo = ticket['tempo_medio_sistema_geral']

plt.figure(figsize=(10, 6))

bins = 30

# Histogramas com cores sólidas e bordas bem definidas
plt.hist(dinheiro_tempo, bins=bins, alpha=1.0, label='Dinheiro (60%)', color='green', edgecolor='black', linewidth=1.5)
plt.hist(ticket_tempo, bins=bins, alpha=1.0, label='Ticket (60%)', color='red', edgecolor='black', linewidth=1.5)

plt.title('Distribuição dos Tempos Médios no Sistema: Dinheiro vs Ticket')
plt.xlabel('Tempo Médio no Sistema (segundos)')
plt.ylabel('Frequência')
plt.legend()
plt.grid(axis='y', alpha=0.7)

plt.tight_layout()
plt.show()
