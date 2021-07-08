********************************************************************************
COMPAS CEM
********************************************************************************

.. rst-class:: lead

A **COMPAS**-flavored combinatorial equilibrium modeling.

.. figure:: /_images/front_cover.png
    :figclass: figure
    :class: figure-img img-fluid

Introduction
============

**CEM** is a form-finding method to create mixed tension-compression
structures in equilibrium. This **COMPAS** package is developed by `Rafael
Pastrana`_ at the CREATE Laboratory at `Princeton University`_ in collaboration
with Patrick Ole Ohlbrock and Pierluigi D'Acunto from the Chair of Structural
Design at `ETH Zürich`_.

.. _Rafael Pastrana: https://github.com/arpastrana/
.. _Princeton University: https://soa.princeton.edu/
.. _ETH Zürich: http://www.schwartz.arch.ethz.ch/

To better picture CEM's underpinnings, please refer to these two excellent resources:

- The `journal paper`_.
- The `original CEM implementation`_ by Ole and Pierluigi.

.. _journal paper: https://www.sciencedirect.com/science/article/abs/pii/S0010448519305342/
.. _original CEM implementation: https://github.com/OleOhlbrock/CEM/

Additionally, feel free to check the :ref:`examples` section to get a first impression of what ``compas_cem`` can do for you.

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
   gettingstarted
   examples
   api
   license
   citing
