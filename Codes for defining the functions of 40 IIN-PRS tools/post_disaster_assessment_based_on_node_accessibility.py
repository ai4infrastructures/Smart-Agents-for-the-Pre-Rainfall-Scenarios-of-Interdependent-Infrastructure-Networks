import json
import networkx as nx

def post_disaster_assessment_based_on_node_accessibility(global_json_path: str):
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

    # Calculate initial node accessibility (proportion of accessible pairs in the largest component)
    largest_wcc_before = max(nx.weakly_connected_components(G), key=len)
    subgraph_before = G.subgraph(largest_wcc_before)
    accessibility_before = sum(len(nx.descendants(subgraph_before, node)) for node in subgraph_before) / (total_nodes * (total_nodes - 1))

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

    # Calculate accessibility after failure in the largest remaining component
    if G_after_failure.number_of_nodes() > 0:
        largest_wcc_after = max(nx.weakly_connected_components(G_after_failure), key=len)
        subgraph_after = G_after_failure.subgraph(largest_wcc_after)
        accessibility_after = sum(len(nx.descendants(subgraph_after, node)) for node in subgraph_after) / (total_nodes * (total_nodes - 1))
    else:
        accessibility_after = 0

    # Calculate network resilience based on accessibility
    network_resilience = accessibility_after / accessibility_before if accessibility_before > 0 else 0

    # Prepare the result to save
    result = {
        'initial_attack_nodes': initial_nodes,  # List of initial attack nodes
        'all_failed_nodes': list(all_failed_nodes),  # Nodes failed due to cascading failure
        'number_of_failed_nodes': len(all_failed_nodes),  # Total number of failed nodes
        'remaining_nodes': remaining_nodes,  # Nodes remaining after cascading failure
        'number_of_remaining_nodes': len(remaining_nodes),  # Total number of remaining nodes
        'accessibility_before': accessibility_before,      # Node accessibility before failure
        'accessibility_after': accessibility_after,        # Node accessibility after failure
        'network_resilience': network_resilience,        # Network resilience ratio
    }

    output_json_path = 'post_disaster_assessment_based_on_node_accessibility.json'
    with open(output_json_path, 'w') as outfile:
        json.dump(result, outfile, indent=4)

    print(f"Network resilience assessment results saved to {output_json_path}")

    # Update the Global_Data.json file with the path
    file_paths['post_disaster_assessment_based_on_node_accessibility'] = output_json_path
    with open(global_json_path, 'w') as file:
        json.dump(file_paths, file, indent=4)

    print(f"Global_Data.json updated with network resilience result path.")

# Usage example
global_json_path = 'Global_Data.json'
post_disaster_assessment_based_on_node_accessibility(global_json_path)
