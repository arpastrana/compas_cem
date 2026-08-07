# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- Added `pyproject.toml`, replacing `setup.py`, `setup.cfg`, `pytest.ini` and `.bumpversion.cfg`.
- Added `mkdocs.yml` and a mkdocs-material documentation site.
- Added `.github/workflows/pr-checks.yml`.
- Added regression baselines for every example under `tests/baseline`, captured from 0.8.6 behaviour.
- Added regression tests that `add_node` and `add_edge` accept both vocabularies, reject a mismatched element, and survive a JSON round trip and a `copy()`.
- Added `Diagram.node_connected_edges`, which returns the edges incident to a node.
- Added `TopologyDiagram.__from_data__`, which restores the integer keys of the trail bookkeeping after a round trip.
- Added regression tests that trails and auxiliary trails survive a JSON round trip.
- Added `plotters/scene_objects.py` and `viewers/scene_objects.py`, replacing the artist and object modules of both visualization backends.
- Added `tests/baseline/render.py`, which renders every example headless for visual review of the plotters.

### Changed

- Migrated from COMPAS 1.17.10 to `compas>=2.15,<3.0`.
- Promoted `compas_plotter>=1.0.1` and `compas_viewer>=2.0` to runtime dependencies. Drawing a diagram is not an optional extra of this package, so installing it installs both backends.
- Rewrote the installation instructions around `pip` and `venv`. conda is being phased out across the COMPAS ecosystem, and `compas` no longer needs installing separately because `compas_cem` declares it.
- Marked the Grasshopper plugin as not installable in this release. It linked into Rhino 6 and 7 through `compas_rhino.install`, which COMPAS 2 removed.
- Renamed `Constraint` to `Goal` throughout, a clean break with no deprecation aliases. The nine concrete classes, the `VectorConstraint` and `FloatConstraint` bases, the `constraints` module, `Optimizer.add_constraint` and `remove_constraint`, the `solve_proxy` wire signature and the eight Grasshopper component directories all follow. This frees the name `Constraint` for genuine hard constraints, which nlopt supports and the package does not yet use.
- Made `Diagram.add_node` and `Diagram.add_edge` accept either a node or edge element, or a key with attributes. COMPAS 2 deserializes a graph by replaying `add_node(key=, attr_dict=)` and `add_edge(u, v, attr_dict=)`, which the object-taking overrides shadowed, breaking `copy()` and `from_json()`. Both entry points now dispatch on the argument, so the authoring API is unchanged and deserialization reaches the base graph.
- Made the entry points reject a mismatched element rather than silently treating it as a node key: `add_node` refuses an edge element, `add_edge` refuses a node element, and a key given both positionally and by name raises.
- Folded `NodeMixins` and `EdgeMixins` into `Diagram` and dropped `compas_cem.data.Data` from its bases. `Datastructure.__inheritance__` walks the MRO up to `Datastructure` calling `__clstype__()` on every class in between, so a plain `object` mixin made `to_json()` raise.
- Changed the `tol` diagram attribute from a format string to an integer count of decimal places, following `compas.tolerance.TOL.geometric_key`.
- Ported serialization from the `data` property pair to `__data__` and `__from_data__` on goals and on edge and node parameters.
- Gave `Goal`, `Parameter`, `EdgeParameter` and `NodeParameter` default constructor arguments, so `__from_data__` can build one without knowing the concrete signature.
- Regenerated `examples/03_bridge_2d.json`, which was COMPAS 1.7.1 JSON and unreadable by COMPAS 2. Node and edge insertion order is preserved, because it sets the order of the optimizer's parameter vector.
- Widened `requires-python` to `>=3.10,<3.14` and both CI matrices to 3.10 through 3.13, now that the `distutils` ceiling is gone.
- Replaced the reStructuredText module docstrings and inline markup with Markdown, and moved parameter and return types out of docstrings and into the signature position that mkdocstrings renders.
- Migrated the plotters from `compas_plotters` artists to `compas_plotter>=1.0.1` scene objects, and the viewers from `compas_view2` objects to `compas_viewer>=2.0` scene objects. Both register through `compas.scene.register` on import, because compas discovers scene object plugins in `compas*` packages only.
- Pinned the plotter node size policy to `relative`. The upstream scene object defaults to `absolute`, which divides the node size by the plotter resolution instead of the node count and draws markers two orders of magnitude smaller.
- Drew the topology load crosses straight onto the canvas. A line scene object fixes its own stacking order in its constructor, which put the crosses underneath the opaque node markers.
- Fixed `state_format` in both visualization backends reading an undefined `edge` instead of the edge it was passed.
- Fixed `DiagramObject` referring to `self.topology`, which it never defined.
- Fixed a `show_nodes` setter that assigned to `_show_edges`.
- Fixed `DiagramArtist.draw_reactions` documenting a `min_load` parameter that its signature calls `min_force`, and `TopologyDiagramObject` documenting its argument as `form_diagram`.
- Moved the documentation from Sphinx and reStructuredText to mkdocs-material with mkdocstrings.
- Converted `README`, `CHANGELOG` and `AUTHORS` from reStructuredText to Markdown.
- Replaced the abandoned `pytest-lazy-fixture` with `pytest-lazy-fixtures`, which lifts the `pytest<8` ceiling.
- Rewrote `tasks.py` to compose `compas_invocations2` tasks.
- Updated CI to `compas-actions.build@v5`, `compas-actions.docs@v5` and `compas-actions.publish@v3`.
- Replaced flake8, isort, doc8 and pydocstyle with ruff, and reformatted the code base to 88 columns.
- Loosened dependency version from `numpy<2` to `numpy>=1.26`. The upper bound was never necessary; the test suite passes on numpy 2.

