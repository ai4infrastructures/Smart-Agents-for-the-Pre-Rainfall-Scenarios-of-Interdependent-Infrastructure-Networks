import json
import networkx as nx

def recovery_order_determined_based_on_propagation_ranges(global_json_path):
    # Load global data file to get the network file path
    with open(global_json_path, 'r') as file:
        file_paths = json.load(file)
        network_file = file_paths.get('interdependent_critical_infrastructures_networks')  # Get network file path
        failure_file = file_paths.get('failure_node_after_HECRAS_simulations')
    if not network_file:
        print("No network file found in Global_Data.json.")
        return

    # Load network data from the specified file
    with open(network_file, 'r') as file:
        network_data = json.load(file)

    nodes = network_data.get('nodes', [])
    edges = network_data.get('edges', [])

    if not nodes or not edges:
        print("Error: Network data is incomplete.")
        return

    # Construct directed graph
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node['Code'], **node)
    for edge in edges:
        G.add_edge(edge['Start'], edge['End'], **edge)

    # Load failure data to get the list of failed nodes
    with open(failure_file, 'r') as file:
        failure_data = json.load(file)
        failed_nodes = failure_data.get('all_failed_nodes', [])

    if not failed_nodes:
        print("Error: No failed nodes found in the failure data.")
        return

    # Calculate propagation range for each node (the number of reachable nodes)
    propagation_ranges = {}
    for node in failed_nodes:  # Only calculate for failed nodes
        if node in G:
            # Using breadth-first search (BFS) to calculate reachable nodes
            reachable_nodes = list(nx.single_source_shortest_path_length(G, node))
            propagation_ranges[node] = len(reachable_nodes) - 1  # Number of nodes this node can reach

    # Sort failed nodes by propagation range (max propagation range first)
    sorted_failed_nodes_by_propagation_range = sorted(propagation_ranges, key=propagation_ranges.get, reverse=True)

    # Recovery process: failed nodes are restored in order of their propagation range (max propagation range first)
    recovery_order = sorted_failed_nodes_by_propagation_range  # The list of nodes to be restored in order

    # Save recovery order to a JSON file
    result = {
        'recovery_order': recovery_order,  # Nodes in the order of their recovery based on propagation range
        'number_of_nodes': len(recovery_order),
    }

    output_json_path = 'recovery_order_determined_based_on_propagation_ranges.json'
    with open(output_json_path, 'w') as outfile:
        json.dump(result, outfile, indent=4)

    # Update the Global_Data.json with the new recovery strategy file path
    with open(global_json_path, 'r') as file:
        global_data = json.load(file)

    global_data['recovery_order_determined_based_on_propagation_ranges'] = output_json_path

    with open(global_json_path, 'w') as file:
        json.dump(global_data, file, indent=4)

    print(f"Global_Data.json updated with recovery strategy result path.")

# Usage example
global_json_path = 'Global_Data.json'
recovery_order_determined_based_on_propagation_ranges(global_json_path)
