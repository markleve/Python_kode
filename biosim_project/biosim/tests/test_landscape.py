# -*-coding: utf-8 -*-

"""
Tests for landscape class with subclasses.
"""

import nose.tools as nt
import math
import random
# plmock is a file with mockfunctions for mocktesting,
# created by Hans Ekkehard Plesser
import plmock
from ..animals import Herbivore, Carnivore, Animal
from ..landscape import Jungle, Savannah, Desert, Mountain, Ocean

__authors__ = 'Elisabeth Flatner and Marie Klever'
__emails__ = 'elisabeth.flatner@nmbu.no, marie.klever@nmbu.no'


class TestParams(object):
    """ Collects test that uses different parameters than default. """

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """ Executed before each test in class to prepare for test. """
        self.copy_params = Savannah.params.copy()

    def teardown(self):
        """ Executed after each test in class to clean up."""
        Savannah.params = self.copy_params

    @staticmethod
    def test_set_parameters_error():
        """
        Testing that ValueError is raised when invalid parameters is given.
        """
        jung = Jungle()
        nt.assert_raises(ValueError, jung.set_parameters, {'alpha': 4})

        sav = Savannah()
        nt.assert_raises(ValueError, sav.set_parameters,
                         {'alpha': 0.4, 'fmax': -2})

        nt.assert_raises(ValueError, sav.set_parameters, {'alpha': 1.2})

    @staticmethod
    def test_set_parameters():
        """ Testing that parameters are updated correctly. """
        sav = Savannah()
        sav.set_parameters({'alpha': 0.6})
        nt.assert_equal(0.6, Savannah.params['alpha'],
                        "Parameters are not updated correctly")

    @staticmethod
    def test_reduce_available_food():
        """
        Testing that available food is updated correctly when food is eaten.
        """
        jung = Jungle()
        jung.reduce_available(200)
        nt.assert_equal(600, jung.available_food,
                        "Available food is updated incorrectly")


def test_fitness_sorting():
    """ Testing that method fitness_sorting sorts list correctly. """
    pop = [{'species': 'Herbivore', 'weight': 20, 'age': 100},
           {'species': 'Herbivore', 'weight': 20, 'age': 0},
           {'species': 'Carnivore', 'weight': 5, 'age': 80},
           {'species': 'Carnivore', 'weight': 16, 'age': 12},
           {'species': 'carnivore', 'weight': 20, 'age': 10}]

    jung = Jungle()
    jung.add_population(pop)
    herb_one, herb_two = jung.herb[0], jung.herb[1]
    carn_one, carn_two, carn_three = jung.carn[0], jung.carn[1], jung.carn[2]

    jung.fitness_sorting(herb_descending=True)
    nt.assert_list_equal([herb_two, herb_one], jung.herb,
                         "Herbivores are not sorted correctly")

    jung.fitness_sorting(herb_descending=False)
    nt.assert_list_equal([herb_one, herb_two], jung.herb,
                         "Herbivores are not sorted correctly")

    nt.assert_list_equal([carn_three, carn_two, carn_one], jung.carn,
                         "Carnivores are not sorted correctly")


def test_num_herb():
    """
    Testing that method num_herbivores returns the correct number of herbivores.
    """
    jung = Jungle()
    jung.add_population([{'species': 'Herbivore', 'weight': 14, 'age': 0},
                         {'species': 'Herbivore', 'weight': 54, 'age': 0},
                         {'species': 'Carnivore', 'weight': 20, 'age': 13}])
    nt.assert_equal(2, jung.total_num_animals(species='herbivore'),
                    "Wrong number of herbivores")


def test_num_carn():
    """
    Testing that method num_carnivores returns the correct number of carnivores.
    """
    jung = Jungle()
    jung.add_population([{'species': 'Herbivore', 'weight': 14, 'age': 0},
                         {'species': 'Herbivore', 'weight': 54, 'age': 0},
                         {'species': 'Carnivore', 'weight': 20, 'age': 13}])
    nt.assert_equal(1, jung.total_num_animals(species='carnivore'),
                    "Wrong number of carnivores")


