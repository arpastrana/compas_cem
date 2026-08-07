"""
Prototype: CEM equilibrium as a pure JAX function.

Validates the proposed architecture (numpy index arrays + lax.scan over sequences
+ lax.while_loop fixed point) against the ground-truth values hardcoded in
tests/equilibrium/test_force.py for the `braced_tower_2d` fixture, which is the
only fixture exercising both direct and indirect deviation edges.
"""

import jax
import jax.numpy as jnp
import numpy as np

jax.config.update("jax_enable_x64", True)


# ------------------------------------------------------------------------------
# Static structure (numpy) -- derived by hand from the braced_tower_2d fixture
# ------------------------------------------------------------------------------

XYZ0 = np.array([[0.0, 0.0, 0.0],
                 [0.0, 1.0, 0.0],
                 [0.0, 2.0, 0.0],
                 [1.0, 0.0, 0.0],
                 [1.0, 1.0, 0.0],
                 [1.0, 2.0, 0.0]])

LOADS = np.zeros((6, 3))
LOADS[2] = [0.0, -1.0, 0.0]
LOADS[5] = [0.0, -1.0, 0.0]

# trail edges, in insertion order, then deviation edges
EDGES = [(0, 1), (1, 2), (3, 4), (4, 5),
         (1, 4), (2, 5), (1, 5), (1, 3), (2, 4)]
IS_TRAIL = np.array([1, 1, 1, 1, 0, 0, 0, 0, 0], dtype=bool)
LENGTHS = np.array([-1.0, -1.0, -1.0, -1.0, 0, 0, 0, 0, 0])
FORCES = np.array([0, 0, 0, 0, -1.0, -1.0, 1.0, 1.0, 1.0])

# build_trails() from supports {0, 3} yields trails (2,1,0) and (5,4,3),
# so _k is 2->0 1->1 0->2 and 5->0 4->1 3->2
SEQUENCES = np.array([[2, 5],
                      [1, 4],
                      [0, 3]])
SUPPORTS = np.array([1, 0, 0, 1, 0, 0], dtype=bool)

NODES = XYZ0.shape[0]
NUM_EDGES = len(EDGES)
K, TRAILS = SEQUENCES.shape


def build_structure():
    """
    Derive the index arrays the traced solver needs. numpy only.
    """
    node_sequence = np.full(NODES, -1, dtype=int)
    for k in range(K):
        node_sequence[SEQUENCES[k]] = k

    # trail edge travelled from sequence k to k+1, per (sequence, trail)
    edge_index = {edge: i for i, edge in enumerate(EDGES)}
    trail_edge = np.zeros((K, TRAILS), dtype=int)
    for k in range(K - 1):
        for t in range(TRAILS):
            u, v = SEQUENCES[k, t], SEQUENCES[k + 1, t]
            trail_edge[k, t] = edge_index.get((u, v), edge_index.get((v, u), 0))

    # a (sequence, trail) slot advances the trail when a next node exists and
    # the current node is not a support
    active = np.zeros((K, TRAILS), dtype=bool)
    active[: K - 1] = ~SUPPORTS[SEQUENCES[: K - 1]]

    # deviation incidence, duplicated so each edge contributes to both endpoints
    deviation = np.flatnonzero(~IS_TRAIL)
    dev_u = np.array([EDGES[e][0] for e in deviation])
    dev_v = np.array([EDGES[e][1] for e in deviation])
    incidence_node = np.concatenate([dev_u, dev_v])
    incidence_other = np.concatenate([dev_v, dev_u])
    incidence_edge = np.concatenate([deviation, deviation])
    # indirect := endpoints sit in different sequences
    indirect = node_sequence[dev_u] != node_sequence[dev_v]
    incidence_indirect = np.concatenate([indirect, indirect])

    return {"sequences": jnp.asarray(SEQUENCES),
            "trail_edge": jnp.asarray(trail_edge),
            "active": jnp.asarray(active),
            "supports_at": jnp.asarray(SUPPORTS[SEQUENCES]),
            "incidence_node": jnp.asarray(incidence_node),
            "incidence_other": jnp.asarray(incidence_other),
            "incidence_edge": jnp.asarray(incidence_edge),
            "incidence_indirect": jnp.asarray(incidence_indirect)}


# ------------------------------------------------------------------------------
# Traced solver
# ------------------------------------------------------------------------------

