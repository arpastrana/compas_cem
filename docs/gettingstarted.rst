********************************************************************************
Getting Started
********************************************************************************

.. _Anaconda: https://www.anaconda.com/
.. _Rhino: https://www.rhino3d.com/
.. _Grasshopper: https://www.grasshopper3d.com/


.. highlight:: bash

Installation
============

Install ``compas_cem`` in only three simple steps.

.. note::

   We assume you have `Anaconda`_ installed in your machine. If not, please download and install it before continuing.

1. Create a virtual environment
--------------------------------

First, create a new anaconda environment from your command line. The only dependency is ``compas``.
Here we chose the name of the environment to be ``cem``, but you can call it ``spacecowboy`` if you prefer.

::

    conda create -n cem COMPAS


2. Activate the virtual environment
-----------------------------------

Next, activate the ``cem`` environment. Anaconda environments are like bubbles that keep installations and dependencies isolated from other parts of your machine. In other words, what happens in ``cem`` stays in ``cem``! 🕺🏻

::

    conda activate cem


3. Install ``compas_cem`` via pip
---------------------------------

Finally, install ``compas_cem`` with a one-liner:

::

   pip install compas-cem


To double-check that everything is up and running, type the following in the
command line and hit enter:

::

    python -c "import compas_cem"

If no errors show up, celebrate 🎉! You have a working installation of
``compas_cem``.


Grasshopper Plugin
==================

There will be times when modeling a complex structure is easier to do with a few mouse-clicks instead of a hundred lines of code.
The `Grasshopper`_ version of ``compas_cem`` allows you to use all the important bits of our constrained form-finding engine in a (familiar) visual programming environment.

To additionally install ``compas_cem`` as a grasshopper plugin, close `Rhino`_, go to the command line and follow the next three steps:

.. note::

   Make sure that the ``cem`` anaconda environment is active and that ``compas_cem`` has been already installed from the command line before proceeding.

1. Remove any leftovers
------------------------

In case there was an older ``COMPAS`` or ``compas_cem`` version linked to `Rhino`_.

::

    python -m compas_rhino.uninstall


2. Link ``compas_cem``
----------------------

Let's connect ``compas_cem``, ``compas_rhino`` and ``compas_ghpython`` to
Rhino. If you were wondering, the last two are installed by default by ``COMPAS``.

Type in your command line:

::

    python -m compas_rhino.install


3. Check your Grasshopper installation
--------------------------------------

Launch grasshopper and start dropping ``compas_cem`` components onto the canvas! Send pictures! 🏖

.. note::

   The ``compas_cem`` plugin for grasshopper is a collection of ``.ghuser`` objects. As such, they have one important limitation: once used in a document, they forget who they are. The don't know they were created out of a ghuser component, they will be simple GHPython components. This has an important consequence: if you update ``compas_cem``, those components already in use will NOT be automatically updated.
