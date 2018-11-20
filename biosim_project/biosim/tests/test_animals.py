# -*-coding: utf-8 -*-

"""
Tests for subclasses Herbivore and Carnivore, and superclass Animal.
"""

import nose.tools as nt
from ..animals import Herbivore, Carnivore
import math

__authors__ = 'Elisabeth Flatner and Marie Klever'
__emails__ = 'elisabeth.flatner@nmbu.no, marie.klever@nmbu.no'


class TestWithParams(object):
    """ Collects tests that uses different parameters than default. """

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """ Executed before each test in class to prepare for test. """
        self.copy_params_herb = Herbivore.params.copy()
        self.copy_params_carn = Carnivore.params.copy()
        self.herb = Herbivore(54)
        self.carn = Carnivore(54)

    def teardown(self):
        """ Executed after each test in class to clean up. """
        Herbivore.params = self.copy_params_herb
        Carnivore.params = self.copy_params_carn

    def test_invalid_param(self):
        """ Test for invalid parameter. """
        nt.assert_raises(ValueError, self.herb.set_parameters,
                         {'eta': 0.8, 'alf': 8})
        nt.assert_raises(ValueError, self.carn.set_parameters,
                         {'DeltaPhiMax': 0})

    def test_invalid_lower_value(self):
        """ Test for value lower than accepted. """
        nt.assert_raises(ValueError, self.herb.set_parameters, {'omega': -5})

    def test_invalid_upper_value(self):
        """ Test for value higher than accepted. """
        nt.assert_raises(ValueError, self.herb.set_parameters,
                         {'eta': 0.2, 'beta': 5, 'F': 0})

    def test_prob_birth_zero(self):
        """
        Testing that probability of birth is zero when the mothers weight is
        smaller than given conditions.
        """
        self.herb.set_parameters({'zeta': 15, 'w_birth': 6, 'sigma_birth': 1})
        nt.assert_equal(0, self.herb.probability_birth(12),
                        "Probability not equal to zero")

    def test_prob_birth_one(self):
        """
        Testing that probability of birth is set to one when bigger than one.
        """
        self.herb.set_parameters({'gamma': 0.1})
        nt.assert_equal(1, self.herb.probability_birth(12),
                        "Probability not equal to one")

    def test_prob_birth_valid(self):
        """ Testing that probability of birth is between zero and one. """
        self.herb.set_parameters({'gamma': 0.07})
        nt.assert_true(0 <= self.herb.probability_birth(12) <= 1,
                       "Probability not between zero and one")

    def test_weight_change_zero(self):
        """ Testing that weight change is zero when eta is zero. """
        self.herb.set_parameters({'eta': 0})
        self.herb.weight_change()
        nt.assert_equal(54, self.herb.weight,
                        "Weight change incorrect, should be zero")

    def test_weight_change_total(self):
        """
        Testing that weight is reduced by its total amount when eta is one.
        """
        self.herb.set_parameters({'eta': 1})
        self.herb.weight_change()
        nt.assert_equal(0, self.herb.weight,
                        "Weight change incorrect, weight should be zero")

    def test_weight_change(self):
        """ Testing that weight is changed correctly. """
        self.herb.set_parameters({'eta': 0.5})
        self.herb.weight_change()
        nt.assert_equal(27, self.herb.weight, "Weight change incorrect")


class TestBirthExtremes(object):
    """ Class that allows us to override probability of birth method. """

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """ Executed before each test in class to prepare for test. """
        self.copy_prob_birth = Herbivore.probability_birth
        self.copy_params = Herbivore.params.copy()

    def teardown(self):
        """ Executed after each test in class to clean up. """
        Herbivore.probability_birth = self.copy_prob_birth
        Herbivore.params = self.copy_params

    @staticmethod
    def test_birth_prob_zero():
        """
        Testing that no herbivore is born when probability of birth is zero.
        """
        Herbivore.probability_birth = lambda _, __: 0
        herb = Herbivore(50, 23)
        nt.assert_is_none(herb.birth(20), "Herbivore is born")

    @staticmethod
    def test_birth_prob_one():
        """ Testing that herbivore is born when probability of birth is one. """
        Herbivore.probability_birth = lambda _, __: 1
        herb = Herbivore(10, 32)
        # Set parameter sigma_birth to almost zero, to force the Gauss
        # distribution to return mean value
        herb.set_parameters({'sigma_birth': math.pow(10, -308)})
        nt.assert_is_not_none(herb.birth(26), "Herbivore is not born")