def test_num_unknown_species():
    """
    Testing that ValueError is raised when an invalid species is asked for.
    """
    jung = Jungle()
    nt.assert_raises(ValueError, jung.total_num_animals, species='Zebra')


def test_animal_aging():
    """ Testing that all animals getting older using mock tests. """
    age_mocker = plmock.FixedValueMethodMocker()
    Animal.aging = age_mocker.get_method()

    jung = Jungle()
    jung.add_population([{'species': 'Herbivore', 'weight': 14, 'age': 0},
                         {'species': 'Herbivore', 'weight': 54, 'age': 0},
                         {'species': 'Carnivore', 'weight': 20, 'age': 13}])
    jung.animal_aging()

    nt.assert_equal(3, age_mocker.num_calls(),
                    "Aging method called a wrong number of times")


def test_weight_change():
    """ Testing that all animals loose weight using mock tests. """

    weight_mocker = plmock.FixedValueMethodMocker()
    Animal.weight_change = weight_mocker.get_method()

    sav = Savannah()
    sav.add_population([{'species': 'Herbivore', 'weight': 14, 'age': 0},
                        {'species': 'Herbivore', 'weight': 54, 'age': 0},
                        {'species': 'Carnivore', 'weight': 20, 'age': 13}])
    num_w = 3
    sav.animal_weight_change()

    nt.assert_equal(num_w, weight_mocker.num_calls(),
                    "Weight_change method called a wrong number of times")


class TestNewborns(object):
    """ Collects test that allows us to override animal.birth methods. """

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """ Executed before each test in class to prepare for test. """
        self.sav = Savannah()
        self.sav.add_population([
            {'species': 'Herbivore', 'weight': 14, 'age': 0},
            {'species': 'Herbivore', 'weight': 54, 'age': 0},
            {'species': 'Carnivore', 'weight': 20, 'age': 13},
            {'species': 'Carnivore', 'weight': 54, 'age': 0}])
        self.copy_animal_birth = Animal.birth

    def teardown(self):
        """ Executed after each test in class to clean up."""
        Animal.birth = self.copy_animal_birth

    def test_newborn_zero(self):
        """
        Testing that no animal gives birth.

        Forces Animal.birth to return None resulting in no animals born.
        """
        Animal.birth = lambda _, __: None
        nt.assert_equal([], self.sav.newborns(self.sav.herb),
                        "Newborn should not exist")

    def test_newborns(self):
        """
        Testing that animal is born.

        Forces Animal.birth to return a new animal with a given class instance.
        """
        new_animal = Animal(5)
        Animal.birth = lambda _, __: new_animal
        nt.assert_equal([new_animal, new_animal],
                        self.sav.newborns(self.sav.carn),
                        " Wrong list of newborns ")

    def test_animal_birth(self):
        """
        Testing the list of animals is updated with the newborn animals.

        Forces Animal.birth to return a new animal with a given class instance.
        """
        new_animal = Animal(5)
        Animal.birth = lambda _, __: new_animal
        herb = self.sav.herb + [new_animal, new_animal]
        carn = self.sav.carn + [new_animal, new_animal]
        self.sav.animal_birth()
        nt.assert_list_equal(herb, self.sav.herb,
                             "List of herbivores updated incorrectly")
        nt.assert_list_equal(carn, self.sav.carn,
                             "List of carnivores updated incorrectly")


def test_newborns_call():
    """
    Testing that all animals get the chance to procreate using mock tests.
    """
    newborn_mock = plmock.FixedValueMethodMocker()
    Animal.birth = newborn_mock.get_method()

    jung = Jungle()
    jung.add_population([{'species': 'Herbivore', 'weight': 14, 'age': 0},
                        {'species': 'Herbivore', 'weight': 54, 'age': 0},
                        {'species': 'Carnivore', 'weight': 20, 'age': 13}])

    jung.newborns(jung.herb)
    jung.newborns(jung.carn)

    nt.assert_equal(3, newborn_mock.num_calls(),
                    "Birth method called wrong number of times")


