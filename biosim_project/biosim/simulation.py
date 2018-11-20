# -*-coding: utf-8 -*-

"""
This script is based on the simulation script in the RandVis project example
given in lecture 15, INF200, 13.01.16 by Hans Ekkehard Plesser at NMBU
"""

import matplotlib.pyplot as plt
import numpy as np
import subprocess
import os
from .island_nature import Island
import random

__authors__ = 'Elisabeth Flatner and Marie Klever'
__emails__ = 'elisabeth.flatner@nmbu.no, marie.klever@nmbu.no'

'''
:mod:`randvis.simulation` provides the user interface to the package.

Each simulation is represented by a :class:`DVSim` instance. On each
instance, the :meth:`DVSim.simulate` method can be called as often as
you like to simulate a given number of steps.

The state of the system is visualized as the simulation runs, at intervals
that can be chosen. The graphics can also be saved to file at regular
intervals. By calling :meth:`DVSim.make_movie` after a simulation is complete,
individual graphics files can be combined into an animation.

.. note::
   * This module requires the program ``ffmpeg`` or ``convert``
     available from `<http://ffmpeg.org>` and `<http://imagemagick.org>`.
   * You need to set the  :const:`_FFMPEG_BINARY` and :const:`_CONVERT_BINARY`
     constants below to the command required to invoke the programs
   * You need to set the :const:`_DEFAULT_FILEBASE` constant below to the
     directory and file-name start you want to use for the graphics output
     files.

Example
--------
::

    sim = DVSim((10, 15), 0.1, 12345, _DEFAULT_FILEBASE)
    sim.simulate(50, 1, 5)
    sim.make_movie()

This code

#. creates a system with a 10x15 matrix, sets the noise level to 0.1,
   the random number generator seed to 12345 and specifies the filename
   for output;
#. performs a simulation of 50 steps, updating the graphics after each
   step and saving a figure after each 5th step;
#. creates a movie from the individual figures saved.

'''


# update these variables to point to your ffmpeg and convert binaries
_FFMPEG_BINARY = 'ffmpeg'
_CONVERT_BINARY = 'convert'

# update this to the directory and file-name beginning
# for the graphics files
_DEFAULT_GRAPHICS_DIR = os.path.join('..', 'data')
_DEFAULT_GRAPHICS_NAME = 'dv'
_DEFAULT_MOVIE_FORMAT = 'mp4'   # alternatives: mp4, gif


