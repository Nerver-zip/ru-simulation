#!/bin/bash

# Verifica se o número de execuções foi passado como argumento
if [ -z "$1" ]; then
  echo "Uso: $0 <N>"
  exit 1
fi

N=$1
ARQUIVO_SAIDA="csv/resultados.csv"
PROGRAMA="src.simulacao"

mkdir -p csv

echo "clientes,espera_media,tempo_total_medio,clientes_prioritarios,clientes_ticket,clientes_com_erro,sem_troco,nao_atendidos" > "$ARQUIVO_SAIDA"

# Executa N vezes
for ((i=1; i<=N; i++)); do
  python3 -m "$PROGRAMA" | grep 'CSV' | cut -d',' -f2- >> "$ARQUIVO_SAIDA"
done

echo "Coleta finalizada. Resultados salvos em $ARQUIVO_SAIDA"
