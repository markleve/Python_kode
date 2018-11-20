"""
Functions implementing "fitness calculation" in biosim project
"""

from math import exp

def _q_factor(phi, x, x_half):
    """
    Calculates q-factor for given parameters.

    :param phi: phi_age or phi_weight
    :param x: age or weight of the animal
    :param x_half: a_half or w_half
    :return: q-factor
    """

    return 1. / (1 + exp(phi * (x - x_half)))

def _fitness(phi_age, age, a_half, phi_weight, weight, w_half):
    """
    Calculates fitness of the animal.

    :param phi_age:
    :param age: age of the animal
    :param a_half:
    :param phi_weight:
    :param weight: weight of the animal
    :param w_half:
    :return: fitness of the animal
    """
    return (_q_factor(phi_age, age, a_half) *
            _q_factor(-phi_weight, weight, w_half))
