"""
Capture the numerical output of every example as a JSON regression fixture.

These fixtures are the safety net for the COMPAS 2 and JAX migrations: they pin
the behaviour of the solver and the optimizer so a later phase can prove it did
not change anything it did not mean to change.

Run from the repository root, against an environment that can import the
package. `MPLBACKEND=Agg` keeps the examples' plotting calls headless.

    PYTHONPATH=src MPLBACKEND=Agg python tests/baseline/capture.py

Two environment variables support comparison runs:

    COMPAS_CEM_SUFFIX      appended to each fixture's filename, so a re-capture
                           can be diffed against the committed fixtures instead
                           of overwriting them
    COMPAS_CEM_FORCE_EPS   overrides the optimizer's `eps`, which nlopt uses as
                           `stopval`. Setting it far below zero stops nlopt from
                           terminating on an already-satisfied objective, which
                           is how the `*_forced.json` fixtures were produced

Solver returns are intercepted rather than read out of each example's globals,
because several examples rebind `form` to a translated copy before plotting.

If the plotters package cannot be imported, a drawing-free stand-in is installed
in its place so the numerical capture still runs, and a note is printed saying so.
"""

import json
import os
import runpy
import sys
import traceback
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EXAMPLES = os.path.join(REPO, "examples")

SCRIPTS = [
    "01_quick_start.py",
    "02_braced_tower_2d.py",
    "03_bridge_2d.py",
    "04_tree_2d.py",
    "05_tensegrity_wheel_2d.py",
]


def form_state(form):
    """
    Extract every numerical quantity a form diagram carries.
    """
    nodes = sorted(form.nodes())
    edges = [tuple(edge) for edge in form.edges()]

    return {
        "nodes": nodes,
        "edges": [list(edge) for edge in edges],
        "xyz": {str(n): list(form.node_coordinates(n)) for n in nodes},
        "reaction": {str(n): list(form.reaction_force(n)) for n in nodes},
        "force": {str(e): form.edge_force(e) for e in edges},
        "length": {str(e): form.edge_length_2(e) for e in edges},
    }


def optimizer_state(optimizer):
    """
    Extract the optimizer's post-solve diagnostics.

    Duration is excluded because it is not reproducible.
    """
    state = {}
    for name in ("penalty", "gradient_norm", "evals", "status"):
        value = getattr(optimizer, name, None)
        if value is None:
            continue
        try:
            state[name] = float(value)
        except (TypeError, ValueError):
            state[name] = str(value)

    gradient = getattr(optimizer, "gradient", None)
    if gradient is not None:
        state["gradient"] = [float(g) for g in gradient]

    return state


class NoOpPlotter:
    """
    A plotter that accepts every call and draws nothing.
    """

    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        """
        Absorb any plotter method the examples reach for.
        """

        def noop(*args, **kwargs):
            return None

        return noop


def stub_plotters():
    """
    Install a drawing-free stand-in for the plotters package.

    The examples import a plotter at module scope, so a plotters package that
    cannot import stops the numerical capture before it starts. Plotting runs
    after the solver in every example and never feeds back into it, so removing
    it leaves the recorded numbers untouched.
    """
    names = ["Plotter", "FormArtist", "TopologyArtist"]

    module = types.ModuleType("compas_cem.plotters")
    for name in names:
        setattr(module, name, NoOpPlotter)
    setattr(module, "__all__", names)

    sys.modules["compas_cem.plotters"] = module


def originals():
    """
    Grab the unwrapped solver entry points once, before any probe is installed.
    """
    import compas_cem.equilibrium as eq
    from compas_cem.optimization import Optimizer

    try:
        from compas_cem.plotters import Plotter
    except ImportError as error:
        print(f"plotters unavailable ({error}); capturing without plots")
        stub_plotters()
    else:
        # examples end in plotter.show(), which would block
        Plotter.show = lambda self, *args, **kwargs: None

    return eq, Optimizer, eq.static_equilibrium, Optimizer.solve


def install_probes(captured, eq, optimizer_cls, real_static, real_solve):
    """
    Wrap the solver entry points so their results are recorded on the way out.

    Always wraps the pristine originals, so probes never stack across examples.
    """

    def static_equilibrium(topology, *args, **kwargs):
        form = real_static(topology, *args, **kwargs)
        captured.setdefault("static_equilibrium", []).append(form_state(form))

        return form

    def solve(self, *args, **kwargs):
        forced = os.environ.get("COMPAS_CEM_FORCE_EPS")
        if forced is not None:
            kwargs["eps"] = float(forced)
        form = real_solve(self, *args, **kwargs)
        captured.setdefault("solve", []).append(
            {"form": form_state(form), "optimizer": optimizer_state(self)}
        )

        return form

    eq.static_equilibrium = static_equilibrium
    optimizer_cls.solve = solve


def main():
    sys.path.insert(0, os.path.join(REPO, "src"))
    suffix = os.environ.get("COMPAS_CEM_SUFFIX", "")
    pristine = originals()

    failed = []
    for script in SCRIPTS:
        captured = {}
        install_probes(captured, *pristine)

        # examples resolve their data files relative to their own location
        cwd = os.getcwd()
        os.chdir(EXAMPLES)
        try:
            runpy.run_path(os.path.join(EXAMPLES, script), run_name="__main__")
            status, error = "ok", None
        except Exception:
            status = "error"
            error = traceback.format_exc().splitlines()[-1]
            failed.append(script)
        finally:
            os.chdir(cwd)

        name = os.path.splitext(script)[0] + suffix
        payload = {
            "example": script,
            "status": status,
            "error": error,
            "captured": captured,
        }
        with open(os.path.join(HERE, name + ".json"), "w") as f:
            json.dump(payload, f, indent=2, sort_keys=True)
            f.write("\n")

        counts = {k: len(v) for k, v in captured.items()}
        print(f"{script:34s} {status:6s} {counts} {error or ''}")

    print(f"\nwrote {len(SCRIPTS)} fixtures to {HERE}")
    if failed:
        print("FAILED:", failed)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
