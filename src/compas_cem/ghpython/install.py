from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from compas.plugins import plugin
from compas_ghpython.components import install_userobjects


@plugin(category='install')
def installable_rhino_packages():
    return ['compas_cem']


@plugin(category='install')
def after_rhino_install(installed_packages):
    if 'compas_cem' not in installed_packages:
        return []

    targetdir = os.path.join(os.path.dirname(__file__), 'components', 'ghuser')
    installed_objects = install_userobjects(targetdir)

    return [('compas_cem', 'Installed {} GH User Objects'.format(len(installed_objects)), True)]