EPS = 1e-12


def safe_normalize(vectors):
    """
    Normalize row-wise without leaking NaNs into the gradient.
    """
    norm = jnp.linalg.norm(vectors, axis=-1, keepdims=True)
    safe = jnp.where(norm > EPS, norm, 1.0)

    return jnp.where(norm > EPS, vectors / safe, vectors)


def deviation_resultants(xyz, forces, structure, use_indirect):
    """
    Sum the force vectors of the deviation edges incident to every node.
    """
    node = structure["incidence_node"]
    other = structure["incidence_other"]
    edge = structure["incidence_edge"]

    directions = safe_normalize(xyz[other] - xyz[node])
    force = forces[edge]
    force = jnp.where(structure["incidence_indirect"] & ~use_indirect, 0.0, force)
    contributions = force[:, None] * directions

    return jax.ops.segment_sum(contributions, node, num_segments=NODES)


def sequence_step(carry, k, lengths, forces, loads, structure, use_indirect):
    """
    Equilibrate every trail at one sequence, then advance each trail one node.
    """
    xyz, residuals, reactions, trail_forces = carry

    nodes = structure["sequences"][k]
    nodes_next = structure["sequences"][jnp.minimum(k + 1, K - 1)]
    edge = structure["trail_edge"][k]
    active = structure["active"][k]
    is_support = structure["supports_at"][k]

    resultants = deviation_resultants(xyz, forces, structure, use_indirect)
    residual_out = residuals[nodes] - loads[nodes] - resultants[nodes]

    reactions = reactions.at[nodes].set(
        jnp.where(is_support[:, None], residual_out, reactions[nodes]))

    length = lengths[edge]
    norm = jnp.linalg.norm(residual_out, axis=-1)
    direction = safe_normalize(residual_out)
    position_next = xyz[nodes] + length[:, None] * direction

    xyz = xyz.at[nodes_next].set(
        jnp.where(active[:, None], position_next, xyz[nodes_next]))
    residuals = residuals.at[nodes_next].set(
        jnp.where(active[:, None], residual_out, residuals[nodes_next]))
    trail_forces = trail_forces.at[edge].set(
        jnp.where(active, jnp.sign(length) * norm, trail_forces[edge]))

    return (xyz, residuals, reactions, trail_forces), None


def equilibrium_pass(state, lengths, forces, loads, structure, use_indirect):
    """
    One sweep over all sequences.
    """
    def step(carry, k):
        return sequence_step(carry, k, lengths, forces, loads, structure, use_indirect)

    carry, _ = jax.lax.scan(step, state, jnp.arange(K))

    return carry


def sweep(xyz, lengths, forces, loads, structure, use_indirect=True):
    """
    One full sequence sweep as a map xyz -> xyz, plus the derived quantities.

    Origin-node positions are never written by the sweep, so they stay pinned to
    the input, which makes this a well-posed fixed-point map.
    """
    zeros_nodes = jnp.zeros((NODES, 3))
    state = (xyz, zeros_nodes, zeros_nodes, jnp.zeros(NUM_EDGES))

    return equilibrium_pass(state, lengths, forces, loads, structure, use_indirect)


def static_equilibrium_whileloop(lengths, forces, loads, xyz, structure, tmax=100, eta=1e-6):
    """
    Faithful port of force_numpy.py: convergence-terminated, NOT reverse-differentiable.
    """
    zeros_nodes = jnp.zeros((NODES, 3))
    init = (xyz, zeros_nodes, zeros_nodes, jnp.zeros(NUM_EDGES))

    def condition(loop):
        t, residual, _ = loop
        return (t < tmax) & ((t < 2) | (residual > eta))

    def body(loop):
        t, _, state = loop
        use_indirect = t > 0
        state_next = equilibrium_pass(state, lengths, forces, loads, structure, use_indirect)
        residual = jnp.linalg.norm(state_next[0] - state[0])

        return t + 1, residual, state_next

    _, residual, state = jax.lax.while_loop(condition, body, (0, jnp.inf, init))
    xyz, _, reactions, trail_forces = state

    return {"xyz": xyz,
            "reactions": reactions,
            "trail_forces": trail_forces,
            "residual": residual}


