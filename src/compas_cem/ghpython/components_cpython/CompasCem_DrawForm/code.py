# r: compas_cem>=0.9.1
"""
Draw a form diagram.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import Rhino
import System

from compas_cem.ghpython import FormDisplaySettings
from compas_cem.ghpython import FormPreview
from compas_cem.ghpython import form_drawing


class DrawFormComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        form: Any,
        node_keys: System.Collections.Generic.List[int],
        edge_keys: System.Collections.Generic.List[object],
        settings: Any,
    ) -> Any:
        self.preview = None

        # The component draws its outputs in color, so their default preview stays off.
        for output in ghenv.Component.Params.Output:  # noqa: F821
            output.Hidden = True

        if not form:
            return

        node_keys = node_keys or None
        edge_keys = edge_keys or None
        settings = settings or FormDisplaySettings()

        drawing = form_drawing(form, node_keys, edge_keys, settings)
        self.preview = FormPreview(drawing)

        outputs = (
            self.preview.node_objects,
            self.preview.support_objects,
            self.preview.edge_objects,
            self.preview.load_objects,
            self.preview.reaction_objects,
        )

        return outputs

    def DrawViewportWires(self, args):
        preview = getattr(self, "preview", None)
        if preview is None:
            return

        selected_color = None
        if ghenv.Component.Attributes.Selected:  # noqa: F821
            selected_color = args.WireColour_Selected

        preview.draw_wires(args.Display, args.Viewport, selected_color)

    def get_ClippingBox(self):
        preview = getattr(self, "preview", None)
        if preview is None:
            return Rhino.Geometry.BoundingBox.Empty

        return preview.clipping_box
