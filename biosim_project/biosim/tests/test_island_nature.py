# -*- coding: utf-8 -*-

"""
Tests for island class.
"""

import plmock
import nose.tools as nt
import numpy as np
from ..landscape import Jungle, Savannah, Desert, Mountain, Ocean, Landscape
from ..island_nature import Island
from ..animals import Carnivore, Herbivore

__authors__ = 'Elisabeth Flatner and Marie Klever'
__emails__ = 'elisabeth.flatner@nmbu.no, marie.klever@nmbu.no'


def test_no_island():
    """
    Testing that ValueError is raised when there are no cells in the island.
    """
    nt.assert_raises(ValueError, Island, """""")


def test_invalid_island_map():
    """Testing that all landscape types on map is valid.  """
    nt.assert_raises(ValueError, Island, """OOOOO
                                            OOJKL""")
    nt.assert_raises(ValueError, Island, """OOOOO
                                            OOJ
                                            S
                                            SSS""")
    nt.assert_raises(ValueError, Island, """OJO
                                            ODO
                                            OOO""")
    nt.assert_raises(ValueError, Island, """OOO
                                            OJJ
                                            OOO""")
    nt.assert_raises(ValueError, Island, """OOO
                                            SJO
                                            OOO""")
    nt.assert_raises(ValueError, Island, """OOO
                                            OJO
                                            OOM""")


def test_island_map():
    """Testing that island map is initialized correctly. """
    isl = Island("""OOOO
                    ODJO
                    OMSO
                    OOOO""")
    class_map = [[Ocean, Ocean, Ocean, Ocean],
                 [Ocean, Desert, Jungle, Ocean],
                 [Ocean, Mountain, Savannah, Ocean],
                 [Ocean, Ocean, Ocean, Ocean]]

    for row, rows in zip(isl.island_map, class_map):
        for col, cols in zip(row, rows):
            nt.assert_is_instance(col, cols,
                                  "Cell is not initialized correctly")


def test_location_does_not_exist():
    """
    Testing that ValueError is raised when location does not exist on map.
    """
    isl = Island("""OOOO
                    OOJO
                    OOOO""")
    pop = [{'loc': (5, 5), 'pop': [{'species': 'Carnivore',
                                    'age': 5, 'weight': 20},
                                   {'species': 'Carnivore',
                                    'age': 8, 'weight': 13},
                                   {'species': 'Herbivore',
                                    'age': 5, 'weight': 20}]}]
    print(len(isl.geogr))
    print(len(isl.geogr[0]))
    nt.assert_raises(ValueError, isl.place_animals, pop)


def test_animals_can_not_live_here():
    """
    Testing that ValueError is raised when animals can not live in location.
    """
    isl = Island("""OOOO
                    OOJO
                    OOOO""")
    pop = [{'loc': (1, 1), 'pop': [{'species': 'Carnivore',
                                    'age': 5, 'weight': 20},
                                   {'species': 'Carnivore',
                                    'age': 8, 'weight': 13},
                                   {'species': 'Herbivore',
                                    'age': 5, 'weight': 20}]}]

    nt.assert_raises(ValueError, isl.place_animals, pop)


