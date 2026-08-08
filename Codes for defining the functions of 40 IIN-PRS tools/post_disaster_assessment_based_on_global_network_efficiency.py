import json
import networkx as nx

def calculate_global_efficiency(graph):
    """Calculate global efficiency of the graph."""
    if graph.number_of_nodes() == 0:
        return 0

    lengths = dict(nx.all_pairs_shortest_path_length(graph))
    total_efficiency = 0
    count = 0

    for source in lengths:
        for target in lengths[source]:
            if source != target:
                distance = lengths[source][target]
                # If there is no path, treat distance as infinity (contributes 0 efficiency)
                if distance != float('inf'):
                    total_efficiency += 1 / distance
                    count += 1

    return total_efficiency / count if count > 0 else 0


def post_disaster_assessment_based_on_global_network_efficiency(global_json_path: str):
    # Load global data file to get the network file path
    with open(global_json_path, 'r') as file:
        file_paths = json.load(file)
        network_file = file_paths.get('interdependent_critical_infrastructures_networks')  # Get network file path
        failure_file = file_paths.get('failure_node_after_HECRAS_simulations')
        cascade_file = file_paths.get('cascade_failure_simulator_based_on_Motter_Lai_model')

    if not network_file:
        print("No network file found in Global_Data.json.")
        return

    # Load network data
    with open(network_file, 'r') as file:
        network_data = json.load(file)

    if not isinstance(network_data, dict):
        print("Error: The network data is not in the correct format.")
        return

    nodes = network_data.get('nodes', [])
    edges = network_data.get('edges', [])

    if not nodes or not edges:
        return "Error: Network data is incomplete."

    # Construct directed graph
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node['Code'], **node)
    for edge in edges:
        G.add_edge(edge['Start'], edge['End'], **edge)

    total_nodes = G.number_of_nodes()
    if total_nodes == 0:
        return "Error: The network is empty."

    # Calculate initial global efficiency
    efficiency_before = calculate_global_efficiency(G)

    with open(failure_file, 'r') as f:
        failure_data = json.load(f)
    initial_nodes = failure_data.get("all_failed_nodes", [])

    with open(cascade_file, 'r') as f:
        cascade_data = json.load(f)
    all_failed_nodes = set(cascade_data.get("failed_nodes", []))

    remaining_nodes = [node for node in G.nodes if node not in all_failed_nodes]

    # Create a new graph without the failed nodes
    G_after_failure = G.copy()
    G_after_failure.remove_nodes_from(all_failed_nodes)

    # Calculate global efficiency after cascading failures
    efficiency_after = calculate_global_efficiency(G_after_failure)

    # Prepare the result to save
    result = {
        'initial_attack_nodes': initial_nodes,  # List of initial attack nodes
        'all_failed_nodes': list(all_failed_nodes),  # Nodes failed due to cascading failure
        'number_of_failed_nodes': len(all_failed_nodes),  # Total number of failed nodes
        'remaining_nodes': remaining_nodes,  # Nodes remaining after cascading failure
        'number_of_remaining_nodes': len(remaining_nodes),  # Total number of remaining nodes
        'efficiency_before': efficiency_before,  # Global efficiency before failure
        'efficiency_after': efficiency_after,  # Global efficiency after failure
        'network_resilience_efficiency': efficiency_after / efficiency_before if efficiency_before > 0 else 0,
        # Network resilience ratio based on efficiency
    }

    output_json_path = 'post_disaster_assessment_based_on_global_network_efficiency.json'
    with open(output_json_path, 'w') as outfile:
        json.dump(result, outfile, indent=4)

    print(f"Network resilience assessment results saved to {output_json_path}")

    # Update the Global_Data.json file with the path
    file_paths['post_disaster_assessment_based_on_global_network_efficiency'] = output_json_path
    with open(global_json_path, 'w') as file:
        json.dump(file_paths, file, indent=4)

    print(f"Global_Data.json updated with network resilience result path.")


# Usage example
global_json_path = 'Global_Data.json'
post_disaster_assessment_based_on_global_network_efficiency(global_json_path)
