import json
import random
import networkx as nx
import math
import matplotlib.pyplot as plt


def fitness(individual, edges):
    """
    Calculate the fitness of an individual, which is the sum of GSCC sizes after each node recovery step.
    :param individual: An individual representing the order of node recovery
    :param edges: List of edges in the network
    :return: Fitness value (sum of GSCC sizes)
    """
    G = nx.DiGraph()
    total = 0
    node_to_out = {}
    for e in edges:
        node_to_out.setdefault(e["Start"], []).append(e["End"])

    N = len(individual)
    for idx, node in enumerate(individual, start=1):  # idx 从 1 到 N
        # —— 同原来逻辑：恢复节点并添加边 —— #
        G.add_node(node)
        for tgt in node_to_out.get(node, []):
            if tgt in G:
                G.add_edge(node, tgt)
        for src, tgts in node_to_out.items():
            if node in tgts and src in G:
                G.add_edge(src, node)

        # 计算 GSCC 大小
        try:
            gscc_size = len(max(nx.strongly_connected_components(G), key=len))
        except ValueError:
            gscc_size = 0

        # 权重：剩余步骤数 = N - idx + 1
        weight = (N - idx + 1) / N
        total += gscc_size * weight

    return total


def generate_neighbor(solution):
    """
    Generate a neighbor solution by swapping two random nodes in the recovery order.
    :param solution: Current solution (node recovery order)
    :return: Neighbor solution
    """
    neighbor = solution.copy()
    idx1, idx2 = random.sample(range(len(neighbor)), 2)
    neighbor[idx1], neighbor[idx2] = neighbor[idx2], neighbor[idx1]
    return neighbor


def acceptance_probability(current_fitness, neighbor_fitness, temperature):
    """
    Calculate the acceptance probability for the neighbor solution.
    :param current_fitness: Fitness of the current solution
    :param neighbor_fitness: Fitness of the neighbor solution
    :param temperature: Current temperature
    :return: Acceptance probability
    """
    if neighbor_fitness > current_fitness:
        return 1.0
    else:
        return math.exp((neighbor_fitness - current_fitness) / temperature)


def recovery_order_determined_based_on_GSCC_by_SA(global_json_path, initial_temperature=1000, cooling_rate=0.995,
                                   stopping_temperature=1e-3, max_iterations=100000):
    """
    Solve the node recovery order using Simulated Annealing based on GSCC for a subset of failed nodes.
    :param global_json_path: Path to the global data JSON file
    :param initial_temperature: Starting temperature for SA
    :param cooling_rate: Rate at which the temperature decreases
    :param stopping_temperature: Temperature at which the algorithm stops
    :param max_iterations: Maximum number of iterations
    :return: Path to the recovery strategy result
    """
    global_json_path = global_json_path.strip().replace('\n', '')

    # Load global data
    with open(global_json_path, 'r') as f:
        global_data = json.load(f)

    network_path = global_data["interdependent_critical_infrastructures_networks"]
    failure_file = global_data.get('failure_node_after_HECRAS_simulations')

    # Load network data
    with open(network_path, 'r') as f:
        network_data = json.load(f)

    # Load failure data
    with open(failure_file, 'r') as f:
        failure_data = json.load(f)

    # Get the failed nodes from the failure data
    failed_nodes = failure_data["all_failed_nodes"]

    # Filter out the failed nodes from the network
    nodes = [node["Code"] for node in network_data["nodes"]]
    failed_nodes = [node for node in nodes if node in failed_nodes]

    edges = network_data.get("edges", [])

    # Initialize current solution with a random permutation of failed nodes
    current_solution = failed_nodes[:]
    random.shuffle(current_solution)
    current_fitness = fitness(current_solution, edges)

    best_solution = current_solution.copy()
    best_fitness = current_fitness

    temperature = initial_temperature
    iteration = 0

    temperature_history = [temperature]  # 记录温度的变化
    fitness_history = [current_fitness]  # 记录适应度的变化

    while temperature > stopping_temperature and iteration < max_iterations:
        # Generate a neighbor solution
        neighbor_solution = generate_neighbor(current_solution)
        neighbor_fitness = fitness(neighbor_solution, edges)

        # Decide whether to accept the neighbor solution
        ap = acceptance_probability(current_fitness, neighbor_fitness, temperature)
        if ap > random.random():
            current_solution = neighbor_solution
            current_fitness = neighbor_fitness

            # Update best solution found
            if current_fitness > best_fitness:
                best_solution = current_solution.copy()
                best_fitness = current_fitness

        # Cool down the temperature
        temperature *= cooling_rate
        iteration += 1

        # 记录每次迭代的温度和适应度
        temperature_history.append(temperature)
        fitness_history.append(best_fitness)

    plt.figure()
    plt.plot(temperature_history, label="Temperature")
    plt.xlabel("Iteration")
    plt.ylabel("Temperature")
    plt.title("Simulated Annealing: Temperature Decay Curve")
    plt.legend()
    plt.tight_layout()

    # 显示图形并暂停2秒后关闭
    plt.show(block=False)
    plt.pause(2)
    plt.close()

    recovery_order = best_solution

    result = {
        'recovery_order': recovery_order,
        'number_of_nodes': len(recovery_order),
    }

    output_json_path = 'recovery_order_determined_based_on_GSCC_by_SA.json'
    with open(output_json_path, 'w') as f:
        json.dump(result, f, indent=4)

    # Update global data
    global_data["recovery_order_determined_based_on_GSCC_by_SA"] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(global_data, f, indent=4)

    return "The path to recovery order result has been saved in global_data.json"


# Usage example
global_json_path = 'Global_Data.json'
recovery_order_determined_based_on_GSCC_by_SA(global_json_path)
