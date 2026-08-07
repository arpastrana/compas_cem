# compas_cem modernization plan

Status: **Phases 0 and 1 complete.** Phase 2 in progress. Target release
**0.9.0**, deliberately breaking.

Written 2026-08-06. Everything marked *verified* below was tested against
COMPAS 2.15.1 / Python 3.12 / JAX 0.10.2; everything marked *unverified* was not.

§1 and §2 describe the **pre-migration** state and are deliberately left as a
snapshot — Phase 0 has since changed the packaging, docs, CI, and dependency
pins described there. §9 records what Phase 0 actually found and changed.

---

## 1. Why this exists

`compas_cem` 0.8.6 (last release 2025-02-24, preceded by a 21-month gap) does not
run on any current stack. It pins `compas==1.17.10`, `numpy<2`,
`trimesh==3.20.0`, `pytest==7.2.1` (locked to the dead `pytest-lazy-fixture`),
`flake8==5.0.4`, and Sphinx on the archived `sphinx_compas_theme`. `.travis.yml`
still targets Python 2.7. `release.yml` uses `::set-output`, disabled by GitHub in
2023. CI tests Python 3.9 only. `optimization/`, `plotters/`, `viewers/` and
`ghpython/` have no tests at all.

Two migrations are wanted: **COMPAS 1.x → 2.x**, and **autograd → JAX**.

## 2. How the package works today

`Diagram(Data, NodeMixins, EdgeMixins, Network)` subclasses COMPAS `Network`, with
`TopologyDiagram` (input) and `FormDiagram` (output). All CEM state lives in
ordinary node/edge attribute dicts.

Edges are **trail** (signed `length`) or **deviation** (signed `force`); the sign
carries the compression/tension state. `build_trails()` walks back from each
support to an origin node and stamps each node with a sequence index `_k`. A
deviation edge is **direct** when both endpoints share a `_k`, **indirect**
otherwise — that distinction is the whole algorithm.

The solver (`equilibrium/force.py`, vectorized in `force_numpy.py`) is two nested
loops: an inner pass over sequences advancing each trail
(`r_out = r_in − q − R_direct − R_indirect`, then
`xyz_next = xyz + length · r̂_out`), and an outer relaxation over `t ≤ tmax`
because indirect deviation edges reference nodes whose positions are not yet
known. Indirect edges are excluded on `t == 0`.

`optimization/` holds 8 `Parameter` classes and 9 `Constraint` classes as soft
penalties summed to one scalar, driven by `nlopt`'s `LD_*` algorithms with
`autograd.grad`.

**The load-bearing hack.** Differentiation runs *through the mutable COMPAS
datastructure*: `_update_parameters` writes autograd boxes into
`topology.node[k]["x"]` and `equilibrium_state_numpy` reads them back. It only
works because the gradient pass gets a `topology.copy()` (`optimizer.py:207`) to
quarantine the boxes while the objective pass (`:216`) mutates the live diagram
with plain floats. Consequences: value and gradient are two separate forward
passes on two different objects, a full deepcopy per `solve()`, and ~7
data-dependent Python branches that autograd tolerates and `jit` would not.

39 Grasshopper components (IronPython 2.7, Rhino 6/7) reach the CPython solver
over `compas.rpc.Proxy` on port 7123.

## 3. Prior art — read this before writing any kernel code

**`arpastrana/jax_cem` already exists**: public, MIT, ~900 LOC, developed
2023–2025, numerically validated against `compas_cem`. `lax.scan` over sequences,
`vmap` over nodes within a sequence, `-1` padding + masks for shifted/unequal
trails, `copysign` force signing, three double-`where` NaN guards.

Use its **`origin/refactor` branch**, not `main`: it splits
`ParameterState` / `EquilibriumStructure` / `EquilibriumModel`, fixes two NaN
bugs, and deleted its own COMPAS bridge in favour of calling `compas_cem`'s
`FormDiagram.from_equilibrium_state` — which is why that method was added here in
0.8.5. `models.py` (510 of the 900 lines) has no COMPAS dependency.

What it lacks: any optimizer layer (examples hand-roll
`scipy.optimize.minimize`), `kmax`, `callback`, and implicit differentiation.

**`jax_fdm` is already on `compas>=2.15,<3.0`** with `compas_plotter>=1.0.1` and
`compas_viewer>=2.0`. It is a working migrated template for every layer needed
here: `ParameterManager`, `Loss(*Error|Regularizer)`, scipy-backed optimizers with
fused jitted `value_and_grad`, `visualization/*/scene_objects.py`, and
`equilibrium/solvers/fixed_point.py` (`custom_vjp` + `lineax` adjoint).

**formax** is the intended future: `jax_fdm` and `jax_cem` consolidating into one
differentiable form-finding framework. `compas_cem` should therefore become the
COMPAS-facing modelling + CAD layer over a **pluggable** kernel, and must not let
kernel types leak into its public API.

## 4. Verified findings

### 4.1 COMPAS 2 core migration is small — 43 lines, 8 files

A scratch copy of the core (diagrams, elements, loads, supports, equilibrium)
solves correctly under COMPAS 2.15.1 after 43 changed lines, reproducing
`tests/equilibrium/test_force.py::bt2_out` to all 16 digits. Full fix list:

