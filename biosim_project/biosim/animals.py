# -*- coding: utf-8 -*-

"""
This module provides classes implementing the animals in the biosim project.
"""

import random
# noinspection PyProtectedMember
from .fitness_workers import _fitness

__authors__ = 'Elisabeth Flatner and Marie Klever'
__emails__ = 'elisabeth.flatner@nmbu.no, marie.klever@nmbu.no'


class Animal(object):
    """This class represents the animals on the island."""

    params = None

    # noinspection PyPep8
    def __init__(self, weight, age=0):
        """
        :param weight: weight of the animal
        :param age: age of the animal
        """
        if weight <= 0:
            raise ValueError("Weight has to be positive and above 0")

        # Source: http://stackoverflow.com/questions/3501382/checking-whether-a-variable-is-an-integer-or-not
        # Accessed: 05.01.16
        if age < 0 or (age - round(age)) != 0:
            raise ValueError("Age has to be a positive integer")

        self._weight = weight
        self._age = age
        self._fitness = None

    @property
    def weight(self):
        """ Returns the weight of the animal. """
        return self._weight

    @weight.setter
    def weight(self, new_weight):
        """
        Updates weight of the animal. Sets fitness value for the animal to None.

        :param new_weight: new weight of the animal
        """
        self._weight = new_weight
        self._fitness = None

    @property
    def age(self):
        """ Returns the age of the animal. """
        return self._age

    @age.setter
    def age(self, new_age):
        """
        Updates age of the animal. Sets fitness value for the animal to None.

        :param new_age: new age for the animal 
        """
        self._age = new_age
        self._fitness = None

    @classmethod
    def set_parameters(cls, new_params):
        """
        Updating default parameters to new parameters.

        Raises valueError when invalid parameters are given.
        :param new_params: dictionary with new parameters
        """

        lower = {'eta': 0, 'omega': 0, 'a_half': 0, 'w_half': 0,
                 'phi_age': 0, 'phi_weight': 0, 'gamma': 0, 'w_birth': 0,
                 'sigma_birth': 0, 'zeta': 0, 'beta': 0, 'mu': 0, 'F': 0,
                 'xi': 0}

        upper = {'eta': 1, 'omega': 1, 'gamma': 1, 'beta': 1, 'mu': 1}

        if 'DeltaPhiMax' in new_params:
            if new_params['DeltaPhiMax'] <= 0:
                raise ValueError("DeltaPhiMax can not be zero or negative")

        for i in new_params:
            if i not in cls.params:
                raise ValueError("Parameter {} not defined for animal"
                                 .format(i))
            if i in lower:
                if new_params[i] < lower[i]:
                    raise ValueError("Parameter {} can not be lower than {}"
                                     .format(i, lower[i]))
            if i in upper:
                if new_params[i] > upper[i]:
                    raise ValueError("Parameter {} can not be higher than {}"
                                     .format(i, upper[i]))

        cls.params.update(new_params)

    def weight_of_animal(self):
        """ Returns the weight of the animal. """
        return self.weight

    def aging(self):
        """ Increases animal age with one. """
        self.age += 1

    def weight_change(self):
        """ Decreases animal weight with a given yearly amount. """
        self.weight -= self.params['eta'] * self.weight

    @property
    def fitness(self):
        """
        Calculates fitness of the animal using cython.

        :return: fitness value
        """

        if self._fitness is None:
            self._fitness = _fitness(self.params['phi_age'], self.age,
                                     self.params['a_half'],
                                     self.params['phi_weight'], self.weight,
                                     self.params['w_half'])
        return self._fitness

    def probability_birth(self, num_animals):
        """
        Calculates the probability of birth.

        :param num_animals: number of animals of the same species in the cell
        :return: probability of birth
        """
        if self.weight < (self.params['zeta'] * (
                    self.params['w_birth'] + self.params['sigma_birth'])):
            prob = 0
        else:
            prob = (self.params['gamma'] * self.fitness *
                    (num_animals - 1))
            if prob > 1:
                prob = 1

        return prob

    def birth(self, num_animals):
        """
        Checks if a animal is born.

        If born, mothers weight is changed and class instance of newborn is
        returned.

        :param num_animals: number of animals of the same species in the cell
        :return: class instance of newborn animal
        """

        prob_birth = self.probability_birth(num_animals)
        if random.random() < prob_birth:
            w_newborn = random.gauss(self.params['w_birth'],
                                     self.params['sigma_birth'])
            # If the weight of the newborn is less or equal to zero, or higher
            # than the weight of the mother, the animal is not born
            if 0 < w_newborn < self.weight:
                w_mother_after = self.weight - self.params['xi'] * w_newborn
                # If the the weight loss is higher than the weight of the
                # mother, the animal is not born
                if w_mother_after > 0:
                    self.weight = w_mother_after
                    return self.__class__(w_newborn)

    def death(self):
        """ Returns True if animal dies. """
        return random.random() < (self.params['omega'] * (1 - self.fitness))

    def prob_migration(self):
        """ Returns the probability for migration. """
        return self.params['mu'] * self.fitness


