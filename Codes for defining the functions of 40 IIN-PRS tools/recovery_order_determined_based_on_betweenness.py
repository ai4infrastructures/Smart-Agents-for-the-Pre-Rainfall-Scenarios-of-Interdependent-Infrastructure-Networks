import json
import networkx as nx


def recovery_order_determined_based_on_betweenness(global_json_path):
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

    # Load failure nodes from the cascading failure identification file
    with open(failure_file, 'r') as file:
        failure_data = json.load(file)
        failed_nodes = failure_data.get("all_failed_nodes", [])

    if not failed_nodes:
        print("Error: No failed nodes found in the failure identification file.")
        return

    # Construct directed graph
    G_full = nx.DiGraph()
    for node in nodes:
        G_full.add_node(node['Code'], **node)
    for edge in edges:
        G_full.add_edge(edge['Start'], edge['End'], **edge)

    # 初始化“激活图” G_active：先把所有故障节点删掉
    G_active = G_full.copy()
    G_active.remove_nodes_from(failed_nodes)


    # Calculate the Betweenness Centrality for each node
    # 动态恢复：每一步选当前剩余失效节点中介数最高的那个
    recovery_order = []
    remaining = set(failed_nodes)

    step = 0


    while remaining:
        step += 1
        best_node, best_score = None, -1.0

        for n in remaining:
            # 临时把候选节点 n 加回子网
            G_active.add_node(n, **G_full.nodes[n])
            for u, _, d in G_full.in_edges(n, data=True):
                if u in G_active:
                    G_active.add_edge(u, n, **d)
            for _, v, d in G_full.out_edges(n, data=True):
                if v in G_active:
                    G_active.add_edge(n, v, **d)

            # —— 在完整的 G_active（包含所有已恢复节点 + n）上算全局 BC ——
            bc_dict = nx.betweenness_centrality(G_active, normalized=True)
            score = bc_dict.get(n, 0.0)

            # 删除 n，恢复到试探前状态
            G_active.remove_node(n)

            if score > best_score:
                best_score, best_node = score, n

        # 真正恢复 best_node
        recovery_order.append(best_node)
        remaining.remove(best_node)
        G_active.add_node(best_node, **G_full.nodes[best_node])
        for u, _, d in G_full.in_edges(best_node, data=True):
            if u in G_active: G_active.add_edge(u, best_node, **d)
        for _, v, d in G_full.out_edges(best_node, data=True):
            if v in G_active: G_active.add_edge(best_node, v, **d)

        print(f"Step {step}: 恢复节点 {best_node} (dynamic BC={best_score:.4f})")

    # Save recovery order to a JSON file
    result = {
        'recovery_order': recovery_order,  # Failed nodes in the order of their recovery based on betweenness centrality
        'number_of_nodes': len(recovery_order),
    }

    output_json_path = 'recovery_order_determined_based_on_betweenness.json'
    with open(output_json_path, 'w') as outfile:
        json.dump(result, outfile, indent=4)

    # Update the global data file with the new recovery strategy result path
    with open(global_json_path, 'r') as file:
        global_data = json.load(file)

    global_data['recovery_order_determined_based_on_betweenness'] = output_json_path

    with open(global_json_path, 'w') as file:
        json.dump(global_data, file, indent=4)

    print(f"Global_Data.json updated with result path.")
    return result

# Usage example
global_json_path = 'Global_Data.json'
recovery_order_determined_based_on_betweenness(global_json_path)
