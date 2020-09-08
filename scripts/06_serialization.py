from compas.rpc import Proxy

from compas_cem.optimization import PlaneGoal
from compas_cem.optimization import TrimeshGoal

from compas_cem.optimization import TrailEdgeConstraint
from compas_cem.optimization import DeviationEdgeConstraint

from compas_cem.optimization import cls_from_dtype

from compas.geometry import Point
from compas.geometry import Plane


constraint = TrailEdgeConstraint((0, 1), -2, 3)
goal = PlaneGoal(0, Plane([0, 0, 0], [0, 0, 1]))

cls = cls_from_dtype(constraint.data["dtype"])

new_constraint = cls.from_data(constraint.data)
assert new_constraint.data == constraint.data


cls = cls_from_dtype(goal.data["dtype"])

new_goal = cls.from_data(goal.data)

print("goal data", goal.data)
print("new goal data", new_goal.data)

assert new_goal.data == goal.data
