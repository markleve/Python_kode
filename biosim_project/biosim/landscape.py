# -*-coding: utf-8 -*-

"""
This module provides classes implementing the landscapes for the biosim project.

"""
import math
import random
from .animals import Herbivore, Carnivore

__authors__ = 'Elisabeth Flatner and Marie Klever'
__emails__ = 'elisabeth.flatner@nmbu.no, marie.klever@nmbu.no'


class Landscape(object):
    """
    This class represents the landscape on the island.
    """

    params = None

    def __init__(self, location=None):
        """
        :param location: tuple representing the cells python coordinates on
        the island
        """
        self.loc = location
        self.herb = []
        self.carn = []
        self.herb_immigrants = []
        self.carn_immigrants = []
        self.available_food = 0

    @classmethod
    def set_parameters(cls, new_params):
        """
        Updates default parameters to new parameters.

        Raises ValueError when invalid parameters are given.
        :param new_params: dictionary with new parameters
        """
        for i in new_params:
            if i not in cls.params:
                raise ValueError("Parameter {} not defined for landscape"
                                 .format(i))

        for i in new_params:
            if new_params[i] < 0:
                raise ValueError("Invalid value for {}".format(i))

        if 'alpha' in new_params:
            if new_params['alpha'] > 1:
                raise ValueError("Invalid value for parameter alpha")

        cls.params.update(new_params)

    def fitness_sorting(self, herb_descending, carn_descending=True):
        """
        Sorts herbivores and carnivores after fitness value.

        :param herb_descending: True if herbivores should be sorted in
                                descending order, else False
        :param carn_descending: True if the carnivore should be sorted in
                                descending order, else False
        """

        self.herb.sort(key=lambda hb: hb.fitness, reverse=herb_descending)
        self.carn.sort(key=lambda cn: cn.fitness, reverse=carn_descending)

    def reduce_available(self, eaten_food):
        """
        Reduces available fodder after the herbivores have eaten.

        :param eaten_food: amount of food eaten by the herbivore
        """
        self.available_food -= eaten_food

    def herb_eating(self):
        """
        All herbivores get an opportunity to eat fodder.

        Herbivores eats in the order of their fitness. The available food is
        reduced by the amount of fodder that the herbivore ate.
        """
        self.fitness_sorting(herb_descending=True)
        num_herb = self.total_num_animals(species='herbivore')
        k = 0
        while k < num_herb and 0 < self.available_food:
            self.reduce_available(self.herb[k].eating(self.available_food))
            k += 1

    def carn_eating(self):
        """
        All carnivores get an opportunity to hunt herbivores.

        Carnivores eats in the order of their fitness.
        """
        self.fitness_sorting(herb_descending=False)
        for carn in self.carn:
            if not self.herb:
                break
            elif carn.fitness < self.herb[0].fitness:
                break

            self.herb = carn.eating(self.herb)

    @staticmethod
    def newborns(animals_procreating):
        """
        Returning list of animals that is born.

        :param animals_procreating: list of class instances of the
                                    animals that are procreating
        :return: list of class instances of newborn animals
        """
        newborn_animals = []
        for animal in animals_procreating:
            new = animal.birth(len(animals_procreating))
            if new is not None:
                newborn_animals.append(new)
        return newborn_animals

    def animal_birth(self):
        """
        All animals get an opportunity to procreate.

        Adds newborn animals to population.
        """
        self.herb += self.newborns(self.herb)
        self.carn += self.newborns(self.carn)

    def neighbour_locations(self):
        """
        Collects the coordinates of the neighbouring cells.

        n1 is upper neighbour
        n2 is neighbour on right side
        n3 is lower neighbour
        n4 is neighbour on left side

        :return: list of tuples with neighbour coordinates
        """
        n1 = ((self.loc[0] - 1), self.loc[1])
        n2 = (self.loc[0], self.loc[1] + 1)
        n3 = ((self.loc[0] + 1), self.loc[1])
        n4 = (self.loc[0], (self.loc[1] - 1))
        return [n1, n2, n3, n4]

    def herb_migration(self, neighbours):
        """
        Moves the herbivore to neighbour cell if condition for migration is
        fulfilled. Updates population of herbivores with remaining herbivores.

        :param neighbours: list of class instances of neighbouring cells
        """
        remaining_herb = []
        for herb in self.herb:
            if random.random() < herb.prob_migration():
                prob_move = self.prob_move(neighbours, animal=herb,
                                           species='herbivore')

                if sum(prob_move) == 0:
                    remaining_herb.append(herb)
                else:
                    pos = self.animal_moves_to(prob_move)
                    neighbours[pos].add_herb_immigrant(herb)
            else:
                remaining_herb.append(herb)

        self.herb = remaining_herb

    def carn_migration(self, neighbours):
        """
        Moves the carnivore to neighbour cell if condition for migration is
        fulfilled. Updates population of carnivores with remaining carnivores.

        :param neighbours: list of class instances of neighbouring cells
        """
        remaining_carn = []
        for carn in self.carn:
            if random.random() < carn.prob_migration():
                prob_move = self.prob_move(neighbours, animal=carn,
                                           species='carnivore')

                if sum(prob_move) == 0:
                    remaining_carn.append(carn)
                else:
                    pos = self.animal_moves_to(prob_move)
                    neighbours[pos].add_carn_immigrant(carn)
            else:
                remaining_carn.append(carn)

        self.carn = remaining_carn

    @staticmethod
    def relative_abundance_of_fodder(neighbours, animal, species):
        """
        Calculates the relative abundance of fodder in each neighbouring cell.

        :param neighbours: list of class instances to neighboring cells
        :param animal: class instance of the animal that shall move
        :param species: species for animal that shall move
        :return: list with neighbours relative abundance of fodder
        """
        return [cell.get_available_fodder(species) /
                ((cell.total_num_animals(species) + 1) * animal.params['F'])
                for cell in neighbours]

    def get_available_fodder(self, species):
        """
        Returns relevant available fodder in the cell.

        :param species: species for animal that shall eat
        """
        if species == 'Herbivore' or species == 'herbivore':
            return self.available_food
        elif species == 'Carnivore' or species == 'carnivore':
            return sum([herb.weight_of_animal() for herb in self.herb])
        else:
            raise ValueError("Given species does not exist")

    def prob_move(self, neighbours, animal, species):
        """
        Calculates probability to move to each neighbour cell.

        :param neighbours: list of class instances to the neighbour cells
        :param animal: the class instance of the animal who moves
        :param species: species for animal that shall move
        :return: list of probabilities to move to neighbour cell
        """
        ek = self.relative_abundance_of_fodder(neighbours, animal=animal,
                                               species=species)
        exp_ek = self.propensity(neighbours, animal, ek)

        # if the cell is surrounded by only mountain and ocean prob_move is zero
        if sum(exp_ek) == 0:
            return [0, 0, 0, 0]

        return [exp_ekj/sum(exp_ek) for exp_ekj in exp_ek]

    @staticmethod
    def propensity(neighbours, animal, ek):
        """
        Calculates the propensity of each neighbour cell.

        :param neighbours: list of class instances to the neighbour cells
        :param animal: the class instance of the animal who moves
        :param ek: relative abundance of fodder for given animal
        :return: list of propensity
        """

        exp_ek = []
        for cell, ekj in zip(neighbours, ek):
            if not cell.animals_can_live_here():
                exp_ek.append(0)
            else:
                exp_ek.append(math.exp(animal.params['lambda'] * ekj))

        return exp_ek

    @staticmethod
    def animal_moves_to(prob_move):
        """
        Returns position of the neighbour cell that the animal moves to.
        """
        if round(sum(prob_move), 15) != 1:
            raise ValueError("Sum of probabilities to move should be one")

        rnd = random.random()
        pos = 0
        prob_acum = prob_move[pos]

        while prob_acum <= rnd:
            pos += 1
            prob_acum += prob_move[pos]
            if pos == 3:
                break

        return pos

    def add_herb_immigrant(self, herb_immigrant):
        """ Add immigrants to list of immigrants in the cell. """
        self.herb_immigrants.append(herb_immigrant)

    def add_carn_immigrant(self, carn_immigrant):
        """ Add immigrants to list of immigrants in the cell. """
        self.carn_immigrants.append(carn_immigrant)

    def add_immigrants_to_pop(self):
        """ Add immigrants to existing population. """
        self.herb.extend(self.herb_immigrants)
        self.herb_immigrants = []

        self.carn.extend(self.carn_immigrants)
        self.carn_immigrants = []

    def total_num_animals(self, species=None):
        """Returns number of given species. """
        if species == 'Herbivore' or species == 'herbivore':
            return len(self.herb) + len(self.herb_immigrants)
        elif species == 'Carnivore' or species == 'carnivore':
            return len(self.carn) + len(self.carn_immigrants)
        else:
            raise ValueError("Given species does not exist")

    def animal_aging(self):
        """ All animals get a year older. """
        for animal in self.herb + self.carn:
            animal.aging()

    def animal_weight_change(self):
        """ All animals lose weight. """
        for animal in self.herb + self.carn:
            animal.weight_change()

    def animal_death(self):
        """
        Investigating weather any of the animals die.

        Population is updated with only surviving animals.
        """
        self.herb = [herb for herb in self.herb if not herb.death()]
        self.carn = [carn for carn in self.carn if not carn.death()]

    def add_population(self, pop):
        """
        Creates class instances for animals and adds them to existing
        population.

        :param pop: list of dictionaries for each animal
        """
        for animal in pop:
            if (animal['species'] == 'Herbivore' or
                    animal['species'] == 'herbivore'):
                self.herb.append(
                    Herbivore(animal['weight'], animal['age']))
            elif (animal['species'] == 'Carnivore' or
                    animal['species'] == 'carnivore'):
                self.carn.append(
                    Carnivore(animal['weight'], animal['age']))
            else:
                raise ValueError("invalid species")

    def animals_can_live_here(self):
        """ Returns True because animals can live in the cell. """
        return True

    def food_growth(self):
        """No food can grow in the cell. """
        return None


