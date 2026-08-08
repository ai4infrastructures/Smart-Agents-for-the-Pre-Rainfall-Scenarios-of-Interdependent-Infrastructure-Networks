import json
import networkx as nx
import random

def cascade_failure_simulator_based_on_Monte_Carlo_model(global_json_path: str,num_simulations=10,propagation_probs=None):
    # 从全局文件中加载网络文件路径和初始失效节点
    with open(global_json_path, 'r') as f:
        file_paths = json.load(f)
    network_file = file_paths.get('interdependent_critical_infrastructures_networks')
    flooded_file = file_paths.get('failure_node_after_HECRAS_simulations')
    if not network_file:
        print("No network file found in Global_Data.json.")
        return

    # 获取初始失效节点
    if not flooded_file:
        print("No flooded-nodes file found in Global_Data.json.")
        return

    with open(flooded_file, 'r') as f:
        flooded_data = json.load(f)

    initial_failed_list = flooded_data.get('all_failed_nodes', [])
    if not initial_failed_list:
        print("No initial failed nodes found in Global_Data.json under 'failure_node_after_HECRAS_simulations'.")
        return
    initial_failed_set = set(initial_failed_list)

    # 加载网络数据
    with open(network_file, 'r') as f:
        network_data = json.load(f)
    nodes = network_data.get('nodes', [])
    edges = network_data.get('edges', [])
    if not nodes or not edges:
        print("Network data is incomplete.")
        return

    total_nodes = len(nodes)

    # 构建有向图
    G_original = nx.DiGraph()
    for node in nodes:
        G_original.add_node(node['Code'], **node)
    for edge in edges:
        G_original.add_edge(edge['Start'], edge['End'], **edge)

    if propagation_probs is None:
        propagation_probs = {
            "power": 0.4,
            "water": 0.2,
            "gas":   0.1
        }

    simulation_results = []
    # 进行多次仿真
    for sim_id in range(1, num_simulations + 1):
        failed_set = set(initial_failed_set)
        failed_order = list(initial_failed_list)
        new_failures = list(initial_failed_list)
        while new_failures:
            current_failures = []
            for u in new_failures:
                for v in G_original.successors(u):
                    # 已失效的跳过
                    if v in failed_set or v in current_failures:
                        continue

                    # 取下游节点 v 的基础设施类型
                    infra = G_original.nodes[v].get("Infrastructure Type")
                    # 找对应的传播概率，默认为 0.3
                    p = propagation_probs.get(infra, 0.3)

                    # 伯努利试验：若小于 p，就认为 v 级联失效
                    if random.random() < p:
                        current_failures.append(v)

            new_failures = current_failures
            for fn in new_failures:
                failed_order.append(fn)
                failed_set.add(fn)

        result = {
            "simulation": sim_id,
            "final_failed_nodes": failed_order,
            "number_of_failed_nodes": len(failed_order),
            "failure_rate": len(failed_order) / total_nodes
        }
        simulation_results.append(result)

    # 输出每次仿真结果
    for result in simulation_results:
        print(
            f"Simulation {result['simulation']}: {result['number_of_failed_nodes']} failed nodes out of {total_nodes} "
            f"({result['failure_rate']:.2%})")

    # 保存仿真结果到文件
    output_json_path = "cascade_failure_simulator_based_on_Monte_Carlo_model.json"
    with open(output_json_path, 'w') as f:
        json.dump(simulation_results, f, indent=4)
    print(f"results saved to {output_json_path}")

    # 更新 Global_Data.json，添加仿真结果文件路径
    file_paths['cascade_failure_simulator_based_on_Monte_Carlo_model'] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(file_paths, f, indent=4)

    return simulation_results

global_json_path = 'Global_Data.json'
cascade_failure_simulator_based_on_Monte_Carlo_model(global_json_path, num_simulations=10)
