Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Unreleased
----------

**Added**

* Added check to skip adding None objects to `AssembleTopologyDiagram` in ghplugin.

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.1.14
----------

**Added**

* Added `draw_arrows` argument to `TopologyPlotter._draw_loads()`
* Implemented `TopologyPlotter._draw_load_arrows()` to display loads as arrows.
* Added import/export diagram from JSON to ghplugin.
* Implemented `TopologyArtist.draw_trails()`.
* `TopologyArtistComponent` in ghplugin can draw trails.
* Added `TopologyDiagram.number_of_trail_edges()` and `TopologyDiagram.number_of_deviation_edges()`.
* Implemented `__repr__()` method in diagrams, elements, supports, loads, parameters, constraints and optimizer.

**Changed**

* Renamed edge to edge_key and node to node_key in ghplugin components.
* Changed display color of loads from green to light green.
* Replaced `NodeResults` wit `SupportNodeResults` component in ghplugin.

**Fixed**

**Deprecated**

**Removed**

* Removed `build_trails` component from gh plugin. Merged with `AssembleTopologyDiagram`.
* Removed user access to specify auxiliary trails directions and lengths in ghplugin.
* Removed `nodes` from input to `TopologyDiagram` in ghplugin.

0.1.13
----------

**Added**

* Added `Optimizer.gradient` and `Optimizer.gradient_norm` as attributes.

**Changed**

* Exposed `eta` and `tmax` in the signature of `Optimizer.solve_nlopt()` instead of hard-coded values.
* Updated ghcomponent `ConstrainedFormFinding` to include `eta` and `tmax` as extra inputs.

**Fixed**

* Converted `Frame` returned by `RhinoPlane.to_compas()` to `Plane` for compatibility of `PlaneConstraint()` in ghplugin.
* Renamed input of ghcomponent `FormFinding` from `eps_min` to `eta`.
* Fixed bug in trail force sign calculation in `equilibrium_state` and in `equilibrium_state_numpy`.

**Deprecated**

**Removed**

0.1.12
----------

**Added**

* Added node coloring for free and support nodes in `FormPlotter()`.
* Added `TopologyPlotter.draw_segments()`
* Added color scheme for `auxiliary_trail_edges` when using `TopologyPlotter.draw_edges()`

**Changed**

**Fixed**

* Set `tight=False` when `axes.autoscale` is called by `Plotter.save()`. Overcropped saved image

**Deprecated**

**Removed**

* Deleted custom edge and node keys in `form_plotter_proxy` and in `topology_plotter_proxy`
* Removed frame polygon from `form_plotter_proxy` and in `topology_plotter_proxy`

0.1.11
----------

**Added**

**Changed**

**Fixed**

* Fixed bug in `static_equilibrium` and `static_equilibrium_numpy` when calculating support forces
* Fixed bug in `TopologyArtist` gh component: took in list of nodes instead of list of edges
* Temporary patch in length calculation in `DeviationEdgeLengthConstraint` that raised error with `autograd`.

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

