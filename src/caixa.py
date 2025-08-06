import random

"""
Caixa retorna troco num modelo ganancioso, priorizando sempre as maiores notas na expectativa de reduzir
as chances de faltar troco no futuro. Troco só pode ser dado na forma de dinheiro, não em tickets.
Dinheiro que entra reabastece o caixa sendo que no caso de serem R$2, existe 40% de chance de vir na forma de 
duas moedas de R$1
"""
class Caixa:
    def __init__(self, estado_inicial=None):
        """
        Inicializa o caixa com um estado fornecido ou com o estado padrão.
        """
        self.cedulas = estado_inicial or {
            1: 20,     # moedas de R$1
            2: 20,     # notas de R$2
            5: 10,     # notas de R$5
            10: 8,    # notas de R$10
            20: 3,     # notas de R$20
            50: 1      # notas de R$50
        }

    def dar_troco(self, valor_troco):
        """
        Tenta dar troco usando o caixa atual com estratégia greedy (maiores cédulas primeiro).
        Se conseguir, atualiza o caixa e retorna o dicionário de cédulas usadas.
        Caso contrário, retorna None.
        """
        cedulas = [50, 20, 10, 5, 2, 1]
        troco = {}
        falta = valor_troco
        usado = {}

        for ced in cedulas:
            if falta <= 0:
                break

            disponivel = self.cedulas.get(ced, 0)
            usar = min(falta // ced, disponivel)
            if usar > 0:
                troco[ced] = usar
                falta -= usar * ced
                usado[ced] = usar

        if falta == 0:
            # Atualiza o caixa
            for ced, qtd in usado.items():
                self.cedulas[ced] -= qtd
            return troco
        else:
            return None  # Troco impossível
    
    def receber_pagamento(self, valor_pago):
        if valor_pago == 2:
            # Se for 2 reais, 40% de chance de ser duas moedas de R$1
            if random.random() < 0.4:
                self.cedulas[1] += 2
            else:
                self.cedulas[2] += 1
        else:
            if valor_pago in self.cedulas:
                self.cedulas[valor_pago] += 1
            else:
                self.cedulas[valor_pago] = 1   

    def repor(self, reposicao=None):
        """
        Reabastece o caixa para o nível inicial definido em reposicao,
        adicionando apenas o que faltar para chegar nessa quantidade.
        """
        reposicao = reposicao or {
            1: 20,
            2: 20,
            5: 10,
            10: 8,
            20: 3,
            50: 1
        }

        for ced, qtd_minima in reposicao.items():
            atual = self.cedulas.get(ced, 0)
            if atual < qtd_minima:
                self.cedulas[ced] = qtd_minima

