
def CEMM(form, topology, max_iters, epsilon=1e-5):
    form = FormDiagram.from_topology_diagram(topology)

    for t in range(max_iters):

        # last_iter_xyz = copy(form.nodes_xyz())  # copy last xyz position

        for sequence in topological_sequences:
            for trail in trails:

                # fetch node triplet
                this_node = topology.get_node_at_trail(trail, sequence)
                next_node = topology.get_node_at_trail(trail, sequence + 1)

                # calculate equilbrium at this node
                r_force = node_equiibrium(this_node, topology)

                # compute position of next node
                form.next_node_xyz(this_node, next_node, r_force)

                # calculate residual forces
                form.residual_forces(this_node, next_node, r_force)

        # verify convergence
        if compute_convergence_energy(form, last_iter_xyz) <= 1e-5:
            break

        return form









            

        
