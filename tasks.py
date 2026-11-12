import os
import tempfile
from pathlib import Path

from compas_invocations2 import build
from compas_invocations2 import grasshopper
from compas_invocations2 import mkdocs
from compas_invocations2 import style
from compas_invocations2 import tests
from invoke import task
from invoke.collection import Collection
from PIL import Image
from PIL import ImageFilter

GHPYTHON = "src/compas_cem/ghpython"

# The drop shadow of the Grasshopper icon guide: black at 65/255, 1 px down and right.
SHADOW_OPACITY = 65 / 255
SHADOW_OFFSET = 1
SHADOW_BLUR = 1.0


def drop_shadow(icon):
    """
    Return the icon over a soft black shadow of its own silhouette.
    """
    silhouette = Image.new("L", icon.size, 0)
    silhouette.paste(icon.getchannel("A"), (SHADOW_OFFSET, SHADOW_OFFSET))
    blurred = silhouette.filter(ImageFilter.GaussianBlur(SHADOW_BLUR))
    opacity_table = [round(level * SHADOW_OPACITY) for level in range(256)]
    shadow_alpha = blurred.point(opacity_table)
    shadowed = Image.new("RGBA", icon.size, (0, 0, 0, 255))
    shadowed.putalpha(shadow_alpha)
    shadowed.alpha_composite(icon)

    return shadowed


@task(help={"component": "Rebuild only the icon in this component folder."})
def build_icons(ctx, component=None):
    """
    Render each component's icon.tex into its 24 px icon.png.

    Needs pdflatex and pdftocairo on the path, from a TeX distribution and poppler.
    """
    source_dir = Path(ctx.base_folder) / ctx.ghuser_cpython.source_dir
    pattern = "{}/icon.tex".format(component or "*")
    sources = sorted(source_dir.glob(pattern))
    for source in sources:
        folder = source.parent
        with tempfile.TemporaryDirectory() as scratch:
            pdf_path = Path(scratch) / "icon.pdf"
            png_stem = Path(scratch) / "icon"
            latex = 'pdflatex -interaction=nonstopmode -halt-on-error -output-directory "{}" icon.tex'
            raster = 'pdftocairo -png -r 72 -transp -singlefile "{}" "{}"'
            with ctx.cd(str(folder)):
                ctx.run(latex.format(scratch), hide=True)
            ctx.run(raster.format(pdf_path, png_stem), hide=True)
            flat = Image.open(png_stem.with_suffix(".png")).convert("RGBA")
        icon = drop_shadow(flat)
        icon.save(folder / "icon.png")
    print("Rendered {} icons.".format(len(sources)))


ns = Collection(
    style.check,
    style.lint,
    style.format,
    mkdocs.docs,
    tests.test,
    tests.testdocs,
    tests.testcodeblocks,
    build.prepare_changelog,
    build.clean,
    build.release,
    build.build_cpython_ghuser_components,
    grasshopper.update_gh_header,
    grasshopper.yakerize,
    grasshopper.publish_yak,
    build_icons,
)

ns.configure(
    {
        "base_folder": os.path.dirname(__file__),
        "ghuser_cpython": {
            "source_dir": "{}/components_cpython".format(GHPYTHON),
            "target_dir": "{}/components_cpython/ghuser".format(GHPYTHON),
        },
        # yakerize resolves these two by config key, not by folder convention.
        "yak": {
            "manifest_path": "{}/yak_template/manifest.yml".format(GHPYTHON),
            "logo_path": "{}/yak_template/icon.png".format(GHPYTHON),
        },
    }
)
