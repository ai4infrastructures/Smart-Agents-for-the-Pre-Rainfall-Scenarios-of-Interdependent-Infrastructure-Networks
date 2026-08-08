import json
import networkx as nx


def cascade_failure_simulator_based_on_Load_Capacity_model_with_uniform_load_redistribution(global_json_path):
    # 清理全局 JSON 文件路径的格式
    global_json_path = global_json_path.strip().replace('"', '')
    output_json_path = 'cascade_failure_simulator_based_on_Load_Capacity_model_with_uniform_load_redistribution.json'

    # 读取 global_data.json 文件
    with open(global_json_path, 'r') as f:
        file_paths = json.load(f)

    # 读取网络拓扑文件
    with open(file_paths['interdependent_critical_infrastructures_networks'], 'r') as f:
        network_topology = json.load(f)

    # 读取负载分布文件
    with open(file_paths['load_distribution'], 'r') as f:
        load_distribution = json.load(f)


    with open(file_paths['failure_node_after_HECRAS_simulations'], 'r') as f:
        flooded_data = json.load(f)
    initial_failed_nodes = set(flooded_data['all_failed_nodes'])

    # 构建有向图
    graph = nx.DiGraph()

    # 添加节点到网络：使用节点代码作为标识，并附加所有节点属性
    for node in network_topology['nodes']:
        graph.add_node(node['Code'], **node)

    # 添加边到网络：从起始节点到终止节点添加边，并附加所有边属性
    for edge in network_topology['edges']:
        graph.add_edge(edge['Start'], edge['End'], **edge)

    # 构建节点负载和容量的字典
    node_data = {entry['Code']: {'load': entry['Initial Load'], 'capacity': entry['Capacity']}
                 for entry in load_distribution['nodes']}

    cascading_failures = []  # 记录级联失效的历史，每个元素包含失效节点的实际负载和容量
    processed_failed_nodes = set(initial_failed_nodes)  # 记录已处理的失效节点，防止重复处理

    # 当前待处理的失效节点，使用集合便于去重
    failed_nodes = initial_failed_nodes

    # 处理级联失效
    while failed_nodes:
        new_failed_nodes = set()  # 存储新出现的失效节点，确保无重复
        for failed_node in failed_nodes:
            # 如果节点不存在于网络中，则跳过
            if not graph.has_node(failed_node):
                continue

            # 记录当前失效节点信息
            cascading_failures.append({
                'failed_node': failed_node,
                'load': node_data[failed_node]['load'],
                'capacity': node_data[failed_node]['capacity']
            })

            # 取出失效节点的负载，并重置其负载为 0，防止重复计算
            load_to_redistribute = node_data[failed_node]['load']
            node_data[failed_node]['load'] = 0

            # 获取该失效节点的所有后继邻居（出边的终点）
            neighbors = [target for _, target in graph.out_edges(failed_node)]
            if neighbors:
                load_per_neighbor = load_to_redistribute / len(neighbors)
                for neighbor in neighbors:
                    # 仅对尚未失效的邻居进行负载传递
                    if neighbor in processed_failed_nodes:
                        continue

                    # 分配负载给邻居（不考虑容量限制）
                    node_data[neighbor]['load'] += load_per_neighbor

                    # 检查邻居是否超出容量，并且该邻居未被记录为失效节点
                    if (node_data[neighbor]['load'] > node_data[neighbor]['capacity'] and
                            neighbor not in processed_failed_nodes and
                            neighbor not in new_failed_nodes):
                        new_failed_nodes.add(neighbor)

        # 更新已处理的失效节点集合
        processed_failed_nodes.update(new_failed_nodes)
        failed_nodes = new_failed_nodes

    # 保存更新后的级联失效记录到新文件
    with open(output_json_path, 'w') as f:
        json.dump(cascading_failures, f, indent=4)

    # 更新 global_data.json 文件，写入新的路径
    file_paths['cascade_failure_simulator_based_on_Load_Capacity_model_with_uniform_load_redistribution'] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(file_paths, f, indent=4)

    return "The cascading failure behavior has been simulated and saved to the specified JSON files."


# 使用示例
global_json_path = 'Global_Data.json'
cascade_failure_simulator_based_on_Load_Capacity_model_with_uniform_load_redistribution(global_json_path)
