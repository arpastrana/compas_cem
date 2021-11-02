********************************************************************************
COMPAS CEM
********************************************************************************

.. rst-class:: lead

Constrained form-finding meets automatic differentiation.

.. figure:: /_images/front_cover.png
    :figclass: figure
    :class: figure-img img-fluid

    Structural model of a form-found bridge over the Sihl river, Switzerland.

.. _COMPAS: https://compas.dev/
.. _Grasshopper: https://grasshopper3d.com/
.. _Rafael Pastrana: https://github.com/arpastrana/
.. _CREATE Laboratory: https://createlaboratory.org/
.. _Princeton University School of Architecture: https://soa.princeton.edu/
.. _ETH Zürich: https://www.schwartz.arch.ethz.ch/
.. _Technical University of Munich: https://www.tum.de/en/
.. _journal paper: https://www.sciencedirect.com/science/article/abs/pii/S0010448519305342/

Introduction
============

COMPAS CEM is a structural design tool that generates efficient form for spatial bar structures subjected to combinations of tension and compression forces.
Examples of such structures are gridshells, bridges, stadiums, tensegrities and multistory buildings.

The generated forms can be steered to meet force and geometrical constraints, such as limiting the length of a selection of elements in the structure, best-fitting an arbitrary target surface, or restraining the magnitude of the reactions forces at the supports of a structure.

This constrained form-finding process is solved under the hood using numerical optimization and automatic differentiation -- two commonplace techniques in the world of machine learning that COMPAS CEM makes readily accesible to designers around the world.

COMPAS CEM is a `COMPAS`_ extension written in pure Python. It runs on Windows, MacOS and Linux and it does not depend on any CAD software to work.

Are you a `Grasshopper`_ person though? Worry not. CAD-independence doesn't mean CAD-incompatibility: we ship COMPAS CEM as a Grasshopper plugin so that you can readily integrate our constrained form-finding engine into your next parametric pipeline.

Feel free to check the :ref:`examples` and the :ref:`api` sections to glimpse into what COMPAS CEM can do for you.

If you are further interested in learning more about the underpinnings of the CEM framework, the constrained form-finding method that COMPAS CEM implements, we refer you to this `journal paper`_.

Authors
-------

COMPAS CEM is developed by `Rafael Pastrana`_ at the `CREATE Laboratory`_ at the `Princeton University School of Architecture`_ in collaboration with Patrick Ole Ohlbrock from the Chair of Structural Design at `ETH Zürich`_ and Pierluigi D'Acunto from the Professorship of Structural Design at the `Technical University of Munich`_.

First Example
==============

With ``compas_cem``, you can create a tension-compression structure in
equilibrium with Python using an object-oriented interface.

.. literalinclude:: ../examples/01_quick_start.py

.. figure:: /_images/01_quick_start.png
    :figclass: figure
    :class: figure-img img-fluid

Table of Contents
=================

.. toctree::
   :maxdepth: 3
   :titlesonly:

   Introduction <self>
   installation
   examples
   api
   changelog
   citing
   license
