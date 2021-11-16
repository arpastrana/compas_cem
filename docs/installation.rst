********************************************************************************
Installation
********************************************************************************

.. _Anaconda: https://www.anaconda.com/
.. _Rhino: https://www.rhino3d.com/
.. _Grasshopper: https://www.grasshopper3d.com/


.. highlight:: bash


Install COMPAS CEM
==================

Install **COMPAS CEM** in only three simple steps.

.. note::

   We assume you have `Anaconda`_ installed in your machine. If not, please download and install it before continuing.

1. Create a virtual environment
--------------------------------

First, create a new anaconda environment from the Anaconda Command Prompt if you are on Windows, or from your Terminal if you are on MacOS or Linux.

The only dependency is **COMPAS**.
Here we chose the name of the environment to be ``cem``, but you can call it ``spacecowboy`` if you prefer.

::

    conda create -n cem COMPAS==1.8.1


2. Activate the virtual environment
-----------------------------------

Next, activate the ``cem`` environment. Anaconda environments are like bubbles that keep installations and dependencies isolated from other parts in your machine. In other words, what happens in ``cem`` stays in ``cem``! 🕺🏻

::

    conda activate cem


3. Install COMPAS CEM via pip
-----------------------------

Finally, install **COMPAS CEM** with a one-liner:

::

   pip install compas-cem


To double-check that everything is up and running, type the following in the
command line and hit enter:

::

    python -c "import compas_cem"

If no errors show up, celebrate 🎉! You have a working installation of **COMPAS CEM**.


Update COMPAS CEM
=================

If you installed COMPAS CEM one day with ``pip`` and you want to update it to the latest available version, the update command is the following:

::

    pip install --upgrade compas-cem


Alternatively, if you want to switch to a specific version, type this:

::

    pip install compas-cem==0.16.1

.. note::

   If you update COMPAS CEM and you had installed the grasshopper plugin, the components already in use may no longer work.


Install the Grasshopper Plugin
==============================

There will be times when modeling a complex structure is easier to do with a few mouse-clicks instead of a hundred lines of code.
The `Grasshopper`_ (GH) version of COMPAS CEM allows you to use all the important bits of our constrained form-finding engine in a (familiar) visual programming environment.

To additionally install COMPAS CEM as a GH plugin, close `Rhino`_, go to the command line and follow the next three steps:

.. note::

   Make sure that the ``cem`` anaconda environment is active and that COMPAS CEM has been already installed from the command line before proceeding.

1. Remove any leftovers
------------------------

In case there was an older COMPAS or COMPAS CEM version linked to `Rhino`_.

::

    python -m compas_rhino.uninstall -v 7.0

.. note::

   The flag `-v 7.0` indicates that we will be uninstalling COMPAS CEM and company from Rhino 7. If you are working with Rhino 6, replace that last bit with `-v 6.0`.

2. Link COMPAS CEM
------------------

Let's connect COMPAS, COMPAS CEM, ``compas_rhino`` and ``compas_ghpython`` to
Rhino. If you were wondering, the last two are installed automatically when we installed COMPAS.

Type in your command line:

::

    python -m compas_rhino.install -v 7.0

.. note::

   The flag `-v 7.0` indicates that we will be installing COMPAS CEM and company in Rhino 7. If you are working with Rhino 6, replace that last bit with `-v 6.0`.


3. Check your Grasshopper installation
--------------------------------------

Launch grasshopper and start dropping COMPAS CEM components onto the canvas! Send pictures! 🏖

.. note::

   The COMPAS CEM plugin for grasshopper is a collection of ``.ghuser`` objects. As such, they have one important limitation: once used in a document, they forget who they are. The don't know they were created out of a ghuser component, they will be simple GHPython components. This has an important consequence: if you update COMPAS CEM, those components already in use will NOT be automatically updated.
