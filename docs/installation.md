# Installation

## Install COMPAS CEM

`compas_cem` is on PyPI, and it pulls in everything it needs to model,
form-find and optimize, `compas` among them. Install it with a one-liner:

```bash
pip install compas-cem
```

To draw diagrams with `compas_cem.plotters` or `compas_cem.viewers`, as the
examples do, install the `viz` extra instead:

```bash
pip install "compas-cem[viz]"
```

The plotter and the viewer are optional so that `compas_cem` stays lean inside
Rhino, which needs neither of them.

If you manage your project with [uv](https://docs.astral.sh/uv/), declare it as
a dependency of that project instead:

```bash
uv add "compas-cem[viz]"
```

To install it into an existing virtual environment without a project, use uv's
pip interface:

```bash
uv pip install "compas-cem[viz]"
```

!!! note

    `compas_cem` supports Python 3.9 to 3.13. The floor is 3.9 because that is
    the Python that Rhino 8 runs.

To double-check that everything is up and running, type the following in the
command line and hit enter:

```bash
python -c "import compas_cem"
```

If no errors show up, celebrate 🎉! You have a working installation of
`compas_cem`.

## Install the Grasshopper Plugin

There will be times when modeling a complex structure is easier to do with a few
mouse-clicks instead of a hundred lines of code. The
[Grasshopper](https://www.grasshopper3d.com/) (GH) version of `compas_cem` lets
you use all the important bits of our constrained form-finding engine in a
(familiar) visual programming environment.

The plugin runs in Rhino 8 and ships on the Rhino package server:

1. In Rhino 8, run the `PackageManager` command.
2. Search for `compas_cem` and install it.
3. Restart Rhino. The components appear under the **COMPAS CEM** tab in
   Grasshopper.

The first component you run installs the `compas-cem` Python package and its
dependencies into Rhino's own Python, so that first run needs an internet
connection and can take a minute.

!!! note

    Rhino 6 and 7 are no longer supported. Their last compatible release is
    `0.8.6`, which installs through COMPAS 1.

## Set up a development environment

To work on `compas_cem` itself, clone the repository and let `uv` set up the
environment. It installs a matching Python, the package in editable mode, the
plotter, the viewer and every development tool, pinned by the committed
`uv.lock`, in one step:

```bash
git clone https://github.com/arpastrana/compas_cem.git
cd compas_cem
uv sync --extra dev
uv run invoke test
```

Prefix commands with `uv run` and they execute inside the project environment,
with no activation step. A bare `uv sync` installs only the runtime
dependencies, the same as `pip install -e .`.

The lock covers Python 3.11 to 3.13. To work on Python 3.9 or 3.10, the Python
that Rhino 8 runs, or if you prefer `pip`, create and activate a virtual
environment and install the same extra:

```bash
pip install -e ".[dev]"
```

See the
[contributing guide](https://github.com/arpastrana/compas_cem/blob/main/CONTRIBUTING.md)
for the rest of the workflow.

## Update COMPAS CEM

If you installed `compas_cem` one day in the past and you want to update it to
the latest available version, the update command is the following:

```bash
pip install --upgrade compas-cem
```

With uv, `uv pip install --upgrade compas-cem` does the same in a plain virtual
environment, and `uv lock --upgrade-package compas-cem` followed by `uv sync`
does it in a uv project.

Alternatively, if you want to switch to a specific version, for example version
`0.8.6`, type this:

```bash
pip install compas-cem==0.8.6
```
