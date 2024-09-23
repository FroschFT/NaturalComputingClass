"""
This module implements a genetic algorithm to optimize Himmelblau's function.
"""

import numpy as np


# Define Himmelblau's function
def himmelblau(x:float, y:float) -> float:
    """
    Calculate the value of the Himmelblau's function for given x and y.
    We have a bidimensional space: x and y, and we evaluate it by Z.
    Himmelblau's function is a multi-modal function used to test
    the performance of optimization algorithms.

    Parameters:
        x (float): The x-coordinate.
        y (float): The y-coordinate.

    Returns:
        float: The value of the Himmelblau's function at the given coordinates.
    """
    return (x**2 + y - 11)**2 + (x + y**2 - 7)**2

class Individuo():
    """
    Classe que representa um individuo da população
    """

    def __init__(self, chromosome=None, geracao = 0):
        """
        Inicializa um individuo com um cromossomo aleatório e calcula o fitness do individuo.

        Parameters:
            chromosome (list): Cromossomo do individuo. Se não fornecido, um aleatório será gerado.
            geracao (int): Número da geração a qual o individuo pertence.

        Attributes:
            chromosome (list): Cromossomo do individuo.
            fitness (float): Valor do fitness do individuo.
            geracao (int): Número da geração a qual o individuo pertence.
            passo_evolutivo (float): O quanto a mutação vai permitir variar o valor no espaço.
            probabilidade_sobrevivencia_relativa_geracao (float): Probabilidade de sobrevivência relativa do individuo na geração.
            probabilidade_limite_inferior (float): Limite inferior da probabilidade de sobrevivência relativa do individuo na geração.
            probabilidade_limite_superior (float): Limite superior da probabilidade de sobrevivência relativa do individuo na geração.
        """
        self.geracao = geracao

        self.chromosome = self.init_chromosome() if chromosome == None else chromosome
        self.fitness = self.cal_fitness()

        self.passo_evolutivo = 1 # o quanto a mutação vai perimitir variar o valor no espaço
        self.probabilidade_sobrevivencia_relativa_geracao = 0
        self.probabilidade_limite_inferior = 0
        self.probabilidade_limite_superior = 0

    def init_chromosome(self):
        """ Inicializa um cromossomo aleatório """
        return list(np.random.uniform(low = -5, high = 5, size = 2))

    def cal_fitness(self):
        '''
        Calculate fitness score, acording to the himmelblau
        function
        '''
        return himmelblau(self.chromosome[0], self.chromosome[1])

    def mutation(self, taxa_mutacao, chromosome = None):
        """
            aplica uma mutação nos cromossomos do individuo
            por padrão e retorna o cromossomo da mutação
        """
        # taxa de mutação permite o quanto os individuos tem a chance de sofre uma mutação
        # o passo evolutivo indica o quanto o de mutação sofre

        chromosome_mutado = self.chromosome if chromosome == None else chromosome

        for i in range(len(self.chromosome)):
            if np.random.random() < taxa_mutacao:
                temp = self.chromosome[i] + np.random.uniform(low = -self.passo_evolutivo, high = self.passo_evolutivo, size = None)
                if temp > 5:
                    temp = 5
                elif temp < -5:
                    temp = -5
                self.chromosome[i] = temp

        if chromosome == None:
            self.chromosome = chromosome_mutado
        
        return chromosome_mutado

    def crossover_default(self, outro_individuo):
        """ a partir dos pais retorna uma possivel recombinação dos cromossomos"""
        corte = np.random.randint(low = 0, high = len(self.chromosome), size = None) # sempre 0 ou 1

        if corte == 0: # mantem a primeira parte
            filho = [self.chromosome[0], outro_individuo.chromosome[1]]
        else:
            filho = [outro_individuo.chromosome[0], self.chromosome[1]]

        return filho

    def reproduction(self, outro_individuo, taxa_mutacao):
        """ Aplica a forma com que o individuo se reproduz
            retona o material genetico para criação de um novo individuo
        """
        # gera o crossover
        cromossomo_do_filho = self.crossover_default(outro_individuo)
        # aplica a mutacao
        cromossomo_do_filho = self.mutation(taxa_mutacao, chromosome = cromossomo_do_filho)

        return cromossomo_do_filho

    def __repr__(self):
        return f'<Individuo(chromosome={self.chromosome}, fitness={self.fitness}, geracao={self.geracao}, prob={self.probabilidade_sobrevivencia_relativa_geracao})>'



