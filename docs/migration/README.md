# compas_cem modernization plan

Status: **Phases 0, 1 and 2 are complete and merged into `main`** (PRs #16, #17
and #18). Phases 3 to 5 not started; **Phase 5 is next.** Target release
**0.9.0**, deliberately breaking. §14 is the current handover and §15 the
Phase 5 blueprint.

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
2. ~~**Grasshopper componentizer for Phase 5**~~ — **resolved 2026-08-07: keep
   the componentizer and follow `compas_fab`.** See §15.

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
  optimizer comparison is worthless. The one-shot script that rebuilt it was not
  kept; the pre-migration file it was derived from is at
  `70e13c1a:examples/03_bridge_2d.json`.
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

See §13.9 for the five options weighed and §13.11 for the decision record.

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

---

## 12. Phase 2 outcome

Delivered on branch `phase-2`, branched off `phase-1`. **Signed off**: Rafael ran
all five examples and the viewer check by hand on 2026-08-07 and confirmed both
backends draw correctly. §12.4 records what was checked and how to rerun it.

| gate | result |
| --- | --- |
| tests | 96/96 (this layer has none; unchanged from Phase 1) |
| `tests/baseline/capture.py` | 01, 02, 03, 04 still byte-identical, with the real plotters back |
| `ruff check` / `format --check` | clean |
| docs | builds with **zero** griffe warnings, down from 8 |
| docstrings | **zero** undocumented public definitions in `plotters` and `viewers`, down from 25/42 and 52/70 |

### 12.1 The highest-variance item was not a problem

§10.4 flagged `viewers/diagramobject.py` reaching into private `compas_view2`
hooks (`_points_data`, `_lines_data`) as the biggest unknown in the plan.
`compas_viewer` 2.0.2 exposes `_read_points_data`, `_read_lines_data`,
`_read_frontfaces_data` and `_read_backfaces_data` on its `GraphObject`, which
are direct equivalents. The port overrides the first two to emit per-node and
per-edge colors, where the upstream versions broadcast a single default.

The other compas_view2 pieces map cleanly too: `Collection` to `Group`, `Text`
to `Tag`, and the `viewer.add(...)` calls to `self.add(...)` on the scene object,
which parents the arrows and labels to the diagram so they show and hide with it.

### 12.2 What the port changed

- `plotters/{formartist,topologyartist,register,proxy}.py` are gone, replaced by
  `plotters/scene_objects.py` with `DiagramPlotterObject` and the form and
  topology subclasses. `proxy.py` was deleted as dead code per §10.4.
- `viewers/{diagramobject,formobject,topologyobject,register}.py` are gone,
  replaced by `viewers/scene_objects.py` on the same shape.
- Both packages register their scene objects on import via
  `compas.scene.register`, and call `register_scene_objects()` first. compas
  auto-discovers plugins in `compas*` packages only and discovers into an empty
  registry only, so a plugin module cannot work here — this is the same
  arrangement `jax_fdm` uses. `__all_plugins__` no longer lists
  `compas_cem.plotters.register`, which no longer exists.
- `compas_plotter>=1.0.1` and `compas_viewer>=2.0` are runtime dependencies in
  `requirements.txt`. See §12.5.

### 12.3 Three things the visual comparison caught

Rendering the same five examples from `main` under the legacy environment and
diffing against the port found three regressions that reading the code did not:

1. **Node markers came out 25 times too small.** The 1.x artist defaulted to
   `sizepolicy="relative"`, which divides the node size by the node count;
   `compas_plotter` 1.0.1 defaults to `"absolute"`, which divides by the plotter
   resolution. `DiagramPlotterObject` pins the default back to `"relative"`.
2. **The default key labels disappeared.** `show_nodetext=True` with no tag drew
   node keys and `u-v` edge keys in 1.x. The first port drew nothing, because it
   treated "no tag" as "no labels". Restored as `default_node_textlabels` and
   `default_edge_textlabels`.
3. **The load crosses vanished behind the nodes.** `compas_plotter`'s
   `LineObject` fixes its own `zorder` at 1000 in its constructor, and the node
   markers draw at 1020, so the crosses were drawn and then covered. Setting
   `zorder` on the returned object afterwards does nothing, because the
   matplotlib artist already exists. The crosses are now drawn straight onto the
   canvas as one `LineCollection`.

Sampling the pixels of both renders confirms the palette is untouched: tension
`(227, 6, 75)` appears at identical pixel counts in the legacy and the ported
image. §10.4 anticipated a colour shift from `COLORS` being 0–255 int tuples that
the plotters layer never normalized; in practice the 1.x plotter accepted them
and the two renders match.

### 12.4 What still needs your eyes

- **The plotters are done and verified.** `renders/` holds the five ported
  images and `renders/legacy/` the same five from `main` under the legacy
  environment. Compare them; they should be indistinguishable. Regenerate with
  `PYTHONPATH=src MPLBACKEND=Agg python tests/baseline/render.py`. The directory
  is gitignored.
- **The viewers are verified.** No example uses the `Viewer`, so
  `renders/viewer_check.py` builds a topology and a form diagram and opens both.
  Run it from the repository root, since it resolves its data file relatively.
  Headless checks alone got as far as confirming that both scene objects resolve
  through `compas.scene` and that their point and line buffers carry the right
  per-element colors; the arrow geometry and the label placement needed a
  display, and were confirmed by hand.

### 12.5 Resolved: the visualization backends are runtime dependencies

`compas_plotter>=1.0.1` and `compas_viewer>=2.0` were briefly parked in
`requirements-dev.txt`, because the docs build imports those modules. Rafael
settled it on 2026-08-07: **both are ordinary runtime dependencies**, in
`requirements.txt`. Unlike `jax_fdm`, which treats its backends as optional and
guards them with `has_backend`, drawing a diagram is not an optional extra of
this package.

The consequence to keep in mind is that installing `compas_cem` now installs
PySide6, which is large. It does not affect a headless install or import:
`import compas_cem` does not reach the viewer, and the CI `check_import` step
passes. Verified on a clean runtime-only environment — no dev extra — where all
five examples run and both `compas_cem.plotters` and `compas_cem.viewers`
import.

`compas` itself is also declared, so it no longer needs installing separately.
That collapsed the installation instructions from four steps to two, and they
now use `pip` and `venv` rather than conda, which is being phased out across the
COMPAS ecosystem.

### 12.6 The four latent bugs are fixed

All four of §10.4's, plus the two docstring faults behind the griffe warnings:

- the undefined `edge` inside `state_format`, in both the plotters and the
  viewers copy — both closures now read the `edge` they are passed;
- `self.topology` referenced on `DiagramObject`, which only defined
  `self.diagram` — `topology` is now a property on the topology subclass only,
  and the base uses `diagram`;
- the `show_nodes` setter that assigned to `_show_edges` — gone with the hand
  rolled property block, replaced by the upstream `show_points`/`show_lines`;
- `ghpython/artists.py` documented a `min_load` parameter on `draw_reactions`,
  whose signature takes `min_force`, copy-pasted from `draw_loads`;
- `viewers/topologyobject.py` documented its constructor argument as
  `form_diagram` on a topology diagram object.

### 12.7 Why the divide-by-zero warnings only appear now

Running examples 04 and 05 under COMPAS 2 prints warnings the legacy stack never
showed:

```
force_numpy.py:168: RuntimeWarning: invalid value encountered in divide
  nrvec = rvec / trail_force
```

**The arithmetic did not change.** Probing the division site in both stacks
records exactly the same operation, `[-0., -0., -0.] / 0.0`, occurring exactly
twice in example 04. This is §9.2's zero-force auxiliary trail, unchanged.

What changed is who was silencing numpy. `compas/numerical/linalg.py` in COMPAS
1.17.10 runs, at module scope:

```python
old_settings = seterr(all="ignore")
```

That mutes every numpy floating-point signal for the whole process, on import,
and never restores it — `old_settings` is assigned and never read again.
`import compas.geometry` pulls that module in transitively, and every example
imports `compas.geometry`, so the entire legacy process ran with floating-point
signalling switched off. COMPAS 2 removed `compas.numerical` altogether, so
nothing calls `seterr` and numpy's default `invalid='warn'` applies.

Forcing `np.seterr(invalid='raise')` makes the difference plain: the migrated
package raises `FloatingPointError` at `force_numpy.py:168`, while the legacy
package raises nothing, because importing `compas.geometry` quietly resets the
state underneath. Note also that only `0/0` signals `invalid` — `nan/nan` and
`nan/2` are silent — so these warnings are the genuine zero-length residual, not
NaN propagating from somewhere upstream.

Two consequences:

- The warnings are **correct and useful**, and should not be suppressed. They are
  the audible form of the bug §9.2 could otherwise only detect by disabling
  `stopval`.
- They disappear when §4.3's double-`where` safe normalize lands in Phase 3/4,
  which §9.2 already says should *repair* examples 04 and 05 rather than
  preserve them. Until then, expect them on those two examples.

### 12.8 An unreported bug left alone in `update_node_xyz`

Noticed while folding the mixins in Phase 1, and **deliberately not fixed**,
because fixing it changes behaviour and the phase was meant to preserve it.

`Diagram.update_node_xyz(key, xyz)` evicts the geometric key of the *new*
position before inserting the node there:

```python
gkey = self.gkey(xyz)          # the key it is about to occupy
if gkey in self.gkey_node:
    del self.gkey_node[gkey]
self._add_node_element(Node(key, xyz))
```

The entry it should evict is the *old* position's, which is the one now stale.
As written, `gkey_node` keeps pointing at the node's previous location forever,
so `node_key(old_xyz)` keeps resolving to a node that has moved away, and the
lookup table grows an entry per move.

It is invisible today because the solver never calls `update_node_xyz` — only
`node_xyz(key, xyz)` does, and nothing on the equilibrium path sets coordinates
that way. The Grasshopper `OriginNodesMove` component is the closest live
caller. Worth fixing alongside the Phase 4 parameter work, which is the first
thing that will move nodes in anger, and worth a regression test that
`node_key(old_xyz)` stops resolving after a move.

---

## 13. API alignment audit: `jax_fdm`, `smax`, `compas_cem`

Written 2026-08-07, before committing to an authoring API for 0.9.0. Nothing in
this section is implemented. It exists so the decision is made once, with the
evidence in front of it, rather than re-derived.

The question that prompted it: `compas_cem` builds diagrams out of element
objects (`add_edge(TrailEdge(0, 1, length=-1.0))`), which is unlike its two
sibling libraries. Which of the three idioms should 0.9.0 adopt, and does the
answer survive wanting **area loads** and **partially fixed supports** later?

### 13.1 Three idioms, and the one difference that cannot be aligned

| | substrate | authoring | supports | loads |
| --- | --- | --- | --- | --- |
| `jax_fdm` | COMPAS `Graph` / `Mesh`, **mutable** | plain `add_node(x=, y=, z=)` and `add_edge(u, v)`. **No element objects, no overrides.** | `node_support(key)`, a boolean `is_support` attribute | `node_load(key, load)`, `face_load(key, load)` |
| `smax` | equinox pytree, **immutable** | `Structure(nodes, elements, supports)` from lists of objects. **No `add_*` at all.** | `Support(node_id, fixity)` over `[ux, uy, uz, rx, ry, rz]`, plus `FixedSupport`, `PinnedSupport`, `RollerSupport(axis=)` | `PointLoad`, `PointMoment`, `LineLoad` under `NodeLoad` / `ElementLoad` bases, grouped by `LoadCase` |
| `compas_cem` | COMPAS `Graph`, **mutable** | `add_node(obj)`, `add_edge(obj)`, `add_support(obj)`, `add_load(obj)` | `type == "support"` attribute | `qx`, `qy`, `qz` attributes |

**`smax` is object-based because equinox pytrees are immutable.** A `Structure`
cannot be mutated, so it must be handed complete collections at construction.
That constraint does not exist for `compas_cem` or `jax_fdm`, both of which sit
on mutable COMPAS datastructures. Its constructor-from-lists shape is therefore
a consequence of JAX and must **not** be imported here.

Which makes `jax_fdm` the only meaningful comparator — and `jax_fdm` is exactly
the "no element objects" design.

### 13.2 `compas_cem` already unwraps the objects

`TopologyDiagram.add_support` and `add_load` resolve the object to bare
attributes on the very next line:

```python
value = support.node if support.node is not None else support.xyz
node = self.node_key(value)
self.node_attribute(node, "type", "support")
```

They are already thin adapters over an attribute write. Half of the object-free
design is in place, inconsistently.

### 13.3 What the element classes actually do

| class | Grasshopper producer | geometry constructor | core call sites | finding |
| --- | --- | --- | --- | --- |
| `Node(key, xyz)` | **none** | — | 6 | `self.attributes = {}` is written and never read anywhere |
| `Edge(u, v, attrs)` | **none** | `from_line` | 1 | `form.py` builds `Edge(u, v, {})` purely to satisfy the API |
| `TrailEdge` | yes | yes | 3 | a real Grasshopper wire value |
| `DeviationEdge` | yes | yes | 2 | a real Grasshopper wire value |
| `NodeLoad`, `NodeSupport` | yes | yes | — | real wire values, unwrapped immediately on add |

The Grasshopper-justified set is exactly **`TrailEdge`, `DeviationEdge`,
`NodeLoad`, `NodeSupport`**. `Node` and `Edge` have **no Grasshopper consumer at
all** and can be removed with no consequence for Phase 5.

Of the roughly 45 element constructions in `src`, all but four are throwaway
`__main__` demo blocks under `optimization/`. The four real ones are
`build_trails`, `from_dualquadmesh`, `update_node_xyz` and the kernel bridge in
`form.py`. Every one of them gets shorter without the objects.

### 13.4 The case *for* the object design, fairly stated

Worth recording, because the decision should not rest on a caricature.

1. **Construction decoupled from a container.** An element describes an intent
   that has no receiver yet — a trail edge can be expressed before any diagram
   exists. That is what enables declarative model definitions, generators that
   emit element lists, model recipes that can be passed around or persisted, and
   fixtures that are data rather than code. Grasshopper is the visible instance
   of this, not the reason for it. `smax` converged on the same property from a
   different direction.
2. **It keeps the datastructure small.** Without objects, every new concept
   becomes another method on `Diagram` — `add_trail_edge`, `add_deviation_edge`,
   `add_area_load`, `add_support(fixity=)` — and the vocabulary migrates into the
   datastructure. With objects the vocabulary lives in `elements/` and `Diagram`
   keeps one polymorphic door, which also lets a third party add an element type
   without subclassing `Diagram`. `smax` is the limit case: its `Structure` has
   almost no methods.

Against which: **this implementation realizes almost none of that.** The objects
are unwrapped on the next line, `Node.attributes` is dead, they raise
`NotImplementedError` on serialization (so the persistable-recipe benefit does
not actually exist), `Edge(u, v, {})` is ceremony, nothing is validated at
construction, and they shadowed the base graph API — which is the defect that
started this whole line of enquiry (§11.3). It is an object model that has been
used as an argument-passing convention.

### 13.5 `edge_length_2` is not redundant

The suspicion that `edge_length_2` only exists because COMPAS 1 could not take a
single tuple key is **wrong**, and acting on it would break the solver. The two
methods return different quantities and both are live:

- `edge_length(edge)` — COMPAS's geometric distance between the end nodes. Used
  in `force.py` to compute the *realized* length after form-finding.
- `edge_length_2(edge)` — the stored signed `length` **attribute**. Read by the
  solver itself, which builds its `edge_lengths` from it, and by the plotters,
  the viewers, the Grasshopper results component and the baseline harness.

What *is* wrong is the name, which exists only to dodge the clash. A
`# TODO: overwrite inheritance` in the test suite dates from the same problem.

Note also that the `length` attribute means the **prescribed** length on a
topology diagram and the **realized** signed length on a form diagram. One name,
two meanings, depending on which diagram is in hand. Worth separating.

### 13.6 Naming conventions to adopt from `jax_fdm`

`jax_fdm` never shadows a COMPAS name — `edge_length` stays geometric and
untouched — and gives every domain quantity its own noun, with a singular
get-or-set form and a plural batch form: `edge_forcedensity` / `edges_forcedensities`,
`edge_force` / `edges_forces`, `edge_loadpath` / `edges_loadpaths`, `edge_load`,
`node_load`, `node_support`, `nodes_supports`, `nodes_free`, `nodes_fixed`.

| `compas_cem` today | proposed | reason |
| --- | --- | --- |
| `edge_length_2(edge)` | `edge_signed_length(edge, length=None)` | its own noun, no clash, get-or-set |
| `edge_force(edge)` | `edge_force(edge, force=None)` | add the setter; then identical to `jax_fdm` |
| `node_load(node)` | `node_load(node, load=None)` | add the setter; then identical to `jax_fdm` |
| `support_nodes()`, `loaded_nodes()`, `origin_nodes()` | `nodes_supports()`, `nodes_loaded()`, `nodes_origins()` | entity-first plural, as `jax_fdm` does throughout |
| — | `edges_forces()`, `edges_lengths()`, `edges_signed_lengths()` | plural batch accessors, which do not exist yet |

Already aligned and to be left alone: `is_node_support(key)` is identical in both.

One name to watch: `compas_cem.NodeLoad` is a *concrete* point load, whereas
`smax.NodeLoad` is the *abstract base* and its concrete class is `PointLoad`. If
the load vocabulary ever grows here, prefer `smax`'s split.

### 13.7 Do area loads and partial supports change the answer?

They do not, and they mildly favour the object-free design.

**Area loads.** The precedent is `FDMesh.face_load(key, load)` in `jax_fdm`, with
`px`/`py`/`pz` per face. `smax` has none yet; one would slot under `ElementLoad`.
The obstacle here is structural: a topology diagram is a `Graph`, so there are no
faces to carry an area load. Two routes — a mesh-backed diagram in the `FDMesh`
mould, which changes the datastructure, or an area load **resolved into nodal
loads when it is added**, through tributary areas. The second fits CEM, because
the solver only ever reads nodal loads. It is also one more attribute-writing
method, whereas the object design would need an `AreaLoad` class for `Diagram` to
dispatch on.

**Partially fixed supports.** `jax_fdm` is boolean-only, which is inherent to
FDM: a node is free or fixed. `smax` carries a full six-degree-of-freedom fixity
because it is a stiffness solver with a real DOF space. CEM has neither —
supports *terminate trails*, and the reaction is whatever the trail delivers.
There is no stiffness matrix to constrain per axis.

`compas_cem` already expresses directional restraint by other means:
`TrailEdge(plane=...)` constrains where a trail lands, and `ReactionForceGoal`
targets the reaction vector. **A roller in CEM is a plane or a goal, not a
fixity flag.** Whether per-axis fixity means anything here should be decided
deliberately rather than adopted by analogy with `smax`.

If it is wanted, take `smax`'s *data* without its class hierarchy:

```python
topology.add_support(node)                            # full, the default
topology.add_support(node, fixity=(True, True, False))
```

A keyword argument is strictly cheaper to add later than a
`FixedSupport`/`PinnedSupport`/`RollerSupport` hierarchy that the diagram must
dispatch on. `smax` needs those classes only because its constructor takes a
*list* of supports.

### 13.8 Where this leaves the decision

Leaning, not yet committed, and **not implemented**:

- Adopt the object-free authoring API, aligned to `jax_fdm`, since the two share
  a substrate and the query API already matches. CEM's vocabulary is small and
  closed, which is the condition under which "vocabulary on the datastructure"
  stays manageable.
- Take §13.6's naming in the same pass, because renaming twice is worse.
- Express future capability as keyword arguments, not subclasses.
- **Keep `TrailEdge`, `DeviationEdge`, `NodeLoad` and `NodeSupport`**, relocated
  into the `ghpython` layer in Phase 5 rather than rewritten — they already do
  the deferred-construction job, and that seam is worth preserving. Drop `Node`
  and `Edge` now; nothing consumes them.
- If declarative or persistable model recipes are ever wanted, that is the point
  at which those four get working `__data__` and are promoted back out.

Sequencing note: relocating the elements breaks the current Grasshopper
components at import. They are already dead under COMPAS 2 (IronPython 2.7,
`RhinoLine`, `compas_ghpython.artists`), so the layer stays non-functional until
Phase 5 either way — but it should be a decision, not a discovery.

### 13.9 The five options considered

Recorded because the letters were used in discussion and are easy to confuse.
All five answer the same question: COMPAS 2 deserializes by calling
`add_node(key=, attr_dict=)` and `add_edge(u, v, attr_dict=)`, which collided
with the object-taking overrides (§11.3). **C is what was chosen and
implemented. A was built during Phase 1's development and then withdrawn before
Phase 1 merged.** See §13.11.

| | approach | for | against |
| --- | --- | --- | --- |
| **A** | `add_element(element)`, one new name, dispatch on `Node` / `Edge` with an explicit `raise` | does not shadow upstream; symmetric with `add_support` / `add_load`; one name to learn | union return type; 119 call sites moved |
| **B** | two names, `add_node_element` / `add_edge_element` | return types stay distinct; closest to the old mental model | two clumsy names instead of one; same churn as A |
| **C** *(chosen)* | keep `add_node` / `add_edge`, dispatch on the **type of the argument** | zero churn — examples, docs, tutorials and Grasshopper all keep working | see below |
| **D** | keep the object-taking names, override `__from_data__` to restore by assignment, as COMPAS 1 did | zero churn | reimplements upstream deserialization and has to track it forever |
| **E** | remove the element objects, use the COMPAS idiom directly | see §13.1–13.8 | vocabulary migrates onto `Diagram` |

**C in full**, since it is the one that keeps the existing signatures:

```python
def add_node(self, node=None, key=None, attr_dict=None, **kwattr):
    if isinstance(node, Node):
        return self._add_node_element(node)
    if node is not None and key is None:
        key = node                    # a positional COMPAS-style call
    return super().add_node(key=key, attr_dict=attr_dict, **kwattr)

def add_edge(self, edge=None, v=None, attr_dict=None, **kwattr):
    if isinstance(edge, Edge):
        return self._add_edge_element(edge)
    return super().add_edge(edge, v, attr_dict=attr_dict, **kwattr)   # edge doubles as u
```

It does work: deserialization passes `key` and `attr_dict` by keyword for nodes
and `u, v` positionally for edges, so neither path collides. What it costs is
that the first positional parameter means two different things, its *name* is
wrong half the time — `edge` when the value is really `u` — the signature cannot
be typed honestly, and `add_node(SomeUnrelatedObject())` is silently accepted as
a node key. It also leaves the package dependent on upstream continuing to call
those two methods in a shape that has been anticipated, which is precisely the
assumption that broke in the move to COMPAS 2.

### 13.10 What completing the object design would cost

The counterfactual to E, costed, so the choice is not made against a caricature.
The two benefits in §13.4 are **separable** — either can be taken without the
other.

**The starting point is better than it looks.** `Goal` and `Parameter` already
round-trip through `__data__` / `__from_data__`, ported in Phase 1. `Optimizer`
and the elements are the only pieces that do not. The package therefore already
has a working serializable object layer for the optimization half; the modelling
half was left unfinished.

**Benefit 1 — construction decoupled from a container.**

| change | scope |
| --- | --- |
| `__data__` / `__from_data__` on `Node`, `Edge`, `TrailEdge`, `DeviationEdge`, `NodeLoad`, `NodeSupport` | six classes. `TrailEdge.plane` needs the `target_dtype` and `cls_from_dtype` treatment that `Goal.__data__` already demonstrates |
| a recipe container that serializes as a unit, and `TopologyDiagram.from_elements(...)` | a new class plus a materialization step |
| pin down node identity, which today is a key **or** a set of coordinates | the hard part |
| merge and compose semantics for two recipes | falls out of coordinate identity, if that is chosen |

The identity rule is the real work. A recipe earns its keep only if it is
key-free, so that it can be generated, merged, transformed and only then
materialized into keys. But `node_key`'s integer passthrough and the `gkey_node`
deduplication are what 20 of the 39 Grasshopper components depend on, so
changing the rule is not a local edit.

Note what this buys *over what already exists*: `TopologyDiagram.to_json()`
works today. A recipe adds key-free identity — composable, mergeable, editable
by hand — and, together with the existing `Goal` and `Parameter` serialization
plus a `__data__` for `Optimizer`, a serializable **whole problem definition**
that can be saved, reloaded, diffed or sent over RPC.

**Benefit 2 — a small datastructure and third-party extensibility.**

| change | scope |
| --- | --- |
| replace the `isinstance` chain with `element.add_to(diagram)`, or a registry | inverts the dependency: `Diagram` imports `elements` today, and `elements` is a leaf, so duck typing keeps it clean |
| route loads and supports through the same door | `add_element(NodeSupport(...))` replaces `add_support` and `add_load`; three doors become one |
| new concepts then never touch `Diagram` | an `AreaLoad` class instead of an `add_area_load` method |

Much cheaper than benefit 1, and it needs no serialization at all.

**Independent of both:** validation at construction, which has a seam that is
entirely unused; `Node.attributes`, written and never read, either used or
deleted; and the `Edge(u, v, {})` ceremony in the kernel bridge removed.

**The cost.**

- Six serialization pairs and their tests, a recipe container, the dispatch
  inversion, and the identity rule — the last carrying real regression risk
  against behaviour the Grasshopper layer depends on.
- `elements` becomes a documented public API surface. It is 8 of 18
  undocumented today, and under E most of it disappears instead.
- Recurring: every new modelling concept becomes a class plus serialization plus
  documentation, rather than one method. This is the cost that compounds.
- Neither branch avoids the §13.6 naming work, nor changes the fix for the
  shadowing defect.

**What decides it.** Not which design reads better in the abstract, but whether
there is a real consumer for key-free composable model recipes. Grasshopper is
not one — it needs values on a wire, which the current classes already provide
without any serialization at all. If something else wants to generate, merge or
persist CEM models programmatically, then the object design is worth completing
and is closer to finished than it appears. If nothing does, benefit 1 is
speculative.

**The cheap middle.** Adopt E in the core, and give the four Grasshopper-
justified classes working `__data__` when they relocate in Phase 5. That yields
serializable wire values and preserves the deferred-construction seam without
making `Diagram` polymorphic or touching the identity rule. Should a recipe
consumer appear later, those four are promoted back out — which is what §13.8
already contemplates.

### 13.11 Decision: option C, implemented

Chosen by Rafael on 2026-08-07. Option A had been built during Phase 1's
development; after this audit, **Phase 1 was rewritten before it was merged**, so
`main` never carried `add_element` (§11.3). The reasoning: C respects the API
that the examples, the documentation, the tutorials and every existing `.gh`
file are written against, and it is the cheapest option to pivot away from
later, in either direction.

`Diagram.add_node` and `Diagram.add_edge` now accept both vocabularies:

```python
topology.add_node(Node(0, [0.0, 0.0, 0.0]))     # element
topology.add_node(0, x=0.0, y=0.0, z=0.0)       # key, as the base graph does
topology.add_edge(TrailEdge(0, 1, length=-1.0))  # element
topology.add_edge(0, 1, attr_dict={...})         # keys, as deserialization replays
```

`add_element` never reached `main`; all 119 call sites use `add_node` and
`add_edge`. `_add_node_element` and `_add_edge_element` remain as the private
element paths. The implementation and its tests ship in Phase 1.

**Two guardrails offset C's known weakness.** §13.9 records that C's danger is a
first positional parameter carrying two meanings, so a wrong object is silently
accepted as a node key:

- the entry points reject a mismatched element — `add_node` refuses an `Edge`,
  `add_edge` refuses a `Node`, and any `compas.data.Data` instance offered as a
  key raises rather than becoming one. A key given both positionally and by name
  also raises.
- eleven tests were added: both vocabularies on both methods, the four rejection
  cases, and JSON round-trip and `copy()` regression tests on three fixtures.
  The round-trip tests are the ones that matter — they exercise the exact path
  that broke in the move to COMPAS 2, and they will fail loudly if upstream ever
  changes how it replays construction again.

Verified behaviour-preserving: 107 tests pass, up from 96; baselines 01 to 04
remain byte-identical and 05 differs as always (§11.2); and the five rendered
examples are **byte-identical before and after the change**, confirmed by
re-rendering across the reversal. Folding C into Phase 1 was verified the same
way — the working tree was compared against the pre-fold branch and only the
narrative in this file and the changelog differed.

**What this does not settle.** The §13.6 naming work is orthogonal and still
owed — `edge_length_2` in particular is not redundant (§13.5) but is badly
named. And E remains available: §13.8's reasoning is unaffected by this choice,
since C changes only which door the element objects enter through, not whether
they exist.

---

## 14. Handover: state at the end of the Phase 1 and 2 run

Written 2026-08-07, at the end of the session that delivered Phases 1 and 2.

### 14.1 Where the branches are

| branch | state |
| --- | --- |
| `main` | Phase 0 (PR #16), **Phase 1 (PR #17)** and **Phase 2 (PR #18)**, each merged as a merge commit with its commits preserved — five for Phase 1, four for Phase 2 |

Both PRs passed **14/14** and both phase branches have been pruned locally and on
the remote, so `main` is the only branch left besides the pre-migration ones
below.

PR #17 was the first CI run of the whole migration, across all twelve build cells
(3.10 to 3.13 on ubuntu, macOS and windows) plus `docs` and the changelog check.
It closed the last verification gap: Windows and Linux had never been exercised,
including the newly-runtime `PySide6`.

Phase 2's own acceptance is visual and was confirmed by hand: all five examples
and `renders/viewer_check.py` were run and inspected (§12.4).

Stale branches were pruned at the end of the run: local `phase-1` and
`phase-0-tooling`, and remote `origin/phase-1`. `phase-0-tooling` was checked
first — its §10.6 content reached `main` by cherry-pick, so nothing was lost.

Six pre-migration remote branches predate this work. Five were pruned on
2026-08-07, after re-verifying that each was fully merged into `main` with zero
unique commits; two were kept:

| branch | last commit | state |
| --- | --- | --- |
| `cad` | 2022-08-24 | **deleted** 2026-08-07, tip was `dfd61dd3` |
| `singular` | 2022-08-26 | **deleted** 2026-08-07, tip was `fda5b7f7` |
| `polyline` | 2022-11-17 | **deleted** 2026-08-07, tip was `6aea47db` |
| `sequences` | 2022-11-17 | **deleted** 2026-08-07, tip was `9a889097` |
| `vectorize` | 2023-04-06 | **deleted** 2026-08-07, tip was `af5a435a` |
| `autograd` | 2022-08-15 | **kept as a legacy branch**, decided 2026-08-07. Tip `0d5c6552` |
| `gh-pages` | — | **kept.** The published docs site, must not be deleted |

The five deletions are recoverable from the recorded tip SHAs while the objects
survive on the remote. `origin` now holds `main`, `autograd` and `gh-pages` only.

`autograd` is kept for the historical record only — it is the first
differentiation attempt, the one Phases 3 and 4 replace with JAX. Nothing on it
is salvageable, and this was checked rather than assumed:

- Its three commits touch **two files**. `examples/06_edge_chain.py` is a
  three-node `autograd.grad` check harness that never existed on `main` under
  either name; the other is a five-line `literal_eval` guard on linestyles in
  `plotters/proxy.py`, a file Phase 2 deleted outright.
- The example imports `force_equilibrium`, `form_equilibrate_numpy`,
  `FormPlotter` and `TrailEdgeConstraint`, and authors on a `FormDiagram`. All
  of those are gone or renamed, so it cannot run against the current tree.
- A raw `git diff` against `main` returns ~122 KB and is misleading. The branch
  forked in July 2021 and still carries the whole pre-`f0bbe26d` examples
  folder that `main` deliberately replaced with the curated five, so the diff is
  mostly `main`'s own progress reported in reverse.

### 14.2 The governing objective

Set by Rafael and recorded here because it decides what comes next: **complete
the COMPAS 2 migration first.** Only afterwards tighten or change API contracts
to align with `jax_fdm` or `smax`. The §13 audit stands as the record for when
that time comes; §13.6's naming work is deferred, not cancelled.

### 14.3 What "complete the COMPAS 2 migration" now means

The `ghpython` layer is the **only** module still on COMPAS 1 APIs — 16 files
referencing `compas_rhino.geometry.Rhino*`, `compas_ghpython.artists`,
`compas.artists` and `installable_rhino_packages`. Every other module is
migrated. That puts **Phase 5 ahead of Phases 3 and 4**, which are JAX
migrations rather than COMPAS 2 ones.

Scope, measured: 39 components totalling 845 lines, of which **26 touch no Rhino
geometry at all** and are near-mechanical; 13 need the §4.5 conversions map;
`artists.py` is 397 lines; `install.py` and `uninstall.py` are 69 lines to
delete, per §5's yak-only decision.

**Phase 5 is no longer blocked.** The componentizer question, §10.5 item 2, was
resolved: keep it, and follow `compas_fab`. **§15 is the blueprint** — the exact
`tasks.py` config, the `yak_template` layout, and the four `release.yml` inputs,
including that the publish job must move to `windows-latest`.

The one prerequisite inside that work, §15.3, is now **resolved**: GUIDs are not
name-derived, so the Phase 1 renames broke nothing. What it uncovered instead is
that GUIDs are random per build, which leaves a decision — pin them or accept
the ecosystem default — to be taken during Phase 5.

### 14.4 Ready to start now, in parallel

The `jax_cem` decoupling and PyPI publish (§10.5 item 1). It gates Phase 3
entirely and blocks nothing else, so it should not wait for Phase 5.

### 14.5 Owed before tagging 0.9.0

- the `gh-pages` migration from the Sphinx layout to mike's `versions.json`;
- a throwaway `v0.9.0-rc1` tag to exercise `release.yml`, which is tag-triggered
  and still completely unrun;
- the version bump; `pyproject.toml` still reads 0.8.6.

A suggestion the plan does not settle: **scope 0.9.0 as "runs on COMPAS 2"** and
leave JAX to the next release. Phase 5 is the natural boundary, and it puts a
working package in users' hands before the kernel work begins.

### 14.6 Working environment

Neither environment is checked in; §10.2 has both recipes. `.venv` is the COMPAS
2 environment (Python 3.12, `compas` 2.15.1, `compas_plotter` 1.0.1,
`compas_viewer` 2.0.2, `nlopt` 2.11, editable install of the package).
`.venv-legacy` is the pre-migration baseline environment and is still needed to
regenerate legacy comparison renders.

`renders/` is gitignored and disposable. Only `renders/viewer_check.py` is kept,
because no example uses the `Viewer` and it is the only way to exercise it; run
it from the repository root. The images were deleted once Phase 2 was signed
off. To regenerate:

```bash
# the current renders
PYTHONPATH=src MPLBACKEND=Agg python tests/baseline/render.py

# the legacy comparison set, from before the COMPAS 2 migration
git worktree add --detach /tmp/legacy-wt 70e13c1a
cp tests/baseline/render.py /tmp/legacy-wt/tests/baseline/render.py
cd /tmp/legacy-wt && PYTHONPATH=src MPLBACKEND=Agg \
    COMPAS_CEM_RENDER_DIR=<repo>/renders/legacy ../.venv-legacy/bin/python \
    tests/baseline/render.py
```

`70e13c1a` is the last commit before Phase 1 merged, so it is the newest tree the
legacy environment can still run.

---

## 15. Decision: the Grasshopper componentizer, and the Phase 5 blueprint

Resolved 2026-08-07, closing §7 item 1 and §10.5 item 2. **Keep
`componentize_cpy.py` producing `.ghuser` files for yak to wrap, and adhere to
the `compas_invocations2` protocol exactly as `compas_fab` does.**

### 15.1 Why there was no real contest

The entire pipeline already exists and is already installed as a dependency.
`compas_invocations2` ships:

| task | what it does |
| --- | --- |
| `build.build_cpython_ghuser_components` | clones `compas-dev/compas-actions.ghpython_components`, runs `componentize_cpy.py`, turns a source directory into a directory of `.ghuser` files. Carries worked-out macOS Mono and `libgdiplus` handling |
| `grasshopper.yakerize` | consumes the `.ghuser` files and builds the `.yak` |
| `grasshopper.publish_yak` | pushes to the yak server |
| `grasshopper.update_gh_header` | rewrites the `# r: compas_cem>=x.y.z` header across every `code.py`, which is §4.5's requirement |
| `build.clean` | already knows to wipe the ghuser target directory |

`compas_cem`'s existing layout — `components/<Name>/{code.py, metadata.json,
icon.png}` — is already exactly what the componentizer consumes. And `yakerize`
copies only files matching `*.ghuser`, so a `.gh` library has **no route into yak
packaging at all**: choosing it would mean building and hosting distribution by
hand, against the grain of the ecosystem, for a package whose whole identity is
being a COMPAS extension.

`compas_timber` turns out not to build Grasshopper components from `tasks.py` at
all, so **`compas_fab` is the model to copy.**

### 15.2 The blueprint, taken from `compas_fab`

**Rename the component directory** to `components_cpython/`, matching
`compas_fab` and the note in §4.5 that it ships `components_cpython/` only.

**`tasks.py`** gains the `grasshopper` import, three tasks, and one config block:

```python
from compas_invocations2 import grasshopper

ns = Collection(
    ...,
    build.build_cpython_ghuser_components,
    grasshopper.yakerize,
    grasshopper.publish_yak,
)
ns.configure(
    {
        "base_folder": os.path.dirname(__file__),
        "ghuser_cpython": {
            "source_dir": "src/compas_cem/ghpython/components_cpython",
            "target_dir": "src/compas_cem/ghpython/components_cpython/ghuser",
            "prefix": "COMPAS CEM: ",
        },
    }
)
```

**Add `src/compas_cem/ghpython/yak_template/`** holding `manifest.yml` and
`icon.png`. The manifest carries `name`, `version: {{ version }}` — which
`yakerize` substitutes from `pyproject.toml` — `authors`, `description`, `url`
and `keywords`.

**`release.yml`** needs no separate yak invocation: `compas-actions.publish@v3`,
which this repository already uses, builds the components itself. The publish
job gains four inputs and **must move from `ubuntu-latest` to `windows-latest`**,
because the componentizer loads `GH_IO.dll`:

```yaml
  publish:
    needs: build
    runs-on: windows-latest
    steps:
      - uses: compas-dev/compas-actions.publish@v3
        with:
          pypi_token: ${{ secrets.PYPI }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          build_ghpython_components: true
          gh_source: src/compas_cem/ghpython/components_cpython
          gh_target: src/compas_cem/ghpython/components_cpython/ghuser
          gh_prefix: "COMPAS CEM: "
          gh_interpreter: "cpython"
          release_name_prefix: COMPAS CEM
```

`yakerize` and `publish_yak` remain available from `tasks.py` for local and
manual publishing, which is also how `compas_fab` arranges it.

### 15.3 Resolved: GUIDs are random per build, not name-derived

Settled 2026-08-07 by reading `componentize_cpy.py` in
`compas-dev/compas-actions.ghpython_components`.

GUIDs are **not** derived from the component name. `metadata.json` may carry an
optional `instanceGuid`, and when it is absent the componentizer mints a fresh
random one:

```python
instance_guid = data.get("instanceGuid")
if not instance_guid:
    instance_guid = System.Guid.NewGuid()
else:
    instance_guid = System.Guid.Parse(instance_guid)
```

The componentizer README confirms it: *"`instanceGuid`: **(optional)**
Statically define a GUID for this instance. Defaults to a new Guid."*

**The Phase 1 renames are therefore harmless here.** `CompasCem_Constraint*` →
`CompasCem_Goal*` changed no GUID, because the directory name never fed one.

The real finding is larger and predates this work. No `instanceGuid` appears in
any of the 39 `metadata.json` files, so **every build emits a fresh random GUID
for every component**, and no `.ghuser` has ever been committed to this
repository. Consequently §5's line — *"`instanceGuid`s preserved so existing
`.gh` files still resolve"* — describes something the current setup cannot
deliver, and never could.

This is not a `compas_cem` defect. A code search across `compas-dev` returns
`instanceGuid` in exactly three files, all of them fixtures in the
componentizer's own `examples/`; no production COMPAS package pins GUIDs.

**Decision owed in Phase 5**, and it is a genuine fork:

- **Accept the ecosystem default.** Ship random GUIDs as `compas_fab` and
  `compas_timber` do, and document in the 0.9.0 notes that components must be
  re-placed in existing `.gh` files. Cheap, conventional, and consistent with
  `Constraint` → `Goal` already being a deliberate break.
- **Pin them.** Add a static `instanceGuid` to all 39 `metadata.json` files so
  every future release is stable. Backward compatibility with 0.8.6 additionally
  requires recovering the GUIDs from the published 0.8.6 yak package's `.ghuser`
  files — they exist nowhere in this repository.

Pinning is worth doing regardless for *future* stability; whether to also
reconstruct the 0.8.6 values depends on how many users hold live `.gh` files,
which is a judgement call rather than a technical one.

---

## 16. Phase 5 outcome

Written 2026-08-07, at the end of the session that ported the `ghpython` layer.
The work sits **uncommitted in the working tree**; nothing was committed.

With this, **no module of the package is on COMPAS 1 APIs**, which is what
§14.3 set as the definition of a complete COMPAS 2 migration.

### 16.1 What changed

| item | outcome |
| --- | --- |
| `components/` → `components_cpython/` | renamed with `git mv`, so the rename is recorded rather than a delete plus add |
| the 39 `code.py` | all ported: `# r: compas_cem>=0.9.0` header, `Grasshopper.Kernel.GH_ScriptInstance`, PEP 484 on `RunScript`, `ghenv.Component` for the two components that touch it |
| the 13 geometry components | on `compas_rhino.conversions`; the counts match §4.5 exactly — point ×5, line ×4, vector ×3, plane ×2, polyline ×1 |
| the 39 `metadata.json` | `isAdvancedMode` dropped, a static `instanceGuid` pinned in each, all 39 unique |
| `artists.py` (397 lines) | replaced by `scene_objects.py`, registering `FormDiagramObject` and `TopologyDiagramObject` in the `Grasshopper` context |
| `install.py`, `uninstall.py`, `register.py` | deleted, along with `__all_plugins__` |
| `tasks.py`, `release.yml`, `yak_template/` | wired per §15.2, with the correction in §16.3 |

Class names follow the viewer port rather than the plotter one —
`DiagramObject`, `FormDiagramObject`, `TopologyDiagramObject` — because the
Grasshopper objects carry no backend name in the way `FormPlotterObject` does.

### 16.2 Resolved: §15.3, pin fresh GUIDs

Decided by Rafael during this session. A static `instanceGuid` is now pinned in
all 39 `metadata.json` files, minted fresh rather than recovered from the
published 0.8.6 yak package.

The consequence to carry into the 0.9.0 notes: components in a `.gh` file built
against **0.8.6 must be re-placed once**, on the upgrade. Every release after
0.9.0 is stable, which is what the old §5 line about preserving `instanceGuid`s
promised and could never deliver.

### 16.3 Corrections to the plan, learned by doing

- **§4.5's `marshalOutGuids` → `marshalGuids` swap is a no-op here.** No
  `metadata.json` in this repository carries either key, so only the
  `isAdvancedMode` half of that instruction applied.
- **§15.2's `tasks.py` snippet is incomplete.** `yakerize` in the installed
  `compas_invocations2` does not find `yak_template/` by convention: it resolves
  `ctx.yak.manifest_path` and `ctx.yak.logo_path` by config key and exits if
  either is missing. A `yak` block was added alongside `ghuser_cpython`. Taken
  as given, the blueprint would have failed at run time.
- **`yakerize` accepts `rh6`, `rh7` or `rh8` only** for `target_rhino`, and
  defaults to `rh8`. There is no `rh9` value to pass, so the Rhino 8 package is
  what a Rhino 9 install loads.
- **Rhino 8 being CPython 3.9 constrains the annotations.** Grasshopper passes
  `None` for an unconnected input, so the honest annotation is `int | None`,
  which 3.9 evaluates at definition time and rejects. Every component therefore
  carries `from __future__ import annotations`.

### 16.4 Latent bugs fixed in passing

- `_draw_forces` normalized a force vector *before* testing its magnitude, so
  any node carrying no load or reaction divided by a zero length. Same class as
  the §12.7 warnings.
- `draw_reactions` searched an empty sequence for the strongest edge force at a
  node with no connected edge. The Phase 2 plotter already guarded this; the
  Grasshopper artist did not.
- The topology JSON import component declared a class named
  `FormDiagramFromJSON` and documented itself as importing a form diagram.
- `CompasCem_ArtistTopology/metadata.json` misspelled `typeHintID` as
  `typeHinID` twice, leaving two inputs without a type hint.
- `CompasCem_ResultsSupportNodes` built its output with `rs.AddPoint`, which
  bakes a point into the Rhino document instead of returning geometry. Now
  `point_to_rhino`.
- The topology draw methods returned `None` instead of an empty list when a
  selection came back empty.

Two Rhino 7 leftovers were also repaired: `.gitignore` and the ruff
`per-file-ignores` both still pointed at `ghpython/components/`.

### 16.5 What is not verified

**The componentizer was never run.** It needs `GH_IO.dll`, and this machine has
neither Mono nor Rhino installed, so no `.ghuser` was built and no `.yak` was
packaged. That verification belongs to CI on `windows-latest`, and
`release.yml` is still tag-triggered and completely unrun (§14.5).

What *was* verified: `ruff check` clean; `ruff format --check` clean over `src`
and `tests`; all 39 `code.py` plus `scene_objects.py` and `tasks.py`
compile; 107/107 tests pass; `compas_cem`, `.ghpython`, `.plotters` and
`.viewers` all import outside Rhino; `mkdocs build --strict` succeeds; and
`invoke --list` shows all fifteen tasks with the new configuration loaded.

The two `ruff format --check` failures under `docs/` are code blocks in this
file and predate the phase. CI's lint runs `ruff check --fix src tests` only, so
they were never a gate.

Nothing in this phase can be exercised without Rhino, so **the acceptance test
is opening Grasshopper**: load the built package, drop each component, and
confirm the two artist components draw. That is the one thing still outstanding.

### 16.6 Left alone deliberately

`CompasCem_ResultsSupportNodes/metadata.json` names its second input `node`
while `RunScript` calls the parameter `support_node_keys`. Grasshopper binds
positionally, so it works. Renaming the metadata entry would change a visible
component input, which is not something a port should do; renaming the code
parameter would make it less clear. Recorded rather than changed.

### 16.7 Owed before tagging 0.9.0

§14.5 still stands in full, and the version bump is now load-bearing: the
component headers read `compas_cem>=0.9.0` while `pyproject.toml` reads 0.8.6.
`grasshopper.update_gh_header` rewrites those headers from the `bumpversion`
version, so bumping first makes them consistent; running it before the bump
would walk them back to 0.8.6.
