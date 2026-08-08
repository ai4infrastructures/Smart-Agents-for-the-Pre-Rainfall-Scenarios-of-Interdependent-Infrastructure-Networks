import json
import networkx as nx

def cascade_failure_simulator_based_on_Motter_Lai_model(global_json_path, alpha=0.3):
    """
    Motter-Lai 级联失效
    --------------------------------
    参数
    ----
    global_json_path : str
        存有各文件路径的 global_data.json
    alpha : float
        冗余系数 C_i = (1+alpha)*L_i，典型 0.2–0.4
    """

    # ---------- 1. 读取文件路径 ----------
    with open(global_json_path, 'r') as f:
        paths = json.load(f)

    topo_path   = paths['interdependent_critical_infrastructures_networks']
    failed_path = paths['failure_node_after_HECRAS_simulations']

    # ---------- 2. 读取拓扑 & 初始失效 ----------
    with open(topo_path, 'r') as f:
        topo = json.load(f)
    with open(failed_path, 'r') as f:
        failed_json = json.load(f)
    initial_failed = set(failed_json['all_failed_nodes'])

    # ---------- 3. 构建无向图 ----------
    G = nx.Graph()
    for n in topo['nodes']:
        G.add_node(n['Code'], **n)
    for e in topo['edges']:
        G.add_edge(e['Start'], e['End'], **e)

    # ---------- 4. 初始负载 / 容量 ----------
    base_load = nx.betweenness_centrality(G, normalized=False)
    capacity  = {n: (1 + alpha) * base_load[n] for n in G}

    # ---------- 5. 级联循环 ----------
    H             = G.copy()                     # 存活子图
    load_now = base_load.copy()
    current_fail = set(initial_failed)
    total_failed = set(initial_failed)
    fail_history = []                         # 结果列表

    while current_fail:
        # 记录本轮失效节点
        for v in current_fail:
            fail_history.append({
                "failed_node": v,
                "initial_load": base_load.get(v, 0),
                "current_load": load_now.get(v, 0),
                "capacity": capacity[v]
            })

        H.remove_nodes_from(current_fail)
        if H.number_of_nodes() == 0:
            break

        load_now    = nx.betweenness_centrality(H, normalized=False)
        next_fail   = {n for n in H if load_now.get(n, 0) > capacity[n]}
        next_fail  -= total_failed              # 去掉已失效

        current_fail = next_fail
        total_failed |= next_fail
    # ---------- 6. 统计失效节点 ----------
    failed_node_list = sorted(total_failed)
    failed_node_count = len(failed_node_list)

    # ---------- 6. 写结果 ----------
    out_path = 'cascade_failure_simulator_based_on_Motter_Lai_model.json'
    result = {
        "failed_node_count": failed_node_count,
        "all_failed_nodes": failed_node_list,
        "fail_history": fail_history
    }

    with open(out_path, 'w') as f:
        json.dump(result, f, indent=4)

    # 把结果路径写回 global_data.json
    paths['cascade_failure_simulator_based_on_Motter_Lai_model'] = out_path
    with open(global_json_path, 'w') as f:
        json.dump(paths, f, indent=4)

    print("result saved to Global_Data.json")
    return {
        "message": f"Cascade finished: {len(total_failed)}/{G.number_of_nodes()} nodes failed; result saved to '{out_path}'.",
        "failed_node_count": failed_node_count,
        "all_failed_nodes": failed_node_list
    }

main_json_path = 'Global_Data.json'
cascade_failure_simulator_based_on_Motter_Lai_model(main_json_path)