### Removed

- Removed the dependency on `trimesh`. It was never imported: its only reference is `optimization/goals/mesh.py`, which is commented out of the package.
- Removed `.travis.yml`, which targeted Python 2.7.
- Removed the `compas_cem.diagrams.mixins` package, folded into `Diagram`.
- Removed `Diagram.connected_edges`, superseded by `node_connected_edges`. COMPAS 2 gives the inherited name a different meaning: it takes no node and returns edge groups per connected component.
- Removed `plotters/proxy.py`. It was dead code calling a `FormPlotter` and a `TopologyPlotter` that no longer exist.
- Removed the `FormArtist`, `TopologyArtist` and `DiagramArtist` plotter classes and the `register_artists` plugin, superseded by the plotter scene objects.

## [0.8.6] 2025-02-24

### Added

### Changed

- Loosened dependency version from `autograd==1.5` to `autograd`.
- Loosened dependency version from `numpy==1.26.3` to `numpy<2`.

### Removed

## [0.8.5] 2025-01-23

### Added

- Implemented `FormDiagram.from_equilibrium_state` constructor for compatibility with `jax_cem`.

### Changed

### Removed

## [0.8.4] 2025-01-15

### Added

### Changed

- Pinned dependency to `nlopt>2.7`.

### Removed

## [0.8.3] 2025-01-15

### Added

### Changed

- Pinned dependency to `nlopt==2.7.1`.

### Removed

## [0.8.2] 2025-01-15

### Added

### Changed

### Removed

## [0.8.1] 2025-01-15

### Added

- Added set conversion in `TopologyDiagram.is_auxiliary_trail_edge()`.

### Changed

- Pinned dependency to `numpy==1.26.3`.
- Pinned dependency to `compas==1.17.10`.
- Updated installation instructions in docs website.
- Set minimum supported python version to `3.8`.
- Bumped to docs action to `docs@.2.21`.
- Pinned `sphinx`, `pytest`, and `pytest-lazy-fixture` dependencies in `requirements_dev.txt`.
- Set `crazy-max/ghaction-github-pages@v3.1.0` in `docs` action.
- Set `compas-actions.docs@v2.2.1` in `docs` action.
- Updated grashopper components in examples.

### Removed

- Removed `compas_singular` dependency.

## [0.8.0] 2023-04-07

### Added

- Added `PolylineConstraint` component to grasshopper plugin.
- Implemented `constraints.PolylineConstraint`.
- Added `EdgeDirectionConstraint` component to grasshopper plugin.
- Implemented `constraints.EdgeDirectionConstraint`.
- Added `Diagram.edge_plane` to query the projection plane of an edge.

### Changed

### Removed

## [0.7.0] 2022-09-26

### Added

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

### Changed

- Plot reaction forces and applied loads as arrow meshes in `viewers.DiagramObject` instead of lines.
- `Topology.auxiliary_trails()` takes `keys` as parameter to iterate over origin node keys and trails.
- `Topology.trails()` takes `keys` as parameter to iterate over origin node keys and trails.
- `Topology.sequence()` takes `keys` as parameter to iterate over origin node keys and trails.
- `Topology.sequences()` outputs tuples with the nodes in every sequence instead of a range to `klast`.
- Set explicit use of `compas_cem.ghpython` artist in `FormArtist`.
- Set explicit use of `compas_cem.ghpython` artists in `TopologyArtist`.

### Fixed

- Prevent `NaN` in next position calculation in `equilibrium_state_numpy`.

### Removed

## [0.6.1] 2022-08-24