class TestDeathExtreme(object):
    """ Collects test that uses different parameters than default. """

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """ Executed before each test in class to prepare for test. """
        self.copy_params = Herbivore.params.copy()

    def teardown(self):
        """ Executed after each test in class to clean up. """
        Herbivore.params = self.copy_params

    @staticmethod
    def test_prob_death_one():
        """
        Testing that herbivore dies when probability of death is one.

        Sets a high age to give zero fitness so that the herbivore dies.
        """
        herb = Herbivore(30, 1000)
        herb.set_parameters({'omega': 1})
        nt.assert_true(herb.death(), "Herbivore should die")

    @staticmethod
    def test_prob_death_zero():
        """
        Testing that herbivore does not die when probability of death is zero.
        """
        herb = Herbivore(30, 8)
        herb.set_parameters({'omega': 0})
        nt.assert_false(herb.death(), "Herbivore should not die")


def test_age_input():
    """ Test that ValueError is raised when invalid age is given. """
    nt.assert_raises(ValueError, Herbivore, 20, age=-55)
    nt.assert_raises(ValueError, Herbivore, 25, age=0.5)
    nt.assert_raises(ValueError, Herbivore, 20, age=-0.04)


def test_aging():
    """ Test that age increases by one. """
    herb = Herbivore(25)
    herb.aging()
    nt.assert_equal(1, herb.age, "Aging is wrong")

    herb = Herbivore(25, 10)
    herb.aging()
    nt.assert_equal(11, herb.age, "Aging is wrong")


def test_weight_input():
    """ Test that ValueError is raised when invalid weight is given. """
    nt.assert_raises(ValueError, Herbivore, -5)
    nt.assert_raises(ValueError, Herbivore, 0)


def test_weight_of_animal():
    """ Test that method weight of animal returns correct value. """
    nt.assert_equal(54, Herbivore(54).weight_of_animal(),
                    "Returns the wrong value for weight")


def test_fitness():
    """
    Test that fitness factor is calculated correctly and that it is between
    zero and one.
    """
    nt.assert_almost_equal(0.98754, Herbivore(54).fitness, 5,
                           "Fitness is wrong")

    nt.assert_almost_equal(0.42508, Herbivore(7, 6).fitness, 5,
                           "Fitness is wrong")

    nt.assert_true(0 <= Herbivore(10, 10).fitness <= 1,
                   "Fitness has to be between 0 and 1")
    nt.assert_true(0 <= Herbivore(30).fitness <= 1,
                   "Fitness has to be between 0 and 1")
    nt.assert_true(0 <= Herbivore(9, 5).fitness <= 1,
                   "Fitness has to be between 0 and 1")


def test_herbivore_eating():
    """
    Testing that ValueError is raised when invalid input value is given.
    Test that herbivore eating returns correct values.
    """
    herb = Herbivore(18)
    nt.assert_raises(ValueError, herb.eating, -2)
    nt.assert_equal(10, herb.eating(20), "Herbivore eats wrong amount of food")
    nt.assert_equal(8, herb.eating(8), "Herbivore eats wrong amount of food")
    nt.assert_equal(0, herb.eating(0), "Herbivore eats wrong amount of food")


def test_herbivore_weight_change_by_eating():
    """ Test weight change in eating method. """
    herb = Herbivore(18)
    herb.eating(20)
    nt.assert_equal(27, herb.weight, "Wrong weight change")

    herb = Herbivore(50, 15)
    herb.eating(2)
    nt.assert_equal(51.8, herb.weight, "Wrong weight change")


def test_birth_with_one_herbivore():
    """ Testing that no herbivore is born, when only one herbivore in cell. """
    herb = Herbivore(50, 23)
    nt.assert_is_none(herb.birth(1), "Herbivore is born")


def bernoulli(p, n):
    """
    Calculates mean value and standard deviation in bernoulli design.

    :param p: probability
    :param n: number of tests
    :return: mean value and standard deviation
    """
    mean = p * n
    std = math.sqrt(n * p * (1 - p))
    return mean, std


def test_birth_bernoulli():
    """
    Using Bernoulli distribution to test birth with an uncertainty of 1 %.
    """
    num_herbivores = 10
    num_tests = 1000
    num_births = 0
    prob_birth = Herbivore(29).probability_birth(num_herbivores)

    for _ in range(num_tests):
        if Herbivore(29).birth(num_herbivores) is not None:
            num_births += 1

    mean, std = bernoulli(prob_birth, num_tests)

    nt.assert_true((mean - (3 * std)) <= num_births <= (mean + (3 * std)),
                   "Number of births outside distribution interval")


def test_death_bernoulli():
    """
    Using Bernoulli distribution to test death with an uncertainty of 1 %.
    """
    herb = Herbivore(29)
    prob_death = herb.params['omega'] * (1 - herb.fitness)
    num_tests = 1000

    num_death = sum([herb.death() for _ in range(num_tests)])

    mean, std = bernoulli(prob_death, num_tests)

    nt.assert_true((mean - (3 * std)) <= num_death <= (mean + (3 * std)),
                   "Number of deaths outside distribution interval")


