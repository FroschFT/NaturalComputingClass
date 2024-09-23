import random
import itertools
import os
import numpy as np
import pandas as pd

basedir = os.path.abspath(os.path.dirname(__file__))

pokedex = pd.read_csv(basedir+"/data/pokemon_dataset.csv")
df_matriz = pd.read_csv(basedir+"/data/matriz_tipo.csv")
pokedex.fillna("NULL", inplace=True)

class Individual:
    """Individual class represents a single individual in the population."""
    def __init__(self):
        self.pokedex_number = 0
        self.name = "teste"
        self.type1 = random.choice(['A', 'B', 'C'])
        self.type2 = random.choice(['A', 'B', 'C', None])
        self.hp = random.randint(50, 100)
        self.attack = random.randint(10, 20)
        self.defense = random.randint(5, 15)
        self.speed = random.randint(1, 10)

        self.capure_rate = random.randint(1, 100)

    def get_pokemon(self):
        """Gets a random pokemon from the pokedex."""
        pokemon = pokedex.sample().to_dict(orient='records')[0]

        if pokemon["type2"] == "NULL":
            type2 = None
        else:
            type2 = pokemon["type2"]

        self.pokedex_number = pokemon["pokedex_number"]
        self.name = pokemon["name"]
        self.type1 = pokemon["type1"]
        self.type2 = type2
        self.hp = pokemon["hp"]
        self.attack = pokemon["attack_total"]
        self.defense = pokemon["defense_total"]
        self.speed = pokemon["speed"]
        self.capure_rate = pokemon["capture_rate"]

    def __repr__(self):
        return f"Individual(pokedex_number={self.pokedex_number}, name={self.name}, type1={self.type1}, type2={self.type2})"

class TeamIndividual:
    """TeamIndividual class represents a team of individuals in the population."""
    def __init__(self, team:list = []):
        self.team = team
        self.fitness = 0
        self.fitness_list = []

    def initialize_random_team(self, quantity:int = 6) -> None:
        """Initializes a random team of 6 individuals."""
        self.team = []
        for _ in range(quantity):
            pokemon = Individual()
            pokemon.get_pokemon()
            self.team.append(pokemon)

    def __repr__(self):
        return f"TeamIndividual(team={self.team}, fitness={self.fitness})"


