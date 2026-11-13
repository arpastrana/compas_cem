# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- Added `compas_cem.ghpython.cross_lines`, the lines of the cross that marks a loaded node, which Draw Topology and the viewer both draw.
- Added `topology_drawing` with `TopologyDrawing` and `StyledPolyline` to `compas_cem.ghpython`, the style rules of Draw Topology in plain Python, and `TopologyPreview`, its Rhino geometry. Draw Form's and Draw Topology's rules share `diagram_display.py`, and their previews `diagram_preview.py`.
- Added `LOAD_CROSS_SIZE` to `compas_cem`: how far a load cross reaches from its node, as a fraction of the diagram's bounding-box diagonal.
- Added a Form Display Settings component in grasshopper that sets how Draw Form draws a form: `force_min` for the smallest load or reaction force to draw, `arrow_scale` for the length of their arrows, named apart from `force_min` so neither reads as the other, `width_min` and `width_max` for the edge widths in pixels, and `radius_min` and `radius_max` for the pipe radii in model units, `radius_max` also sizing the thickened nodes. Its `settings` output is a frozen dataclass rather than a named tuple, since Grasshopper unpacks a tuple output into its items.
- Added `ARROW_HEADPORTION`, `ARROW_HEADWIDTH` and `ARROW_BODYWIDTH` to `compas_cem`, the arrow proportions as fractions of an arrow's length (head length, head radius, body radius), with `_2D` variants for the plotter, whose widths are full widths as matplotlib takes them. Every engine draws its arrows with them.
- Added `form_drawing`, `FormDisplaySettings`, `edge_widths`, `edge_radii` and `reaction_shifts` to `compas_cem.ghpython`: the style rules of Draw Form in plain Python, testable outside Rhino. Added `FormPreview`, which turns them into Rhino geometry once per solution so a viewport redraw only loops over Rhino objects.
- Added `TopologyDiagram.auxiliary_support_nodes`, which yields the support nodes that end the auxiliary trails, not their origin nodes.
- Added an `is_absolute` flag to every optimization parameter. With `is_absolute=True`, `bound_low` and `bound_up` are the values the parameter may take instead of distances from its start value, and edge bounds are signed, negative in compression. It defaults to `False` and is saved with the parameter's data, so scripts and files that predate it keep their relative bounds.
- Added `Optimizer.check_start_bounds`, which `solve` runs first: a parameter whose start value lies outside its bounds raises a `ValueError` naming the parameter, its start value and its bounds, where NLopt raised a bare `invalid_argument`. Absolute bounds can exclude the start value; relative bounds always contain it.

### Changed

