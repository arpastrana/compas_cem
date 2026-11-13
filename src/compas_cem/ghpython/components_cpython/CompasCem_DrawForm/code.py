# r: compas_cem>=0.9.1
"""
Draw a form diagram in color, with its loads and reaction forces as arrows. The outputs are Rhino model objects: a Model Object or Data parameter keeps their colors and plot weights, a Line, Curve or Point parameter only their geometry. Press bake to add the drawing to the Rhino document.
"""

from __future__ import annotations

from dataclasses import replace
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
        thicken: bool | None,
        decompose: bool | None,
        show_loads: bool | None,
        show_reactions: bool | None,
        show_labels: bool | None,
        bake: bool | None,
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
        is_decomposed = True if decompose is None else bool(decompose)
        are_loads_shown = True if show_loads is None else bool(show_loads)
        are_reactions_shown = True if show_reactions is None else bool(show_reactions)
        settings = replace(
            settings,
            decompose=is_decomposed,
            show_loads=are_loads_shown,
            show_reactions=are_reactions_shown,
            show_labels=bool(show_labels),
        )

        drawing = form_drawing(form, node_keys, edge_keys, settings)
        self.preview = FormPreview(drawing, bool(thicken), settings.thick_sides)

        if bake:
            baked_ids = self.preview.bake(Rhino.RhinoDoc.ActiveDoc)
            remark = Grasshopper.Kernel.GH_RuntimeMessageLevel.Remark
            message = "Baked {} objects.".format(len(baked_ids))
            ghenv.Component.AddRuntimeMessage(remark, message)  # noqa: F821

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

        preview.draw_wires(args.Display, selected_color)

    def DrawViewportMeshes(self, args):
        preview = getattr(self, "preview", None)
        if preview is None:
            return

        selected_material = None
        if ghenv.Component.Attributes.Selected:  # noqa: F821
            selected_material = args.ShadeMaterial_Selected

        preview.draw_meshes(args.Display, selected_material)

    def get_ClippingBox(self):
        preview = getattr(self, "preview", None)
        if preview is None:
            return Rhino.Geometry.BoundingBox.Empty

        return preview.clipping_box
