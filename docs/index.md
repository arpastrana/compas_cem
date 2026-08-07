# COMPAS CEM

The [Combinatorial Equilibrium Modeling (CEM)](https://doi.org/10.1016/j.cad.2022.103435)
framework for [COMPAS](https://compas.dev/).

<figure markdown="span">
  ![Constrained form-finding of a spiral staircase](images/staircase_24_fps_128_colors.gif)
  <figcaption>Constrained form-finding of a spiral staircase.</figcaption>
</figure>

The [CEM framework](https://doi.org/10.1016/j.cad.2022.103435) is a numerical
form-finding approach to generate forms in static equilibrium for spatial bar
structures subjected to combinations of tension-compression forces and design
goals.
**COMPAS CEM** encapsulates the CEM framework into an open-source structural design
tool that enables the formulation and the solution of constrained form-finding
problems in plain and simple [Python](https://www.python.org/) code.

## Main features

* **Mix tension and compression forces:** Explore a wider spectrum of structural
  typologies by combining internal tension and compression forces in the same
  structure. Design space frames, bridges, tensegrities, and staircases and go beyond
  the conventional catalog of compression-only shells and cable-nets!

* **Solve constrained form-finding problems efficiently via automatic
  differentiation:** Generate forms in static equilibrium that simultaneously meet a
  priori design goals such as best-fitting a global target shape, restraining
  bar lengths, and controlling the reaction forces at the supports of a structure.

* **Usable across different 3D modeling software and operating systems:** COMPAS CEM
  runs on Windows, MacOS and Linux (perhaps one day also in the
  [metaverse](https://apnews.com/article/meta-facebook-explaining-the-metaverse-f57e01cd5739840945e89fd668b0fa27))
  and it does not depend on any CAD software to work. However, it provides the
  necessary interfaces to be seamlessly used inside popular design environments like
  [Rhino](https://www.rhino3d.com/), [Blender](https://www.blender.org/), and
  [Grasshopper](https://grasshopper3d.com/). As a [COMPAS](https://compas.dev/)
  extension, COMPAS CEM offers native integration and data exchange with other
  extensions and plugins in the COMPAS ecosystem.

* **Move those sliders with the Grasshopper plugin:** Are you a
  [Grasshopper](https://grasshopper3d.com/) person? Worry not. COMPAS CEM is shipped
  too as a precooked Grasshopper plugin to readily integrate our constrained
  form-finding engine into your next spaghetti pipeline 🍝.

## Credits

COMPAS CEM is developed by [Rafael Pastrana](https://pastrana.xyz/) at
[Princeton](https://soa.princeton.edu/), with the support of
[Ole Ohlbrock](https://schwartz.arch.ethz.ch/Team/patrickoleohlbrock.php?lan=en),
[Pierluigi D'Acunto](https://www.professoren.tum.de/en/dacunto-pierluigi) and
[Stefana Parascho](https://people.epfl.ch/stefana.parascho?lang=en).

This work has been supported in part by the U.S. National Science Foundation under
grant OAC-2118201 and the
[NSF Institute for Data Driven Dynamical Design](https://www.mines.edu/id4).