- Added a `bake` input to Draw Form and Draw Topology. Wired to a Button, every press adds the drawing to the Rhino document as one undo step, each category on its own sublayer of `COMPAS CEM::Form` or `COMPAS CEM::Topology`. Lines bake with their colors and plot weights, loads and reactions with an arrowhead, deviation edges with Rhino's dashed linetype, loaded only if the document lacks one, and thickened meshes with their colors and a render material of the same color, named after its hex code and reused across bakes, since rendered views shade a mesh with its material rather than its display color. Labels, the support and origin nodes, which repeat nodes, and the trails, which repeat trail edges, are not baked. The outputs' model objects cannot carry arrowheads or linetypes, and a Line or Curve parameter keeps only the geometry, so baking from the outputs lost what the button keeps.
- Added `thick_sides` to Form Display Settings, the number of faces around every thickened pipe, arrow and node sphere, 8 by default and at least 3.
- Revised the descriptions and docstrings of the Grasshopper components: the draw components' outputs explain where their colors survive, the toggles read as "Whether to…", every code docstring matches its component's description, and duplicated, misspelled and misattributed descriptions are fixed.
- Added `decompose`, `show_loads`, `show_reactions` and `show_labels` toggles to Draw Form. `decompose`, on by default, draws every load and reaction force as up to three arrows, one per x, y and z component, each placed and cleared like a whole arrow, and skips a component smaller than `force_min`. `show_loads` and `show_reactions`, on by default, hide their category everywhere: it neither previews nor bakes, and its output is empty, so the outputs always match the drawing. The names match the form plotter's. `show_labels`, off by default, labels every drawn edge with its force in the viewport only; it moved from Form Display Settings, since a toggle is reached for more often than the settings. `FormDisplaySettings` keeps all four as fields, so a script sets every display option in one place, and Draw Form sets them from its toggles.
- Made Trail Edge and Deviation Edge warn when a line is connected but an input they need is missing, where they returned nothing silently: Trail Edge without a length or a plane, or with a length but no `state`; Deviation Edge without a `state` or a `force`. Components already placed in a definition keep their old code.
- Made the viewer skip a force arrow without length, from a zero scale or a zero force, which has no axis to build its cylinder and cone on. Draw Form now draws a form without edges, and the viewer a topology without nodes, where both raised on an empty sequence.
- Made Draw Topology draw the topology in color, with the topology plotter's defaults: nodes by type (supports green, origin nodes purple, the rest light gray), edges by the state their length or force sets (blue in compression, red in tension, auxiliary trails orange), deviation edges always dashed, and a black cross at every loaded node. Its outputs keep their names and become Rhino 8 model objects that bake with their colors and a 2 px plot weight, drawn by the component with their default preview off, as Draw Form's are. `loads` now holds the crosses, two lines per loaded node in the XY plane, so it bakes what is drawn; the load lines are gone, along with `force_min` and `force_scale`. Deviation edges are dashed in the viewport, and bake dashed through the `bake` input. A `show_labels` toggle, off by default, labels the drawn nodes with their keys and the drawn edges with `u-v`, in the viewport only. Components already placed in a definition keep their inputs and outputs.
- Made the viewer mark the loaded nodes of a topology with the same crosses instead of arrows, as the topology plotter and Draw Topology do.
- Made Draw Form draw the form in color. Edges are red in tension and blue in compression, with widths spread linearly over the settings' bounds by absolute force across the whole form, so a selection keeps its widths. Free nodes are light gray, so they show against a white background, and supports green; loads are green and reactions gray, drawn as lines halfway between the width bounds that end in Rhino's own arrowhead, sized on screen as Grasshopper draws a vector; a shaded cone read as a solid in a line drawing. A selected Draw Form takes Grasshopper's selection color.
- Made Draw Form's outputs Rhino 8 model objects that carry each item's color and plot weight. The outputs keep their names and still plug into Line, Curve and Point inputs, which keep the geometry only; a Model Object or Data parameter keeps the attributes too. The plot weight is the pixel width at 96 dpi, so Print Display shows baked lines at their preview width. Model objects drop curve arrowheads, so a load or reaction collected from an output bakes as a plain line.
- Made Draw Form draw its own outputs and switch their default preview off on every solve, since Grasshopper's preview ignores per-item colors. The component's Preview switches the drawing on and off. Grasshopper does not bake hidden outputs, so the right-click Bake of Draw Form and Draw Topology does nothing; their `bake` input does the baking instead. A data type written in Python could preview and bake per output, but Grasshopper cannot convert it into Line or Curve inputs, which would break definitions that pipe the edges.
- Added a `thicken` input to Draw Form, off by default. When on, the nodes become spheres of radius `radius_max`, the edges capped pipe meshes whose radii spread by absolute force over the settings' `radius_min` and `radius_max`, and the loads and reactions solid arrows. Every output then holds meshes, which bake with their colors, so a definition that expects points or lines downstream must keep `thicken` off. A sphere is as wide as the widest pipe, every pipe stops one sphere radius short of its nodes, since a sphere is meshed with flat faces inside its true surface and a pipe trimmed only to meet the true sphere still poked through, and the arrows move along their own direction by the sphere radius, back when they end at a node and ahead when they start at it, so neither end hides inside a sphere. The meshes are merged into one per color for drawing; a solve with 10,000 edges builds them in about 0.35 s.
- Gave every arrow the same proportions, as fractions of its length, so the CEM engines draw forces alike. The plotter draws matplotlib `FancyArrow` patches in one collection, in place of compas_plotter's arrows of a fixed screen size. The viewer draws a cylinder body and a cone head, in place of compas_viewer's vectors. Draw Form uses the same cone in both modes.
- Made every load arrow end at its node, so its head touches the node it loads, in the plotter, the viewer, Draw Form and the load lines of Draw Topology. Loads started at their node and pointed away, which read as a force leaving it. Reactions keep their rule: they end at a support they push into.
- Moved Draw Form's `force_min` and `force_scale` into Form Display Settings, and corrected the `form` description, which called it a topology diagram. Components already placed in a definition keep their inputs and plain outputs.
- Made `FormDiagramObject` take its reaction shifts from the shared `reaction_shifts`.
- Renamed Edge Forces and Lengths to Edge Forces and removed its `lengths` output, which returned the stored signed length whose sign follows the force and confused post-processing. `forces` stays signed, negative in compression. Unsigned lengths come from the Length component on Draw Form's `edges`, which follow the same `edge_keys`. Components already placed in a definition keep both outputs.
- Added a `filter_auxiliary` input to Disassemble Topology in grasshopper. When `True`, every output leaves out the auxiliary trails, their edges and their support nodes: `auxiliary_trail_keys` comes out empty, `trail_keys` loses only the auxiliary trails, and `sequence_keys` loses the auxiliary support nodes but keeps every sequence, an emptied one as an empty tuple, so a tuple's position stays its sequence number, as the library already does for sequences without nodes. Origin nodes stay, since an auxiliary trail starts at a node of the structure.
- Added a toggle as the first input of the JSON components: `read` on Import Topology Diagram and Import Form Diagram, `export` on Export Diagram, so a file is read or written only on demand. While it is off, the components output nothing; Export Diagram outputs `data` only on the run that writes the file. `import` is a Python keyword, so it cannot name an input.
- Made the bounds of the eight Grasshopper parameter components absolute: they now set `is_absolute=True`, since bounds relative to the start value were hard to read. Components already placed in a definition keep their relative bounds. Corrected the node key description of the three load parameter components, which named an origin node where any loaded node applies.
- Added a `state` input under `line` to the Trail Edge and Deviation Edge components. Its sign sets tension (positive) or compression (negative), the components take only the absolute value of `length` and `force`, and a zero `state` raises a warning. Trail Edge takes either a `length` or a `plane`, with a warning when both are connected; with a plane, `state` is optional and signs the unit length Trail Edge stores, so the topology records the intended state and Draw Topology colors the edge by it; the plane's position still ends the trail when the form is found, and the length applies only to a trail that never meets the plane. An unsigned placeholder drew every compression trail ending at a plane in red.
- Corrected the `TrailEdge` docstring and the Trail Edge `plane` description, which said a plane keeps the length's sign. The solver replaces the signed length with the distance to the plane, so the plane's position sets the state, and the length applies only if the trail runs parallel to the plane.
- Called the CEM the combinatorial equilibrium method instead of the Combinatorial Equilibrium Modeling framework, as the repository description does: in the README and the documentation's home page, which now describe the 3D bar systems it models and their purely axial forces, and in the site description, the PyPI summary, the package docstring, the yak manifest, the software citation and the Colors component's description.
- Raised the Grasshopper components' `compas_cem` requirement to the current version and added it to `bump-my-version`, so every release raises it, with `test_component_headers` to catch a stale header. Rhino upgrades the library only when the requirement rises above the version it holds, so under the 0.9.1 plugin a Rhino holding 0.9.0 kept it and Info reported v0.9.0.
- Switched the license metadata to PEP 639: an SPDX `license = "MIT"` and `license-files = ["LICENSE", "AUTHORS.md"]` replace the `license` table and the `License ::` classifier, which setuptools deprecates and stops supporting in builds from 2027-02-18. The build now requires setuptools 77.0.3: 77.0 added the fields, 77.0.0 and 77.0.2 have no files on PyPI, and 77.0.3 fixed their first bugs. The wheel and sdist ship the same two license files as before, which setuptools' default globs already picked up, and their metadata now reads `License-Expression: MIT`.