class TestAnnualProcesses(object):
    """
    Collect tests that uses mock to count number of times a method is
    called.
    """

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """ Executed before each test in class to prepare for test. """
        self.copy_food_growth_landscape = Landscape.food_growth
        self.copy_food_growth_jungle = Jungle.food_growth
        self.copy_food_growth_savannah = Savannah.food_growth
        self.copy_herb_eating = Landscape.herb_eating
        self.copy_carn_eating = Landscape.carn_eating
        self.copy_animal_birth = Landscape.animal_birth
        self.copy_herb_migration = Landscape.herb_migration
        self.copy_carn_migration = Landscape.carn_migration
        self.copy_add_immigrants = Landscape.add_immigrants_to_pop
        self.copy_animal_aging = Landscape.animal_aging
        self.copy_animal_lose_weight = Landscape.animal_weight_change
        self.copy_animal_death = Landscape.animal_death

        self.map = """OOOOO
                      OJSMO
                      ODJOO
                      OOOOO"""
        self.num_calls = 20

    def teardown(self):
        """ Executed after each test in class to clean up."""
        Landscape.food_growth = self.copy_food_growth_landscape
        Jungle.food_growth = self.copy_food_growth_jungle
        Savannah.food_growth = self.copy_food_growth_savannah
        Landscape.herb_eating = self.copy_herb_eating
        Landscape.carn_eating = self.copy_carn_eating
        Landscape.animal_birth = self.copy_animal_birth
        Landscape.herb_migration = self.copy_herb_migration
        Landscape.carn_migration = self.copy_carn_migration
        Landscape.add_immigrants_to_pop = self.copy_add_immigrants
        Landscape.animal_aging = self.copy_animal_aging
        Landscape.animal_weight_change = self.copy_animal_lose_weight
        Landscape.animal_death = self.copy_animal_death

    def test_food_growth_landscape(self):
        """
        Testing that food_growth method is called a correct number of times for
        the landscape class.
        """
        food_growth_mocker = plmock.FixedValueMethodMocker()
        Landscape.food_growth = food_growth_mocker.get_method()

        island = Island(self.map)
        island.food_growth_in_all_cells()
        num_landscape = 17

        nt.assert_equal(num_landscape, food_growth_mocker.num_calls(),
                        "Food_growth method is called an incorrect number of "
                        "times for landscape")

    def test_food_growth_jungle(self):
        """
        Testing that food_growth method is called a correct number of times for
        the jungle class.
        """
        food_growth_mocker = plmock.FixedValueMethodMocker()
        Jungle.food_growth = food_growth_mocker.get_method()

        island = Island(self.map)
        island.food_growth_in_all_cells()
        num_jung = 2

        nt.assert_equal(num_jung, food_growth_mocker.num_calls(),
                        "Food_growth is called an incorrect number of times for"
                        "jungle")

    def test_food_growth_savannah(self):
        """
        Testing that food_growth method is called a correct number of times for
        the savannah class
        """
        food_growth_mocker = plmock.FixedValueMethodMocker()
        Savannah.food_growth = food_growth_mocker.get_method()

        island = Island(self.map)
        island.food_growth_in_all_cells()
        num_sav = 1

        nt.assert_equal(num_sav, food_growth_mocker.num_calls(),
                        "Food_growth is called an incorrect number of times for"
                        "savannah")

    def test_all_animals_aging(self):
        """
        Testing that animal_aging method is called a correct number of times.
        """
        aging_mocker = plmock.FixedValueMethodMocker()
        Landscape.animal_aging = aging_mocker.get_method()

        island = Island(self.map)
        island.all_animals_aging()

        nt.assert_equal(self.num_calls, aging_mocker.num_calls(),
                        "Animal_aging method is called an incorrect "
                        "number of times")

    def test_all_animals_lose_weight(self):
        """
        Testing that animal_weight_change method is called a correct number of
        times.
        """

        weight_mocker = plmock.FixedValueMethodMocker()
        Landscape.animal_weight_change = weight_mocker.get_method()

        island = Island(self.map)
        island.all_animals_lose_weight()

        nt.assert_equal(self.num_calls, weight_mocker.num_calls(),
                        "Animal_weight_change method is called an incorrect "
                        "number of times")

    def test_all_herb_eating(self):
        """
        Testing that herb_eating method is called a correct number of times.
        """

        herb_eat_mocker = plmock.FixedValueMethodMocker()
        Landscape.herb_eating = herb_eat_mocker.get_method()

        island = Island(self.map)
        island.all_herb_eating()

        nt.assert_equal(self.num_calls, herb_eat_mocker.num_calls(),
                        "Herb_eating method is called an incorrect number of "
                        "times")

    def test_all_carn_eating(self):
        """
        Testing that carn_eating method is called a correct number of times.
        """

        carn_eat_mocker = plmock.FixedValueMethodMocker()
        Landscape.carn_eating = carn_eat_mocker.get_method()

        island = Island(self.map)
        island.all_carn_eating()

        nt.assert_equal(self.num_calls, carn_eat_mocker.num_calls(),
                        "Carn_eating method is called an incorrect number of "
                        "times")

    def test_all_animals_give_birth(self):
        """
        Testing that animal_birth method is called a correct number of times.
        """

        animal_birth_mocker = plmock.FixedValueMethodMocker()
        Landscape.animal_birth = animal_birth_mocker.get_method()

        island = Island(self.map)
        island.animals_give_birth()

        nt.assert_equal(self.num_calls, animal_birth_mocker.num_calls(),
                        "Animal_birth method is called an incorrect number of "
                        "times")

    def test_animals_migrate(self):
        """
        Testing that methods connected to animals migrate are called a
        correct number of times.
        """
        herb_migrate_mocker = plmock.FixedValueMethodMocker()
        Landscape.herb_migration = herb_migrate_mocker.get_method()
        carn_migrate_mocker = plmock.FixedValueMethodMocker()
        Landscape.carn_migration = carn_migrate_mocker.get_method()
        immigrants_mocker = plmock.FixedValueMethodMocker()
        Landscape.add_immigrants_to_pop = immigrants_mocker.get_method()

        isl = Island(self.map)
        isl.animals_migrate()

        nt.assert_equal(6, herb_migrate_mocker.num_calls(),
                        "Herb_migration method is called an incorrect number "
                        "of times")
        nt.assert_equal(6, carn_migrate_mocker.num_calls(),
                        "Carn_migration method is called an incorrect number "
                        "of times")
        nt.assert_equal(12, immigrants_mocker.num_calls(),
                        "Add_immigrants_to_pop method is called an incorrect "
                        "number of times")

    def test_animal_dies(self):
        """
        Testing that animal_death method is called a correct number of times.
        """

        animal_death_mocker = plmock.FixedValueMethodMocker()
        Landscape.animal_death = animal_death_mocker.get_method()

        island = Island(self.map)
        island.animals_die()

        nt.assert_equal(self.num_calls, animal_death_mocker.num_calls(),
                        "Animal_death method is called an incorrect number of "
                        "times")


