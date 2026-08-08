import json
import networkx as nx
from collections import defaultdict
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value


def recovery_plan_determined_under_resource_constraints(global_json_path):
    # Load all data files
    global_json_path = global_json_path.strip()
    with open(global_json_path, 'r') as f:
        global_data = json.load(f)

    try:
        # Load interdependent network data
        with open(global_data["resource_constrained_interdependent_critical_infrastructures_networks"], 'r') as f:
            network_data = json.load(f)

        # Load population data
        with open(global_data["population_data"], 'r') as f:
            population_data = json.load(f)

        # Load failure nodes data
        with open(global_data["failure_node_after_HECRAS_simulations"], 'r') as f:
            failure_data = json.load(f)
        failed_nodes = failure_data["all_failed_nodes"]

    except Exception as e:
        return {"status": "error", "message": f"Data loading failed: {str(e)}"}

    # Build population lookup dictionary
    population_lookup = {str(item["Id"]): item["Population"] for item in population_data}

    # Build graph and service area mapping
    G = nx.DiGraph()
    node_service_areas = defaultdict(list)  # {node_code: [area1, area2]}
    area_nodes = defaultdict(list)  # {area: [node1, node2]}

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

    # Configuration
    RESOURCE_LIMITS = {'type_1': 50, 'type_2': 40, 'type_3': 30}

    # Step 2: Analyze initial area failures (using predefined failed_nodes)
    initial_failed_areas = set()
    initial_affected_population = 0

    for area, nodes in area_nodes.items():
        total_serving_nodes = len(nodes)
        failed_serving_nodes = len([n for n in nodes if n in failed_nodes])

        # Area fails if >50% serving nodes fail
        if failed_serving_nodes / total_serving_nodes > 0.5:
            initial_failed_areas.add(area)
            initial_affected_population += population_lookup.get(area, 0)

    # Step 3: Prepare optimization data
    nodes_data = []
    for node_code in failed_nodes:
        node_info = next((n for n in network_data["nodes"] if n.get("Code") == node_code), None)
        if not node_info:
            continue

        # Get original resource demands
        demands = {
            'type_1': node_info.get("resource_demand_type_1", 1),
            'type_2': node_info.get("resource_demand_type_2", 1),
            'type_3': node_info.get("resource_demand_type_3", 1)
        }

        # Calculate node value (degree × service areas / resource cost)
        degree = G.degree(node_code)
        service_count = len(node_service_areas.get(node_code, [])) or 1

        node_value = (service_count) / (sum(demands.values()) or 1)

        nodes_data.append({
            'code': node_code,
            'value': node_value,
            'demands': demands,
            'info': node_info,
            'service_areas': node_service_areas.get(node_code, [])
        })

    if not nodes_data:
        return {"status": "error", "message": "No valid nodes for optimization"}

    # Step 4: Linear Programming Optimization
    prob = LpProblem("Network_Recovery", LpMaximize)
    node_vars = {i: LpVariable(f"node_{i}", cat="Binary") for i in range(len(nodes_data))}

    # Objective and constraints
    prob += lpSum(nodes_data[i]['value'] * node_vars[i] for i in range(len(nodes_data)))
    for res_type in RESOURCE_LIMITS:
        prob += lpSum(nodes_data[i]['demands'][res_type] * node_vars[i]
                      for i in range(len(nodes_data))) <= RESOURCE_LIMITS[res_type]

    try:
        prob.solve()
    except Exception as e:
        return {"status": "error", "message": f"LP solver failed: {str(e)}"}

    # Step 5: Create backup nodes and analyze recovery
    new_nodes = []
    resource_usage = {k: 0 for k in RESOURCE_LIMITS}
    restored_nodes = [nodes_data[i]['code'] for i in range(len(nodes_data)) if value(node_vars[i]) == 1]

    # Calculate restored areas
    restored_areas = set()
    restored_population = 0
    still_failed_areas = set()
    still_affected_population = 0

    for area in initial_failed_areas:
        total_serving_nodes = len(area_nodes[area])
        # Count how many original serving nodes are still down
        remaining_failed = len([n for n in area_nodes[area]
                              if n in failed_nodes and n not in restored_nodes])

        # Area is restored if failed nodes <=50%
        if remaining_failed / total_serving_nodes <= 0.5:
            restored_areas.add(area)
            restored_population += population_lookup.get(area, 0)
        else:
            still_failed_areas.add(area)
            still_affected_population += population_lookup.get(area, 0)

    # Create backup nodes
    for i in range(len(nodes_data)):
        if value(node_vars[i]) == 1:
            original_node = nodes_data[i]['info']
            backup_node = original_node.copy()
            backup_node["Code"] = f"Backup_{original_node['Code']}"
            backup_node["Facility"] = f"Backup_{original_node.get('Facility', 'Facility')}"

            # Explicitly include original demands
            backup_node.update({
                "resource_demand_type_1": nodes_data[i]['demands']['type_1'],
                "resource_demand_type_2": nodes_data[i]['demands']['type_2'],
                "resource_demand_type_3": nodes_data[i]['demands']['type_3']
            })

            new_nodes.append(backup_node)
            for res in resource_usage:
                resource_usage[res] += nodes_data[i]['demands'][res]

    # Prepare final output
    output_data = {
        "initial_state": {
            "failed_nodes": failed_nodes,
            "failed_areas": list(initial_failed_areas),
            "affected_population": initial_affected_population,
        },
        "recovery_results": {
            "restored_nodes": restored_nodes,
            "new_backup_nodes": new_nodes,
            "restored_areas": list(restored_areas),
            "restored_population": restored_population,
            "remaining_failed_areas": list(still_failed_areas),
            "remaining_affected_population": still_affected_population,
            "resource_usage": resource_usage,
            "resource_utilization": {k: f"{v / RESOURCE_LIMITS[k]:.1%}" for k, v in resource_usage.items()},
            "total_restored_value": sum(
                nodes_data[i]['value'] for i in range(len(nodes_data)) if value(node_vars[i]) == 1),
            "lp_status": prob.status
        },
        "parameters": {
            "resource_limits": RESOURCE_LIMITS,
            "area_failure_threshold": ">50% serving nodes failed"
        }
    }

    # Save output
    output_path = 'recovery_plan_determined_under_resource_constraints.json'
    try:
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=4)

        # Update global data
        global_data["recovery_plan_determined_under_resource_constraints"] = output_path
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
            "resource_utilization": output_data["recovery_results"]["resource_utilization"],
        },
        "output_file": output_path
    }


# Execution
global_json_path = 'Global_Data.json'
recovery_plan_determined_under_resource_constraints(global_json_path)