### Removed

## [0.9.1] 2026-11-11

### Added

- Added uv instructions: `uv add` and `uv pip install` in the installation guide and the README, and `uv sync --extra dev` with `uv run` for contributors, pinned by a committed `uv.lock`. `.gitignore` excluded the lock on the belief that it would pin every CI job, but CI installs with pip, and uv's pip interface ignores a lock anyway. The pip commands stay as the fallback, and CI still installs with pip. The development tools stay in the `dev` extra rather than dependency groups, because `compas-actions` installs `.[dev]`.
- Added an icon for each Grasshopper component, replacing the CEM logo all 38 shared; Info keeps the logo. Each component folder holds the TikZ source `icon.tex` beside its `icon.png`, and `components_cpython/icon_style.tex` holds the shared palette, group tiles and styles. The icons follow the conventions of the CEM diagrams and the Grasshopper icon guide's empty border and drop shadow. Each tile is framed in a dark shade of its group's color, since a light frame washed out in Grasshopper.
- Added the `build-icons` task, which renders each `icon.tex` into a 24 px `icon.png` with its drop shadow. It needs `pdflatex` and `pdftocairo`; the icons are committed, so building the plugin does not.
- Added `pillow` to the `dev` extra, which `tasks.py` imports for the drop shadow.

### Changed