### Added

### Changed

### Fixed

- Fixed mising `kappa` argument in `optimization.solve_proxy`

### Removed

## [0.6.0] 2022-08-18

### Added

- `ConstrainedFormFinding` GH component outputs optimized `TopologyDiagram`.
- `compas_cem.plotters.TopologyArtist` has node size and edge width default parameters.
- `compas_cem.plotters.FormArtist` has node size and edge width default parameters.
- Added support for gradient computation via finite differences.
- Added support for the `VAR` optimization algorithm from NLOpt.
- Added gradient convergence treshold `kappa` to the signature of `Optimizer.solve`.
- Added `kappa` as input to the `ConstrainedFormFinding` GH component.
- Implemented `Diagram.is_edge_supported`

### Changed

- Changed GH components folder prefix from CEM to CompasCem.
- Renamed `compas_cem.optimization.Optimizer.solve_nlopt` to `solve`.
- Refactored `compas_cem.optimization.Parameter`.
- Refactored calculation of trail edge length via plane intersection in `static_equilibrium`.
- Refactored calculation of trail edge length via plane intersection in `static_equilibrium_numpy`.

### Fixed

- Fixed bug in `compas_cem.equilibrium.equilibrium_state` where `residual` calculation was undefined when `tmax=1`.

### Deprecated

- Deprecated `Optimizer.solve_nlopt` and `.solve_nlopt_proxy`.

### Removed

## [0.5.0] 2022-06-03

### Added

- Implemented `compas_cem.plotters.Plotter`.
- Implemented `compas_cem.viewers.Viewer`.
- Implemented `compas_cem.viewers.DiagramObject`.
- Implemented `compas_cem.viewers.TopologyDiagramObject`.
- Implemented `compas_cem.viewers.FormDiagramObject`.
- Created `compas_cem.viewers`.

### Changed

### Removed

## [0.4.1] 2022-06-02

### Added

- Implemented `ProxyServer` GH component to accelerate optimization time in Rhino.
- Added `compas_cem.diagrams.Diagram.__str__()`.

### Changed

- Changed `ConstrainedFormFinding` GH component to check for existing `ProxyServer`.
- Changed `nlopt_status` flags for better interpretability in ghpython.

### Fixed

- Fixed bug in `compas_cem.ghpython.artists` registration.
- Fixed bug in serialization and target computation in `optimization.constraints.VectorConstraint`.
- Fixed bug in `Plane` creation caused by old version of `compas_rhino.RhinoPlane.from_geometry`.

### Removed

- Removed `compas_cem.loads.NodeLoad.from_rhino_point_and_vector`
- Removed `compas_cem.supports.NodeSupport.from_rhino_point`
- Removed `compas_cem.elements.Edge.from_rhino_line`
- Removed `compas_cem.elements.Node.from_rhino_point`
- Removed `compas_cem.data.GHData`.

## [0.4.0] 2022-05-31

### Added

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

### Changed

- Changed reaction force global color from dark blue to dark gray.
- Changed data serialization mechanism to comply with `compas.data.Data`.

### Fixed

- Fixed bug in auxiliary trails coloring in `compas_cem.plotters`.

### Deprecated

- Deprecated `TopologyPlotter`.
- Deprecated `FormPlotter`.

### Removed

- Removed `compas_cem.optimization.serialization.Serializable`.
- Removed `compas_cem.ghpython.components.Node` component.

## [0.2.2] 2021-11-16

### Added

### Changed

### Fixed

- Pinned COMPAS dependency to version 1.8.1 due to NetworkPlotter deprecation.

### Removed

## [0.2.1] 2021-11-09

### Added

### Changed

- Changed reaction forces display color from dark green to dark gray.
- Changed loads display color from light green to dark green.

### Fixed

- Trail-building was ignored assembling deviation-only topology diagrams in ghplugin.
- Fixed bug: Wrapped `EdgeSearch` tuple output in a list in ghplugin.

### Removed

- Removed support for gradient-free NLopt optimization algorithms.
- Dropped "LD" subscript to identify NLopt optimization algorithms.

## [0.1.15] 2021-09-08

### Added

- Added check to skip adding None objects to `AssembleTopologyDiagram` in ghplugin.

### Changed

### Removed

## [0.1.14] 2021-09-07

### Added

- Added `draw_arrows` argument to `TopologyPlotter._draw_loads()`
- Implemented `TopologyPlotter._draw_load_arrows()` to display loads as arrows.
- Added import/export diagram from JSON to ghplugin.
- Implemented `TopologyArtist.draw_trails()`.
- `TopologyArtistComponent` in ghplugin can draw trails.
- Added `TopologyDiagram.number_of_trail_edges()` and `TopologyDiagram.number_of_deviation_edges()`.
- Implemented `__repr__()` method in diagrams, elements, supports, loads, parameters, constraints and optimizer.