class TestAnimalDeath(object):
    """ Collects test that allows us to override animal.death method. """

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """ Executed before each test in class to prepare for test. """
        self.jung = Jungle()
        self.jung.add_population([
            {'species': 'Herbivore', 'weight': 14, 'age': 0},
            {'species': 'Herbivore', 'weight': 54, 'age': 0},
            {'species': 'Carnivore', 'weight': 20, 'age': 13},
            {'species': 'Carnivore', 'weight': 54, 'age': 0}])
        self.copy_animal_death = Animal.death

    def teardown(self):
        """ Executed after each test in class to clean up."""
        Animal.death = self.copy_animal_death

    def test_all_animal_dies(self):
        """Testing that animals are updated correctly if all animal dies. """
        Animal.death = lambda _: True
        self.jung.animal_death()
        nt.assert_list_equal([], self.jung.herb,
                             "List of surviving herbivores updated incorrectly")
        nt.assert_list_equal([], self.jung.carn,
                             "List of surviving carnivores updated incorrectly")

    def test_all_animal_survive(self):
        """Testing that animals are updated correctly if no animal dies. """
        Animal.death = lambda _: None
        herb = self.jung.herb
        carn = self.jung.carn
        self.jung.animal_death()
        nt.assert_list_equal(herb, self.jung.herb,
                             "List of surviving herbivores updated incorrectly")
        nt.assert_list_equal(carn, self.jung.carn,
                             "List of surviving carnivores updated incorrectly")


def test_jungle():
    """
    Testing that food_growth method updates available_food in the jungle
    correctly.
    """
    jung = Jungle()
    jung.add_population([{'species': 'Herbivore', 'weight': 14, 'age': 0},
                         {'species': 'Carnivore', 'weight': 20, 'age': 13},
                         {'species': 'Carnivore', 'weight': 54, 'age': 0}])

    jung.reduce_available(600)
    jung.food_growth()
    nt.assert_equal(800, jung.available_food,
                    "Available food is updated incorrectly")


def test_savannah():
    """
    Testing that food_growth method updates available_food in the savannah
    correctly.
    """
    sav = Savannah()
    sav.add_population([{'species': 'Herbivore', 'weight': 14, 'age': 0},
                        {'species': 'Herbivore', 'weight': 54, 'age': 0},
                        {'species': 'Carnivore', 'weight': 20, 'age': 13}])

    sav.reduce_available(50)
    sav.food_growth()
    nt.assert_equal(265, sav.available_food,
                    "Available food is updated incorrectly")


def test_landscape_with_no_food():
    """
    Testing that food_growth returnes None for landscape that has no fodder that
    can grow.
    """
    nt.assert_is_none(Desert().food_growth(), "No food can grow in the desert")
    nt.assert_is_none(Mountain().food_growth(),
                      "No food can grow on the mountains")
    nt.assert_is_none(Ocean().food_growth(), "No food can grow in the ocean")


