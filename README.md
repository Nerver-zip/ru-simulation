# Simulação de Filas com SimPy - Modelo M/M/1 (Caixa do RU)

**Disciplina:** Análise de Desempenho de Sistemas 2025/1
---

## Descrição do Projeto

Este projeto implementa uma simulação do atendimento em um Restaurante Universitário (RU) da UFPel, modelando um único caixa com regras específicas de atendimento, formas de pagamento e compra de tickets. O objetivo é analisar o impacto das escolhas dos clientes (forma de pagamento, compra de tickets, prioridade) e das políticas operacionais sobre o desempenho do sistema.

---

## Objetivos da Simulação

- Avaliar como diferentes formas de pagamento (PIX, dinheiro, ticket) influenciam métricas como tempo médio de espera, tempo total no sistema, eventos anômalos e uso do caixa.
- Analisar o efeito da venda de tickets sobre o sistema, comparando dias com e sem venda de tickets.
- Manter controle sobre os parâmetros de chegada, prioridades e tempos de atendimento para isolar o efeito das políticas de pagamento e ticket.

---

## Componentes Principais

### Entidades

- **Cliente:** Usuário que realiza pagamento via PIX, dinheiro ou ticket, pode comprar tickets antecipados e pode ser prioritário.
- **Caixa:** Responsável pelo atendimento, controle do troco com política gananciosa e reabastecimento dinâmico.
- **Fila:** Estrutura FIFO com prioridade para clientes prioritários; fila principal para atendimento e fila paralela para pagamentos via PIX.

### Eventos Modelados

- Chegada e atendimento de clientes.
- Eventos anômalos (falta de troco, erros).
- Pagamentos paralelos via PIX.
- Compra de tickets que bloqueia fila principal.

---

## Políticas e Regras

- Atendimento em fila única prioritária.
- Pagamentos via PIX são processados paralelamente, não bloqueando fila principal.
- Compra de tickets bloqueia a fila principal até o fim da operação.
- Compra de tickets permitida apenas em dias específicos (segunda e terça).
- Política gananciosa de troco.
- Atendimento sem recusa, mesmo com falta de troco, porém com atraso adicional.

---

## Parâmetros do Modelo

- Intervalos de tempo para chegadas, atendimento e pagamento baseados em distribuições exponenciais e normais.
- Proporção de clientes por forma de pagamento configurável.
- Probabilidade fixa para eventos anômalos.
- Estado inicial e reposição do caixa fixos.

---

## Saídas e Métricas Coletadas

- Tempo médio de espera e tempo total no sistema por forma de pagamento e geral.
- Utilização do caixa.
- Pico e média do tamanho da fila.
- Tempo máximo de espera registrado.
- Quantidade de clientes prioritários atendidos.
- Frequência de eventos anômalos e falta de troco.
- Número de clientes não atendidos.

---

## Estrutura do Código

- **caixa.py:** Gerenciamento do caixa e troco.
- **cliente.py:** Geração de clientes com características realistas e probabilidades.
- **simulacao.py:** Fluxo da simulação, gerência de filas, atendimento, pagamento e coleta de métricas.

---

## Como Rodar

1. Certifique-se de ter Python 3 e a bibliotecas listadas em 'requirements.txt' instaladas.
2. Escolha seus parâmetros.
3. Execute o script `run.sh` para iniciar a simulação, passe como argumento o número de execuções a serem feitas.
4. Os resultados serão exportados para CSV.
5. Em `debug.py` é possível ver a simulação detalhadamente com saída no terminal.
---
## Observações
Este projeto permite explorar os impactos operacionais das políticas de atendimento e formas de pagamento no RU, fornecendo subsídios para decisões sobre o uso do caixa, incentivo a meios de pagamento e venda de tickets.

---
*Desenvolvido por Marcelo Augusto Etcheverria - 2025*