### Changed

- Renamed edge to edge_key and node to node_key in ghplugin components.
- Changed display color of loads from green to light green.
- Replaced `NodeResults` wit `SupportNodeResults` component in ghplugin.

### Removed

- Removed `build_trails` component from gh plugin. Merged with `AssembleTopologyDiagram`.
- Removed user access to specify auxiliary trails directions and lengths in ghplugin.
- Removed `nodes` from input to `TopologyDiagram` in ghplugin.

## [0.1.13] 2021-08-25

### Added

- Added `Optimizer.gradient` and `Optimizer.gradient_norm` as attributes.

### Changed

- Exposed `eta` and `tmax` in the signature of `Optimizer.solve_nlopt()` instead of hard-coded values.
- Updated ghcomponent `ConstrainedFormFinding` to include `eta` and `tmax` as extra inputs.

### Fixed

- Converted `Frame` returned by `RhinoPlane.to_compas()` to `Plane` for compatibility of `PlaneConstraint()` in ghplugin.
- Renamed input of ghcomponent `FormFinding` from `eps_min` to `eta`.
- Fixed bug in trail force sign calculation in `equilibrium_state` and in `equilibrium_state_numpy`.

### Removed

## [0.1.12] 2021-07-14

### Added

- Added node coloring for free and support nodes in `FormPlotter()`.
- Added `TopologyPlotter.draw_segments()`
- Added color scheme for `auxiliary_trail_edges` when using `TopologyPlotter.draw_edges()`

### Changed

### Fixed

- Set `tight=False` when `axes.autoscale` is called by `Plotter.save()`. Overcropped saved image

### Removed

- Deleted custom edge and node keys in `form_plotter_proxy` and in `topology_plotter_proxy`
- Removed frame polygon from `form_plotter_proxy` and in `topology_plotter_proxy`

## [0.1.11] 2021-07-09

### Added

### Changed

### Fixed

- Fixed bug in `static_equilibrium` and `static_equilibrium_numpy` when calculating support forces
- Fixed bug in `TopologyArtist` gh component: took in list of nodes instead of list of edges
- Temporary patch in length calculation in `DeviationEdgeLengthConstraint` that raised error with `autograd`.

### Removed

## [0.1.9] 2021-07-08

### Added

- Added automatical creation of auxiliary trails.
- Added `auxiliary_trails=False` to the signature of `TopologyDiagram.build_trails()`.
- Added `TopologyDiagram.auxiliary_trails()` iterator.
- Added `TopologyDiagram.auxiliary_trail_edges()` iterator.
- Added `TopologyDiagram.is_auxiliary_trail_edge()` edge filter.
- Added `TopologyDiagram.number_of_auxiliary_trails()`.
- Added property `TopologyDiagram.auxiliary_trail_length` with setter.
- Added property `TopologyDiagram.auxiliary_trail_vector` with setter.
- Created first full version of GH plugin under `compas_cem.ghpython.components`

### Changed

- Changed `TopologyDiagram.trails()` to return an iterable of trails instead of a dictionary.
- Changed `TopologyDiagram.build_trails()` to not return anything.
- The type of a trail is `tuple`, no longer `list` to reflect they are immutable.
- Splitted `Constraint()` into children classes `VectorConstraint()` and `FloatConstraint()`.
- Renamed `error` to `penalty` in `compas_cem.optimization`.
- Refactores examples folder.

### Fixed

- Changed check for `None` in `NodeMixins.node_xyz()`.

### Removed

- Removed `None` from default arguments in optimization constraints and parameters.

## [0.1.6] 2021-07-05

### Added

- Implemented `TopologyArtist` and `FormArtist`
- Added `compas_cem.rhino_install` to streamline the symlink with Rhino
- Added `src/compas_cem/ghpython/components/ghuser/` to `.gitignore`

### Changed

- Refactored `compas_cem.rhino_install` into `compas_cem.ghpython.install`
- Refactored `compas_cem.rhino_install` into `compas_cem.ghpython.uninstall`

### Removed

- Removed `compas_cem.rhino_install`

## [0.1.4] 2021-07-04

### Added

### Changed

### Removed

- Deleted tag regex from `.bumpversion.cfg`

## [0.1.3] 2021-07-04

### Added

- Added automatic tag versioning to `CHANGELOG.md`

### Changed

- Renamed `CHANGELOG.md` to `CHANGELOG.rst`

### Removed