class BioSim(object):
    """Provides user interface for simulation, including visualization."""

    def __init__(self, island_map, ini_pop, seed,
                 img_dir=None, img_name=_DEFAULT_GRAPHICS_NAME,
                 img_fmt='png'):
        """
        :param island_map: specification about the island's geography
        :type island_map: multiline str
        :param ini_pop: initial animal population on the island
        :type ini_pop: dictionary
        :param seed: random generator seed
        :type seed: int
        :param img_dir: directory for image files; no images if None
        :type img_dir: str
        :param img_name: beginning of name for image files
        :type img_name: str
        :param img_fmt: image file format suffix, default 'png'
        :type img_fmt: str
        """

        random.seed(seed)

        self._island_map = island_map
        self._island = Island(self._island_map)
        self._island.place_animals(ini_pop)

        if img_dir is not None:
            self._img_base = os.path.join(img_dir, img_name)
        else:
            self._img_base = None
        self._img_fmt = img_fmt

        self._step = 0
        self._final_step = None
        self._img_ctr = 0

        # the following will be initialized by _setup_graphics
        self._fig = None
        self._map_ax = None
        self._img_axis = None
        self._pop_ax = None
        self._herb_line = None
        self._carn_line = None
        self._herb_map_ax = None
        self._carn_map_ax = None
        self._count_year = None

        # limits for color code in population maps
        self._color_min_herb = None
        self._color_max_herb = None
        self._color_min_carn = None
        self._color_max_carn = None

        # maximum and default limit for ordinate in line graph
        self._ymax = None
        self._ylim = 200

    def simulate(self, num_steps, vis_steps=1, img_steps=None,
                 color_min_herb=0, color_max_herb=180, color_min_carn=0,
                 color_max_carn=180, ymax=None):
        """
        Run simulation while visualizing the result.

        :param num_steps: number of simulation steps to execute
        :param vis_steps: interval between visualization updates
        :param img_steps: interval between visualizations saved to files
                          (default: vis_steps)
        :param color_min_herb: color code minimum for herbivore
                                (default: 0)
        :param color_max_herb: color code maximum for herbivore
                                (default: 180)
        :param color_min_carn: color code minimum for carnivore
                                (default: 0)
        :param color_max_carn: color code maximum for carnivore
                                (default: 180)
        :param ymax: maxvalue for ylimit

        .. note:: Image files will be numbered consecutively.
        """

        if img_steps is None:
            img_steps = vis_steps

        # if max value for ordinate is given, ymax is set to given value
        if ymax is not None:
            self._ymax = ymax
        else:
            self._ymax = None

        self._color_min_herb = color_min_herb
        self._color_max_herb = color_max_herb
        self._color_min_carn = color_min_carn
        self._color_max_carn = color_max_carn

        self._final_step = self._step + num_steps
        self._setup_graphics()

        while self._step < self._final_step and 0 < self.total_num_animals():

            if self._step % vis_steps == 0:
                self._update_graphics()

            if self._step % img_steps == 0:
                self._save_graphics()

            self._island.annual_cycle()
            self._update_num_animals()
            self._step += 1

            if self.total_num_animals() <= 0:
                print('There are no animals left on the island ')

    def make_movie(self, movie_fmt=_DEFAULT_MOVIE_FORMAT):
        """
        Creates MPEG4 movie from visualization images saved.

        .. :note:
            Requires ffmpeg

        The movie is stored as img_base + movie_fmt
        """

        if self._img_base is None:
            raise RuntimeError("No filename defined.")

        if movie_fmt == 'mp4':
            # noinspection PyPep8
            try:
                # Parameters chosen according to http://trac.ffmpeg.org/wiki/Encode/H.264,
                # section "Compatibility"
                subprocess.check_call([_FFMPEG_BINARY, '-i', '{}_%05d.png'
                                      .format(self._img_base),
                                       '-y',
                                       '-profile:v', 'baseline',
                                       '-level', '3.0',
                                       '-pix_fmt', 'yuv420p',
                                       '{}.{}'.format(self._img_base,
                                                      movie_fmt)])
            except subprocess.CalledProcessError as err:
                print("ERROR: ffmpeg failed:", err)
        elif movie_fmt == 'gif':
            try:
                subprocess.check_call([_CONVERT_BINARY,
                                       '-delay', '1',
                                       '-loop', '0',
                                       '{}_*.png'.format(self._img_base),
                                       '{}.{}'.format(self._img_base,
                                                      movie_fmt)])
            except subprocess.CalledProcessError as err:
                print("ERROR: convert failed:", err)
        else:
            raise ValueError('Unknown movie format: ' + movie_fmt)

    def _setup_graphics(self):
        """Creates subplots."""

        # create new figure window
        if self._fig is None:
            self._fig = plt.figure(figsize=(12, 8))

        rgb_value = {'O': (0.0, 0.0, 1.0),  # blue
                     'M': (0.5, 0.5, 0.5),  # grey
                     'J': (0.0, 0.6, 0.0),  # dark green
                     'S': (0.5, 1.0, 0.5),  # light green
                     'D': (1.0, 1.0, 0.5)}  # light yellow

        kart_rgb = [[rgb_value[column] for column in row]
                    for row in self._island_map.split()]

        # Add upper left subplot showing a map with the geography of the island.
        if self._map_ax is None:
            self._map_ax = self._fig.add_axes([0.05, 0.525, 0.35, 0.45],
                                              title='Island map')
            self._map_ax.imshow(kart_rgb, interpolation='nearest')
            self._img_axis = self._fig.add_axes([0.41, 0.59, 0.1, 0.35])
            self._img_axis.axis('off')

            for ix, name in enumerate(('Ocean', 'Mountain', 'Jungle',
                                       'Savannah', 'Desert')):
                self._img_axis.add_patch(plt.Rectangle
                                         ((0., ix * 0.2), 0.3, 0.1,
                                          edgecolor='none',
                                          facecolor=rgb_value[name[0]]))
                self._img_axis.text(0.35, ix * 0.2, name,
                                    transform=self._img_axis.transAxes)

        # Add upper right subplot for line graph of number of animals on the
        # island.
        if self._pop_ax is None:
            self._pop_ax = self._fig.add_axes([0.6, 0.58, 0.35, 0.35],
                                              title='Number of animals on the '
                                                    'island',
                                              xlabel='year',
                                              ylabel='number of animals')

        # needs updating on subsequent calls to simulate()
        self._pop_ax.set_xlim(0, self._final_step + 1)

        if self._herb_line is None:
            self._herb_line = self._pop_ax.plot(
                np.arange(0, self._final_step), np.nan * np.ones(
                    self._final_step), 'b-')[0]

            self._carn_line = self._pop_ax.plot(
                np.arange(0, self._final_step), np.nan * np.ones(
                    self._final_step), 'r-')[0]
        else:
            xdata, ydata_herb = self._herb_line.get_data()
            ydata_carn = self._carn_line.get_ydata()
            xnew = np.arange(xdata[-1] + 1, self._final_step)

            if len(xnew) > 0:
                ynew = np.nan * np.ones_like(xnew)
                self._herb_line.set_data(np.hstack((xdata, xnew)),
                                         np.hstack((ydata_herb, ynew)))
                self._carn_line.set_data(np.hstack((xdata, xnew)),
                                         np.hstack((ydata_carn, ynew)))

        # Add lower left subplot for map illustrating the distribution of
        # herbivores on the island.
        if self._herb_map_ax is None:
            self._herb_map_ax = self._fig.add_axes([0.05, 0.025, 0.4, 0.45],
                                                   title='Distribution of '
                                                         'herbivores')
            self._herb_img_axis = None

        # Add lower right subplot for map illustrating the distribution of
        # carnivores on the island.
        if self._carn_map_ax is None:
            self._carn_map_ax = self._fig.add_axes([0.57, 0.025, 0.4, 0.45],
                                                   title='Distribution of '
                                                         'carnivores')
            self._carn_img_axis = None

        if self._count_year is None:
            self._count_year = self._fig.add_axes([0.36, 0.35, 0.2, 0.2])
            self._count_year.axis('off')

        # Add lower center subplot for counter of number of years that are
        # simulated
            self._template = 'Year: {:5}'
            self._txt = self._count_year.text(0.5, 0.5, self._template.
                                              format(0),
                                              horizontalalignment='left',
                                              verticalalignment='bottom',
                                              transform=self._count_year.
                                              transAxes, fontsize='large',
                                              weight='bold')

    def _update_distribution_maps(self, num_herb_cell, num_carn_cell):
        """
        Update the 2D-view of the system.

        Updates subplots showing the distribution of herbivores and carnivores
        on the island.
        :param num_herb_cell: total number of herbivores in each cell
        :param num_carn_cell: total number of carnivores in each cell
        """

        if self._herb_img_axis is not None:
            self._herb_img_axis.set_data(num_herb_cell)
            self._carn_img_axis.set_data(num_carn_cell)
        else:
            self._herb_img_axis = self._herb_map_ax.imshow(
                num_herb_cell, interpolation='nearest',
                vmin=self._color_min_herb, vmax=self._color_max_herb)

            plt.colorbar(self._herb_img_axis, ax=self._herb_map_ax,
                         orientation='horizontal')

            self._carn_img_axis = self._carn_map_ax.imshow(
                num_carn_cell, interpolation='nearest',
                vmin=self._color_min_carn, vmax=self._color_max_carn)

            plt.colorbar(self._carn_img_axis, ax=self._carn_map_ax,
                         orientation='horizontal')

    def _update_num_animals(self):
        """ Updates total number of animals for each year in the simulation. """

        num_herb, num_carn = self._island.number_of_animals()

        ydata_herb = self._herb_line.get_ydata()
        ydata_herb[self._step] = num_herb

        ydata_carn = self._carn_line.get_ydata()
        ydata_carn[self._step] = num_carn

    def _update_pop_graph(self):
        """
        Updates line graph showing the total number of different animal species
        on the island.
        """

        self._pop_ax.legend(('Herbivores', 'Carnivores'), loc='upper left',
                            fontsize='small')

        ydata_herb = self._herb_line.get_ydata()
        self._herb_line.set_ydata(ydata_herb)

        ydata_carn = self._carn_line.get_ydata()
        self._carn_line.set_ydata(ydata_carn)

        # updates ordinate simultaneously if ymax is not given
        # else ylim is set to given ymax
        if self._ymax is None and self._step % 2 == 0:
            max_herb = max(ydata_herb)
            max_carn = max(ydata_carn)

            if max_herb > max_carn:
                if max_herb > self._ylim:
                    self._ylim = 1.2 * max_herb
            else:
                if max_carn > self._ylim:
                    self._ylim = 1.2 * max_carn

            self._pop_ax.set_ylim(0, self._ylim)

        else:
            self._pop_ax.set_ylim(0, self._ymax)

    def _update_counter(self):
        """ Updates counter with number of years that are simulated. """
        self._txt.set_text(self._template.format(self._step+1))

    def _update_graphics(self):
        """Updates graphics with current data."""

        self._update_distribution_maps(self._island.num_herb_in_cells(),
                                       self._island.num_carn_in_cells())
        self._update_pop_graph()

        self._update_counter()

        plt.pause(1e-6)

    def _save_graphics(self):
        """Saves graphics to file if file name given."""

        if self._img_base is None:
            return

        plt.savefig('{base}_{num:05d}.{type}'.format(base=self._img_base,
                                                     num=self._img_ctr,
                                                     type=self._img_fmt))
        self._img_ctr += 1

    def add_population(self, population):
        """
        Places new animals in correct location on the island.

        :param population: Dictionary with new animals
        """
        self._island.place_animals(population)

    def num_years(self):
        """ Returns total number of years that have been simulated. """
        return self._step

    def total_num_animals(self):
        """ Returns total number of animals on the island. """
        num_herb, num_carn = self._island.number_of_animals()
        return num_herb + num_carn

    def total_num_by_species(self):
        """ Returns total number of herbivores and carnivores. """
        num_herb, num_carn = self._island.number_of_animals()
        return {'herbivores': num_herb, 'carnivores': num_carn}

    def num_animals_per_cell(self):
        """ Returns number of animals per cell in map. """
        herbivores = self._island.num_herb_in_cells()
        carnivores = self._island.num_carn_in_cells()
        return {'herbivores': herbivores, 'carnivores': carnivores}
