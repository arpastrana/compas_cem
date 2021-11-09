********************************************************************************
COMPAS CEM
********************************************************************************

.. start-badges

.. image:: https://github.com/arpastrana/compas_cem/workflows/build/badge.svg
    :target: https://github.com/arpastrana/compas_cem/actions
    :alt: Github Actions Build Status

.. image:: https://img.shields.io/pypi/v/compas-cem.svg
    :target: https://pypi.python.org/pypi/compas-cem
    :alt: PyPI Package latest release

.. image:: https://img.shields.io/pypi/pyversions/compas-cem
   :target: https://pypi.org/project/compas-cem
   :alt: Python versions

.. image:: https://zenodo.org/badge/107952684.svg
   :target: https://zenodo.org/badge/latestdoi/107952684
   :alt: Zenodo DOI

.. image:: https://img.shields.io/github/license/arpastrana/compas_cem.svg
    :target: https://github.com/arpastrana/compas_cem/blob/main/LICENSE
    :alt: License

.. image:: https://img.shields.io/twitter/follow/compas_dev?style=social
   :target: https://twitter.com/compas_dev
   :alt: Twitter follow


.. end-badges

.. _COMPAS: https://compas.dev/
.. _COMPAS CEM Docs: https://arpastrana.github.io/compas_cem/latest/index.html
.. _CEM Framework: https://arxiv.org/abs/2111.02607
.. _Rafael Pastrana: https://pastrana.xyz/
.. _Princeton: https://soa.princeton.edu/
.. _Ole Ohlbrock: https://schwartz.arch.ethz.ch/Team/patrickoleohlbrock.php?lan=en
.. _Pierluigi D'Acunto: https://www.professoren.tum.de/en/dacunto-pierluigi
.. _Stefana Parascho: https://soa.princeton.edu/content/stefana-parascho
.. _Anaconda: https://www.anaconda.com/
.. _Rhino: https://www.rhino3d.com/
.. _Blender: https://www.blender.org/
.. _Grasshopper: https://grasshopper3d.com/
.. _metaverse: https://apnews.com/article/meta-facebook-explaining-the-metaverse-f57e01cd5739840945e89fd668b0fa27


.. figure:: ./docs/_images/staircase_24_fps_128_colors.gif
    :figclass: figure
    :class: figure-img img-fluid


The `Combinatorial Equilibrium Modeling (CEM) <https://arxiv.org/abs/2111.02607>`_ framework for `COMPAS`_.

The `CEM framework`_ is a numerical form-finding approach to generate forms in static equilibrium for spatial bar structures subjected to combinations of tension-compression forces and design constraints.
**COMPAS CEM** encapsulates the `CEM framework`_ into an open-source structural design tool that enables the formulation and the solution of constrained form-finding problems in plain and simple `Python <https://www.python.org/>`_ code.


Main features
=============

* **Mix tension and compression forces:** Explore a wider spectrum of structural typologies by combining internal tension and compression forces in the same structure. Design space frames, bridges, tensegrities, and staircases and go beyond the conventional catalog of compression-only shells and cable-nets!

* **Solve constrained form-finding problems efficiently:** Generate forms in static equilibrium that simultaneously meet a priori design constraints such as best-fitting a global target shape, restraining bar lengths, and controlling the reaction forces at the supports of a structure. Do so efficiently using **automatic differentiation** and **gradient-based optimization**.

* **Usable across 3D modeling software and operating systems:**  is written in Python. It runs on Windows, MacOS and Linux (perhaps one day in the `metaverse`_) and it does not depend on any CAD software to work. However, it provides the necessary interfaces to be seamlessly used inside popular design environments like `Rhino`_, `Blender`_, and `Grasshopper`_. As a `COMPAS`_ extension, **COMPAS CEM** offers native integration and data exchange with other extensions and plugins in the `COMPAS`_ ecosystem.

* **Move those sliders with the Grasshopper plugin** Are you a `Grasshopper`_ person? Worry not. **COMPAS CEM** also ships as a precooked `Grasshopper`_ plugin so that you can readily integrate our constrained form-finding engine into your next spaghetti pipeline 🍝.


Installation
============


These are succint instructions to install **COMPAS CEM** and its `Grasshopper`_ plugin.
For detailed guidance, please refer to the `COMPAS CEM Docs`_.

Install **COMPAS CEM** in a dedicated `Anaconda`_ environment via ``pip``:

::

   pip install compas-cem

To double-check that everything is up and running, type the following in the
command line and hit enter:

::

    python -c "import compas_cem"

If no errors show up, celebrate 🎉! You have a working installation of **COMPAS CEM**.


Grasshopper plugin
------------------

Once **COMPAS CEM** was installed from the comment line, we can additionally link it to `Rhino`_ and use it as `Grasshopper`_ plugin:

::

    python -m compas_rhino.install -v 7.0

The flag ``-v 7.0`` indicates that we will be installing **COMPAS CEM** and company in Rhino 7. If you are working with Rhino 6, replace that last bit with ``-v 6.0``.


First steps
===========

* `COMPAS CEM Docs`_
* `COMPAS CEM Examples <https://arpastrana.github.io/compas_cem/latest/examples.html>`_
* `COMPAS CEM API Reference <https://arpastrana.github.io/compas_cem/latest/api.html>`_
* `COMPAS Tutorials <https://compas.dev/compas/latest/tutorial.html>`_
* `COMPAS API Reference <https://compas.dev/compas/latest/api.html>`_


Are you a bug hunter?
=====================

If you find a bug or want to suggest a potential enhancement,
please help us tackle it by filing a `report <https://github.com/arpastrana/compas_cem/issues>`_.


Questions and feedback
======================

We encourage the use of the `COMPAS framework forum <https://forum.compas-framework.org/>`_ for questions and discussions.


Contributing
============

Pull requests are warmly welcome! Check the `Contributor's Guide <https://github.com/arpastrana/compas_cem/blob/main/CONTRIBUTING.md>`_
for more details.


Citing
======

If you use **COMPAS CEM** for a project or research, please cite us using these `references <https://arpastrana.github.io/compas_cem/latest/citing.html>`_.


Credits
=======

COMPAS CEM is developed by `Rafael Pastrana`_ at `Princeton`_, with the endorsement and support of `Ole Ohlbrock`_, `Pierluigi D'Acunto`_ and `Stefana Parascho`_.


License
=======

MIT
