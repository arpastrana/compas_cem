Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Unreleased
----------

**Added**

- Added set conversion in `TopologyDiagram.is_auxiliary_trail_edge()`.

**Changed**

- Pinned dependency to `numpy==1.26.3`.
- Pinned dependency to `compas==1.17.10`.
- Updated installation instructions in docs website.
- Set minimum supported python version to `3.8`.
- Bumped to docs action to `docs@.2.21`.
- Pinned `sphinx, `pytest`, and `pytest-lazy-fixture` dependencies in `requirements_dev.txt`.
- Set `crazy-max/ghaction-github-pages@v3.1.0` in `docs` action.
- Set `compas-actions.docs@v2.2.1` in `docs` action.
- Updated grashopper components in examples.

**Fixed**

**Deprecated**

**Removed**

- Removed `compas_singular` dependency.

0.8.0
----------

**Added**

- Added `PolylineConstraint` component to grasshopper plugin.
- Implemented `constraints.PolylineConstraint`.
- Added `EdgeDirectionConstraint` component to grasshopper plugin.
- Implemented `constraints.EdgeDirectionConstraint`.
- Added `Diagram.edge_plane` to query the projection plane of an edge.

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.7.0
----------

**Added**

- Added sequence coloring for nodes to `plotters.TopologyArtist`.
- Automatically compute edge widths from a two-tuple with `plotters.FormArtist`.
- Automatically compute edge widths from a two-tuple with `viewers.DiagramObject`.
- Created `MoveOriginNodes` GH component.
- Implemented `ShiftTrails` GH component.
- Implemented `Topology.number_of_sequences()`
- Enabled `static_equilibrium` calculations up to a `kmax` sequence.
- Implemented `Topology.trails_sequences` mapping.
- Implemented `Topology.trail_sequence` mapping.
- Implemented `Topology.shift_trail` to change the starting sequence of a trail.
- Implemented `Topology.from_dualquadmesh`.
- Created colors for direct and indirect deviation edges.
- An origin node can be parametrized by more than one optimization parameter (position and applied load).
- An edge can be assigned more than one constraint for optimization.
- A node can be assigned more than one constraint for optimization.
- Enabled `NodeLoad` x, y, z components to be used as an optimization parameter.

**Changed**

- Plot reaction forces and applied loads as arrow meshes in `viewers.DiagramObject` instead of lines.
- `Topology.auxiliary_trails()` takes `keys` as parameter to iterate over origin node keys and trails.
- `Topology.trails()` takes `keys` as parameter to iterate over origin node keys and trails.
- `Topology.sequence()` takes `keys` as parameter to iterate over origin node keys and trails.
- `Topology.sequences()` outputs tuples with the nodes in every sequence instead of a range to `klast`.
- Set explicit use of `compas_cem.ghpython` artist in `FormArtist`.
- Set explicit use of `compas_cem.ghpython` artists in `TopologyArtist`.

**Fixed**

- Prevent `NaN` in next position calculation in `equilibrium_state_numpy`.

**Deprecated**

**Removed**

0.6.1
----------

**Added**

**Changed**

**Fixed**

- Fixed mising `kappa` argument in `optimization.solve_proxy`

**Deprecated**

**Removed**

0.6.0
----------

**Added**

- `ConstrainedFormFinding` GH component outputs optimized `TopologyDiagram`.
- `compas_cem.plotters.TopologyArtist` has node size and edge width default parameters.
- `compas_cem.plotters.FormArtist` has node size and edge width default parameters.
- Added support for gradient computation via finite differences.
- Added support for the `VAR` optimization algorithm from NLOpt.
- Added gradient convergence treshold `kappa` to the signature of `Optimizer.solve`.
- Added `kappa` as input to the `ConstrainedFormFinding` GH component.
- Implemented `Diagram.is_edge_supported`

**Changed**

- Changed GH components folder prefix from CEM to CompasCem.
- Renamed `compas_cem.optimization.Optimizer.solve_nlopt` to `solve`.
- Refactored `compas_cem.optimization.Parameter`.
- Refactored calculation of trail edge length via plane intersection in `static_equilibrium`.
- Refactored calculation of trail edge length via plane intersection in `static_equilibrium_numpy`.

**Fixed**

- Fixed bug in `compas_cem.equilibrium.equilibrium_state` where `residual` calculation was undefined when `tmax=1`.

**Deprecated**

- Deprecated `Optimizer.solve_nlopt` and `.solve_nlopt_proxy`.


**Removed**


0.5.0
----------

**Added**

- Implemented `compas_cem.plotters.Plotter`.
- Implemented `compas_cem.viewers.Viewer`.
- Implemented `compas_cem.viewers.DiagramObject`.
- Implemented `compas_cem.viewers.TopologyDiagramObject`.
- Implemented `compas_cem.viewers.FormDiagramObject`.
- Created `compas_cem.viewers`.

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.4.1
----------

**Added**

- Implemented `ProxyServer` GH component to accelerate optimization time in Rhino.
- Added `compas_cem.diagrams.Diagram.__str__()`.

**Changed**

- Changed `ConstrainedFormFinding` GH component to check for existing `ProxyServer`.
- Changed `nlopt_status` flags for better interpretability in ghpython.

**Fixed**

- Fixed bug in `compas_cem.ghpython.artists` registration.
- Fixed bug in serialization and target computation in `optimization.constraints.VectorConstraint`.
- Fixed bug in `Plane` creation caused by old version of `compas_rhino.RhinoPlane.from_geometry`.

**Deprecated**

**Removed**

- Removed `compas_cem.loads.NodeLoad.from_rhino_point_and_vector`
- Removed `compas_cem.supports.NodeSupport.from_rhino_point`
- Removed `compas_cem.elements.Edge.from_rhino_line`
- Removed `compas_cem.elements.Node.from_rhino_point`
- Removed `compas_cem.data.GHData`.

0.4.0
----------

**Added**

- Added spiral staircase ghpython example.
- Added Jenssen tensegrity ghpython example.
- Added tube bridge 3d ghpython example.
- Added bridge 2d ghpython example.
- Added dome ghpython example.
- Implemented `TopologyDiagram.is_node_support()`.
- Renamed node and edge key search GH components.
- Implemented `compas_cem.data.Data`.
- Implemented `compas_cem.plotters.TopologyArtist`.
- Implemented `compas_cem.plotters.FormArtist`.
- Implemented `compas_cem.optimization.Parameter`.
- Added artists registration for plotters and grasshopper via `compas.plugins.plugin`.

**Changed**

- Changed reaction force global color from dark blue to dark gray.
- Changed data serialization mechanism to comply with `compas.data.Data`.

**Fixed**

- Fixed bug in auxiliary trails coloring in `compas_cem.plotters`.

**Deprecated**

- Deprecated `TopologyPlotter`.
- Deprecated `FormPlotter`.

**Removed**

- Removed `compas_cem.optimization.serialization.Serializable`.
- Removed `compas_cem.ghpython.components.Node` component.

0.2.2
----------

**Added**

**Changed**

**Fixed**

* Pinned COMPAS dependency to version 1.8.1 due to NetworkPlotter deprecation.

**Deprecated**

**Removed**

0.2.1
----------

**Added**

**Changed**

* Changed reaction forces display color from dark green to dark gray.
* Changed loads display color from light green to dark green.

**Fixed**

* Trail-building was ignored assembling deviation-only topology diagrams in ghplugin.
* Fixed bug: Wrapped `EdgeSearch` tuple output in a list in ghplugin.

**Deprecated**

**Removed**

* Removed support for gradient-free NLopt optimization algorithms.
* Dropped "LD" subscript to identify NLopt optimization algorithms.

0.1.15
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

