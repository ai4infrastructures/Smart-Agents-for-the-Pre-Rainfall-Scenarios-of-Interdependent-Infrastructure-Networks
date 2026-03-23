import json
import networkx as nx


def recovery_order_determined_based_on_node_degree(global_json_path):
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

    # Load failure data (failed nodes) from the specified file
    with open(failure_file, 'r') as file:
        failure_data = json.load(file)
        failed_nodes = failure_data.get('all_failed_nodes', [])

    if not failed_nodes:
        print("Error: No failed nodes found in the failure data.")
        return

    # Construct directed graph
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node['Code'], **node)
    for edge in edges:
        G.add_edge(edge['Start'], edge['End'], **edge)

    # Filter nodes that are in the failed nodes list
    failed_node_degrees = {node: G.degree(node) for node in failed_nodes if node in G.nodes}

    # Sort failed nodes by degree (maximum degree first)
    sorted_failed_nodes = sorted(failed_node_degrees, key=failed_node_degrees.get, reverse=True)

    # Recovery process: nodes are restored in order of their degree (max degree first)
    recovery_order = sorted_failed_nodes  # The list of failed nodes to be restored in order

    # Save recovery order to a JSON file
    result = {
        'recovery_order': recovery_order,  # Failed nodes in the order of their recovery based on degree
        'number_of_nodes': len(recovery_order),
    }

    output_json_path = 'recovery_order_determined_based_on_node_degree.json'
    with open(output_json_path, 'w') as outfile:
        json.dump(result, outfile, indent=4)

    print(f"Recovery strategy saved to {output_json_path}")

    # Update the Global_Data.json file with the recovery strategy path
    file_paths['recovery_order_determined_based_on_node_degree'] = output_json_path
    with open(global_json_path, 'w') as file:
        json.dump(file_paths, file, indent=4)

    print(f"Global_Data.json updated with result path.")
    return result

# Usage example
global_json_path = 'Global_Data.json'
recovery_order_determined_based_on_node_degree(global_json_path)
