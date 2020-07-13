# compas_cem

A **compas**-flavored implementation of the Combinatorial Equilibrium Modelling (CEM) method.

![](https://github.com/arpastrana/compas_cem/tree/master/docs/images/swap_dev_6fps.gif)

## Getting Started

CEM is a new form-finding approach to generate mixed tension-compression, spatial structures in equilibrium. This method is developed by Patrick Ole Ohlbrock and Pierluigi D'Acunto at the [Chair of Structural Design at the ETH Zurich](http://www.schwartz.arch.ethz.ch/). 

To have a better grasp of the algorithm running under the hood, we refer you these three excellent resources: to the CEM's [journal paper](https://www.sciencedirect.com/science/article/abs/pii/S0010448519305342), to the [condensed notes](https://github.com/arpastrana/compas_cem/tree/master/cem_method.md)  in this repository, and to the [first CEM repository](https://github.com/OleOhlbrock/CEM/) created by the authors.

Additionally, feel free to check this [hello world example]((https://github.com/arpastrana/compas_cem/tree/master/scripts/01_hello_world.py)) to get a feeling of what `compas_cem` can do for you.

## Installation

The preferred way to install `compas_cem` is to build it from source in only four simple steps.

First, create a new `conda` environment from your command line. The only requirements (until now) are `python` version **3.7** and `compas` version **0.16.1**.

```bash
conda create -n cem python=3.7 COMPAS=0.16.1
conda activate cam
```

We need to fetch `compas_cem` from this repository. Go to the folder where you want to store it and run the following. For example, if you are a mac user and want to put it in the pre-existing `~/code/` folder:

```bash
cd ~/code/
git clone https://github.com/arpastrana/compas_cem.git
```

Next, Move into the the repository's folder (the one you've just cloned) and install `compas_cem` using `pip`:

```bash
cd compas_cem
pip install -e .
```

To verify that everything is running like a charm, still in your command line interface, type the following and hit enter:

```bash
>>> python -c "import compas_cem"
```

If no errors arise, celebrate! You have a working installation of `compas_cem`.

## Contributing

Contributions and pull requests are welcome! Make sure to read our [contribution guide](https://github.com/arpastrana/compas_cem/tree/master/CONTRIBUTING.md).

Additionally, please don't forget to do ``invoke test`` in your command line to double check that the package is working before you make a pull request.

## Issue tracker

If you find a bug or want to suggest a potential enhancement,
please help us tackle it by [filing a report](https://github.com/arpastrana/compas_cem/issues).


## License

The contents of this repository are under an MIT license.
