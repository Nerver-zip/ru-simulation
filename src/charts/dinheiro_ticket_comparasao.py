import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Leitura dos dados
dinheiro = pd.read_csv('csv/resultados_ticket.csv')['tempo_medio_sistema_geral']

# Cálculo média e mediana
media = dinheiro.mean()
mediana = dinheiro.median()

# Plot
plt.figure(figsize=(8,5))
sns.histplot(dinheiro, kde=True, color='royalblue', bins=15)

plt.title(f'Distribuição do Tempo Médio no Sistema - Ticket (60%)\nMédia = {media:.2f}, Mediana = {mediana:.2f}')
plt.xlabel('Tempo Médio no Sistema (segundos)')
plt.ylabel('Frequência')
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()
