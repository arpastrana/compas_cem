********************************************************************************
COMPAS CEM
********************************************************************************

.. start-badges
.. end-badges

.. _COMPAS: https://compas.dev/
.. _Rafael Pastrana: https://pastrana.xyz/
.. _Princeton University School of Architecture: https://soa.princeton.edu/
.. _Ole Ohlbrock: https://schwartz.arch.ethz.ch/Team/patrickoleohlbrock.php?lan=en
.. _Pierluigi D'Acunto: https://www.professoren.tum.de/en/dacunto-pierluigi
.. _Stefana Parascho: https://soa.princeton.edu/content/stefana-parascho
.. _Anaconda: https://www.anaconda.com/
.. _Rhino: https://www.rhino3d.com/
.. _Blender: https://www.blender3d.com/
.. _Grasshopper: https://grasshopper3d.com/
.. _metaverse: https://bit.ly/3kiBBWC/

The Combinatorial Equilibrium Modeling (CEM) framework for `COMPAS`_.

.. figure:: /_images/staircase_24_fps_128_colors.gif
    :figclass: figure
    :class: figure-img img-fluid

    Constrained form-finding of a spiral staircase. Bars in tension and compression are colored in blue and red, respectively. Given a fixed topology diagram (left), the CEM framework leverages automatic differentiation to compute a constrained form diagram (middle) wherein the lateral chords of the staircase geometrically match the target design curves (middle, in dark gray).  The architectural interpretation of the resulting form diagram is provided on the right.

The CEM framework is a numerical form-finding approach to generate forms in static equilibrium for spatial bar structures subjected to combinations of tension-compression forces and design constraints.
**COMPAS CEM** encapsulates the CEM framework into an open-source structural design tool that enables the formulation and the solution of constrained form-finding problems in plain and simple Python code.
As one of its extensions, **COMPAS CEM** offers native integration and data exchange with other extensions and plugins in the `COMPAS`_ ecosystem.


Main features
=============

* **Mix tension and compression forces.** Explore a wider spectrum of structural typologies by combining internal tension and compression forces in the same structure. Design space frames, bridges, stadiums, tensegrities and staircases and go beyond the conventional catalog of compression-only shells and cable-nets!

* **Solve constrained form-finding problems efficiently.** Generate forms in static equilibrium that simultaneously meet a priori design constraints such as best-fitting a global target shape, restraining bar forces and lengths, and controlling the reaction forces at the supports of a structure. Do so efficiently using **automatic differentiation** and **gradient-based optimization**.

* **Usable across 3D modeling software and operating systems.**  **COMPAS CEM** is written in Python. It runs on Windows, MacOS and Linux (perhaps one day in the `metaverse`_) and it does not depend on any CAD software to work. However, it provides the necessary interfaces to be seamlessly used inside popular design environments like `Rhino`_, `Blender`_, and `Grasshopper`_.

* **Move those sliders with the Grasshopper plugin** Are you a Grasshopper person? Worry not. COMPAS CEM also ships as a precooked Grasshopper plugin so that you can readily integrate COMPAS CEM's constrained form-finding engine into your next spaghetti pipeline 🍝.


Installation
============

.. note::
   Here we provide succint instructions to install **COMPAS CEM** and it `Grasshopper`_ plugin. For detailed installation and upgrade guidance, please refer to the docs.

Install **COMPAS CEM** in a dedicated `Anaconda`_ environment with a one-liner via `pip`:

::

   pip install compas-cem

To double-check that everything is up and running, type the following in the
command line and hit enter:

::

    python -c "import compas_cem"

If no errors show up, celebrate 🎉! You have a working installation of **COMPAS CEM**.


Grasshopper plugin
------------------

Once **COMPAS CEM** was installed from the comment line, we can additionally link it to `Rhino`_ and deploy it as `Grasshopper`_ plugin:

::

    python -m compas_rhino.install -v 7.0

The flag `-v 7.0` indicates that we will be installing **COMPAS CEM** and company in Rhino 7. If you are working with Rhino 6, replace that last bit with `-v 6.0`.


First steps
===========

* `COMPAS CEM Docs <https://arpastrana.github.io/compas_cem/latest/index.html>`_
* `COMPAS CEM Examples <https://arpastrana.github.io/compas_cem/latest/examples.html>`_
* `COMPAS CEM API Reference <https://arpastrana.github.io/compas_cem/latest/api.html>`_
* `COMPAS Tutorials <https://compas.dev/compas/latest/tutorial.html>`_
* `COMPAS API Reference <https://compas.dev/compas/latest/api.html>`_


Questions and feedback
======================

We encourage the use of the `COMPAS framework forum <https://forum.compas-framework.org/>`_ for questions and discussions.


Are you a bug hunter?
=====================

If you find a bug or want to suggest a potential enhancement,
please help us tackle it by filing a `report <https://github.com/arpastrana/compas_cem/issues>`_.


Contributing
============

Pull requests are warmly welcome! Check the `Contributor's Guide <https://github.com/arpastrana/compas_cem/blob/main/CONTRIBUTING.md>`_
for more details.


Credits
=======

COMPAS CEM is developed by `Rafael Pastrana`_ at the `Princeton University School of Architecture`_, with the endorsement and support of `Ole Ohlbrock`_, `Pierluigi D'Acunto`_ and `Stefana Parascho`_.


License
=======

MIT
