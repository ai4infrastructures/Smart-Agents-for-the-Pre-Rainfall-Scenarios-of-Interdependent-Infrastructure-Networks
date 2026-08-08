import json
import networkx as nx
import math

def cascade_failure_simulator_based_on_Load_Capacity_model_with_nearest_neighbour_load_redistribution(main_json_path):
    main_json_path = main_json_path.strip().replace('"', '')
    output_json_path = 'cascade_failure_simulator_based_on_Load_Capacity_model_with_nearest_neighbour_load_redistribution.json'

    # 读取 global_data.json 文件
    with open(main_json_path, 'r') as f:
        file_paths = json.load(f)

    # 读取网络拓扑文件
    with open(file_paths['interdependent_critical_infrastructures_networks'], 'r') as f:
        network_topology = json.load(f)

    # 读取负载分布文件
    with open(file_paths['load_distribution'], 'r') as f:
        load_distribution = json.load(f)

    with open(file_paths['failure_node_after_HECRAS_simulations'], 'r') as f:
        flooded_data = json.load(f)

    # 构建有向图
    G = nx.DiGraph()

    # 添加节点到网络，并记录节点的坐标
    node_positions = {}  # 保存节点的坐标信息
    for node in network_topology['nodes']:
        G.add_node(node['Code'], **node)
        node_positions[node['Code']] = node['Coordinates']  # 假设节点包含 Coordinates 字段

    # 添加边到网络
    for edge in network_topology['edges']:
        G.add_edge(edge['Start'], edge['End'], **edge)

    # 构建节点负载和容量的字典
    node_data = {entry['Code']: {'load': entry['Initial Load'], 'capacity': entry['Capacity']} for entry in
                 load_distribution['nodes']}

    # 获取初始失效节点（从 hecras_simulated_flooded_nodes 的 all_failed_nodes 字段获取）
    failed_nodes = flooded_data['all_failed_nodes']

    cascading_failures = []  # 记录级联失效的历史
    processed_failed_nodes = set(failed_nodes)

    # 处理级联失效
    while failed_nodes:
        new_failed_nodes = []
        for node in failed_nodes:
            if not G.has_node(node):
                continue

            # 记录失效节点信息，显示实际的负载值
            cascading_failures.append({
                'failed_node': node,
                'load': node_data[node]['load'],
                'capacity': node_data[node]['capacity']
            })

            # 获取邻居节点（从失效节点出发的边的终点）
            neighbors = [edge[1] for edge in G.out_edges(node)]
            if neighbors:
                # 找到地理位置最近的邻居（使用平方距离避免开方计算）
                nearest_neighbor = min(
                    neighbors,
                    key=lambda neighbor: (node_positions[node][0] - node_positions[neighbor][0]) ** 2 +
                                           (node_positions[node][1] - node_positions[neighbor][1]) ** 2
                )

                # 将失效节点的负载全部分配给最近的邻居
                node_data[nearest_neighbor]['load'] += node_data[node]['load']

                # 检查是否超出容量，但不限制负载，记录实际值，并避免重复处理已失效节点
                if node_data[nearest_neighbor]['load'] > node_data[nearest_neighbor]['capacity'] and nearest_neighbor not in processed_failed_nodes:
                    new_failed_nodes.append(nearest_neighbor)

        processed_failed_nodes.update(failed_nodes)
        failed_nodes = new_failed_nodes

    # 保存更新后的级联失效记录到新文件
    with open(output_json_path, 'w') as f:
        json.dump(cascading_failures, f, indent=4)

    # 更新 global_data.json 文件，写入新的路径
    file_paths['cascade_failure_simulator_based_on_Load_Capacity_model_with_nearest_neighbour_load_redistribution'] = output_json_path
    with open(main_json_path, 'w') as f:
        json.dump(file_paths, f, indent=4)

    return "The cascading failure behavior has been simulated and saved to the specified JSON files."

# 使用示例
main_json_path = 'Global_Data.json'
cascade_failure_simulator_based_on_Load_Capacity_model_with_nearest_neighbour_load_redistribution(main_json_path)
