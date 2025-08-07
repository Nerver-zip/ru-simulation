#!/bin/bash

# Verifica se o número de execuções foi passado como argumento
if [ -z "$1" ]; then
  echo "Uso: $0 <N>"
  exit 1
fi

N=$1
ARQUIVO_SAIDA="csv/resultados_ticket.csv"
PROGRAMA="src.simulacao"

mkdir -p csv

echo "clientes_atendidos,espera_media_geral,tempo_medio_sistema_geral,espera_media_dinheiro_ticket,tempo_medio_sistema_dinheiro_ticket,espera_media_pix,tempo_pagamento_pix_paralelo,tempo_medio_sistema_pix,clientes_prioritarios,clientes_ticket,clientes_com_erro,sem_troco,clientes_nao_atendidos,fila_pix_media,fila_pix_pico,fila_pix_final" > "$ARQUIVO_SAIDA"

# Executa N vezes
for ((i=1; i<=N; i++)); do
  python3 -m "$PROGRAMA" | grep 'CSV' | cut -d',' -f2- >> "$ARQUIVO_SAIDA"
done

echo "Coleta finalizada. Resultados salvos em $ARQUIVO_SAIDA"