def test_carn_kills_herb_bernoulli():
    """
    Using Bernoulli distribution to test carn_kills_herb() with an uncertainty
    of 1 %.
    """
    herb = Herbivore(20, 53)
    carn = Carnivore(20, 13)

    prob_carn_kill = carn.prob_kill(herb.fitness)
    num_tests = 1000
    num_kill = 0

    for _ in range(num_tests):
        if carn.carn_kills_herb(herb):
            num_kill += 1

    mean, std = bernoulli(prob_carn_kill, num_tests)

    nt.assert_true((mean - (3 * std)) <= num_kill <= (mean + (3 * std)))


class TestProbKill(object):
    """
    Collects test that uses different parameters than default and allows
    us to override methods.
    """

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """ Executed before each test in class to prepare for test. """
        self.copy_prob_kill = Carnivore.prob_kill
        self.copy_params = Carnivore.params.copy()
        self.carn = Carnivore(20, 13)
        self.herb = Herbivore(20, 13)

    def teardown(self):
        """ Executed after each test in class to clean up. """
        Carnivore.prob_kill = self.copy_prob_kill
        Carnivore.params = self.copy_params

    def test_carn_kills_herb(self):
        """
        Test that the method returns True when probability to kill is forced to
        be 100 %.
        """
        Carnivore.prob_kill = lambda _, __: 1
        nt.assert_true(self.carn.carn_kills_herb(self.herb),
                       "Herbivore should die")

    def test_carn_kill_one(self):
        """
        Test that the method returns True when probability to kill is set to be
        100 % for the given animals.
        """
        self.carn.set_parameters({'DeltaPhiMax': 0.02})
        nt.assert_true(self.carn.carn_kills_herb(self.herb),
                       "Herbivore should die")

    def test_carn_kill(self):
        """ Test that the method returns the correct value. """
        nt.assert_almost_equal(0.01983, self.carn.prob_kill(0.8), 5,
                               "Returns wrong value for prob_kill")


class TestCarnEating(object):
    """
    Collects tests that allows us to override method carn_kill_herb and change
    default parameters.
    """

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """ Executed before each test in class to prepare for test. """
        self.copy_carn_kills_herb = Carnivore.carn_kills_herb
        self.copy_params = Carnivore.params.copy()
        self.carn = Carnivore(20, 13)
        self.herbs = [Herbivore(20, 13), Herbivore(12)]

    def teardown(self):
        """ Executed after each test in class to clean up. """
        Carnivore.carn_kills_herb = self.copy_carn_kills_herb
        Carnivore.params = self.copy_params

    def test_carn_full(self):
        """ Test that no herbivores are eaten when the carnivore is full. """
        self.carn.set_parameters({'F': 0})
        nt.assert_list_equal(self.herbs, self.carn.eating(self.herbs),
                             "Returns wrong list of herbivores")

    def test_carn_fitness_low(self):
        """
        Test that no herbivores are eaten when the carnivore has lower fitness.
        """
        nt.assert_list_equal(self.herbs, Carnivore(250, 87).eating(self.herbs),
                             "Returns wrong list of herbivores")

    def test_carn_kills(self):
        """
        Test that correct herbivore is killed and that the corresponding weight
        change is correct.
        """
        Carnivore.carn_kills_herb = lambda _, __: True
        herb_one = Herbivore(60, 45)
        herb_two = Herbivore(12)
        nt.assert_list_equal([herb_two], self.carn.eating([herb_one, herb_two]),
                             "Returns wrong list of herbivores")
        nt.assert_equal(57.5, self.carn.weight_of_animal(),
                        "Weight gain is wrong")

    def test_carn_do_not_kill(self):
        """
        Test that herbivore escapes carnivore with higher fitness and the
        weight change is correct.
        """
        Carnivore.carn_kills_herb = lambda _, __: False
        nt.assert_list_equal(self.herbs, self.carn.eating(self.herbs))
        nt.assert_equal(20, self.carn.weight_of_animal(),
                        "The animal should not gain weight")

    def test_carn_kills_all(self):
        """
        Test that all herbivores are killed and that the weight gain is correct.
        """
        Carnivore.carn_kills_herb = lambda _, __: True
        nt.assert_list_equal([], self.carn.eating(self.herbs),
                             "Should not return any surviving herbivores")
        nt.assert_equal(44, self.carn.weight_of_animal(),
                        "Weight gain is wrong")


def test_prob_migration():
    """Testing that the method returns the correct probability of migration. """
    nt.assert_almost_equal(0.18256, Herbivore(20, 6).prob_migration(), 5,
                           "Returns the wrong probability of migration for the "
                           "animal")
