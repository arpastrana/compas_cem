********************************************************************************
Installation
********************************************************************************

.. _Anaconda: https://www.anaconda.com/
.. _Rhino: https://www.rhino3d.com/
.. _Grasshopper: https://www.grasshopper3d.com/
.. _COMPAS installation: https://compas.dev/compas/latest/installation
.. _COMPAS known installation issues: https://compas.dev/compas/latest/installation#known-issues


.. highlight:: bash


Install COMPAS CEM
==================

Install ``compas_cem`` in only four steps.

.. note::

   We assume you have `Anaconda`_ installed in your machine. If not, please download and install it before continuing.

1. Create a virtual environment
--------------------------------

First, create a new anaconda environment from the Anaconda Command Prompt if you are on Windows, or from your Terminal if you are on MacOS or Linux.

Here we chose the name of the environment to be ``cem``, but you can call it ``spacecowboy`` if you prefer.

::

    conda create -n cem


2. Activate the virtual environment
-----------------------------------

Next, activate the ``cem`` environment. Anaconda environments are like bubbles that keep installations and dependencies isolated from other parts in your machine. In other words, what happens in ``cem`` stays in ``cem``! 🕺🏻

::

    conda activate cem


3. Install COMPAS via conda
----------------------------

As a ``compas`` extension, ``compas_cem`` requires ``compas`` to work.
The recommended way to install ``compas`` is through conda, but you can consult other installation options in the `COMPAS installation`_ documentation.


::

    conda install -c conda-forge compas

.. note::

   You may run into errors when installing ``compas``. If you encounter a problem such as not being able to install ``planarity``, that "Microsoft Visual C++ Build Tools are missing", or that ``numpy`` fails to pass a sanity check, please refer to `COMPAS known installation issues`_ page for instructions on how to solve these problems.



4. Install COMPAS CEM via pip
-----------------------------

Finally, install ``compas_cem`` with a one-liner:

::

   pip install compas-cem


To double-check that everything is up and running, type the following in the
command line and hit enter:

::

    python -c "import compas_cem"

If no errors show up, celebrate 🎉! You have a working installation of ``compas_cem``.


Install the Grasshopper Plugin
==============================

There will be times when modeling a complex structure is easier to do with a few mouse-clicks instead of a hundred lines of code.
The `Grasshopper`_ (GH) version of ``compas_cem`` allows you to use all the important bits of our constrained form-finding engine in a (familiar) visual programming environment.

To additionally install ``compas_cem`` as a GH plugin, close `Rhino`_, go to the command line and follow the next three steps:

.. note::

   Make sure that the ``cem`` anaconda environment is active and that ``compas_cem`` has been installed before proceeding.

1. Remove any leftovers
------------------------

In case there was an older ``compas`` or ``compas_cem`` M version linked to `Rhino`_.

::

    python -m compas_rhino.uninstall -v 7.0

.. note::

   The flag `-v 7.0` indicates that we will be uninstalling ``compas_cem`` and company from Rhino 7. If you are working with Rhino 6, replace that last bit with `-v 6.0`.

2. Link COMPAS CEM
------------------

Let's connect ``compas``, ``compas_cem``, ``compas_rhino`` and ``compas_ghpython`` to
Rhino. If you were wondering, the last two are installed automatically when we first installed ``compas``.

Type in your command line:

::

    python -m compas_rhino.install -v 7.0

.. note::

   The flag `-v 7.0` indicates that we will be installing ``compas_cem`` and company in Rhino 7. If you are working with Rhino 6, replace that last bit with `-v 6.0`.


3. Check your Grasshopper installation
--------------------------------------

Launch grasshopper and start dropping ``compas_cem`` components onto the canvas! Send pictures! 🏖

.. note::

   The ``compas_cem`` plugin for grasshopper is a collection of ``.ghuser`` objects. As such, they have one important limitation: once used in a document, they forget who they are. The don't know they were created out of a ghuser component, they will be simple GHPython user components. This has an important consequence: if you update ``compas_cem``, those components already in use will NOT be automatically updated.


Update COMPAS CEM
=================

If you installed ``compas_cem`` one day in the past with ``pip`` and you want to update it to the latest available version, the update command is the following:

::

    pip install --upgrade compas-cem


Alternatively, if you want to switch to a specific version, type this:

::

    pip install compas-cem==0.16.1

.. note::

   If you update ``compas_cem`` and you had installed the grasshopper plugin, the components already in use may no longer work.
