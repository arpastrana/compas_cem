********************************************************************************
COMPAS CEM
********************************************************************************

.. rst-class:: lead

.. _CEM Framework: https://doi.org/10.1016/j.cad.2022.103435
.. _COMPAS: https://compas.dev/
.. _Rafael Pastrana: https://pastrana.xyz/
.. _Princeton: https://soa.princeton.edu/
.. _Ole Ohlbrock: https://schwartz.arch.ethz.ch/Team/patrickoleohlbrock.php?lan=en
.. _Pierluigi D'Acunto: https://www.professoren.tum.de/en/dacunto-pierluigi
.. _Stefana Parascho: https://people.epfl.ch/stefana.parascho?lang=en
.. _Rhino: https://www.rhino3d.com/
.. _Blender: https://www.blender.org/
.. _Grasshopper: https://grasshopper3d.com/
.. _metaverse: https://apnews.com/article/meta-facebook-explaining-the-metaverse-f57e01cd5739840945e89fd668b0fa27


The `Combinatorial Equilibrium Modeling (CEM) <https://doi.org/10.1016/j.cad.2022.103435>`_ framework for `COMPAS`_.

.. figure:: /images/staircase_24_fps_128_colors.gif
    :figclass: figure
    :class: figure-img img-fluid

    Constrained form-finding of a spiral staircase.


The `CEM framework`_ is a numerical form-finding approach to generate forms in static equilibrium for spatial bar structures subjected to combinations of tension-compression forces and design constraints.
**COMPAS CEM** encapsulates the `CEM framework`_ into an open-source structural design tool that enables the formulation and the solution of constrained form-finding problems in plain and simple `Python <https://www.python.org/>`_ code.


Main features
-------------

* **Mix tension and compression forces:** Explore a wider spectrum of structural typologies by combining internal tension and compression forces in the same structure. Design space frames, bridges, tensegrities, and staircases and go beyond the conventional catalog of compression-only shells and cable-nets!

* **Solve constrained form-finding problems efficiently via automatic differentiation:** Generate forms in static equilibrium that simultaneously meet a priori design constraints such as best-fitting a global target shape, restraining bar lengths, and controlling the reaction forces at the supports of a structure.

* **Usable across different 3D modeling software and operating systems:** COMPAS CEM runs on Windows, MacOS and Linux (perhaps one day also in the `metaverse`_) and it does not depend on any CAD software to work. However, it provides the necessary interfaces to be seamlessly used inside popular design environments like `Rhino`_, `Blender`_, and `Grasshopper`_. As a `COMPAS`_ extension, COMPAS CEM offers native integration and data exchange with other extensions and plugins in the COMPAS ecosystem.

* **Move those sliders with the Grasshopper plugin:** Are you a `Grasshopper`_ person? Worry not. COMPAS CEM is shipped too as a precooked Grasshopper plugin to readily integrate our constrained form-finding engine into your next spaghetti pipeline 🍝.


Credits
-------

COMPAS CEM is developed by `Rafael Pastrana`_ at `Princeton`_, with the support of `Ole Ohlbrock`_, `Pierluigi D'Acunto`_ and `Stefana Parascho`_.

This work has been supported in part by the U.S. National Science Foundation under grant OAC-2118201 and the `NSF Institute for Data Driven Dynamical Design <https://www.mines.edu/id4>`_.


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