class Jungle(Landscape):
    """
    This class represents the landscape jungle.
    """

    params = {'fmax': 800}

    def __init__(self, location=None):
        """
        :param location: tuple representing the cells location on the island
        """
        super(Jungle, self).__init__(location)
        self.loc = location
        self.available_food = Jungle.params['fmax']

    def food_growth(self):
        """ Growth of fodder each year. """
        self.available_food = Jungle.params['fmax']


class Savannah(Landscape):
    """
    This class represents the landscape savannah.
    """

    params = {'fmax': 300, 'alpha': 0.3}

    def __init__(self, location=None):
        """
        :param location: tuple representing the cells location on the island
        """
        super(Savannah, self).__init__(location)
        self.loc = location
        self.available_food = Savannah.params['fmax']

    def food_growth(self):
        """ Growth of fodder each year. """
        self.available_food = (self.available_food + Savannah.params['alpha'] *
                               (Savannah.params['fmax'] - self.available_food))


class Desert(Landscape):
    """
    This class represents the landscape desert.
    """

    def __init__(self, location=None):
        """
        :param location: tuple representing the cells location on the island
        """
        super(Desert, self).__init__(location)
        self.loc = location


class Mountain(Landscape):
    """
    This class represents the landscape mountain.
    """

    def __init__(self, location=None):
        """
        :param location: tuple representing the cells location on the island
        """
        super(Mountain, self).__init__(location)
        self.loc = location

    def animals_can_live_here(self):
        """ Returns False because animals can not live in the cell. """
        return False

    def add_population(self, pop):
        """Raises ValueError if population is added to cell. """
        if pop is not None:
            raise ValueError("Animals can not live here")


class Ocean(Landscape):
    """
    This class represents the landscape ocean.
    """

    def __init__(self, location=None):
        """
        :param location: tuple representing the cells location on the island
        """
        super(Ocean, self).__init__(location)
        self.loc = location

    def animals_can_live_here(self):
        """ Returns False because animals can not live in the cell. """
        return False

    def add_population(self, pop):
        """Raises ValueError if population is added to cell. """
        if pop is not None:
            raise ValueError("Animals can not live here")