class AlgoritmoGenetico():
    """
    Classe que representa o algoritmo genético
    """
    def __init__(self, tamanho_populacao):
        """
        Inicializa o algoritmo genético com uma população de tamanho_populacao.

        Parameters:
            tamanho_populacao (int): Tamanho da população.

        Attributes:
            tamanho_populacao (int): Tamanho da população.
            populacao (list): Lista de individuos da população.
            geracao (int): Número da geração atual.
            melhor_solucao (Individuo): Melhor solução encontrada até o momento.
            lista_solucoes (list): Lista contendo as soluções de cada geração.
        """
        self.tamanho_populacao = tamanho_populacao
        self.populacao = []
        self.geracao = 0
        self.melhor_solucao = 0
        self.lista_solucoes = []

    def melhor_individuo(self, individuo):
        """ verifica se o individuo é o melhor da população """
        if self.melhor_solucao.fitness > individuo.fitness:
            self.melhor_solucao = individuo

    def ordena_populacao(self):
        """ ordena a população de acordo com o fitness """
        self.populacao = sorted(self.populacao, key = lambda x:x.fitness)

    def soma_fitness(self):
        """ soma o fitness de todos os individuos da população """ # nota global da população
        soma = 0
        for individuo in self.populacao:
            soma += individuo.fitness
        return soma

    def avaliar_populacao(self):
        """avalia os individuos referente a população"""
        nota_global = self.soma_fitness()
        for x in range(self.tamanho_populacao):
            self.populacao[x].probabilidade_sobrevivencia_relativa_geracao = (self.populacao[-x-1].fitness/nota_global)

        nota_global = 0
        # definir os limites
        for individuo in self.populacao:
            individuo.probabilidade_limite_inferior = nota_global
            nota_global += individuo.probabilidade_sobrevivencia_relativa_geracao
            individuo.probabilidade_limite_superior = nota_global

    def inicializa_populacao(self):
        """ inicializa a população com individuos aleatórios """
        for _ in range(self.tamanho_populacao):
            self.populacao.append(Individuo()) #gera individuos de forma aleatória da lista de produtos
        self.ordena_populacao()
        self.melhor_solucao = self.populacao[0]
        self.avaliar_populacao()

    def selecionar_individuo(self):
        """ seleciona um individuo da população de acordo com a probabilidade de sobrevivência """
        valor_sorteado = np.random.random() 
        # s = np.random.poisson(lam=1, size=2000)
        # s = s/np.max(s)*np.random.random()
        # valor_sorteado = random.choice(s)
        for individuo in self.populacao:
            if individuo.probabilidade_limite_inferior >= valor_sorteado and individuo.probabilidade_limite_superior > valor_sorteado:
                break
        return individuo

    def reproducao_default(self, taxa_mutacao, geracao):
        """ utiliza da população atual
            retornar uma nova população.
            realizado o cruzamento 2 a 2 de cada
            individuo da população seguindo a ordem da população atual
        """

        nova_populacao = []
        i = 0

        for _ in range(0, self.tamanho_populacao, 2):
            pai = self.selecionar_individuo()
            mae = self.selecionar_individuo()

            cromossomos_filho1 = pai.reproduction(mae, taxa_mutacao)
            cromossomos_filho2 = mae.reproduction(pai, taxa_mutacao)

            nova_populacao.append(Individuo(chromosome=cromossomos_filho1, geracao=geracao))
            nova_populacao.append(Individuo(chromosome=cromossomos_filho2, geracao=geracao))

            i += 2

        return nova_populacao

    def atualizar_populacao(self, nova_populacao, geracao):
        """ Executa o algoritmo genetico """
        self.populacao = nova_populacao
        self.ordena_populacao()
        self.melhor_individuo(self.populacao[0])
        self.avaliar_populacao()
        self.geracao = geracao

    def visualiza_geracao(self):
        """ Mostra a geração atual """
        melhor = self.populacao[0]
        print(f"G:{self.geracao} -> fitness: {melhor.fitness:.2f} coordenadas: {melhor.chromosome}")

    def run_algoritmo(self, taxa_mutacao, numero_geracoes):
        """ Executa o algoritmo genetico """

        ## Bloco de Gerações
        for geracao in range(numero_geracoes):
            nova_populacao = self.reproducao_default(taxa_mutacao, geracao)
            self.atualizar_populacao(nova_populacao = nova_populacao, geracao = geracao)
            self.lista_solucoes.append(self.populacao[0])
            self.visualiza_geracao()
        print(f"\nMelhor solução -> G: {self.melhor_solucao.geracao} \.fitness: {self.melhor_solucao.fitness:.2f} coordenadas: {self.melhor_solucao.chromosome}")
