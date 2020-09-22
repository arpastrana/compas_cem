********************************************************************************
Getting Started
********************************************************************************

.. _Anaconda: https://www.continuum.io/
.. _Rhino: https://www.rhino3d.com/
.. _Grasshopper: https://www.grasshopper3d.com/
.. _repo: https://github.com/compas-dev/compas_viewers/


.. highlight:: bash

Installation
============

The preferred way to install ``compas_cem`` is to build it from source in only five simple steps.


1. Create a virtual environment
-------------------------------

First, create and activate a new `Anaconda`_ environment from your command line.
The only dependencies are ``python``, ``COMPAS``, and ``rtree``.

::

    conda create -n cem python=3.7 COMPAS=0.16.2 rtree=0.9.4
    conda activate cem

.. note::
	Make sure you install ``python`` version ``3.7``, ``COMPAS`` version
	``0.16.4``, and ``rtree`` version ``0.9.4``. The name of the new environment
	is ``cem``.

2. Get the ``compas_cem`` repo
-------------------------------

We need to fetch ``compas_cem`` from this repository. Go to the folder where you
want to store it and run the following. For example, if you are a macOS user and
wish to put it in a pre-existing ``~/code/`` folder:

::

    cd ~/code/
    git clone https://github.com/arpastrana/compas_cem.git


3. Install ``compas_cem`` from source
-------------------------------------

Next, move into the the repository's folder (the one we've just cloned) and
install ``compas_cem`` as an editable package via ``pip``:

::

    cd compas_cem
    pip install -e .


4. Verify your installation
----------------------------

To double-check that everything is up and running, still in your command line interface, type the following and hit enter:

::

    python -c "import compas_cem"

If no errors show up, celebrate 🎉! You have a working installation of
``compas_cem``.


5. Optional Dependencies
------------------------

As a CAD-agnostic framework, ``COMPAS`` has developed ``compas_viewers``, a
standalone package to display 3d geometry from the command line. This is pretty
helpful when you want to orbit and zoom around a form-found model without
resorting to a full-blown CAD software like `Rhino`_. 

Some of the examples presented depend on ``compas_viewers`` to display the
resulting form-found structure. However, the viewers package **is entirely
optional**, and is not required for ``compas_cem`` internals to operate.

If you are interested to, please follow the installation instructions provided
by the ``compas_viewers`` developer in this `repo`_.


Linking ``compas_cem`` to Rhino and Grasshopper
===============================================

There will be times when modeling a complex structure is easier to do with a few
mouse-clicks instead of a hundred lines of code. ``COMPAS`` enables connecting
``compas_cem`` to `Rhino`_ and `Grasshopper`_ to access (almost) all of its
functionality from the inside.

To create the link, follow the next three steps from the command line:


1. Remove any leftovers
------------------------

In case there was an older **COMPAS** version linked to Rhino.

::

    python -m compas_rhino.uninstall

2. Link ``compas_cem``
----------------------

Let's connect ``compas_cem``, ``compas_rhino`` and ``compas_ghpython`` to
Rhino. If you were wondering, the last two come with a default ``COMPAS`` installation.

Type in your command line:

::

    python -m compas_rhino.install -p compas_cem compas_rhino compas_ghpython
    
.. note::

	Make sure that you are in the ``cem`` anaconda environment we created
	earlier while you do this.

3. Check your Rhino installation
---------------------------------

Open Rhino and try to import ``compas``, ``compas_rhino``, ``compas_ghpython``,
and ``compas_cem`` with a ``RhinoPython`` script.

.. code-block:: python

	import compas
	import compas_rhino
	import compas_ghpython
	import compas_cem

And voilá 🥐
