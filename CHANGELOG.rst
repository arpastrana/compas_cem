Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Unreleased
----------

**Added**

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.1.10
----------

**Added**

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.1.9
----------

**Added**
* Added automatical creation of auxiliary trails.
* Added `auxiliary_trails=False` to the signature of `TopologyDiagram.build_trails()`.
* Added `TopologyDiagram.auxiliary_trails()` iterator.
* Added `TopologyDiagram.auxiliary_trail_edges()` iterator.
* Added `TopologyDiagram.is_auxiliary_trail_edge()` edge filter.
* Added `TopologyDiagram.number_of_auxiliary_trails()`.
* Added property `TopologyDiagram.auxiliary_trail_length` with setter.
* Added property `TopologyDiagram.auxiliary_trail_vector` with setter.
* Created first full version of GH plugin under `compas_cem.ghpython.components`

**Changed**

* Changed `TopologyDiagram.trails()` to return an iterable of trails instead of a dictionary.
* Changed `TopologyDiagram.build_trails()` to not return anything.
* The type of a trail is `tuple`, no longer `list` to reflect they are immutable.
* Splitted `Constraint()` into children classes `VectorConstraint()` and `FloatConstraint()`.
* Renamed `error` to `penalty` in `compas_cem.optimization`.
* Refactores examples folder.

**Fixed**

* Changed check for `None` in `NodeMixins.node_xyz()`.

**Deprecated**

**Removed**

* Removed `None` from default arguments in optimization constraints and parameters.

0.1.8
----------

**Added**

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.1.7
----------

**Added**

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.1.6
----------

**Added**

* Implemented `TopologyArtist` and `FormArtist`
* Added `compas_cem.rhino_install` to streamline the symlink with Rhino
* Added `src/compas_cem/ghpython/components/ghuser/` to `.gitignore`

**Changed**

* Refactored `compas_cem.rhino_install` into `compas_cem.ghpython.install`
* Refactored `compas_cem.rhino_install` into `compas_cem.ghpython.uninstall`

**Fixed**

**Deprecated**

**Removed**
* Removed `compas_cem.rhino_install`

0.1.5
----------

**Added**

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.1.4
----------

**Added**

**Changed**

**Fixed**

**Deprecated**

**Removed**

* Deleted tag regex from `.bumpversion.cfg`

0.1.3
------
**Added**

* Added automatic tag versioning to `CHANGELOG.md`

**Changed**

* Renamed `CHANGELOG.md` to  `CHANGELOG.rst`

**Fixed**

**Deprecated**

**Removed**