- Refreshed `.editorconfig` from the 2021 template so editors agree with the pre-commit hooks: two-space indentation now covers `.yaml` as well as `.yml`, Python uses ruff's 88 columns, and the Markdown and `LICENSE` exceptions, which the whitespace and end-of-file hooks undo, are gone with the `Makefile` and Windows script sections that matched no file.
- Limited `uv.lock` to Python 3.11 and newer through `[tool.uv] environments`. Resolved for 3.9 and 3.10 too, the lock pinned releases of Pillow, filelock, urllib3, cryptography and other development and plotting dependencies that have no security fix for those Pythons, which opened about a hundred Dependabot alerts. The package still supports Python 3.9, CI still tests 3.9 to 3.13 with pip, and work on 3.9 or 3.10 uses the pip route.
- Extended the copyright years in `LICENSE` from 2020-2021 to 2020-2026, and set `compas_cem.__copyright__` to the license's holder with no year. It read `Copyright 2020 - Princeton University`.
- Moved every workflow to `actions/checkout@v7` and `actions/setup-python@v7`. The `dev-docs` job still ran the deprecated Node 20 releases `checkout@v4` and `setup-python@v5`.
- Replaced the `Zomzog/changelog-checker` action, unmaintained since 2022 and declaring the retired `node12` runtime, with a shell step that lists the pull request's changed files with `gh pr diff --name-only`. The `no changelog` label still skips it.
- Replaced the warning that the Grasshopper plugin is not installable with Package Manager instructions for Rhino 8 in the README and the installation guide. 0.9.0 ships the plugin on the Rhino package server, so the 0.9.0 README on PyPI still carries the outdated warning.
- Pointed the README's links to the examples, the API reference and the citing page at the `latest` documentation instead of `dev`, now that 0.9.0 is published.
- Shrank the header animation to 960 by 540 pixels at 12 frames per second, 4.4 MB, from 1280 by 720 at 24 frames per second and 13.5 MB. PyPI loads README images through an image proxy, so the 0.9.0 page shows a broken image: GitHub's raw file host labels a file that large `application/octet-stream`, and such proxies refuse non-image types and files over about 5 MB, as GitHub's own proxy does for the larger file.

### Removed

- Removed the last conda references: the `conda.recipe/` line in `.gitignore` and conda as a virtual environment example in `CONTRIBUTING.md`. Every dependency installs with pip.

## [0.9.0] 2026-11-10

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
- Added `ghpython/scene_objects.py`, replacing `ghpython/artists.py` with `compas.scene` scene objects that register themselves in the `Grasshopper` context.
- Added `src/compas_cem/ghpython/yak_template/`, holding the `manifest.yml` and the package icon that `yakerize` wraps the built components with.
- Added the `build_cpython_ghuser_components`, `update_gh_header`, `yakerize` and `publish_yak` tasks to `tasks.py`, together with the `ghuser_cpython` and `yak` configuration blocks they read.
- Added a static `instanceGuid` to all 39 component `metadata.json` files. The componentizer mints a fresh random GUID whenever the field is absent, so every build emitted different GUIDs and broke the components already placed in a `.gh` file.
- Added a `dev-docs` job that publishes the documentation built from `main` as the `dev` version. `compas-actions.docs` deploys mkdocs on a version tag only, so between releases the site would otherwise show the last release and nothing newer.
- Added a concurrency group to the build, docs and pull request workflows, so pushing to a pull request cancels its own in-flight run instead of queueing a second one. Pushes and tags keep a run-unique group, so a stuck run cannot hold up a deploy.
- Added `workflow_dispatch` to the build and docs workflows, so either can be run by hand.
- Added the yak publish to the release workflow. After the PyPI upload, which the components' `# r:` header installs from, it packages the components with `invoke yakerize` and pushes them with `invoke publish-yak`, authenticated by the `YAK_TOKEN` secret. `compas-actions.publish` only builds the components, so no release had reached the Rhino package server. The push cannot be rehearsed on the test server: it is wiped each night and keeps its own records, so it rejects the API key that `yak login --ci` issues on the production server. A manual run that pushed there built and packaged the components on Windows, then failed with a 401.
- Added a `viz` extra, read from `requirements-viz.txt`, holding `compas_plotter>=1.0.1` and `compas_viewer>=2.0`, the backends of `compas_cem.plotters` and `compas_cem.viewers`. They stay out of the core install so that `compas_cem` stays lean inside Rhino 8, where the viewer would otherwise pull in PySide6 and PyOpenGL for nothing. The `dev` extra includes them. Importing either module without them raises an `ImportError` that names the extra.
- Added a Made with COMPAS badge and a badge linking to the Computer-Aided Design article underpinning the framework to `README.md`.
- Added a pre-commit configuration with ruff check and format, whitespace, end-of-file, YAML, TOML, JSON and merge-conflict checks, and a check that fails when a personal name appears in project prose outside the authorship files, or in a commit message. `invoke lint` runs `ruff check --fix` on `src` and `tests` only and never checks formatting, so the hook is the only check on formatting, `examples` and `tasks.py`. A `pre-commit` job in the pull request checks runs every hook on every file, so these checks also gate merges; commit messages are checked locally only.

