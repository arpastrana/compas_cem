import os

from compas_invocations2 import build
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
)

# Grasshopper component building attaches here in Phase 5, once the components
# are ported to Rhino 8 CPython and packaged with yak.
ns.configure({"base_folder": os.path.dirname(__file__)})
