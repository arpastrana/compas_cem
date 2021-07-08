# COMPAS CEM

Constrained form-finding meets automatic differentiation.

![sihl_bridge](./docs/_images/from_cover.png)

## Introduction

COMPAS CEM is a structural design tool that generates efficient form for spatial bar structures subjected to combinations of tension and compression forces.
Examples of such structures are gridshells, bridges, stadiums, tensegrities and multistory buildings.

The generated forms can be steered to meet force and geometrical constraints, such as limiting the length of a selection of elements in the structure, best-fitting an arbitrary target surface, or restraining the magnitude of the reactions forces at the supports of a structure. This constrained form-finding process is solved under the hood using numerical optimization and automatic differentiation -- two commonplace techniques in the world of machine learning that COMPAS CEM makes readily accesible to designers around the world.

COMPAS CEM is a [COMPAS](https://compas.dev) extension written in pure Python. It runs on Windows, MacOS and Linux and it does not depend on any CAD software to work.

Are you a [Grasshopper](https://grasshopper3d.com) person though? Worry not. CAD-independence doesn't mean CAD-incompatibility: we ship COMPAS CEM as a ***Grasshopper plugin** so that you can readily integrate our constrained form-finding engine into your next parametric pipeline.

Feel free to check the [examples](https://github.com/arpastrana/compas_cem/tree/master/examples/) and the [docs](https://arpastrana.github.io/compas_cem) to get a glimpse of what COMPAS CEM can do for you.
If you are further interested in learning more about the underpinnings of the CEM framework, the constrained form-finding method that COMPAS CEM implements, we refer you to this [journal paper](https://www.sciencedirect.com/science/article/abs/pii/S0010448519305342).

## Authors

COMPAS CEM is developed by [Rafael Pastrana](https://pastrana.xyz) at the [CREATE Laboratory](https://createlaboratory.org) at the [Princeton University School of Architecture](https://soa.princeton.edu/) in collaboration Patrick Ole Ohlbrock from the Chair of Structural Design at [ETH Zürich](http://www.schwartz.arch.ethz.ch/) and Pierluigi D'Acunto from the Professorship of Structural Design at the [Technical University of Munich](https://www.tum.de/en/).

## Installation

Install `compas_cem` in only three simple steps.

**We assume you have [Anaconda](https://www.anaconda.com/) installed in your machine. If not, please download and install it before continuing.**

First, create a new anaconda environment from your command line. The only dependency is `compas`.
Here we chose the name of the environment to be `cem`, but you can call it `spacecowboy` if you prefer.

```bash
conda create -n cem COMPAS
```

Next, activate the `cem` environment. Anaconda environments are like bubbles that keep installations and dependencies isolated from other parts of your machine. In other words, what happens in `cem` stays in `cem`! 🕺🏻

```bash
conda activate cem
```

Finally, install `compas_cem` with a one-liner:

```bash
pip install compas-cem
```

To double-check that everything is up and running, while still in the command line, type the following and hit enter:

```bash
python -c "import compas_cem"
```

If no errors show up, celebrate 🎉! You have a working installation of `compas_cem`.

## Grasshopper Plugin

There will be times when modeling a complex structure is easier to do with a few mouse-clicks instead of a hundred lines of code.
The grasshopper version of `compas_cem` allows you to use all the important bits of our constrained form-finding engine in a (familiar) visual programming environment. 

To additionally install `compas_cem` as a grasshopper plugin, close Rhino, go to the command line and activate the anaconda environment where `compas_cem` lives. Note that you should have installed `compas_cem` from your command line before installing the grasshopper plugin. 

```bash
conda activate cem
```

Remove any leftovers inn case there was an older `compas` or ``compas_cem`` version linked to Rhino.

```bash
python -m compas_rhino.uninstall
```

Let's connect ``compas_cem``, ``compas_rhino`` and ``compas_ghpython`` to
Rhino. If you were wondering, the last two are installed by default by ``compas``.

```bash
python -m compas_rhino.install
```

Launch grasshopper and start dropping `compas_cem` components onto the canvas! Send pictures! 🏖 

### Caveat

The `compas_cem` plugin for grasshopper is a collection of `.ghuser` objects. As such, they have one important limitation: once used in a document, they forget who they are. The don't know they were created out of a ghuser component, they will be simple GHPython components. This has an important consequence: if you update `compas_cem`, those components already in use will NOT be automatically updated. More information [here](https://github.com/compas-dev/compas-actions.ghpython_components).

## Contributing

Pull requests are welcome!

Make sure to read our [contribution guide](https://github.com/arpastrana/compas_cem/tree/master/CONTRIBUTING.md).
Please don't forget to run ``invoke test`` in your command line before making a pull request.

## Issue tracker

If you find a bug or want to suggest a potential enhancement,
please help us tackle it by [filing a report](https://github.com/arpastrana/compas_cem/issues).

## License

MIT.