class Herbivore(Animal):
    """
    Represents the animal herbivore.

    This class provides all characteristics for herbivores, including aging,
    weight change, fitness, feeding, birth and death.
    """

    params = {'eta': 0.05, 'omega': 0.4, 'a_half': 40.0, 'w_half': 10.0,
              'phi_age': 0.2, 'phi_weight': 0.1, 'gamma': 0.2, 'w_birth': 8.0,
              'sigma_birth': 1.5, 'zeta': 3.5, 'xi': 1.2, 'beta': 0.9,
              'mu': 0.25, 'lambda': 1.0, 'F': 10.0}

    def __init__(self, weight, age=0):
        """
        :param weight: weight of the herbivore
        :param age: age of the herbivore
        """
        super(Herbivore, self).__init__(weight, age)

    def eating(self, available_food):
        """
        Calculates how much food the herbivore eats and adjusts its weight.

        :param available_food: amount of food available in the cell
        :return: the amount of food eaten by herbivore
        """

        if available_food < 0:
            raise ValueError("Amount of available food can not be negative")

        if Herbivore.params['F'] <= available_food:
            self.weight += Herbivore.params['beta'] * Herbivore.params['F']
            return Herbivore.params['F']
        else:
            self.weight += Herbivore.params['beta'] * available_food
            return available_food


class Carnivore(Animal):
    """
    Represents the animal carnivore.

    This class provides all characteristics for carnivores, including aging,
    weight change, fitness, feeding, birth and death.
    """

    params = {'eta': 0.125, 'omega': 0.9, 'a_half': 60.0, 'w_half': 4.0,
              'phi_age': 0.4, 'phi_weight': 0.4, 'gamma': 0.8, 'w_birth': 6.0,
              'sigma_birth': 1.0, 'zeta': 3.5, 'xi': 1.1, 'beta': 0.75,
              'mu': 0.4, 'lambda': 1.0, 'F': 50.0, 'DeltaPhiMax': 10.0}

    def __init__(self, weight, age=0):
        """
        :param weight: weight of the carnivore
        :param age: age of the carnivore
        """
        super(Carnivore, self).__init__(weight, age)

    def prob_kill(self, herb_fit):
        """
        Returns the probability of a herbivore being killed.

        :param herb_fit: fitness of the herbivore
        """

        return (self.fitness - herb_fit) / self.params['DeltaPhiMax']

    def carn_kills_herb(self, herbivore):
        """
        Returns True if a herbivore is killed by the carnivore.

        :param herbivore: the herbivore who is being hunted
        :return: True if herbivore is killed
        """
        if (0 < (self.fitness - herbivore.fitness) <
                self.params['DeltaPhiMax']):
            if random.random() < self.prob_kill(herbivore.fitness):
                return True
        else:
            return True

    def eating(self, herbivores):
        """
        Returns a list of the surviving herbivores.

        Changes the weight of the carnivore when it has eaten.
        :param herbivores: list of herbivores that can be eaten
        :return: list of surviving herbivores
        """
        eaten_food = 0
        surviving_herbivores = []

        for herb in herbivores:
            if (self.fitness <= herb.fitness or
                    eaten_food == Carnivore.params['F']):
                surviving_herbivores.extend(herbivores[herbivores.index(herb):])
                break
            else:
                if self.carn_kills_herb(herb):
                    if (eaten_food + herb.weight_of_animal() >
                            Carnivore.params['F']):
                        self.weight += ((Carnivore.params['F'] - eaten_food) *
                                        Carnivore.params['beta'])
                        eaten_food = Carnivore.params['F']
                    else:
                        self.weight += (herb.weight_of_animal() *
                                        Carnivore.params['beta'])
                        eaten_food += herb.weight_of_animal()
                else:
                    surviving_herbivores.append(herb)

        return surviving_herbivores
