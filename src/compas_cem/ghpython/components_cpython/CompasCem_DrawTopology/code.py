# r: compas_cem>=0.9.1
"""
Draw a topology diagram in color, with its deviation edges dashed and its loaded nodes crossed. The outputs are Rhino model objects: a Model Object or Data parameter keeps their colors and plot weights, a Line, Curve or Point parameter only their geometry. Press bake to add the drawing to the Rhino document.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import Rhino
import System

from compas_cem.ghpython import TopologyPreview
from compas_cem.ghpython import topology_drawing


class DrawTopologyComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        topology: Any,
        node_keys: System.Collections.Generic.List[int],
        edge_keys: System.Collections.Generic.List[object],
        show_labels: bool | None,
        bake: bool | None,
    ) -> Any:
        self.preview = None

        # The component draws its outputs in color, so their default preview stays off.
        for output in ghenv.Component.Params.Output:  # noqa: F821
            output.Hidden = True

        if not topology:
            return

        node_keys = node_keys or None
        edge_keys = edge_keys or None

        drawing = topology_drawing(topology, node_keys, edge_keys, bool(show_labels))
        self.preview = TopologyPreview(drawing)

        if bake:
            baked_ids = self.preview.bake(Rhino.RhinoDoc.ActiveDoc)
            remark = Grasshopper.Kernel.GH_RuntimeMessageLevel.Remark
            message = "Baked {} objects.".format(len(baked_ids))
            ghenv.Component.AddRuntimeMessage(remark, message)  # noqa: F821

        outputs = (
            self.preview.node_objects,
            self.preview.origin_objects,
            self.preview.support_objects,
            self.preview.edge_objects,
            self.preview.trail_edge_objects,
            self.preview.deviation_edge_objects,
            self.preview.trail_objects,
            self.preview.load_objects,
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

    def get_ClippingBox(self):
        preview = getattr(self, "preview", None)
        if preview is None:
            return Rhino.Geometry.BoundingBox.Empty

        return preview.clipping_box
