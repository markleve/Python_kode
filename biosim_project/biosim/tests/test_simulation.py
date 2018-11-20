# -*- coding: utf-8 -*-

"""
Test for methods in BioSim class in simulation file.
"""
import nose.tools as nt
import numpy as np
from ..simulation import BioSim

__authors__ = 'Elisabeth Flatner and Marie Klever'
__emails__ = 'elisabeth.flatner@nmbu.no, marie.klever@nmbu.no'


class TestSimulation(object):
    """Collects tests that have the same input values. """

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """ Executed before each test in class to prepare for test. """
        self.map_one = """OOOOO
                          OJSMO
                          ODJJO
                          OOOOO"""

        self.ini_pop = [{'loc': (3, 3), 'pop': [{'species': 'Herbivore',
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

        self.new_pop = [{'loc': (3, 3), 'pop': [{'species': 'Carnivore',
                                                 'age': 5, 'weight': 20},
                                                {'species': 'Carnivore',
                                                 'age': 8, 'weight': 13},
                                                {'species': 'Carnivore',
                                                 'age': 5, 'weight': 20}]},
                        {'loc': (2, 3), 'pop': [{'species': 'Herbivore',
                                                 'age': 7, 'weight': 22},
                                                {'species': 'Herbivore',
                                                 'age': 9, 'weight': 13},
                                                {'species': 'Herbivore',
                                                 'age': 9, 'weight': 18}]}
                        ]

    def test_num_years(self):
        """Testing that method returns correct number of years. """
        sim = BioSim(self.map_one, self.ini_pop, 123456)
        sim.simulate(num_steps=5, vis_steps=100, img_steps=2000)
        nt.assert_equal(5, sim._step, "Returns wrong number of years")

    def test_total_num_animals(self):
        """Testing that method returns correct number of animals. """
        sim = BioSim(self.map_one, self.ini_pop, 123456)
        nt.assert_equal(9, sim.total_num_animals(),
                        "Returns wrong number of animals")

    def test_total_num_by_species(self):
        """
        Testing that correct dictionary with total number of herbivores and
        carnivores is returned.
        """
        sim = BioSim(self.map_one, self.ini_pop, 123456)
        nt.assert_dict_equal({'herbivores': 5, 'carnivores': 4},
                             sim.total_num_by_species(),
                             "Returns wrong dictionary of herbivores and "
                             "carnivores")

    def test_total_animals_by_cell(self):
        """
        Testing that correct array of total number of herbivores and
        carnivores is returned.
        """
        sim = BioSim(self.map_one, self.ini_pop, 123456)
        carnivores = np.array([[0, 0, 0, 0, 0],
                               [0, 3, 0, 0, 0],
                               [0, 0, 1, 0, 0],
                               [0, 0, 0, 0, 0]])
        herbivores = np.array([[0, 0, 0, 0, 0],
                               [0, 0, 3, 0, 0],
                               [0, 0, 2, 0, 0],
                               [0, 0, 0, 0, 0]])

        res = sim.num_animals_per_cell()
        nt.assert_true((herbivores == res['herbivores']).all(),
                       "Returns wrong array of number of herbivores")
        nt.assert_true((carnivores == res['carnivores']).all(),
                       "Returns wrong array of number of carnivores")
