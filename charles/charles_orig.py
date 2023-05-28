import uuid
from random import shuffle, choice, sample, random
from operator import attrgetter
from copy import deepcopy
import numpy as np
import time


# change representation to list of lists
# create more crossover methods


class Individual:
    def __init__(
            self,
            representation=None,
            size=None,
            valid_set=None,  # do we need a valid set??
    ):
        if representation is None:
            self.representation = [np.random.uniform(size=size[i]) for i in range(len(size))]
        else:
            self.representation = [np.array(representation[rep_i]) for rep_i in range(4)]
        self.fitness = self.get_fitness()

    def get_fitness(self):
        raise Exception("You need to monkey patch the fitness path.")

    def set_weights(self):
        raise Exception("You need to monkey patch the set_weights path.")

    def index(self, value):
        return self.representation.index(value)

    def __len__(self):
        return len(self.representation)

    def __getitem__(self, position):
        return self.representation[position]

    def __setitem__(self, position, value):
        self.representation[position] = value

    def __repr__(self):
        return f"Individual(size={len(self.representation)}); Fitness: {self.fitness}"


class Population:
    def __init__(self, size, optim, individuals=[], **kwargs):
        self.individuals = []
        self.size = size
        self.optim = optim
        self.elite= []

        for _ in range(size):
            self.individuals.append(
                Individual(
                    size=kwargs["sol_size"]
                )
            )




    def evolve(self, gen_start, gen_end, xo_prob, mut_prob, select, mutate, crossover, elitism=True, ms=0.1, runkey=uuid.uuid4()):
        lstReturn = []

        for i in range(gen_start, gen_end+1):
            new_pop = []
            stepstart = time.time()

            if elitism > 0:
                if self.optim == "max":
                    elite = sorted(self.individuals, key=attrgetter("fitness"), reverse=True)[:elitism]
                    self.elite = elite
                elif self.optim == "min":
                    elite = sorted(self.individuals, key=attrgetter("fitness"))[:elitism]
                    self.elite = elite

            while len(new_pop) < self.size:
                parent1, parent2 = select(self), select(self)

                # Crossover
                if random() < xo_prob:
                    offspring1, offspring2 = crossover(parent1, parent2)
                else:
                    offspring1, offspring2 = parent1, parent2

                # Mutation
                #if random() < mut_prob:
                    offspring1 = mutate(individual=offspring1, ms=ms)
                #if random() < mut_prob:
                    offspring2 = mutate(individual=offspring2, ms=ms)

                x1 = Individual(representation=offspring1)
                x2 = Individual(representation=offspring2)

                new_pop.append(x1)
                if len(new_pop) < self.size:
                    new_pop.append(x2)

            if elitism > 0:
                if self.optim == "max":
                    for elem in elite:
                        worst = min(new_pop, key=attrgetter("fitness"))
                        if elem.fitness > worst.fitness:
                            new_pop.pop(new_pop.index(worst))
                            new_pop.append(elem)
                elif self.optim == "min":
                    for elem in elite:
                        worst = max(new_pop, key=attrgetter("fitness"))
                        if elem.fitness < worst.fitness:
                            new_pop.pop(new_pop.index(worst))
                            new_pop.append(elem)

            self.individuals = new_pop

            if self.optim == "max":
                bestfitnessinpop = max(self, key=attrgetter("fitness"))
                # print(f'Best individual: {max(self, key=attrgetter("fitness"))}')
            if self.optim == "min":
                bestfitnessinpop = min(self, key=attrgetter("fitness"))
                # print(f'Best individual: {min(self, key=attrgetter("fitness"))}')
            stepstop = time.time()
            lstReturn.append([runkey, i, bestfitnessinpop.fitness, stepstop - stepstart])

        return lstReturn

    def __len__(self):
        return len(self.individuals)

    def __getitem__(self, position):
        return self.individuals[position]
