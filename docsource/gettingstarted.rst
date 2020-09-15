********************************************************************************
Getting Started
********************************************************************************

.. _Anaconda: https://www.continuum.io/
.. _Rhino: https://www.rhino3d.com/

.. highlight:: bash

Installation
============

The preferred way to install ``compas_cem`` is to build it from source in only four simple steps.


1. Create a virtual environment
-------------------------------

First, create a new `Anaconda`_ environment from your command line. The only
requirements (until now) are ``python``, ``compas``, and ``rtree``.

::

    conda create -n cem python=3.7 COMPAS=0.16.2 rtree=0.9.4
    conda activate cem

.. note::
	Make sure you install ``python`` version ``3.7``, ``COMPAS`` version
	``0.16.4``, and ``rtree`` version ``0.9.4``.

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

Next, Move into the the repository's folder (the one you've just cloned) and install ``compas_cem`` using ``pip``:

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


Linking ``compas_cem`` to Rhino
===============================

As with any other **COMPAS** runs independently from any CAD platform. However,
there will be times when modeling a complex structure is easier and more natural
to do with a few mouse-clicks instead of a hundred lines of code.

Therefore, the **COMPAS** framework allows you to link ``compas_cem`` to
`Rhino`_ with a few lines of code, so that you can access (almost) all the 
package functionality inside.

To link ``compas_cem`` to Rhino, follow the next three steps in your command line:

1. Remove any leftovers
------------------------

In case you had older **COMPAS** versions linked to Rhino before.

::

    python -m compas_rhino.uninstall

2. Link ``compas_cem``
----------------------

Now, let's link ``compas_cem``, ``compas_rhino`` and ``compas_ghpython`` to
Rhino. If you were wondering, the last two come with a default **COMPAS** installation.

Type in your command line:

::

    python -m compas_rhino.install -p compas_cem compas_rhino compas_ghpython
    
.. note::

	Make sure that you are in the ``cem`` anaconda environment while you do it.

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