class GeneticAlgorithm:
    """GeneticAlgorithm class represents the genetic algorithm.
    Used to find the best team (comination of individuals) to beat the oponent team."""
    def __init__(self, population_size:int = 20, tournament_size:int = 0, oponent_team:TeamIndividual = None):
        self.population_size = population_size
        self.tournament_size = tournament_size
        self.population = [] # list of TeamIndividual
        self.oponent_team = oponent_team # a TeamIndividual
        self.global_gen_fitness = 0
        self.historical_fitness = []
        self.fittest_team = 0

    def initialize_oponent_team(self) -> None:
        """Initializes a random oponent team."""
        self.oponent_team = TeamIndividual()
        self.oponent_team.initialize_random_team(6)

    def best_team(self, team:TeamIndividual) -> None:
        """Updates the fittest team if the team passed as argument is fitter."""
        if team.fitness > self.fittest_team.fitness:
            self.fittest_team = team

    def best_team_population(self, population:list) -> TeamIndividual:
        """Returns the fittest team in the population."""
        fittest_team = max(population, key=lambda x: x.fitness)
        return fittest_team

    def attack_multiplier(self, individual:Individual, oponent_individual:Individual) -> float:
        """Calculates the attack multiplier of an individual based on his oponent individual."""
        # 2x2 matrix with the types attack multipliers
        # 2x6 matrix with the types of the individuals
        # 2x6 transpose matrix with the types of the oponent individuals, vector now
        # mulipliers = {
        #     'A': {'A': 1, 'B': 2, 'C': 0.5},
        #     'B': {'A': 0.5, 'B': 1, 'C': 2},
        #     'C': {'A': 2, 'B': 0.5, 'C': 1}
        # }


        attack_multiplier1 = df_matriz.set_index("tipo")[f"{oponent_individual.type1}"].to_dict()[f"{individual.type1}"]

        if oponent_individual.type2 == None: # in case oponent_individual has only one type
            attack_multiplier2 = 1
        else:
            attack_multiplier2 = df_matriz.set_index("tipo")[f"{oponent_individual.type2}"].to_dict()[f"{individual.type1}"]

        if individual.type2 == None: # in case individual has only one type
            attack_multiplier3 = 1
        else:
            attack_multiplier3 = df_matriz.set_index("tipo")[f"{oponent_individual.type1}"].to_dict()[f"{individual.type2}"]

        if individual.type2 != None and oponent_individual.type2 != None: # in case both individuals has two types
            attack_multiplier4 = df_matriz.set_index("tipo")[f"{oponent_individual.type2}"].to_dict()[f"{individual.type2}"]
        else:
            attack_multiplier4 = 1

        attack_multiplier = attack_multiplier1 * attack_multiplier2 * attack_multiplier3 * attack_multiplier4

        return attack_multiplier

    def calculate_fitness_individual(self, individual:Individual, oponent_individual:Individual) -> float:
        """Calculates the fitness of an individual based on his oponent individual."""

        attack_multiplier = self.attack_multiplier(individual, oponent_individual)

        hp_coef = individual.hp / oponent_individual.hp
        speed_coef = individual.speed / oponent_individual.speed # proability of attacking or the attacking rate

        fitness = hp_coef + ((individual.attack/oponent_individual.defense) * attack_multiplier) * speed_coef

        return fitness

    def calculate_team_fitness(self, team:TeamIndividual) -> float:
        """Calculates the fitness of a team based on his oponent team."""
        # code for calculating fitness of a team based on his opponents team
        # fitness = sum of fitness of each individual
        for individual in team.team:
            fitness_list_temp = []
            fitness = 0
            for oponent_individual in self.oponent_team.team:
                fitness = self.calculate_fitness_individual(individual, oponent_individual)
                fitness_list_temp.append(fitness)
                team.fitness += fitness
            team.fitness_list.append(fitness_list_temp)
        return team.fitness

    def calculate_population_fitness(self) -> None:
        """Calculates the fitness of each team in the population."""
        for team in self.population:
            self.calculate_team_fitness(team)

    def calculate_global_fitness(self) -> None:
        for team in self.population:
            self.global_gen_fitness += team.fitness

    def sort_population(self):
        self.population = sorted(self.population, key = lambda x:x.fitness)

    def initialize_population(self) -> None:
        """Initializes a random population."""
        fittest_team = None
        for _ in range(self.population_size):
            team = None
            team = TeamIndividual()
            team.initialize_random_team(6)
            self.population.append(team)
        self.calculate_population_fitness()
        self.calculate_global_fitness()
        fittest_team = self.best_team_population(self.population)
        self.historical_fitness.append(fittest_team)
        # not using self.best_team because in the first generation 
        # all teams could have negative fitness and the fittest team 
        # would be 0 in that way could break the logic on future generations
        self.fittest_team = fittest_team # self.best_team(fittest_team)
        print(f"Generation 0: Fittest individual has fitness {fittest_team.fitness}")

    def roulette_wheel_selection(self) -> TeamIndividual:
        """ Selects an individual from the population using roulette wheel selection
    The roulette_wheel_selection method calculates the selection 
probabilities for each individual in the population based on 
their fitness, and then uses the itertools.accumulate 
function to calculate the cumulative probabilities. 
It then generates a random number between 0 and 1, 
and iterates over the cumulative probabilities until it finds 
the index of the first individual whose cumulative probability 
is greater than or equal to the random number. 
This individual is then selected for the next generation."""
        # one individual can be selected multiple times
        # because of that the same individual can be selected for crossover
        # that way in the crossover we can have the same individual as parent1 and parent2
        # resuling in the same individual as child
        selection_probabilities = [team.fitness / self.global_gen_fitness for team in self.population]
        cumulative_probabilities = list(itertools.accumulate(selection_probabilities))
        random_number = random.random()
        for i, probability in enumerate(cumulative_probabilities):
            if random_number <= probability:
                break
        return self.population[i]

    def tournament_selection(self) -> list:
        """Selects individuals from the population using tournament selection"""
        selected_individuals = []
        for i in range(self.population_size):
            tournament = random.sample(self.population, self.tournament_size)
            winner = max(tournament, key=lambda x: x.fitness)
            selected_individuals.append(winner)
        return selected_individuals

    def crossover(self, parent1:TeamIndividual, parent2:TeamIndividual) -> list:
        """Crossover method takes two parents and returns a child"""
        crosspoint = random.randint(0, 5)
        parent1_cut = parent1.team[:crosspoint]
        parent2_cut = parent2.team[crosspoint:]
        child = parent1_cut + parent2_cut
        return child

    def mutation(self, team:list, mutation_rate:float = 0.1) -> list:
        """Mutation method takes an team and mutates it's individuals with a given mutation rate"""
        mutated_team = []
        i = 0
        for x in team:
            pokemon = x
            if random.random() < mutation_rate:
                pokemon = Individual()
                pokemon.get_pokemon()
            mutated_team.append(pokemon)
            i += 0
        return mutated_team

    def reproduce(self, selected_teams:list, mutation_rate:float = 0.1) -> list:
        """Reproduce method takes a list of selected team's and returns a new population"""
        new_population = []
        for _ in range(self.population_size):
            parent1, parent2 = random.sample(selected_teams, 2)
            child_team = self.crossover(parent1, parent2)
            child_team = self.mutation(child_team, mutation_rate)
            child = TeamIndividual(child_team)
            new_population.append(child)
        return new_population

    def run(self, max_generations:int = 100, mutation_rate:float = 0.1) -> None:
        """Runs the genetic algorithm"""
        self.initialize_oponent_team()
        self.initialize_population()
        self.calculate_population_fitness()
        for generation in range(1, max_generations):
            selected_individuals = [self.roulette_wheel_selection() for _ in range(self.population_size)]
            self.population = self.reproduce(selected_individuals, mutation_rate)
            self.calculate_population_fitness()
            self.calculate_global_fitness()
            fittest_team = self.best_team_population(self.population)
            self.historical_fitness.append(fittest_team)
            self.best_team(fittest_team)

            print(f"Generation {generation}: Fittest individual has fitness {fittest_team.fitness}")