# Installation

## Install COMPAS CEM

`compas_cem` is on PyPI, and it pulls in everything it needs — `compas`, the
plotter and the viewer among them. Install it with a one-liner:

```bash
pip install compas-cem
```

!!! note

    `compas_cem` requires Python 3.10 or newer.

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

!!! warning

    The Grasshopper plugin is **not installable in this release.** It targeted
    Rhino 6 and 7 through `compas_rhino.install`, which does not exist in COMPAS
    2, and it is being reworked for Rhino 8 and 9 with
    [yak](https://developer.rhino3d.com/guides/yak/) packaging. Until that lands,
    use `compas_cem` from Python.

## Update COMPAS CEM

If you installed `compas_cem` one day in the past and you want to update it to
the latest available version, the update command is the following:

```bash
pip install --upgrade compas-cem
```

Alternatively, if you want to switch to a specific version, for example version
`0.8.6`, type this:

```bash
pip install compas-cem==0.8.6
```
