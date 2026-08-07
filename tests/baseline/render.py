"""
Render every example to an image, for visual review of the plotters layer.

There are no tests for the visualization layer and none are worth inventing, so
the acceptance for it is somebody looking at the output. This runs the examples
headless and saves what each one would have shown.

    PYTHONPATH=src MPLBACKEND=Agg python tests/baseline/render.py

Images land in `renders/` at the repository root, which is gitignored. Set
`COMPAS_CEM_RENDER_DIR` to write them somewhere else.
"""

import os
import runpy
import sys
import traceback

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


def main():
    """
    Run every example and save its plot instead of showing it.
    """
    sys.path.insert(0, os.path.join(REPO, "src"))

    outdir = os.environ.get("COMPAS_CEM_RENDER_DIR", os.path.join(REPO, "renders"))
    os.makedirs(outdir, exist_ok=True)

    from compas_cem.plotters import Plotter

    saved = []
    failed = []

    def show(self, *args, **kwargs):
        path = os.path.join(outdir, show.name + ".png")
        self.save(path, bbox_inches="tight")
        saved.append(path)

    Plotter.show = show

    cwd = os.getcwd()
    for script in SCRIPTS:
        show.name = os.path.splitext(script)[0]
        before = len(saved)

        os.chdir(EXAMPLES)
        try:
            runpy.run_path(os.path.join(EXAMPLES, script), run_name="__main__")
            status = "ok" if len(saved) > before else "no plot"
        except Exception:
            status = "error: " + traceback.format_exc().splitlines()[-1]
            failed.append(script)
        finally:
            os.chdir(cwd)

        print(f"{script:34s} {status}")

    print(f"\nwrote {len(saved)} images to {outdir}")
    if failed:
        print("FAILED:", failed)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