| Break | Fix |
| --- | --- |
| `compas.utilities.geometric_key` | `compas.tolerance.TOL.geometric_key` |
| `compas.utilities.pairwise` / `iterable_like` / `flatten` | `compas.itertools` |
| `compas.datastructures.Network` | `Graph` (`Network is Graph` is still a live alias) |
| `attributes["tol"] = "3f"` | `= 3`. **Semantic change**: 1.x took a format string, 2.x takes an int decimal count |
| `topology.has_edge(*edge)` | `has_edge(edge)` |
| `form.edge_length(u, v)` | `edge_length((u, v))`; same for `edge_midpoint`, `edge_vector`, `edge_coordinates` |
| `self.connected_edges(node)` | **Silently changed meaning** — 2.x `connected_edges(self)` returns edge groups per connected component. No drop-in; needs a helper over `neighbors()` |
| object-taking `add_node`/`add_edge` overrides | `Graph.__from_data__` calls `add_node(key=, attr_dict=)`. Breaks `copy()`, `from_json()`, and `FormDiagram.from_topology_diagram` |
| `NodeMixins`/`EdgeMixins` are plain `object` subclasses | **In no migration guide.** `Datastructure.__inheritance__` walks the MRO to `Datastructure` calling `cls.__clstype__()` on everything between, so a non-`Data` mixin makes `to_json()` raise. Fix by folding the mixins into `Diagram` |
| `compas.numerical.connectivity_matrix` | `compas.matrices.connectivity_matrix` |

Two more, from the migration guide rather than the spike: `Data.data` →
`__data__`, `dtype` → `__dtype__`, `from_data` → `__from_data__`, with
`DATASCHEMA`/`JSONSCHEMANAME` removed; and **COMPAS 1 JSON files are not readable
by COMPAS 2**, so `examples/03_bridge_2d.json` and `examples/data/*.json` must be
regenerated.

### 4.2 Pre-existing serialization bug

`attributes["_trails"]` is `{int origin_node: tuple_of_nodes}` and COMPAS
serializes `attributes` verbatim with no key round-tripping:

```
original  _trails: {2: (2, 1, 0)}
roundtrip _trails: {'2': [2, 1, 0]}
t2.trail(2)  ->  KeyError: 2
```

`static_equilibrium` still works on a deserialized diagram by accident (the
stringified key is read and written consistently), but `trail(key)`,
`trail_sequences(key)` and `shift_trail(key, ...)` — all public, all used by the
Grasshopper components — are broken on anything loaded from JSON. This is a 1.x
bug, not a 2.x regression.

### 4.3 The JAX kernel architecture, validated

`proto_jax_cem.py` (in this folder) rebuilds the kernel from scratch and validates
it on `braced_tower_2d`, the only fixture with both direct and indirect deviation
edges:

- **numerical parity PASS** under `jax.jit` — 6 node positions, 4 trail forces, 2 reactions;
- **gradient parity PASS** — implicit-diff reverse mode vs central differences, max abs error **8.7e-11**.

Three findings, the third a trap:

1. **Direct vs indirect only matters for the `t == 0` mask.** Both resultants read
   the same `scan` carry, which already holds current-iteration positions for
   sequences `≤ k` and last-iteration for `> k` — exactly what the Python loop
   does, for free. One `segment_sum` over all deviation edges suffices.
2. **`lax.while_loop` is not reverse-differentiable.** A faithful port of the
   `eta`-terminated loop gives correct values but `jax.grad` raises. The outer
   relaxation must be posed as a fixed point with implicit differentiation. This
   is why `jax_cem` uses a checkpointed `while_loop`; `jax_fdm`'s
   `equilibrium/solvers/fixed_point.py` is the better template.