### Changed

- Migrated from COMPAS 1.17.10 to `compas>=2.15,<3.0`.
- Rewrote the installation instructions around `pip` and `venv`. conda is being phased out across the COMPAS ecosystem, and `compas` no longer needs installing separately because `compas_cem` declares it.
- Marked the Grasshopper plugin as not installable in this release. It linked into Rhino 6 and 7 through `compas_rhino.install`, which COMPAS 2 removed.
- Renamed `Constraint` to `Goal` throughout, a clean break with no deprecation aliases. The nine concrete classes, the `VectorConstraint` and `FloatConstraint` bases, the `constraints` module, `Optimizer.add_constraint` and `remove_constraint`, and the eight Grasshopper component directories all follow. This frees the name `Constraint` for genuine hard constraints, which nlopt supports and the package does not yet use.
- Made `Diagram.add_node` and `Diagram.add_edge` accept either a node or edge element, or a key with attributes. COMPAS 2 deserializes a graph by replaying `add_node(key=, attr_dict=)` and `add_edge(u, v, attr_dict=)`, which the object-taking overrides shadowed, breaking `copy()` and `from_json()`. Both entry points now dispatch on the argument, so the authoring API is unchanged and deserialization reaches the base graph.
- Made the entry points reject a mismatched element rather than silently treating it as a node key: `add_node` refuses an edge element, `add_edge` refuses a node element, and a key given both positionally and by name raises.
- Folded `NodeMixins` and `EdgeMixins` into `Diagram` and dropped `compas_cem.data.Data` from its bases. `Datastructure.__inheritance__` walks the MRO up to `Datastructure` calling `__clstype__()` on every class in between, so a plain `object` mixin made `to_json()` raise.
- Changed the `tol` diagram attribute from a format string to an integer count of decimal places, following `compas.tolerance.TOL.geometric_key`.
- Ported serialization from the `data` property pair to `__data__` and `__from_data__` on goals and on edge and node parameters.
- Gave `Goal`, `Parameter`, `EdgeParameter` and `NodeParameter` default constructor arguments, so `__from_data__` can build one without knowing the concrete signature.
- Regenerated `examples/03_bridge_2d.json`, which was COMPAS 1.7.1 JSON and unreadable by COMPAS 2. Node and edge insertion order is preserved, because it sets the order of the optimizer's parameter vector.
- Changed `requires-python` from `>=3.8` to `>=3.9,<3.14`, and both CI matrices to 3.9 through 3.13, now that the `distutils` ceiling is gone. The floor is 3.9 because Rhino 8 runs CPython 3.9 and every Grasshopper component installs this package into it; a 3.10 floor made that install fail. The macOS cell for 3.9 is left out because `compas-actions.build` skips it without running anything.
- Replaced the reStructuredText module docstrings and inline markup with Markdown, and moved parameter and return types out of docstrings and into the signature position that mkdocstrings renders.
- Migrated the plotters from `compas_plotters` artists to `compas_plotter>=1.0.1` scene objects, and the viewers from `compas_view2` objects to `compas_viewer>=2.0` scene objects. Both register through `compas.scene.register` on import, because compas discovers scene object plugins in `compas*` packages only.
- Pinned the plotter node size policy to `relative`. The upstream scene object defaults to `absolute`, which divides the node size by the plotter resolution instead of the node count and draws markers two orders of magnitude smaller.
- Drew the topology load crosses straight onto the canvas. A line scene object fixes its own stacking order in its constructor, which put the crosses underneath the opaque node markers.
- Fixed `state_format` in both visualization backends reading an undefined `edge` instead of the edge it was passed.
- Fixed `DiagramObject` referring to `self.topology`, which it never defined.
- Fixed a `show_nodes` setter that assigned to `_show_edges`.
- Fixed `DiagramArtist.draw_reactions` documenting a `min_load` parameter that its signature calls `min_force`, and `TopologyDiagramObject` documenting its argument as `form_diagram`.
- Renamed `ghpython/components/` to `ghpython/components_cpython/`, matching `compas_fab` and the CPython-only component format that Rhino 8 loads.
- Named every Grasshopper component `<name> (COMPAS CEM)` instead of `COMPAS CEM: <name>`. The componentizer only knows a prefix, so the suffix lives in each `metadata.json` name and the `prefix` settings in `tasks.py` and `release.yml` are gone. The instance GUIDs are unchanged, so components already placed in a definition still resolve.
- Renamed the Form Artist and Topology Artist components to Draw Form and Draw Topology, and the `08_Artists` subcategory to `08_Visualization`. Their directories are now `CompasCem_DrawForm`, `CompasCem_DrawTopology` and `CompasCem_Colors`. COMPAS 2 replaced artists with scene objects, so the artist vocabulary was legacy. The instance GUIDs are unchanged. A plotter docstring and the quick start example drop the word too.
- Made the Constrained Form-Finding component solve in-process. It solved through `compas.rpc.Proxy`, which finds its interpreter through the `compas_bootstrapper` module that the COMPAS 1 Rhino installer wrote, so under COMPAS 2 it launched whatever `python` was on Rhino's path, without `compas_cem`. Rhino 8 runs CPython, so nlopt and autograd run inside Rhino and the component drives `Optimizer` directly, as the Python examples do.
- Ported all 39 Grasshopper components to Rhino 8 CPython: a `# r: compas_cem>=0.9.0` requirements header, `Grasshopper.Kernel.GH_ScriptInstance` in place of `ghpythonlib.componentbase.executingcomponent`, PEP 484 annotations on `RunScript`, and the injected `ghenv.Component` in place of `self`, which is no longer the component.
- Ported the 13 components that read Rhino geometry from the removed `compas_rhino.geometry.Rhino*` wrappers to the `compas_rhino.conversions` functions that replaced them.
- Annotated component inputs as optional where Grasshopper passes `None` for an unconnected input, under `from __future__ import annotations` so that Rhino 8, which is CPython 3.9, does not evaluate the unions at definition time.
- Read node positions in the Grasshopper scene objects from the scene object rather than from the diagram, so a transformation set on the object applies to everything it draws.
- Built the documentation on Python 3.12 instead of the `compas-actions.docs` default of 3.10. On 3.10 the resolver pairs `pymdown-extensions` 12, whose highlighter gained a required argument, with `mkdocstrings` 1.0.6, the last release for 3.10, which does not pass it, so every API page fails to render.
- Moved the release publish job from `ubuntu-latest` to `windows-latest` and gave it the component-building inputs, because the componentizer loads `GH_IO.dll`.
- Fixed `_draw_forces` normalizing a force vector before testing its magnitude, which divided by a zero length at a node carrying no load or reaction.
- Fixed the Draw Form and Draw Topology components passing their diagram positionally to the scene object. The first parameter of a COMPAS 2 graph scene object is `show_nodes`, so the diagram never reached the object and every draw failed on a `None` graph. Both now pass it as `item`.
- Fixed the Export Diagram component returning `diagram.data`, which COMPAS 2 replaced with `__data__`, so it raised after writing the file. It now returns the JSON string it wrote, from `to_jsonstring`, which `from_jsonstring` can read back.
- Fixed `draw_reactions` raising on a node with no connected edge, where it searched an empty sequence for the strongest edge force.
- Fixed the topology JSON import component declaring a class named `FormDiagramFromJSON` and documenting itself as importing a form diagram.
- Fixed a `typeHinID` misspelling in the Draw Topology component's `metadata.json`, which left two of its inputs without a type hint.
- Replaced `rs.AddPoint` in the support node results component with `point_to_rhino`. The `rhinoscriptsyntax` call bakes a point into the Rhino document instead of returning geometry to the component output.
- Returned an empty list rather than `None` from the topology draw methods when a selection is empty.
- Fixed the five Python example pages showing `--8 < --"examples/…"` instead of the example source. A pymdownx snippet marker is valid python, so `ruff format` reformatted it as an expression inside the fenced block and the include stopped resolving. Markdown is now excluded from the formatter.
- Moved the documentation from Sphinx and reStructuredText to mkdocs-material with mkdocstrings.
- Converted `README`, `CHANGELOG` and `AUTHORS` from reStructuredText to Markdown.
- Replaced the abandoned `pytest-lazy-fixture` with `pytest-lazy-fixtures`, which lifts the `pytest<8` ceiling.
- Rewrote `tasks.py` to compose `compas_invocations2` tasks.
- Updated CI to `compas-actions.build@v5`, `compas-actions.docs@v5` and `compas-actions.publish@v3`.
- Replaced the Zenodo badge in `README.md` with a static shields.io badge on the concept DOI `10.5281/zenodo.5705740`, which always resolves to the latest deposit. The badge Zenodo generates is rendered on request and frequently times out behind the GitHub image proxy, so it showed up broken.
- Fixed the badges and links in `README.md`. The Python badge read the classifiers of the latest PyPI release, so it showed 3.8 and 3.9; it now reads `requires-python` from `pyproject.toml` on `main`. The documentation links pointed at Sphinx pages the mkdocs site does not have, and the COMPAS tutorial and API links at pages COMPAS 2 moved. The build badge uses the current workflow badge URL.
- Shrank the header animation from 3200 by 1800 pixels and 76.5 MB to 1280 by 720 pixels and 13.5 MB, renamed it `staircase.gif`, and linked it from `README.md` by absolute URL. PyPI does not host the repository's files, so the relative path showed as a broken image on the package page.
- Replaced flake8, isort, doc8 and pydocstyle with ruff, and reformatted the code base to 88 columns.
- Loosened dependency version from `numpy<2` to `numpy>=1.26`. The upper bound was never necessary; the test suite passes on numpy 2.
- Pinned ruff to 0.16.1 in `requirements-dev.txt`, matching the pre-commit hook, so the hook, `invoke lint` and CI run the same ruff.
- Replaced the stale `master` branch with `main` in `CONTRIBUTING.md` and dropped it from the pull request checks trigger.

