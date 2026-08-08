import json
import networkx as nx


def cascade_failure_simulator_based_on_Load_Capacity_model_with_proportional_load_redistribution(main_json_path):
    main_json_path = main_json_path.strip().replace('"', '')
    output_json_path = 'cascade_failure_simulator_based_on_Load_Capacity_model_with_proportional_load_redistribution.json'

    # Load global_data.json
    with open(main_json_path, 'r') as f:
        file_paths = json.load(f)

    # Load network topology
    with open(file_paths['interdependent_critical_infrastructures_networks'], 'r') as f:
        network_topology = json.load(f)

    # Load load distribution
    with open(file_paths['load_distribution'], 'r') as f:
        load_distribution = json.load(f)


    with open(file_paths['failure_node_after_HECRAS_simulations'], 'r') as f:
        flooded_data = json.load(f)

    # Construct directed graph
    G = nx.DiGraph()

    # Add nodes to the network
    for node in network_topology['nodes']:
        G.add_node(node['Code'], **node)

    # Add edges to the network
    for edge in network_topology['edges']:
        G.add_edge(edge['Start'], edge['End'], **edge)

    # Create dictionary for node load and capacity
    node_data = {entry['Code']: {'load': entry['Initial Load'], 'capacity': entry['Capacity']} for entry in
                 load_distribution['nodes']}

    # Get initial failed nodes from hecras_simulated_flooded_nodes's 'all_failed_nodes'
    failed_nodes = flooded_data['all_failed_nodes']

    cascading_failures = []  # Record cascading failure history
    processed_failed_nodes = set(failed_nodes)

    # Process cascading failures
    while failed_nodes:
        new_failed_nodes = []
        for node in failed_nodes:
            if not G.has_node(node):
                continue

            # Record failed node information with actual load value (even if it exceeds capacity)
            cascading_failures.append({
                'failed_node': node,
                'load': node_data[node]['load'],
                'capacity': node_data[node]['capacity']
            })

            # Get neighboring nodes and calculate load based on connection strength
            neighbors = [edge[1] for edge in G.out_edges(node)]
            if neighbors:
                total_connection_strength = sum(G.degree(neighbor) for neighbor in neighbors)

                for neighbor in neighbors:
                    # Redistribute load based on the neighbor's connection strength (degree)
                    load_to_redistribute = node_data[node]['load'] * (G.degree(neighbor) / total_connection_strength)
                    node_data[neighbor]['load'] += load_to_redistribute

                    # Check if load exceeds capacity but do not cap it in node_data
                    if node_data[neighbor]['load'] > node_data[neighbor]['capacity'] and neighbor not in processed_failed_nodes:
                        new_failed_nodes.append(neighbor)

        processed_failed_nodes.update(failed_nodes)
        failed_nodes = new_failed_nodes

    # Save cascading failure history to new file
    with open(output_json_path, 'w') as f:
        json.dump(cascading_failures, f, indent=4)

    # Update global_data.json with new path
    file_paths['cascade_failure_simulator_based_on_Load_Capacity_model_with_proportional_load_redistribution'] = output_json_path
    with open(main_json_path, 'w') as f:
        json.dump(file_paths, f, indent=4)

    return "The cascading failure behavior has been simulated and saved to the specified JSON files."


# Example usage
main_json_path = 'Global_Data.json'
cascade_failure_simulator_based_on_Load_Capacity_model_with_proportional_load_redistribution(main_json_path)
