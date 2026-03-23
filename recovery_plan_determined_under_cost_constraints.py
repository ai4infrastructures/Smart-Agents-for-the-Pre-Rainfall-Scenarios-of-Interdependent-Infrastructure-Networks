import json
import networkx as nx
from collections import defaultdict
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value

def recovery_plan_determined_under_cost_constraints(global_json_path):
    global_json_path = global_json_path.strip()
    with open(global_json_path, 'r') as f:
        global_data = json.load(f)

    try:
        with open(global_data["resource_constrained_interdependent_critical_infrastructures_networks"], 'r') as f:
            network_data = json.load(f)

        with open(global_data["population_data"], 'r') as f:
            population_data = json.load(f)

        # 读取级联失效节点数据
        with open(global_data["failure_node_after_HECRAS_simulations"], 'r') as f:
            failure_data = json.load(f)
            failed_nodes = failure_data["all_failed_nodes"]

    except Exception as e:
        return {"status": "error", "message": f"Data loading failed: {str(e)}"}

    population_lookup = {str(item["Id"]): item["Population"] for item in population_data}

    G = nx.DiGraph()
    node_service_areas = defaultdict(list)
    area_nodes = defaultdict(list)

    for node in network_data["nodes"]:
        if not isinstance(node, dict) or "Code" not in node:
            continue
        G.add_node(node["Code"], **node)
        areas = [a.strip() for a in str(node.get("Service Area", "")).split(',') if a.strip()]
        node_service_areas[node["Code"]] = areas
        for area in areas:
            area_nodes[area].append(node["Code"])

    for edge in network_data["edges"]:
        if edge["Start"] in G.nodes and edge["End"] in G.nodes:
            G.add_edge(edge["Start"], edge["End"], **edge)

    # Step 2: Analyze initial area failures
    initial_failed_areas = set()
    initial_affected_population = 0
    for area, nodes in area_nodes.items():
        total = len(nodes)
        failed = len([n for n in nodes if n in failed_nodes])
        if failed / total > 0.5:
            initial_failed_areas.add(area)
            initial_affected_population += population_lookup.get(area, 0)

    # Step 3: Prepare optimization data
    raw_metrics = []
    for node_code in failed_nodes:
        degree = G.degree(node_code)
        service_count = len(node_service_areas.get(node_code, [])) or 1
        raw_metrics.append((node_code, degree, service_count))

    degrees = [d for _, d, _ in raw_metrics]
    service_counts = [s for _, _, s in raw_metrics]
    min_d, max_d = min(degrees), max(degrees)
    min_s, max_s = min(service_counts), max(service_counts)
    d_range = max_d - min_d or 1
    s_range = max_s - min_s or 1

    nodes_data = []
    for node_code, d, s in raw_metrics:
        norm_d = (d - min_d) / d_range
        norm_s = (s - min_s) / s_range
        node_info = next((n for n in network_data["nodes"] if n.get("Code") == node_code), None)
        if not node_info:
            continue
        r1 = node_info.get("resource_demand_type_1", 1)
        r2 = node_info.get("resource_demand_type_2", 1)
        r3 = node_info.get("resource_demand_type_3", 1)
        cost = r1 * 2 + r2 * 3 + r3 * 5
        value_score = (norm_d * norm_s) / (cost or 1)
        nodes_data.append({
            'code': node_code,
            'value': value_score,
            'cost': cost,
            'info': node_info,
            'service_areas': node_service_areas.get(node_code, [])
        })

    if not nodes_data:
        return {"status": "error", "message": "No valid nodes for optimization"}

    prob = LpProblem("Network_Recovery", LpMaximize)
    node_vars = {i: LpVariable(f"node_{i}", cat="Binary") for i in range(len(nodes_data))}

    prob += lpSum(nodes_data[i]['value'] * node_vars[i] for i in range(len(nodes_data)))
    TOTAL_COST_LIMIT = 300
    prob += lpSum(nodes_data[i]['cost'] * node_vars[i] for i in range(len(nodes_data))) <= TOTAL_COST_LIMIT

    try:
        prob.solve()
    except Exception as e:
        return {"status": "error", "message": f"LP solver failed: {str(e)}"}

    new_nodes = []
    restored_nodes = [nodes_data[i]['code'] for i in range(len(nodes_data)) if value(node_vars[i]) == 1]
    restored_areas = set()
    restored_population = 0
    still_failed_areas = set()
    still_affected_population = 0

    for area in initial_failed_areas:
        total = len(area_nodes[area])
        failed_remaining = len([n for n in area_nodes[area] if n in failed_nodes and n not in restored_nodes])
        if failed_remaining / total <= 0.5:
            restored_areas.add(area)
            restored_population += population_lookup.get(area, 0)
        else:
            still_failed_areas.add(area)
            still_affected_population += population_lookup.get(area, 0)

    for i in range(len(nodes_data)):
        if value(node_vars[i]) == 1:
            original = nodes_data[i]['info']
            backup = original.copy()
            backup["Code"] = f"Backup_{original['Code']}"
            backup["Facility"] = f"Backup_{original.get('Facility', 'Facility')}"
            backup.update({
                "resource_demand_type_1": original.get("resource_demand_type_1", 1),
                "resource_demand_type_2": original.get("resource_demand_type_2", 1),
                "resource_demand_type_3": original.get("resource_demand_type_3", 1),
                "Cost": nodes_data[i]['cost']
            })
            new_nodes.append(backup)

    output_data = {
        "initial_state": {
            "failed_nodes": failed_nodes,
            "failed_areas": list(initial_failed_areas),
            "affected_population": initial_affected_population
        },
        "recovery_results": {
            "restored_nodes": restored_nodes,
            "new_backup_nodes": new_nodes,
            "restored_areas": list(restored_areas),
            "restored_population": restored_population,
            "remaining_failed_areas": list(still_failed_areas),
            "remaining_affected_population": still_affected_population,
            "total_restored_value": sum(nodes_data[i]['value'] for i in range(len(nodes_data)) if value(node_vars[i]) == 1),
            "total_cost": sum(nodes_data[i]['cost'] for i in range(len(nodes_data)) if value(node_vars[i]) == 1),
            "lp_status": prob.status,
            "cost_limit": TOTAL_COST_LIMIT
        },
        "parameters": {
            "area_failure_threshold": ">50% serving nodes failed"
        }
    }

    output_path = 'recovery_plan_determined_under_cost_constraints.json'
    try:
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=4)
        global_data["recovery_plan_determined_under_cost_constraints"] = output_path
        with open(global_json_path, 'w') as f:
            json.dump(global_data, f, indent=4)
    except Exception as e:
        return {"status": "error", "message": f"Failed to save results: {str(e)}"}

    return {
        "status": "success",
        "summary": {
            "initial_failed_areas": len(initial_failed_areas),
            "initial_affected_population": initial_affected_population,
            "restored_areas": len(restored_areas),
            "restored_population": restored_population,
            "remaining_failed_areas": len(still_failed_areas),
            "remaining_affected_population": still_affected_population,
            "total_cost": output_data["recovery_results"]["total_cost"]
        },
        "output_file": output_path
    }


global_json_path = 'Global_Data.json'
recovery_plan_determined_under_cost_constraints(global_json_path)

