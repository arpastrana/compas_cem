# from compas.geometry import Sphere
# from compas_view2.app import App
# viewer = App()
# # viewer.add(Sphere([0, 0, 0], 1.0))
# viewer.add(Sphere([0, 0, 0], 1.0),
#           u=64,
#           v=64,
#           show_points=True,
#           show_lines=True,
#           show_faces=True,
#           color=(0.7, 0., 0.7),
#           pointcolor=(1.0, 0.0, 0.0),
#           linecolor=(0.0, 0.0, 1.0),
#           facecolor=(0.0, 1.0, 1.0),
#           pointsize=10,
#           linewidth=2,
#           opacity=0.5,
#           is_selected=False,
#           is_visible=True)
# viewer.show()


# import compas
# from compas.geometry import Sphere
# from compas.colors import Color

# from compas_view2.app import App

# sphere = Sphere([0, 0, 0], 1.0)

# # =============================================================================
# # Visualization
# # =============================================================================

# viewer = App(width=960, height=540)
# viewer.view.camera.rx = -60
# viewer.view.camera.rz = 0
# viewer.view.camera.distance = 5

# viewer.add(sphere, u=64, v=64, facecolor=Color.cyan(), linecolor=Color.blue())


# @viewer.on(interval=50, frames=180, record=True, record_path="docs/_images/example_orbiting.gif")
# def orbit(f):
#     viewer.view.camera.rz += 1


# viewer.show()


from compas.geometry import Point, Polyline, Bezier
from compas.colors import Color
from compas_view2.app import App

curve = Bezier([[0, 0, 0], [3, 6, 0], [5, -3, 0], [10, 0, 0]])

viewer = App(viewmode="shaded", enable_sidebar=True, width=1600, height=900)
viewer.view.camera.tx = -5.0
viewer.view.camera.rz = 0
viewer.view.camera.rx = -20

pointobj = viewer.add(Point(* curve.point(0)), size=20, color=(1, 0, 0))
curveobj = viewer.add(Polyline(curve.locus()), linewidth=2)


@viewer.checkbox(text="Show Point", checked=True)
def check(checked):
    pointobj.is_visible = checked
    viewer.view.update()


@viewer.slider(title="Slide Point", maxval=100, step=1, bgcolor=Color.white())
def slide(value):
    value = value / 100
    pointobj._data = curve.point(value)
    pointobj.update()
    viewer.view.update()


@viewer.button(text="Reset")
def click():
    if viewer.confirm('This will reset the point to parameter t=0.'):
        pointobj._data = curve.point(0)
        pointobj.update()
        slide.value = 0
        viewer.view.update()


@viewer.radio(title='Display', items=[
    {'text': 'Ghosted', 'value': 'ghosted', 'checked': viewer.view.mode == 'ghosted'},
    {'text': 'Shaded', 'value': 'shaded', 'checked': viewer.view.mode == 'shaded'},
    {'text': 'Lighted', 'value': 'lighted', 'checked': viewer.view.mode == 'lighted'},
    {'text': 'Wireframe', 'value': 'wireframe', 'checked': viewer.view.mode == 'wireframe'}
])
def select(value):
    viewer.view.mode = value
    viewer.view.update()


viewer.run()