class TestHerbEating(object):
    """ Collects test that allows us to reset jungle params. """

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """ Executed before each test in class to prepare for test. """
        self.copy_jungle_params = Jungle.params.copy()
        self.orig_reduce_available = Jungle.reduce_available

    def teardown(self):
        """ Executed after each test in class to clean up."""
        Jungle.params = self.copy_jungle_params
        Jungle.reduce_available = self.orig_reduce_available

    @staticmethod
    def test_no_food():
        """
        Testing that herb.eating() is called the correct number of times when
        there is no food for the herbivores.
        """
        reduce_mock = plmock.FixedValueMethodMocker()
        Jungle.reduce_available = reduce_mock.get_method()

        Jungle.set_parameters({'fmax': 0})
        jung = Jungle()
        jung.add_population([{'species': 'Herbivore', 'weight': 14, 'age': 0},
                             {'species': 'Herbivore', 'weight': 54, 'age': 0},
                             {'species': 'Herbivore', 'weight': 54, 'age': 12}])

        jung.herb_eating()
        nt.assert_equal(0, reduce_mock.num_calls())

    @staticmethod
    def test_herb_eating():
        """ Testing that the method herb_eating works as it should. """
        Jungle.set_parameters({'fmax': 5})

        jung = Jungle()
        jung.add_population([{'species': 'Herbivore', 'weight': 8, 'age': 0},
                            {'species': 'Herbivore', 'weight': 78, 'age': 9}])
        herb_one, herb_two = jung.herb[0], jung.herb[1]
        jung.herb_eating()

        nt.assert_equal(82.5, herb_two.weight_of_animal(),
                        "Weight gain is wrong for the herbivore who ate")
        nt.assert_equal(8, herb_one.weight_of_animal(),
                        "Weight gain is wrong for the herbivore who ate")
        nt.assert_equal(0, jung.available_food,
                        "Available food is updated incorrectly")

        sav = Savannah()
        sav.add_population([{'species': 'Herbivore', 'weight': 9, 'age': 0}])
        sav.herb_eating()

        nt.assert_equal(18, sav.herb[0].weight_of_animal(),
                        "Weight gain is wrong for the herbivore who ate")
        nt.assert_equal(290, sav.available_food,
                        "Available food is updated incorrectly")

        des = Desert()
        des.add_population([{'species': 'Herbivore', 'weight': 6, 'age': 0}])
        des.herb_eating()

        nt.assert_equal(6, des.herb[0].weight_of_animal(),
                        "Weight gain is wrong for the herbivore who ate")
        nt.assert_equal(0, des.available_food,
                        "Available food is updated incorrectly")


def test_no_carn_eating():
    """
    Test that no herbivore are eaten when the carnivores fitness is lower than
    the herbivores.
    """
    sav = Savannah()

    sav.add_population([{'species': 'Herbivore', 'weight': 9, 'age': 0},
                        {'species': 'Herbivore', 'weight': 7, 'age': 0},
                        {'species': 'Carnivore', 'weight': 87, 'age': 554},
                        {'species': 'Carnivore', 'weight': 78, 'age': 879}])
    herb_one, herb_two = sav.herb[0], sav.herb[1]
    sav.carn_eating()

    nt.assert_list_equal([herb_two, herb_one], sav.herb,
                         "Number of herbivores updated incorrectly after "
                         "carnivore eating")


class TestCarnEating(object):
    """ Collects test that overrides methods in carn eating. """

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """ Executed before each test in class to prepare for test. """
        self.orig_carn_eating = Carnivore.eating
        self.copy_prob_kill = Carnivore.prob_kill

    def teardown(self):
        """ Executed after each test in class to clean up."""
        Carnivore.eating = self.orig_carn_eating
        Carnivore.prob_kill = self.copy_prob_kill

    @staticmethod
    def test_no_carn_eating_when_no_herb():
        """
        Test that carn.eating is not called when there is no herbivores to eat.
        """
        eat_mock = plmock.FixedValueMethodMocker()
        Carnivore.eating = eat_mock.get_method()

        jung = Jungle()
        jung.add_population([{'species': 'Carnivore', 'weight': 9, 'age': 0}])
        jung.carn_eating()
        nt.assert_equal(0, eat_mock.num_calls(),
                        "Eating method called wrong number of times")

    @staticmethod
    def test_no_carn_eating_when_low_fitness():
        """
        Test that carn.eating is not called when the carnivores have lower
        fitness than the herbivores.
        """
        eat_mock = plmock.FixedValueMethodMocker()
        Carnivore.eating = eat_mock.get_method()

        sav = Savannah()
        sav.add_population([{'species': 'Herbivore', 'weight': 7, 'age': 0},
                            {'species': 'Herbivore', 'weight': 9, 'age': 0},
                            {'species': 'Carnivore', 'weight': 87, 'age': 554},
                            {'species': 'Carnivore', 'weight': 78, 'age': 879}])

        sav.carn_eating()
        nt.assert_equal(0, eat_mock.num_calls(),
                        "Eating method called wrong number of times")

    @staticmethod
    def test_carn_eating():
        """ Testing that carn_eating works correctly. """
        Carnivore.prob_kill = lambda _, __: 1

        des = Desert()
        des.add_population([{'species': 'Herbivore', 'weight': 98, 'age': 70},
                            {'species': 'Herbivore', 'weight': 78, 'age': 90},
                            {'species': 'Carnivore', 'weight': 7, 'age': 0}])
        herb_two = des.herb[0]
        carn_one = des.carn[0]
        des.carn_eating()

        nt.assert_list_equal([herb_two], des.herb,
                             "List of herbivores updated incorrectly after "
                             "carnivores ate")
        nt.assert_equal(44.5, carn_one.weight_of_animal(),
                        "Weight gain is wrong for the carnivore who ate")