### Removed

- Removed the dependency on `trimesh`. It was never imported: its only reference is `optimization/goals/mesh.py`, which is commented out of the package.
- Removed `.travis.yml`, which targeted Python 2.7.
- Removed the `compas_cem.diagrams.mixins` package, folded into `Diagram`.
- Removed `Diagram.connected_edges`, superseded by `node_connected_edges`. COMPAS 2 gives the inherited name a different meaning: it takes no node and returns edge groups per connected component.
- Removed `plotters/proxy.py`. It was dead code calling a `FormPlotter` and a `TopologyPlotter` that no longer exist.
- Removed the `FormArtist`, `TopologyArtist` and `DiagramArtist` plotter classes and the `register_artists` plugin, superseded by the plotter scene objects.
- Removed `ghpython/install.py` and `ghpython/uninstall.py`, and with them the `installable_rhino_packages` and `after_rhino_install` plugin hooks. Grasshopper components ship through yak only.
- Removed `ghpython/artists.py` and `ghpython/register.py`, superseded by the Grasshopper scene objects, which register on import as the plotter and viewer ones do.
- Removed the `__all_plugins__` declaration from `compas_cem/__init__.py`, which named the three deleted modules.
- Removed the Proxy Server Grasshopper component. It only started and stopped the RPC server that the Constrained Form-Finding component no longer uses.
- Removed `optimization.solve_proxy` and the `compas_cem.PROXY_PORT` constant. They existed only for the RPC call that the Constrained Form-Finding component no longer makes. A solver that cannot run inside Rhino, such as a JAX backend on Rhino 8's Python 3.9, would need its own entry point, not this nlopt wrapper.
- Removed `isAdvancedMode` from all 39 component `metadata.json` files. It only meant anything to the Rhino 7 IronPython component format.

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