def test_randomize_cell_structure():
    """
    Testing that cells at the edge of the map is not included in the returned
    list of randomized cells.
    """
    map_one = """OOOOO
                 OJSMO
                 ODJOO
                 OOOOO"""

    island_one = Island(map_one)
    nt.assert_equal(6, len(island_one.randomize_cell_structure()),
                    "Wrong length of returned list")
    map_two = """OO
                 OO"""

    island_two = Island(map_two)
    nt.assert_equal(0, len(island_two.randomize_cell_structure()),
                    "Wrong length of returned list")
    nt.assert_list_equal([], island_two.randomize_cell_structure(),
                         "Wrong list returned")


def test_get_neighbours():
    """Testing that list of correct neighbour classes is returned. """
    island_map = """OOOOO
                    OJSMO
                    ODJOO
                    OOOOO"""

    island = Island(island_map)
    neighbours = [island.island_map[1][2], island.island_map[2][3],
                  island.island_map[3][2], island.island_map[2][1]]
    neighbour_loc = [(1, 2), (2, 3), (3, 2), (2, 1)]
    nt.assert_list_equal(neighbours, island.get_neighbours(neighbour_loc),
                         "Returns wrong list of neighbours")


class TestPopulation(object):
    """ Collects tests that changes default parameters. """

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """ Executed before each test in class to prepare for test. """
        self.copy_params_herb = Herbivore.params
        self.copy_params_carn = Carnivore.params
        self.copy_prob_carn_kill = Carnivore.prob_kill
        self.map_one = """OOOOO
                          OJSMO
                          ODJJO
                          OOOOO"""
        self.pop = [{'loc': (3, 3), 'pop': [{'species': 'Herbivore',
                                             'age': 5, 'weight': 20},
                                            {'species': 'Herbivore',
                                             'age': 8, 'weight': 13},
                                            {'species': 'Carnivore',
                                             'age': 5, 'weight': 20}]},
                    {'loc': (2, 3), 'pop': [{'species': 'Herbivore',
                                             'age': 7, 'weight': 22},
                                            {'species': 'Herbivore',
                                             'age': 9, 'weight': 13},
                                            {'species': 'Herbivore',
                                             'age': 9, 'weight': 18}]},
                    {'loc': (2, 2), 'pop': [{'species': 'Carnivore',
                                             'age': 12, 'weight': 20},
                                            {'species': 'Carnivore',
                                             'age': 5, 'weight': 12},
                                            {'species': 'Carnivore',
                                             'age': 6, 'weight': 24}]}
                    ]

    def teardown(self):
        """ Executed after each test in class to clean up."""
        Herbivore.params = self.copy_params_herb
        Carnivore.params = self.copy_params_carn
        Carnivore.prob_kill = self.copy_prob_carn_kill

    def test_place_animals(self):
        """Testing that animals are placed in correct location. """
        isl = Island(self.map_one)
        isl.place_animals(self.pop)

        num_herb = [[0, 0, 0, 0, 0], [0, 0, 3, 0, 0], [0, 0, 2, 0, 0],
                    [0, 0, 0, 0, 0]]
        num_carn = [[0, 0, 0, 0, 0], [0, 3, 0, 0, 0], [0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0]]

        for row, rows in zip(isl.island_map, num_herb):
            for cell, num in zip(row, rows):
                nt.assert_equal(num, len(cell.herb),
                                "Herbivores placed in wrong location")

        for row, rows in zip(isl.island_map, num_carn):
            for cell, num in zip(row, rows):
                nt.assert_equal(num, len(cell.carn),
                                "Carnivores placed in wrong location")

    def test_constant_population(self):
        """
        Testing that no animals get lost when simulating migration.

        Sets parameter gamma and omega so that no animals give birth or die.
        """
        Herbivore.set_parameters({'gamma': 0, 'omega': 0})
        Carnivore.set_parameters({'gamma': 0, 'omega': 0})
        Carnivore.prob_kill = lambda _, __: 0

        island = Island(self.map_one)
        island.place_animals(self.pop)
        num_herb, num_carn = island.number_of_animals()

        for year in range(100):
            island.annual_cycle()

        num_herb_after, num_carn_after = island.number_of_animals()
        nt.assert_equal(num_herb, num_herb_after,
                        "Number of herbivores is not constant")
        nt.assert_equal(num_carn, num_carn_after,
                        "Number of carnivores is not constant")

    def test_number_of_animals(self):
        """Testing that method counts number of animals on island correctly. """

        isl = Island(self.map_one)
        isl.place_animals(self.pop)
        herb, carn = isl.number_of_animals()
        nt.assert_equal(5, herb, "Number of herbivores on island is incorrect")
        nt.assert_equal(4, carn, "Number of carnivores on island is incorrect")

    def test_num_herb_in_cell(self):
        """
        Testing that method returns array with number of herbivores in each
        cell.
        """
        herbivores = np.array([[0, 0, 0, 0, 0],
                               [0, 0, 3, 0, 0],
                               [0, 0, 2, 0, 0],
                               [0, 0, 0, 0, 0]])
        isl = Island(self.map_one)
        isl.place_animals(self.pop)
        nt.assert_true((herbivores == isl.num_herb_in_cells()).all(),
                       "Returns wrong array of number of herbivores in each "
                       "cell")

    def test_num_carn_in_cell(self):
        """
        Testing that method returns array with number of carnivores in each
        cell.
        """
        carnivores = np.array([[0, 0, 0, 0, 0],
                               [0, 3, 0, 0, 0],
                               [0, 0, 1, 0, 0],
                               [0, 0, 0, 0, 0]])
        isl = Island(self.map_one)
        isl.place_animals(self.pop)
        nt.assert_true((carnivores == isl.num_carn_in_cells()).all(),
                       "Returns wrong array of number of carnivores in each "
                       "cell")
