import os

from compas_invocations2 import build
from compas_invocations2 import grasshopper
from compas_invocations2 import mkdocs
from compas_invocations2 import style
from compas_invocations2 import tests
from invoke.collection import Collection

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
)

GHPYTHON = "src/compas_cem/ghpython"

ns.configure(
    {
        "base_folder": os.path.dirname(__file__),
        "ghuser_cpython": {
            "source_dir": "{}/components_cpython".format(GHPYTHON),
            "target_dir": "{}/components_cpython/ghuser".format(GHPYTHON),
            "prefix": "COMPAS CEM: ",
        },
        # yakerize resolves these two by config key, not by folder convention.
        "yak": {
            "manifest_path": "{}/yak_template/manifest.yml".format(GHPYTHON),
            "logo_path": "{}/yak_template/icon.png".format(GHPYTHON),
        },
    }
)
