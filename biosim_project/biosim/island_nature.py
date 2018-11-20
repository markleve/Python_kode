# -*-coding: utf-8 -*-

"""
This module provides a class implementing the island for the biosim project.
"""

from .landscape import Jungle, Savannah, Desert, Mountain, Ocean
import random
import numpy as np

__authors__ = 'Elisabeth Flatner and Marie Klever'
__emails__ = 'elisabeth.flatner@nmbu.no, marie.klever@nmbu.no'


class Island(object):
    """
    This class represents the island with all cells.
    """

    def __init__(self, geogr):
        """

        :param geogr: string with specifications about the islands geography
        """

        self.geogr = geogr.split()

        isl_width = max([len(stri) for stri in self.geogr])
        for row_str in self.geogr:
            if len(row_str) != isl_width:
                raise ValueError("Island has to be a rectangle")

        for letter in self.geogr[0]:
            if letter != 'O':
                raise ValueError("Island must be surrounded by ocean")

        for letter in self.geogr[-1]:
            if letter != 'O':
                raise ValueError("Island must be surrounded by ocean")

        for row_letter in self.geogr[1:-1]:
            if row_letter[0] != 'O' or row_letter[-1] != 'O':
                raise ValueError("Island must be surrounded by ocean")

        self.island_map = []

        if len(self.geogr) == 0:
            raise ValueError("Island map is empty, there is no island")

        for row_num in range(len(self.geogr)):
            row = []
            for col_num in range(len(self.geogr[0])):
                letter = self.geogr[row_num][col_num]
                if letter == 'J':
                    row.append(Jungle((row_num, col_num)))
                elif letter == 'S':
                    row.append(Savannah((row_num, col_num)))
                elif letter == 'D':
                    row.append(Desert((row_num, col_num)))
                elif letter == 'M':
                    row.append(Mountain((row_num, col_num)))
                elif letter == 'O':
                    row.append(Ocean((row_num, col_num)))
                else:
                    raise ValueError(
                        "Landscape type does not exist on the island")

            self.island_map.append(row)

    def place_animals(self, population):
        """
        Places populations of animals in the correct location on the island.

        :param population: dictionary with location and corresponding population
        """

        for pop in population:
            row, col = (pop['loc'][0] - 1), (pop['loc'][1] - 1)

            if (len(self.island_map)-1) < row or (
                        (len(self.island_map[0])-1) < col):
                raise ValueError("Position ({}, {}) does not exist on map".
                                 format(row, col))

            if self.island_map[row][col].animals_can_live_here():
                self.island_map[row][col].add_population(pop['pop'])
            else:
                raise ValueError("Animals can not live in position ({}, {})"
                                 .format(row, col))

    def food_growth_in_all_cells(self):
        """ Allows food to grow in all the cells on the island. """
        for row in self.island_map:
            for cell in row:
                cell.food_growth()

    def all_herb_eating(self):
        """ All herbivores on the island eats. """
        for row in self.island_map:
            for cell in row:
                cell.herb_eating()

    def all_carn_eating(self):
        """ All carnivores on the island eats. """
        for row in self.island_map:
            for cell in row:
                cell.carn_eating()

    def animals_give_birth(self):
        """ All animals on the island get the opportunity to give birth. """
        for row in self.island_map:
            for cell in row:
                cell.animal_birth()

    def randomize_cell_structure(self):
        """
        Randomizes the order of the cells on the island. Does not include
        coordinates of the outer edges of the island.

        :return: randomized list of class instances to the island cells
        """

        locations = [(row, col) for row in range(1, len(self.geogr) - 1)
                     for col in range(1, len(self.geogr[0]) - 1)]
        random.shuffle(locations)

        return [(self.island_map[loc[0]][loc[1]]) for loc in locations]

    def animals_migrate(self):
        """All animals on the island get an opportunity to migrate. """
        rnd_island = self.randomize_cell_structure()

        for cell in rnd_island:
            neighbours = self.get_neighbours(cell.neighbour_locations())
            cell.herb_migration(neighbours)
        for cell in rnd_island:
            cell.add_immigrants_to_pop()

        for cell in rnd_island:
            neighbours = self.get_neighbours(cell.neighbour_locations())
            cell.carn_migration(neighbours)
        for cell in rnd_island:
            cell.add_immigrants_to_pop()

    def get_neighbours(self, loc_neighbours):
        """
        Finds the class instances to the neighbouring cells.

        :param loc_neighbours: list of tuples with locations to all neighbour
                               cells
        :return: list of class instances to all neighbour cells
        """
        return [self.island_map[neighbour[0]][neighbour[1]]
                for neighbour in loc_neighbours]

    def all_animals_aging(self):
        """ All animals on the island get one year older. """
        for row in self.island_map:
            for cell in row:
                cell.animal_aging()

    def all_animals_lose_weight(self):
        """ All animals on the island loses weight. """
        for row in self.island_map:
            for cell in row:
                cell.animal_weight_change()

    def animals_die(self):
        """ Controls if any of the animals on the island dies. """
        for row in self.island_map:
            for cell in row:
                cell.animal_death()

    def annual_cycle(self):
        """Simulates one year on the island. """
        self.food_growth_in_all_cells()
        self.all_herb_eating()
        self.all_carn_eating()
        self.animals_give_birth()
        self.animals_migrate()
        self.all_animals_aging()
        self.all_animals_lose_weight()
        self.animals_die()

    def number_of_animals(self):
        """
        Counts number of herbivores and carnivores on the island.

        :return: number of herbivores and carnivores on the island
        """
        num_herbs = 0
        num_carns = 0

        for row in self.island_map:
            for cell in row:
                num_herbs += cell.total_num_animals(species='herbivore')
                num_carns += cell.total_num_animals(species='carnivore')
        return num_herbs, num_carns

    def num_herb_in_cells(self):
        """Returns array with number of herbivores in each cell. """
        herbivores = np.zeros((len(self.geogr), len(self.geogr[0])))

        for row in range(len(self.island_map)):
            for cell in range(len(self.island_map[row])):
                herbivores[row, cell] = (
                    self.island_map[row][cell].total_num_animals('herbivore'))
        return herbivores

    def num_carn_in_cells(self):
        """Returns array with number of carnivores in each cell. """
        carnivores = np.zeros((len(self.geogr), len(self.geogr[0])))

        for row in range(len(self.island_map)):
            for cell in range(len(self.island_map[row])):
                carnivores[row, cell] = (
                    self.island_map[row][cell].total_num_animals('carnivore'))
        return carnivores