def test_neighbor_locations():
    """Testing that correct positions of neighboring cells are returned. """
    des = Desert((2, 4))

    nt.assert_list_equal([(1, 4), (2, 5), (3, 4), (2, 3)],
                         des.neighbour_locations(),
                         "Returns wrong locations for neighboring cells")


class TestMigration(object):
    """Collect tests that allows us to override methods. """

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """ Executed before each test in class to prepare for test. """
        self.copy_animal_prob_migration = Animal.prob_migration
        self.pop = [{'species': 'Herbivore', 'weight': 14, 'age': 0},
                    {'species': 'Herbivore', 'weight': 54, 'age': 0},
                    {'species': 'Carnivore', 'weight': 87, 'age': 0},
                    {'species': 'Carnivore', 'weight': 25, 'age': 0}]

    def teardown(self):
        """ Executed after each test in class to clean up."""
        Animal.prob_migration = self.copy_animal_prob_migration

    def test_all_migrate(self):
        """
        Testing that all animals moves when the probability to move is 100 %.
        """
        Animal.prob_migration = lambda _: 1
        sav = Savannah()
        sav.add_population(self.pop)

        sav.herb_migration([Savannah(), Jungle(), Mountain(), Savannah()])
        nt.assert_list_equal([], sav.herb,
                             "Remaining herbivores updated incorrectly")

        sav.carn_migration([Savannah(), Jungle(), Mountain(), Savannah()])
        nt.assert_list_equal([], sav.carn,
                             "Remaining carnivores updated incorrectly")

    def test_no_to_ocean_and_mountain(self):
        """
        Testing that no animals move to ocean and mountain when probability to
        move is 100 %.
        """
        Animal.prob_migration = lambda _: 1
        jung = Jungle()
        jung.add_population(self.pop)
        herb_one, herb_two = jung.herb[0], jung.herb[1]
        carn_one, carn_two = jung.carn[0], jung.carn[1]

        jung.herb_migration([Ocean(), Mountain(), Ocean(), Mountain()])
        nt.assert_list_equal([herb_one, herb_two], jung.herb,
                             "Remaining herbivores updated incorrectly")

        jung.carn_migration([Ocean(), Mountain(), Ocean(), Mountain()])
        nt.assert_list_equal([carn_one, carn_two], jung.carn,
                             "Remaining carnivores updated incorrectly")

    def test_no_migration(self):
        """
        Testing that no animal migrates when probability to migrate is zero.
        """
        Animal.prob_migration = lambda _: 0
        sav = Savannah()
        sav.add_population(self.pop)

        herb_one, herb_two = sav.herb[0], sav.herb[1]
        carn_one, carn_two = sav.carn[0], sav.carn[1]

        sav.herb_migration([Jungle(), Jungle(), Desert(), Mountain()])
        nt.assert_list_equal([herb_one, herb_two], sav.herb,
                             "Remaining herbivores updated incorrectly")

        sav.carn_migration([Jungle(), Jungle(), Desert(), Mountain()])
        nt.assert_list_equal([carn_one, carn_two], sav.carn,
                             "Remaining carnivores updated incorrectly")