def static_equilibrium(lengths, forces, loads, xyz, structure, tmax=100, eta=1e-6):
    """
    Solve for static equilibrium. Pure, jittable, reverse-differentiable.

    The outer relaxation is posed as a fixed point on the node coordinates and
    solved with implicit differentiation, so the adjoint cost is independent of
    the iteration count.
    """
    import optimistix

    # Origin nodes are never written by a sweep, so if they are carried as
    # fixed-point variables their rows of (I - J) vanish and the adjoint solve is
    # singular. Pin them to the parameter inside the map instead.
    origins = structure["sequences"][0]

    def fixed_point_map(coordinates, args):
        coordinates = coordinates.at[origins].set(xyz[origins])

        return sweep(coordinates, lengths, forces, loads, structure)[0]

    solver = optimistix.FixedPointIteration(rtol=eta, atol=eta)
    solution = optimistix.fixed_point(fixed_point_map,
                                      solver,
                                      xyz,
                                      max_steps=tmax,
                                      throw=False)

    converged, _, reactions, trail_forces = sweep(solution.value, lengths, forces,
                                                 loads, structure)

    return {"xyz": converged,
            "reactions": reactions,
            "trail_forces": trail_forces,
            "residual": jnp.linalg.norm(converged - solution.value)}


# ------------------------------------------------------------------------------
# Validation against tests/equilibrium/test_force.py::bt2_out
# ------------------------------------------------------------------------------

EXPECTED_XYZ = np.array([[0.11891271935545733, 0.04623304043571308, 0.0],
                         [-0.14550216351451895, 1.0106420665842952, 0.0],
                         [0.0, 2.0, 0.0],
                         [1.5829003695589805, 0.11137412111377487, 0.0],
                         [1.1455022100524879, 1.010642073428508, 0.0],
                         [1.0, 2.0, 0.0]])

EXPECTED_FORCE = {(0, 1): -1.5154917766302523,
                  (1, 2): -1.6714301665432025,
                  (3, 4): -1.1120156232900127,
                  (4, 5): -1.6714302901903129}

EXPECTED_REACTION = {0: [-0.4007185806081004, 1.4615539484361662, -0.0],
                     3: [0.40071844900288345, 0.5384458270605735, -0.0]}


def main():
    structure = build_structure()
    solve = jax.jit(lambda lengths, forces, loads, xyz:
                    static_equilibrium(lengths, forces, loads, xyz, structure, eta=1e-5))

    result = solve(jnp.asarray(LENGTHS), jnp.asarray(FORCES),
                   jnp.asarray(LOADS), jnp.asarray(XYZ0))

    print("residual:", float(result["residual"]))

    ok = True
    print("\nnode xyz")
    for node in range(NODES):
        got = np.asarray(result["xyz"][node])
        want = EXPECTED_XYZ[node]
        match = np.allclose(got, want, rtol=1e-5, atol=1e-8)
        ok &= match
        print(f"  {node}  {'ok ' if match else 'BAD'}  {got}  expected {want}")

    print("\ntrail forces")
    for edge, want in EXPECTED_FORCE.items():
        got = float(result["trail_forces"][EDGES.index(edge)])
        match = np.allclose(got, want, rtol=1e-5)
        ok &= match
        print(f"  {edge}  {'ok ' if match else 'BAD'}  {got:.16f}  expected {want:.16f}")

    print("\nreaction forces")
    for node, want in EXPECTED_REACTION.items():
        got = np.asarray(result["reactions"][node])
        match = np.allclose(got, want, rtol=1e-5, atol=1e-8)
        ok &= match
        print(f"  {node}  {'ok ' if match else 'BAD'}  {got}  expected {want}")

    print("\nPARITY:", "PASS" if ok else "FAIL")

    # gradient of a toy loss through the whole fixed point
    def loss(forces):
        state = static_equilibrium(jnp.asarray(LENGTHS), forces, jnp.asarray(LOADS),
                                   jnp.asarray(XYZ0), structure, eta=1e-5)
        return jnp.sum(jnp.square(state["xyz"][0] - jnp.array([0.5, 0.0, 0.0])))

    value, gradient = jax.value_and_grad(loss)(jnp.asarray(FORCES))
    print("\nvalue_and_grad through the fixed point")
    print("  loss:", float(value))
    print("  dloss/dforces:", np.asarray(gradient))
    print("  finite in gradient:", bool(np.all(np.isfinite(np.asarray(gradient)))))


if __name__ == "__main__":
    main()
