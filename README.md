# COMPAS CEM

[![Github Actions Build Status](https://github.com/arpastrana/compas_cem/workflows/build/badge.svg)](https://github.com/arpastrana/compas_cem/actions)
[![License](https://img.shields.io/github/license/arpastrana/compas_cem.svg)](https://github.com/arpastrana/compas_cem/blob/main/LICENSE)
[![PyPI Package latest release](https://img.shields.io/pypi/v/compas-cem.svg)](https://pypi.python.org/pypi/compas-cem)
[![Python versions](https://img.shields.io/pypi/pyversions/compas-cem)](https://pypi.org/project/compas-cem)
[![ArXiv paper](https://img.shields.io/badge/arXiv-2111.02607-b31b1b.svg)](https://arxiv.org/abs/2111.02607)
[![Zenodo DOI](https://zenodo.org/badge/278780552.svg)](https://zenodo.org/badge/latestdoi/278780552)

![](docs/images/staircase_24_fps_128_colors.gif)

The [Combinatorial Equilibrium Modeling (CEM)](https://doi.org/10.1016/j.cad.2022.103435) framework for [COMPAS](https://compas.dev/).

The [CEM framework](https://doi.org/10.1016/j.cad.2022.103435) is a numerical form-finding approach to generate forms in static equilibrium for spatial bar structures subjected to combinations of tension-compression forces and design goals.
**COMPAS CEM** encapsulates the [CEM framework](https://doi.org/10.1016/j.cad.2022.103435) into an open-source structural design tool that enables the formulation and the solution of constrained form-finding problems in plain and simple [Python](https://www.python.org/) code.

## Main features

- **Mix tension and compression forces:** Explore a wider spectrum of structural typologies by combining internal tension and compression forces in the same structure. Design space frames, bridges, tensegrities, and staircases and go beyond the conventional catalog of compression-only shells and cable-nets!

- **Solve constrained form-finding problems efficiently via automatic differentiation:** Generate forms in static equilibrium that simultaneously meet a priori design goals such as best-fitting a global target shape, restraining bar lengths, and controlling the reaction forces at the supports of a structure.

- **Usable across different 3D modeling software and operating systems:** COMPAS CEM runs on Windows, MacOS and Linux (perhaps one day in the [metaverse](https://apnews.com/article/meta-facebook-explaining-the-metaverse-f57e01cd5739840945e89fd668b0fa27)) and it does not depend on any CAD software to work. However, it provides the necessary interfaces to be seamlessly used inside popular design environments like [Rhino](https://www.rhino3d.com/), [Blender](https://www.blender.org/), and [Grasshopper](https://grasshopper3d.com/). As a [COMPAS](https://compas.dev/) extension, COMPAS CEM offers native integration and data exchange with other extensions and plugins in the COMPAS ecosystem.

- **Move those sliders with the Grasshopper plugin:** Are you a [Grasshopper](https://grasshopper3d.com/) person? Worry not. COMPAS CEM is also shipped as a precooked Grasshopper plugin to readily integrate our constrained form-finding engine into your next spaghetti pipeline 🍝.

## Installation

These are succint instructions to install **COMPAS CEM** and its [Grasshopper](https://grasshopper3d.com/) plugin.
For detailed guidance, please refer to the [COMPAS CEM Docs](https://arpastrana.github.io/compas_cem/latest/index.html).

Install **COMPAS CEM** in a dedicated [Anaconda](https://www.anaconda.com/) environment via `pip`:

```bash
pip install compas-cem
```

To double-check that everything is up and running, type the following in the
command line and hit enter:

```bash
python -c "import compas_cem"
```

If no errors show up, celebrate 🎉! You have a working installation of **COMPAS CEM**.

### Grasshopper plugin

**Warning**: Note that [Grasshopper](https://grasshopper3d.com/) plugin of **COMPAS CEM** is only supported in **Rhino 6** and **Rhino 7**.

Once **COMPAS CEM** was installed from the comment line, we can additionally link it to [Rhino](https://www.rhino3d.com/) and use it as [Grasshopper](https://grasshopper3d.com/) plugin:

```bash
python -m compas_rhino.install -v 7.0
```

The flag `-v 7.0` indicates that we will be installing **COMPAS CEM** and company in Rhino 7. If you are working with Rhino 6, replace that last bit with `-v 6.0`.

## First steps

- [COMPAS CEM Docs](https://arpastrana.github.io/compas_cem/latest/index.html)
- [COMPAS CEM Examples](https://arpastrana.github.io/compas_cem/latest/examples.html)
- [COMPAS CEM API Reference](https://arpastrana.github.io/compas_cem/latest/api.html)
- [COMPAS Tutorials](https://compas.dev/compas/latest/tutorial.html)
- [COMPAS API Reference](https://compas.dev/compas/latest/api.html)

## Are you a bug hunter?

If you find a bug or want to suggest a potential enhancement,
please help us tackle it by filing a [report](https://github.com/arpastrana/compas_cem/issues).

## Questions and feedback

We encourage the use of the [COMPAS framework forum](https://forum.compas-framework.org/) for questions and discussions.

## Contributing

Pull requests are warmly welcome! Check the [Contributor's Guide](https://github.com/arpastrana/compas_cem/blob/main/CONTRIBUTING.md)
for more details.

## Citing

If you use **COMPAS CEM** for a project or research, please cite us using these [references](https://arpastrana.github.io/compas_cem/latest/citing.html).

## Acknowledgements

This work has been supported in part by the U.S. National Science Foundation under grant OAC-2118201 and the [NSF Institute for Data Driven Dynamical Design](https://www.mines.edu/id4).

## License

MIT