3. **Origin nodes must be pinned to the parameter *inside* the fixed-point map.**
   A sweep never writes them, so as fixed-point variables their rows of `I − J`
   vanish and the adjoint solve is singular (`lineax`: "operator was not
   well-posed"). Overwriting them from the parameter zeroes those Jacobian rows
   instead. Needs a regression test.

### 4.4 Rhino 8 is CPython 3.9.11 — that, not C extensions, is the constraint

Rhino 8's ScriptEditor uses pip and does install binary C-extension wheels
(numpy, scikit-learn, even torch are reported working in-process). Rhino 9 WIP
ships CPython 3.13.3. Wheel ceiling on 3.9, verified against PyPI respecting
`requires_python`:

| package | max on Rhino 8 (py3.9) | latest |
| --- | --- | --- |
| `jaxlib` / `jax` | **0.4.30** (Jul 2024) | 0.11.0 |
| `lineax` | **0.0.7** | 0.1.1 |
| `optimistix` | **0.0.10** | 0.1.0 |
| `equinox` | 0.11.10 | 0.13.8 |
| `nlopt` | 2.9.1 | 2.11.0 |
| `numpy` | 2.0.2 | 2.5.1 |
| `scipy` | 1.13.1 | 1.18.0 |
| `autograd` | 1.8.0 | 1.9.1 |
| `compas` | 2.15.1 | 2.15.1 |

**The decisive consequence:** `lineax` caps at 0.0.7 on py3.9, but `jax_fdm`
requires `lineax>=0.1.0` for the `Normal` operator used by its fixed-point
adjoint. The implicit-differentiation machinery **cannot be installed inside
Rhino 8 at all.** Keeping `compas.rpc.Proxy` for the JAX path is forced, not
chosen.

Also: **no report exists anywhere** (McNeel Discourse, COMPAS forum, compas-dev
issues) of anyone running `jax` inside Rhino 8. Nearest precedent is torch, which
worked in-process but crashed Rhino on file reopen until McNeel fixed it in 8.3
RC. *Unverified* whether `jaxlib 0.4.30` imports and traces inside Rhino at all.

### 4.5 Grasshopper / Rhino 8 API map

| COMPAS 1.x | COMPAS 2.15.1 |
| --- | --- |
| `compas_rhino.geometry.RhinoPoint/Line/Plane/Vector/Polyline` (~78 uses) | removed → `compas_rhino.conversions.{point,line,plane,vector,polyline}_to_compas`; GH curve inputs use `curve_to_compas_polyline` |
| `compas_ghpython.draw_points/draw_lines/draw_polylines` | still exist but **no longer top-level re-exports** → `compas_ghpython.drawing` |
| `compas_ghpython.artists.NetworkArtist` / `MeshArtist` | removed → `compas_ghpython.scene.GraphObject` / `MeshObject` |
| `compas_ghpython.utilities.ghtree_to_list` | **`compas_ghpython.utilities` no longer exists** → `compas_ghpython.sets` |
| `compas.artists.Artist` + `Artist.register(..., context="Grasshopper")` | **`compas.artists` removed** → `compas.scene.register(item_type, sceneobject_type, context=...)`; subclass `compas_ghpython.scene.GHSceneObject` |
| `compas.datastructures.network_transformed` | removed, no function replacement → `Graph.transformed(T)` method |
| `compas_ghpython.components.install_userobjects` / `fetch_ghio_lib` / `compas.plugins.plugin` | unchanged |
| `compas.rpc.Proxy` | alive, near-unchanged — `capture_output` now defaults `True`, new `path` / `working_directory` |

Component format: `# r: compas_cem>=x.y.z` header,
`ghpythonlib.componentbase.executingcomponent` → `Grasshopper.Kernel.GH_ScriptInstance`,
PEP 484 annotations on `RunScript`. Subtle: **`self` is no longer the component**,
so `self.Component`/`self.RuntimeMessages` are gone — use the injected
`ghenv.Component` (with `# noqa: F821`). `scriptcontext.sticky` still works. In
`metadata.json`, drop `isAdvancedMode` and swap `marshalOutGuids` →
`marshalGuids`; everything else ports as-is.

`compas_fab` ships `components_cpython/` **only**, with **no `install.py`** — the
`installable_rhino_packages`/`after_rhino_install` path is abandoned for yak.

## 5. Decisions taken

| Decision | Choice |
| --- | --- |
| ruff line length | **88** (matching `jax_fdm`/`smax`, not the COMPAS template's 179). Set in `[tool.ruff]`, `[tool.ruff.lint.pycodestyle] max-doc-length`, and `.editorconfig` |
| `Constraint` → `Goal` | **Clean break**, no deprecation aliases. Frees the name `Constraint` for genuine hard constraints later (nlopt's `add_inequality_constraint` is unused today) |
| JAX kernel | **Dependency, not vendored.** Publish the kernel to PyPI, then `compas_cem[jax]` |
| Dependency direction | Move `ParameterState.from_topology_diagram` and `EquilibriumStructure.from_topology_diagram` **down into `compas_cem`** so the kernel depends on `compas` only, never `compas_cem`. Breaks the cycle |
| Parameter system | **Not** a copy of `jax_fdm`'s `ParameterManager` (which self-documents as needing refactor). equinox-native: `ravel_pytree` for flat `x` + free inverse, `eqx.partition`/`combine` for optimizable-vs-frozen, `eqx.tree_at` for injection, bounds as a same-shaped pytree |
| Optimizer backend | **nlopt retained**, fed fused jitted `value_and_grad` |
| formax scope | Undecided. Build the parameter system here for now, designed to be liftable |
| Rhino | **Rhino 8 + 9 only.** Rhino 7 / IronPython dropped |
| GH packaging | **yak only.** `install.py`/`uninstall.py` and the install plugin hooks deleted. `instanceGuid`s preserved so existing `.gh` files still resolve |

## 6. Phases

**Phase 0 — baseline + tooling.** Capture ground truth *first*: a legacy env
(compas 1.17.10, numpy<2, autograd, nlopt≤2.9.1) and recorded outputs for all 5
examples and 5 solver fixtures as JSON regression fixtures. Then adopt
`compas-dev/compas_package_template`: `pyproject.toml` replacing
`setup.py`/`setup.cfg`/`pytest.ini`/`.bumpversion.cfg`, `compas_invocations2`
replacing the 300-line `tasks.py`, `compas-actions.build@v5`/`docs@v5`/`publish@v3`
+ `pr-checks.yml`, Sphinx → mkdocs-material + mkdocstrings + mike, rST →
Markdown, `pytest-lazy-fixture` → `pytest-lazy-fixtures`. Delete `.travis.yml`.
**Do the 88-column reformat as one isolated commit** or every later diff becomes
unreadable.

**Phase 1 — COMPAS 2 core + the rename.** The §4.1 fix list done properly: fold
the mixins into `Diagram`, rename the object-taking `add_node`/`add_edge`, rewrite
`data` getters/setters as `__data__`/`__from_data__`, fix the §4.2 `_trails` bug,
regenerate the JSON fixtures. Plus `Constraint` → `Goal` (9 classes,
`VectorGoal`/`FloatGoal` bases, `goals/` module, `Optimizer.add_goal`, and the
`solve_proxy` wire signature). Green against Phase 0 ground truth ends the phase.

**Phase 2 — visualization.** `compas_plotter` 1.0.1 + `compas_viewer` 2.0.2,
artists → `compas.scene` SceneObjects using `jax_fdm/visualization/*/scene_objects.py`
as the pattern, colours become `compas.colors.Color`. Fix the latent bugs found en
route: undefined `edge` in `state_format` (`viewers/diagramobject.py:679`,
`plotters/topologyartist.py:272`), `self.topology` on `DiagramObject`
(`diagramobject.py:635`), and the `show_nodes` setter writing `_show_edges`
(`diagramobject.py:374`).

**Phase 3 — kernel seam, no vendoring.** `compas_cem` owns the contract both ways:
`TopologyDiagram → (structure, params)` adapters moved down from the kernel, and
`(eqstate, structure) → FormDiagram` via the existing `from_equilibrium_state`
(note its argument order is the reverse of the kernel's `form_from_eqstate`).
Kernel arrives via `compas_cem[jax]`. Upstream to the kernel: jaxtyping shape
annotations replacing bare `jax.Array`, the `node_index`/`edge_index` pytree
hazard (Python dicts annotated as arrays — want `eqx.field(static=True)`), the
per-node → per-edge trail-length/plane debt (a TODO since 2023), and the §4.3
implicit-diff and origin-pinning findings.

**Phase 4 — parameters and goals, equinox-native.** Per §5. Accept knowingly that
`ravel_pytree` orders `x` by pytree traversal, not insertion order as today, so
gradient and bounds vectors will be ordered differently from 0.8.6. `kmax` needs a
masked scan; **`callback` cannot survive traced control flow** — drop it on the
JAX path and document that.

**Phase 5 — Rhino 8 and 9.** Convert the 39 components to `components_cpython` per
§4.5, yak packaging (`yakerize -t rh8` → `publish-yak`), delete the install hooks.
Proxy retained for the JAX path only (§4.4). Revisit in-process on Rhino 9.

Phases 0–2 are fully unblocked. Phase 3 is gated on two upstream tasks in the
kernel repo (decouple from `compas_cem`, publish to PyPI), which can run in
parallel.

## 7. Open questions

1. **Componentizer.** yak packages `.ghuser` files but does not build them.
   Keep `componentize_cpy.py` via `invoke build-cpython-ghuser-components` (what
   `compas_fab` and `compas_timber` do), or something more radical such as
   shipping script components inside a `.gh` library?
2. **Who does the kernel decoupling and PyPI release** — upstream directly, or
   prepared as a branch there once Phases 0–2 land here?
3. **formax and the optimization layer.** If formax inherits `jax_fdm`'s goals,
   losses, parameters and optimizers, then Phase 4's parameter system is
   building what formax will own, and `compas_cem`'s `Optimizer` should shrink to
   a thin adapter. Currently deferred: build here, designed to be lifted.

## 8. Evidence not in this folder

The following were produced during planning in a session-scoped scratchpad and
are **not preserved**. Recreate if needed:

- a patched scratch copy of the core proving the 43-line §4.1 result;
- clones of `arpastrana/jax_cem` (branch `refactor`) and
  `compas-dev/compas_package_template`.

`proto_jax_cem.py` in this folder *is* preserved — it is the §4.3 validation and
runs standalone against any env with `jax` + `optimistix` (verified on JAX 0.10.2,
optimistix 0.1.0).

## 9. Phase 0 outcome

Delivered on branch `phase-0-tooling`. Gate at completion: `ruff check` clean,
`ruff format --check` clean, **92/92 tests pass**, `uv build` produces both sdist
and wheel with all 39 Grasshopper components' assets intact, and re-capturing
every example baseline after the 105-file reformat produced **byte-identical**
JSON — proving the reformat behaviour-preserving.

The baseline environment is `.venv-legacy` (gitignored, built with `uv`):
Python 3.10 + compas 1.17.10 + numpy 2.2.6 + autograd + nlopt 2.11.

### 9.1 Four findings about the 0.8.6 dependency set

1. **`numpy<2` was never necessary.** The full suite passes on numpy 2.2.6.
2. **The documented 0.8.6 stack is uninstallable on Apple Silicon.** `numpy<2`
   forces `nlopt==2.7.1` (2.8.0 onward all require `numpy>=2`), and 2.7.1 ships
   no arm64 macOS wheel — only `macosx_10_9_x86_64`, manylinux, and win_amd64.
3. **`compas==1.17.10` caps Python at 3.11.** It imports
   `distutils.version.LooseVersion`; `distutils` was removed in Python 3.12.
   Hence `requires-python = ">=3.9,<3.12"` and a 3.9–3.11 CI matrix until Phase 1
   moves to COMPAS 2 and lifts both together.
4. **`trimesh` was an unused hard dependency**, referenced only by the
   commented-out `optimization/constraints/mesh.py`, which never imports it.

### 9.2 Examples 04 and 05 do not actually optimize

This changes Phase 4's success criterion and is the most important Phase 0
finding. With nlopt's `stopval` at its default `eps=1e-6`, both examples report
success — but their objective is *already* ~1e-31 at the starting point, because
`TrailEdgeForceConstraint(force=0.0)` on freshly built auxiliary trails is
satisfied from the outset. nlopt exits after 3–9 evaluations having done nothing.

Disabling `stopval` exposes the real behaviour:

| example | evals | penalty | NaN gradient components | status |
| --- | --- | --- | --- | --- |
| 03 bridge | 35 | 1.94e-12 | 0/9 | `FTOL_REACHED` |
| 04 tree | 100 (max) | 9.86e-32, unchanged | 2/3 | `ITERSMAX_REACHED` |
| 05 tensegrity | — | — | — | `nlopt.runtime_error` |

Cause: `nrvec = rvec / trail_force` at `force_numpy.py:157` with
`trail_force == 0` on a zero-force auxiliary trail edge. The `if np.isnan(...)`
guard on the next line repairs the *value* but autograd still propagates NaN
through the *derivative*, so the NaN poisons the gradient vector and LBFGS cannot
move. Example 03, which has no auxiliary trails, is unaffected.

Consequences:

- `tests/baseline/0{4,5}_*.json` are a bar to **beat**, not to reproduce. The
  `*_forced.json` companions record the broken state for comparison.
- Example 03 is currently the only trustworthy optimizer regression target.
- §4.3's double-`where` safe-normalize is the fix, so Phase 3/4 should *repair*
  these two examples rather than preserve their behaviour. Add a regression test
  that a zero-force auxiliary trail yields a finite gradient.

### 9.3 Carried forward

- `mkdocs build --strict` fails on 8 griffe warnings from source docstrings
  (`ghpython/artists.py:282`, `viewers/diagramobject.py:60`,
  `viewers/topologyobject.py:19` document parameters absent from their
  signatures). Phase 1/2.
- Every `src/compas_cem/*/__init__.py` module docstring still contains
  `.. currentmodule::` / `.. autosummary::` rST, which mkdocstrings renders
  verbatim on each API page. Phase 1.
- `docs/installation.md` and `README.md` still document `compas==1.17.10`,
  `compas_view2`, Rhino 6/7 and `compas_rhino.install`. Phase 2/5.
- `gh-pages` needs a one-time migration from the Sphinx layout (`latest/`,
  `doc_versions.txt`) to mike's `versions.json`. Note that `compas-actions.docs@v5`
  publishes only on tag pushes, so `main` no longer updates `latest/`.

## 10. Handover: state and the Phase 1–2 execution order

### 10.1 Where things stand

Phase 0 is on branch `phase-0-tooling`, pushed, and open as **PR #16** against
`main`. Five commits: the plan, the template adoption, the test migration, the
ruff migration, and the Phase 0 write-up.

CI ran for the first time on that PR and is **green** — all nine `build` cells
(3.9/3.10/3.11 × ubuntu/macos/windows), `docs`, and the changelog checker.

Two corrections to earlier sections, both learned from that run:

- **`mkdocs.docs` does not pass `--strict`.** The 8 griffe warnings in §9.3 do
  *not* red the docs job. They are still worth fixing, but they are not blocking.
- **`compas-actions.build@v5` does not skip macOS + Python 3.9.** An earlier note
  claimed it did; that cell ran and passed.

> **Line numbers in §1–§9 predate the 88-column reformat.** The reformat rewrote
> 105 files after that research was done, so `file:line` citations in those
> sections are approximate. Symbol names, call shapes, and file paths are all
> still accurate — re-grep for the symbol rather than trusting the line.

### 10.2 Environments

Neither environment is checked in; both must be built in a fresh clone.

**Legacy baseline env** (`.venv-legacy`, gitignored) — the only environment that
can run pre-Phase-1 code:

```bash
uv venv --python 3.10 .venv-legacy
uv pip install --python .venv-legacy/bin/python --only-binary :all: \
    "compas==1.17.10" "numpy>=2" "trimesh==3.20.0" autograd nlopt \
    "pytest==7.2.1" pytest-lazy-fixtures matplotlib
```

Note `numpy>=2`, not the historical `numpy<2` — see §9.1, items 1 and 2. Do not
install `pytest-lazy-fixture` (singular): merely having it importable breaks
collection on pytest 9.

**Phase 1 needs a second, COMPAS 2 environment.** `.venv-legacy` cannot run
migrated code. Build it as `.venv` (already gitignored) on Python 3.12 with
`compas>=2.15,<3`, `numpy`, `autograd`, `nlopt`, and the `dev` extra.

**Regression harness:** `tests/baseline/capture.py`, verified to reproduce all
five committed fixtures byte-for-byte. Usage, including the `COMPAS_CEM_SUFFIX`
and `COMPAS_CEM_FORCE_EPS` comparison modes, is in its module docstring.

### 10.3 Phase 1 — COMPAS 2 core and the `Goal` rename

Branch off `main` once PR #16 merges. Suggested order, because the dependencies
are real:

1. **Build the COMPAS 2 env** and confirm the package fails the way §4.1 predicts.
2. **Regenerate `examples/03_bridge_2d.json`** and `examples/data/*.json`. COMPAS 1
   JSON is unreadable by COMPAS 2, and example 03 is the *only* trustworthy
   optimizer regression target (§9.2) — losing it costs the phase its safety net.
   Regenerate from the legacy env, then confirm it loads under COMPAS 2.
3. **Apply the §4.1 fix list.** Nine items; all verified.
4. **Fold `NodeMixins` and `EdgeMixins` into `Diagram`.** Fixes the `__clstype__`
   serialization break *and* the fragile `super().__init__` chain in one move.
   Serial work — it changes the MRO, so do not fan this out.
5. **Rename the object-taking `add_node`/`add_edge`** so `Graph.__from_data__`
   stops colliding with them.
6. **Port serialization to `__data__` / `__from_data__`.** Sites: both `data`
   property pairs in `optimization/constraints/constraint.py`, plus
   `optimization/parameters/edge.py` and `optimization/parameters/node.py`. Also
   `Constraint`'s use of `to_data`/`from_data`/`dtype` on its target geometry.
7. **Fix the `_trails` JSON key round-trip** (§4.2) and add a regression test that
   `trail(key)` works on a deserialized diagram.
8. **`Constraint` → `Goal`, clean break.** 9 concrete classes, the
   `VectorConstraint`/`FloatConstraint` bases → `VectorGoal`/`FloatGoal`, the
   `constraints/` module → `goals/`, `Optimizer.add_constraint` → `add_goal`, and
   the `solve_proxy(constraints=...)` wire signature. Also the 8
   `CompasCem_Constraint*` Grasshopper component directories — **preserve each
   `instanceGuid`** so existing `.gh` files still resolve. This step fans out well.
9. **Flip `compas>=2.15,<3`**, widen `requires-python` to `>=3.10,<3.14`, and
   widen both CI matrices to 3.10–3.13 — one commit, since §9.1 item 3 ties them
   together.

Acceptance: 92/92 tests pass; `tests/baseline/capture.py` reproduces the
committed fixtures for examples 01, 02 and 03; `ruff check`/`format --check`
clean; `uv build` still ships the Grasshopper assets; docs build.

Expect examples 04 and 05 to keep failing their baselines — that is §9.2, not a
regression. Do not chase it in Phase 1.

### 10.4 Phase 2 — visualization

`compas.artists` no longer exists. Target `compas_plotter>=1.0.1` and
`compas_viewer>=2.0`, and use `jax_fdm/visualization/{plotters,viewers}/scene_objects.py`
as the pattern — that package is already on COMPAS 2 and solves the same problem.

- **`plotters/`**: `plotter.py` is a pure passthrough wrapper; `formartist.py` and
  `topologyartist.py` are the real work. **Delete `plotters/proxy.py`** — it is
  dead code calling a `FormPlotter`/`TopologyPlotter` that no longer exists.
- **`viewers/`**: `diagramobject.py` is the bulk of the phase and reaches into
  private compas_view2 hooks (`_points_data`, `_lines_data`). Confirm
  `compas_viewer` exposes equivalents before committing to the estimate — this is
  the highest-variance item in the whole plan.
- **Colours**: `compas_cem.COLORS` holds 0–255 int tuples; COMPAS 2 wants
  `compas.colors.Color`. The viewers layer already normalizes via `.rgb`; the
  plotters layer does not.
- **`__all_plugins__`** must point at scene modules, and the two `register.py`
  files move from `Artist.register(..., context=)` to `compas.scene.register`.
- **Geometry constructors**: `Circle(plane, radius)` and
  `Cylinder(circle, height=)` were both reworked in COMPAS 2.

Four latent bugs to fix while in these files, all found during research:
undefined `edge` inside `state_format` in both `viewers/diagramobject.py` and
`plotters/topologyartist.py`; `self.topology` referenced on `DiagramObject`,
which only defines `self.diagram`; and a `show_nodes` setter that writes
`_show_edges`. Also clear the 8 griffe docstring warnings from §9.3 here, since
they live in `ghpython/artists.py`, `viewers/diagramobject.py` and
`viewers/topologyobject.py`.

Acceptance is **human and visual** — there are no tests for this layer and none
are worth inventing. Run examples 01–05 and look at the output. Plan for a
review round rather than a green check.

### 10.5 Open decisions

Neither blocks Phase 1 or 2, but Phase 3 stalls without the first:

1. **Who decouples `jax_cem` from `compas_cem` and publishes it to PyPI** — see
   §5 and the cycle-breaking note. The two `from_topology_diagram` constructors
   move down into this repo; the kernel then depends on `compas` only.
2. **Grasshopper componentizer for Phase 5** — keep `componentize_cpy.py`
   producing `.ghuser` for yak to wrap (what `compas_fab` and `compas_timber` do),
   or ship script components inside a `.gh` library instead.

Also owed before tagging 0.9.0: the `gh-pages` → mike migration, and a throwaway
`v0.9.0-rc1` tag to exercise `release.yml`, which is tag-triggered and therefore
still unverified.

### 10.6 Docstring pass

**142 of 376** public definitions carry no docstring, and a further **30** carry
an empty one. This is a standing requirement across the package, not a one-off
task.

| module | missing | total | rewritten by |
| --- | --- | --- | --- |
| `viewers` | 52 | 70 | Phase 2 |
| `optimization` | 34 | 110 | Phase 4 |
| `plotters` | 25 | 42 | Phase 2 |
| `diagrams` | 15 | 86 | Phase 1 (lightly) |
| `ghpython` | 8 | 25 | Phase 5 |
| `elements`, `loads`, `supports`, `data` | 8 | 18 | — |
| `equilibrium` | 0 | 25 | Phase 3 |

**Sequencing: document each module in the phase that rewrites it, not up front.**
The three worst-covered modules are exactly the ones Phases 2 and 4 replace, so
documenting them now is work thrown away. Two consequences:

- Phase 1 covers `diagrams`, `elements`, `loads`, `supports`, `data` — the modules
  no later phase rewrites, plus the ones it already touches.
- Do **not** document `plotters/proxy.py`; Phase 2 deletes it as dead code.
- `equilibrium/` is already fully documented — it is the best-maintained module in
  the package. Match its standard.

**Form.** Every docstring is multi-line, even a one-liner: `"""` alone, content,
`"""` alone. No blank line after it before the first statement — ruff enforces
this as `D202`, which is already in `select`.

```python
def disassemble(form):
    """
    Disassemble a form diagram into its constituent parts.
    """
```

**Content rules**, which matter more than the form:

- **Distill intent from the body.** Read the code and make the summary *true*.
  Several existing summaries lie — wrong defaults claimed, wrong units,
  copy-pasted from a neighbouring function. Fix those rather than appending to
  them.
- **Types live only in the signature, never in the docstring.** `mkdocs.yml`
  configures mkdocstrings with `docstring_style: numpy` and
  `docstring_section_style: list`, so griffe merges the signature annotation into
  the rendered entry. Write typeless `name :` entries — colon, nothing after —
  for both parameters and returns. A bare `Returns` description with no `name :`
  renders as a *type*, so keep the name.
- **Notes stay short and general.** State the mechanism and its consequence.
  Never cite a specific example, benchmark, file path, or measured number — those
  rot. Rationale and measurements belong in `CHANGELOG.md`.
- **Trim Notes that only restate Parameters or Returns.** Keep the ones carrying
  real information: numerical or gradient behaviour, NaN and edge-case handling,
  formulas, construction conventions, invariants.

Note that the existing docstrings use the older `` ``int`` `` / `:class:`X``
reStructuredText inline markup throughout. Convert as you touch each file; the
rendered output is Markdown now.

**Also in scope, and related:** the 8 griffe warnings in §9.3 are docstrings
documenting parameters that do not exist in their signature, and every
`src/compas_cem/*/__init__.py` module docstring still contains
`.. currentmodule::` / `.. autosummary::` rST that mkdocstrings renders verbatim
on the API pages.

**Verify per file**: `ruff check` and `ruff format --check`, then `invoke docs`,
then actually look at the rendered page to confirm the type comes from the
signature and that no description has been mistaken for a type.

### 10.7 Working agreement for the unattended Phase 1–2 run

Authorized 2026-08-07, and **scoped to that run only** — this is not standing
permission for any later session.

- **Commit locally on phase branches. Do not push. Do not merge. Do not touch
  `main`.** Work is reviewed in the morning from the local branches.
- Branch `phase-1` off `main` *after* PR #16 is merged.
- **Carry `[Docs] Scoped the docstring pass into the phase plan` forward.** It was
  committed locally on `phase-0-tooling` and deliberately not pushed, so it is
  *not* part of PR #16 and will not reach `main` when #16 merges. Cherry-pick it
  onto `phase-1` so §10.6 is not lost.
- **Do not start Phase 2 until Phase 1's acceptance gate in §10.3 is green.** A
  half-finished Phase 1 underneath a Phase 2 rewrite is very hard to unpick.
- Phase 2 acceptance is visual and cannot be self-certified. Render examples 01–05
  headless (`MPLBACKEND=Agg`), save the figures somewhere gitignored, and leave a
  note pointing at them for review rather than declaring the phase done.
- If a decision is needed that §5 or §10.5 does not already settle, stop and write
  it up. Do not guess at an architectural choice unattended.

---

## 11. Phase 1 outcome

Delivered on branch `phase-1`, branched off `main` after PR #16 merged, with the
`[Docs] Scoped the docstring pass` commit cherry-picked across as §10.7 required.

**Acceptance gate, all green:**

| gate | result |
| --- | --- |
| tests | **96/96** (92 inherited + 4 new round-trip tests) |
| `tests/baseline/capture.py` | examples **01, 02, 03 and 04** byte-identical to the legacy fixtures |
| `ruff check src tests` | clean |
| `ruff format --check src tests` | clean |
| `uv build` | sdist and wheel, all **39** Grasshopper components with `code.py`, `metadata.json` and icon |
| docs | builds, 8 griffe warnings, all in Phase 2/5 files (§9.3) |

Example 04 reproducing was not expected — §9.2 predicted 04 and 05 would both
drift. Only 05 does. See §11.2.

### 11.1 Corrections to the plan, learned by doing

- **`examples/data/*.json` did not need regenerating.** They are bare COMPAS
  `Mesh` data dictionaries with no type envelope, and `Mesh.__from_data__` reads
  them unchanged under COMPAS 2. Only `examples/03_bridge_2d.json`, which does
  carry a `compas 1.7.1` envelope, had to be rebuilt. §10.3 step 2 overstated the
  work.
- **Insertion order is load-bearing and the plan did not say so.** Rebuilding
  `03_bridge_2d.json` with nodes in sorted order left every physical quantity
  right but permuted the optimizer's gradient vector, moving the converged
  geometry by ~5e-9. The original file stores nodes in the order `7, 3, 5, 0, 4,
  2, 1, 6`; preserving it makes the fixture reproduce exactly. Anything that
  rebuilds a diagram from scratch has to preserve insertion order or the
  optimizer comparison is worthless.
- **`compas.numerical.connectivity_matrix` is never imported.** §4.1 lists it;
  the package does not use it.
- **`connected_edges` needed a rename, not just a helper.** COMPAS 2 keeps the
  name for a different operation, so the COMPAS 1 behaviour was restored as
  `Diagram.node_connected_edges` rather than shadowing the base method. Four call
  sites, one of them each in `plotters`, `viewers` and `ghpython`.
- **`gkey_node` is a pre-existing shadow, not a 2.x regression.** COMPAS 1's
  `Network` already had a `gkey_node` method, and compas_cem has always
  overridden it with a cached property. Left as is; behaviour is unchanged.
- **There are no `instanceGuid`s to preserve.** §10.3 step 8 says to preserve
  them when renaming the Grasshopper component directories. No `instanceGuid`
  appears anywhere in the repository, and no componentizer is wired into
  `tasks.py` — Phase 0 removed it and Phase 5 reattaches it. GUID assignment is
  therefore entirely a **Phase 5** question, and the eight directories were
  renamed freely. Phase 5 must confirm how `componentize_cpy.py` derives GUIDs
  before shipping, or existing `.gh` files will not resolve.
- **`ruff format --check` has never been clean repository-wide.** At the Phase 0
  merge commit, 10 files failed it. CI does not see this: `invoke lint` runs
  `ruff check --fix src tests`, so `examples/` and `docs/` are outside the gate.
  Phase 1 leaves exactly one file failing, `docs/migration/proto_jax_cem.py`,
  which is preserved §8 evidence and deliberately untouched.

### 11.2 Example 05 is the only baseline that drifts

Static equilibrium is **bit-identical** between the two stacks. The drift is
entirely inside the optimizer, and it is §9.2, not a regression:

| | legacy | COMPAS 2 |
| --- | --- | --- |
| evaluations | 3 | 3 |
| penalty | 4.681609e-31 | 4.743238e-31 |
| gradient norm | nan | nan |
| NaN gradient components | 3 / 24 | 3 / 24 |
| status | `NLOPT_EPSVAL_REACHED` | `NLOPT_EPSVAL_REACHED` |

Two of 32 nodes move, by 6.6e-3 and 4.1e-3. Both are auxiliary-trail nodes whose
position is undetermined because the gradient reaching them is NaN. The
objective is already ~1e-31 at the start, so nlopt exits immediately and the
step it does take is decided by floating-point noise. Repairing this is Phase
3/4 work, via the double-`where` safe normalize in §4.3.

### 11.3 The authoring API, decided after the fact

§10.3 step 5 says to rename the object-taking `add_node`/`add_edge` but does not
say what to. Phase 1 first shipped a single `Diagram.add_element(element)`
dispatching on `Node` versus `Edge`.

That was **reconsidered before this branch was merged.** An audit of the two
sibling libraries, `jax_fdm` and `smax`, led Rafael to keep `add_node` and
`add_edge` and dispatch on the type of the argument, so that the authoring API,
the tutorials and every existing `.gh` file survive untouched. Phase 1 was
rewritten to ship that directly, so `main` never carried `add_element`.

What landed:

```python
topology.add_node(Node(0, [0.0, 0.0, 0.0]))      # element
topology.add_node(0, x=0.0, y=0.0, z=0.0)        # key, as the base graph does
topology.add_edge(TrailEdge(0, 1, length=-1.0))  # element
topology.add_edge(0, 1, attr_dict={...})         # keys, as deserialization replays
```

Two guardrails offset the known weakness of dispatching on a first positional
parameter that carries two meanings: the entry points reject a mismatched
element — `add_node` refuses an `Edge`, `add_edge` refuses a `Node`, and any
`compas.data.Data` offered as a key raises rather than becoming one — and eleven
tests cover both vocabularies, the rejection cases, and JSON round-trip and
`copy()` regressions. The round-trip tests matter most: they exercise the exact
path that broke in the move to COMPAS 2.

### 11.4 Carried into Phase 2

- The examples import `compas_cem.plotters` at module scope, which cannot import
  under COMPAS 2. `tests/baseline/capture.py` now falls back to a drawing-free
  stand-in and prints a line saying so. It self-retires: once `plotters` imports
  again, the real one is used. **Delete `NoOpPlotter` and `stub_plotters` from
  `capture.py` when Phase 2 lands.**
- `plotters` and `viewers` had their `compas.utilities` imports moved to
  `compas.itertools` / `compas.tolerance` and their `connected_edges` call sites
  renamed, so Phase 2 starts on files that fail for one reason only:
  `compas.artists` and `compas_plotters` no longer exist.
- The 8 griffe warnings of §9.3 are untouched and still live in
  `ghpython/artists.py`, `viewers/diagramobject.py` and
  `viewers/topologyobject.py`.
- The docstring convention now writes typeless `name :` entries, per §10.6. The
  package carries **no signature annotations at all**, so those entries currently
  render with a name and a description and no type. That is the intended end
  state only once annotations exist; adding them is not scheduled by any phase.

### 11.5 Docstring pass, Phase 1 share

Covered `diagrams`, `elements`, `loads`, `supports` and `data` per §10.6, plus
every `src/compas_cem/*/__init__.py` module docstring, which all carried
`.. currentmodule::` / `.. autosummary::` rST that mkdocstrings rendered
verbatim. Also fixed on the way past:

- `data/__init__.py` documented itself as `compas_cem.diagrams`, under a
  `Diagrams` heading — a copy-paste that had been there since the module existed.
- `TopologyDiagram` was documented as "The very heart of life" and `FormDiagram`
  as "The heart of life", with a `Returns` section on a class.
- `auxiliary_trail_vector` documented its return as "length : the edge length".
- The `keys` flag on the trail iterators documented only its default.
- 11 empty `""" """` docstrings removed rather than filled, on dunders and
  property setters that inherit their meaning.
