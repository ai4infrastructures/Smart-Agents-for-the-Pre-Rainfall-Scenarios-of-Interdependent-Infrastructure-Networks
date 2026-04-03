import json
import random


def network_generator_for_resource_constrained_interdependent_critical_infrastructures(input_file):
    input_file = input_file.strip().replace('"', '')

    def find_nearest_service(nodes, target_location):
        """ Finds the nearest service node that covers the specified location, if available. """
        for node in nodes:
            if node.get('Service Area'):
                if target_location in node['Service Area'].split(','):
                    return node['Code']
        return None

    def add_service_edges_and_demands(nodes, edges, total_resources, node_count):
        """ Adds edges based on the demands and calculates random resource demands, ensuring that demands do not exceed the total resource. """
        remaining_resource_1 = total_resources['resource_type_1']
        remaining_resource_2 = total_resources['resource_type_2']
        remaining_resource_3 = total_resources['resource_type_3']

        # Track total demands for each resource type (separate for nodes and edges)
        node_demand_type_1, node_demand_type_2, node_demand_type_3 = 0, 0, 0
        edge_demand_type_1, edge_demand_type_2, edge_demand_type_3 = 0, 0, 0

        for i, node in enumerate(nodes):
            target_location = node['Location']
            service_node_code = find_nearest_service(nodes, target_location)
            if service_node_code:
                edges.append({
                    "Code": f"{service_node_code}_{node['Code']}",
                    "Start": service_node_code,
                    "End": node['Code'],
                    "Infrastructure Type": "service_link"
                })

                # Dynamically adjust the maximum resource that can be allocated to the node
                if remaining_resource_1 > 0 and remaining_resource_2 > 0 and remaining_resource_3 > 0:
                    max_demand_per_node_1 = remaining_resource_1 // (node_count - i)
                    max_demand_per_node_2 = remaining_resource_2 // (node_count - i)
                    max_demand_per_node_3 = remaining_resource_3 // (node_count - i)

                    resource_demand_1 = random.randint(1, max_demand_per_node_1)
                    resource_demand_2 = random.randint(1, max_demand_per_node_2)
                    resource_demand_3 = random.randint(1, max_demand_per_node_3)

                    node['resource_demand_type_1'] = resource_demand_1
                    node['resource_demand_type_2'] = resource_demand_2
                    node['resource_demand_type_3'] = resource_demand_3

                    node_demand_type_1 += resource_demand_1
                    node_demand_type_2 += resource_demand_2
                    node_demand_type_3 += resource_demand_3

                    remaining_resource_1 -= resource_demand_1
                    remaining_resource_2 -= resource_demand_2
                    remaining_resource_3 -= resource_demand_3

                else:
                    # Set resource demands to 0 if no resources remain
                    node['resource_demand_type_1'] = 0
                    node['resource_demand_type_2'] = 0
                    node['resource_demand_type_3'] = 0

        # Add random resource allocation to each edge (scaled down)
        for edge in edges:
            edge_resource_type_1 = random.randint(1, total_resources['resource_type_1'] // 200)
            edge_resource_type_2 = random.randint(1, total_resources['resource_type_2'] // 200)
            edge_resource_type_3 = random.randint(1, total_resources['resource_type_3'] // 200)

            edge['resource_allocation_type_1'] = edge_resource_type_1
            edge['resource_allocation_type_2'] = edge_resource_type_2
            edge['resource_allocation_type_3'] = edge_resource_type_3

            # Add edge resource demands to total demands
            edge_demand_type_1 += edge_resource_type_1
            edge_demand_type_2 += edge_resource_type_2
            edge_demand_type_3 += edge_resource_type_3

        # Return both node and edge total demands
        return {
            'node': {
                'resource_type_1': node_demand_type_1,
                'resource_type_2': node_demand_type_2,
                'resource_type_3': node_demand_type_3
            },
            'edge': {
                'resource_type_1': edge_demand_type_1,
                'resource_type_2': edge_demand_type_2,
                'resource_type_3': edge_demand_type_3
            }
        }

    """ Processes the network to add new service links based on demands and saves the modified JSON data. """
    with open(input_file, 'r') as file:
        data = json.load(file)
    infrastructure_networks = data['infrastructures_networks']
    with open(infrastructure_networks, 'r') as file:
        json_data = json.load(file)

    nodes = json_data['nodes']
    edges = json_data['edges']

    # Generate random total resources for the three new resource types
    total_resources = {
        'resource_type_1': random.randint(1500, 2000),
        'resource_type_2': random.randint(1500, 2000),
        'resource_type_3': random.randint(1500, 2000)
    }

    node_count = len(nodes)  # Total number of nodes

    # Add service edges and collect total demands for each type
    total_demands = add_service_edges_and_demands(nodes, edges, total_resources, node_count)

    # Save the modified network to a new file
    json_data['edges'] = edges
    json_data['total_resources'] = total_resources
    json_data['total_demands'] = total_demands  # Separate node and edge demands

    with open('resource_constrained_interdependent_critical_infrastructures_networks.json', 'w') as outfile:
        json.dump(json_data, outfile, indent=4)

    # Update the Global_Data.json to store the path to the new file
    data['resource_constrained_interdependent_critical_infrastructures_networks'] = 'resource_constrained_interdependent_critical_infrastructures_networks.json'
    with open(input_file, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    return json.dumps({"status": "success", "output_path": input_file})
    print("The modified network has been saved to resource_constrained_interdependent_critical_infrastructures_networks.json.")

# Example usage:
modified_network = network_generator_for_resource_constrained_interdependent_critical_infrastructures('Global_Data.json')