def test_prob_move():
    """
    Testing that method returns correct values of probability to move.
    """
    jung = Jungle()
    jung.propensity = lambda _, __, ___: [0, 0, 0, 0]
    neig = [Ocean(), Mountain(), Ocean(), Mountain()]
    nt.assert_list_equal([0, 0, 0, 0],
                         jung.prob_move(neig, Herbivore(2, 3), 'herbivore'),
                         "Returns wrong list of probability to move")


def test_animals_can_live_here():
    """Testing the method returns correct boolean expression. """
    nt.assert_true(Jungle().animals_can_live_here(),
                   "Animals can live in the Jungle ")
    nt.assert_true(Savannah().animals_can_live_here(),
                   "Animals can live in the Savannah")
    nt.assert_true(Desert().animals_can_live_here(),
                   "Animals can live in the Desert")
    nt.assert_false(Mountain().animals_can_live_here(),
                    "Animals can´t live in the Mountain")
    nt.assert_false(Ocean().animals_can_live_here(),
                    "Animals can´t live in the Ocean")


def test_get_available_fodder():
    """Testing that a given species get correct available fodder. """
    jung = Jungle()
    jung.add_population([{'species': 'Herbivore', 'weight': 3, 'age': 5},
                         {'species': 'Herbivore', 'weight': 32, 'age': 5},
                         {'species': 'Carnivore', 'weight': 32, 'age': 5},
                         {'species': 'Carnivore', 'weight': 23, 'age': 31}])

    nt.assert_equal(800, jung.get_available_fodder('herbivore'),
                    "Returns the wrong amount of available fodder")
    nt.assert_equal(35, jung.get_available_fodder('carnivore'),
                    "Returns the wrong amount of available fodder")
    nt.assert_raises(ValueError, jung.get_available_fodder, 'zebra')


def test_relative_abundance_of_fodder():
    """Testing that method returns correct values for all neighbours."""
    jung = Jungle()
    sav = Savannah()
    oce = Ocean()
    mount = Mountain()
    des = Desert()

    pop = [{'species': 'Herbivore', 'weight': 32, 'age': 54},
           {'species': 'Herbivore', 'weight': 2, 'age': 43},
           {'species': 'Carnivore', 'weight': 32, 'age': 5},
           {'species': 'Carnivore', 'weight': 3, 'age': 54}]
    jung.add_population(pop)
    sav.add_population(pop)

    nt.assert_list_equal([80./3, 10, 0, 0], des.relative_abundance_of_fodder(
        [jung, sav, oce, mount], animal=Herbivore(2, 3), species='herbivore'),
                         "Returns wrong list of available fodder")
    nt.assert_list_equal([34./150, 34./150, 0, 0],
                         des.relative_abundance_of_fodder(
                             [jung, sav, oce, mount], animal=Carnivore(2, 3),
                             species='carnivore'),
                         "Returns wrong list of available fodder")


def test_propensity():
    """Testing that method returns correct values of propensity."""
    neig = [Ocean(), Mountain(), Desert(), Jungle()]
    ek = [0.32, 0.43, 0.54, 0.2]
    sav = Savannah()
    nt.assert_list_equal([0, 0, math.exp(0.54), math.exp(0.2)],
                         sav.propensity(neig, Herbivore(2, 3), ek),
                         "Returns wrong list of propensity")


