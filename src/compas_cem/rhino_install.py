from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import compas
import compas.plugins


@compas.plugins.plugin(category='install')
def installable_rhino_packages():
    return ['compas_cem']


# @compas.plugins.plugin(category='install')
# def after_rhino_install(installed_packages):
#     if 'compas_cem' not in installed_packages:
#         return []

#     import compas_fab.rhino.components.install
#     return compas_fab.rhino.components.install.install()


# @compas.plugins.plugin(category='install')
# def after_rhino_uninstall(installed_packages):
#     if 'compas_cem' not in installed_packages:
#         return []

#     import compas_fab.rhino.components.install
#     return compas_fab.rhino.components.install.uninstall()


if __name__ == "__main__":
    pass