class TestAnimalMovesTo(object):
    """ Collects test that override random.random method. """

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """ Executed before each test in class to prepare for test. """
        self.orig_random_random = random.random

    def teardown(self):
        """ Executed after each test in class to clean up."""
        random.random = self.orig_random_random

    @staticmethod
    def test_animal_moves_to():
        """Testing that method returns correct position of neighbour. """

        # Source: test_sims_stats.py in L13 INF200, stat_tests, ransim
        # created by Hans Ekkehard Plesser, NMBU
        rnd_and_result = ((0.1, 0), (0.25, 1), (0.4, 1), (0.8, 2), (0.84, 3),
                          (0.99, 3))

        rnd_num, expected_results = zip(*rnd_and_result)
        random.random = plmock.FuncReturningValueSequence(rnd_num)
        jung = Jungle()
        results = [jung.animal_moves_to([0.25, 0.18, 0.4, 0.17]) for _ in
                   rnd_and_result]
        print(results)
        nt.assert_equal(results, list(expected_results))


def test_add_herb_immigrants():
    """Testing that herbivore immigrant is added to immigrants in cell. """
    jung = Jungle()
    herb_one = Herbivore(2, 3)

    jung.add_herb_immigrant(herb_one)
    nt.assert_list_equal([herb_one], jung.herb_immigrants,
                         "Did not add immigrant to list of immigrants")


def test_add_carn_immigrants():
    """Testing that carnivore immigrant is added to immigrants in cell. """
    des = Desert()
    carn_one = Carnivore(7)
    des.add_carn_immigrant(carn_one)
    nt.assert_list_equal([carn_one], des.carn_immigrants,
                         "Did not ass immigrant to list of immigrants")


def test_add_immigrants_to_pop():
    """Testing that immigrants are added to population. """
    sav = Savannah()

    herb_immi = Herbivore(2, 3)

    ini_pop = [{'species': 'Herbivore', 'weight': 3, 'age': 4},
               {'species': 'Herbivore', 'weight': 2, 'age': 3},
               {'species': 'Carnivore', 'weight': 8, 'age': 90}]

    sav.add_population(ini_pop)
    herb_one, herb_two = sav.herb[0], sav.herb[1]
    carn_one = sav.carn[0]

    sav.add_herb_immigrant(herb_immi)
    sav.add_immigrants_to_pop()

    nt.assert_list_equal([herb_one, herb_two, herb_immi], sav.herb,
                         "Did not add immigrants to existing population")

    carn_immi_one, carn_immi_two = Carnivore(87, 75), Carnivore(8, 6)
    carn_immigrants = [carn_immi_one, carn_immi_two]

    for carn in carn_immigrants:
        sav.add_carn_immigrant(carn)
    sav.add_immigrants_to_pop()

    nt.assert_list_equal([carn_one] + carn_immigrants, sav.carn,
                         "Did not add immigrants to existing population")


def test_add_population():
    """
    Testing that class instances is created for new animals and that new
    animals are added to existing population.
    """
    pop = [{'species': 'Herbivore', 'weight': 3, 'age': 4},
           {'species': 'Herbivore', 'weight': 2, 'age': 3},
           {'species': 'Carnivore', 'weight': 8, 'age': 90}]

    des = Desert()
    des.add_population(pop)
    des.add_population(pop)

    nt.assert_equal(4, len(des.herb),
                    "Wrong number of herbivores added to list of herbivores")
    nt.assert_equal(2, len(des.carn),
                    "Wrong number of carnivores added to list of carnivores")

    for herb in des.herb:
        nt.assert_is_instance(herb, Herbivore,
                              "Wrong class instance created for the herbivores")
    for carn in des.carn:
        nt.assert_is_instance(carn, Carnivore,
                              "Wrong class instance created for the carnivore")

    nt.assert_raises(ValueError, des.add_population,
                     [{'species': 'Zebra', 'weight': 8, 'age': 90}])

    mout = Mountain()
    nt.assert_raises(ValueError, mout.add_population, pop)

    oce = Ocean()
    nt.assert_raises(ValueError, oce.add_population, pop)
