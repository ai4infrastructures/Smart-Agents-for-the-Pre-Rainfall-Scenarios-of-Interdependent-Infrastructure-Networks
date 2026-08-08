import json
import random
import networkx as nx
import matplotlib.pyplot as plt
import math


def initialize_population(nodes, population_size):
    """
    Initialize the population with random permutations of nodes.
    :param nodes: List of all nodes
    :param population_size: Size of the population
    :return: List of initialized individuals
    """
    population = []
    for _ in range(population_size):
        individual = nodes[:]
        random.shuffle(individual)
        population.append(individual)
    return population


def build_edge_maps(edges):
    # edges: list of {"Start":…, "End":…}
    node_to_out_edges = {}
    node_to_in_edges  = {}
    for e in edges:
        s, t = e["Start"], e["End"]
        node_to_out_edges.setdefault(s, []).append(t)
        node_to_in_edges .setdefault(t, []).append(s)
    return node_to_out_edges, node_to_in_edges

def fitness(individual, node_to_out_edges, node_to_in_edges, total_nodes):
    G = nx.DiGraph()
    total = 0
    for step, node in enumerate(individual):
        G.add_node(node)

        # 1) 添加出边
        for tgt in node_to_out_edges.get(node, []):
            if tgt in G:
                G.add_edge(node, tgt)

        # 2) 添加入边
        for src in node_to_in_edges.get(node, []):
            if src in G:
                G.add_edge(src, node)

        # 3) 计算当前最大强连通子图大小
        if G.number_of_nodes() > 0:
            largest_scc = max(nx.strongly_connected_components(G), key=len)
            current_scc_size = len(largest_scc)

            # 4) 权重计算：剩余恢复步骤数为总节点数减去当前恢复步骤
            remaining_steps = total_nodes - step
            weight = 1 / (remaining_steps + 1)  # 使用倒数权重

            # 将权重和GSCC大小结合
            total += current_scc_size * weight  # 权重化适应度
    return total


def selection(population, fitness_scores, total_nodes, k):
    """
    Roulette-wheel selecting k individuals (allow repeats), considering the weight of remaining steps.
    """
    total = sum(fitness_scores)
    if total <= 0:
        return random.choices(population, k=k)

    # 防止除零错误
    weighted_fitness = [f * (1 / max(total_nodes - i, 1)) for i, f in enumerate(fitness_scores)]
    weighted_total = sum(weighted_fitness)
    probs = [f / weighted_total for f in weighted_fitness]

    return random.choices(population, weights=probs, k=k)


def crossover(parent1, parent2):
    """
    Single-offspring Order Crossover.
    """
    n = len(parent1)
    child = [None] * n
    i, j = sorted(random.sample(range(n), 2))
    child[i:j] = parent1[i:j]
    pos = j
    for gene in parent2[j:] + parent2[:j]:
        if gene not in child:
            child[pos] = gene
            pos = (pos + 1) % n
    return child


def mutation(individual, mutation_rate=0.02):
    """
    Single-swap mutation: with prob. mutation_rate swap one random pair.
    """
    if random.random() < mutation_rate:
        i, j = random.sample(range(len(individual)), 2)
        individual[i], individual[j] = individual[j], individual[i]
    return individual

def recovery_order_determined_based_on_GSCC_by_GA(global_json_path, population_size=50, generations=100, crossover_rate=0.8,
                                    mutation_rate=0.02):
    """
    Solve the node recovery order using Genetic Algorithm based on GSCC.
    :param global_json_path: Path to the global data JSON file
    :param population_size: Size of the population
    :param generations: Number of generations to run the algorithm
    :param crossover_rate: Probability of performing crossover
    :param mutation_rate: Probability of mutation
    :return: Path to the recovery strategy result
    """
    global_json_path = global_json_path.strip().replace('\n', '')

    with open(global_json_path, 'r') as f:
        global_data = json.load(f)

    network_path = global_data["interdependent_critical_infrastructures_networks"]
    failure_file = global_data.get('failure_node_after_HECRAS_simulations')

    with open(network_path, 'r') as f:
        network_data = json.load(f)

    # Read the failed nodes from the external file
    with open(failure_file, 'r') as f:
        failure_data = json.load(f)

    failed_nodes = failure_data.get("all_failed_nodes", [])

    nodes = failed_nodes  # Use only the failed nodes for recovery
    edges = network_data.get("edges", [])

    node_to_out_edges, node_to_in_edges = build_edge_maps(edges)

    population = initialize_population(nodes, population_size)

    best_ind, best_fit = None, -1
    fitness_history = []   # 新增：记录每代最优适应度

    total_nodes = len(nodes)
    # —— 主循环中的修改后选择-交叉-变异部分 ——#
    for gen in range(generations):
        scores = [fitness(ind, node_to_out_edges, node_to_in_edges, total_nodes) for ind in population]
        gen_best = max(scores)
        fitness_history.append(gen_best)
        if gen_best > best_fit:
            best_fit, best_ind = gen_best, population[scores.index(gen_best)]

        elite_cnt = max(1, int(0.05 * population_size))
        elite_idx = sorted(range(len(population)), key=lambda i: scores[i], reverse=True)[:elite_cnt]
        elites = [population[i] for i in elite_idx]

        needed = population_size - elite_cnt
        if needed <= 0:
            break

        pair_cnt = math.ceil(needed / 2)
        parents = selection(population, scores, total_nodes, k=pair_cnt * 2)
        offspring = []
        for i in range(0, len(parents), 2):
            p1, p2 = parents[i], parents[i + 1]
            if random.random() < crossover_rate:
                c1 = crossover(p1, p2)
                c2 = crossover(p2, p1)
            else:
                c1, c2 = p1[:], p2[:]
            offspring.extend([mutation(c1, mutation_rate), mutation(c2, mutation_rate)])
        offspring = offspring[:needed]

        population = elites + offspring

    plt.figure(figsize=(8, 5))
    plt.plot(range(1, len(fitness_history)+1), fitness_history, marker='o')
    plt.title('GA Recovery Strategy: Best Fitness per Generation')
    plt.xlabel('Generation')
    plt.ylabel('Max GSCC Size')
    plt.grid(True, linestyle='--', alpha=0.5)

    plt.show(block=False)  # 非阻塞地弹出窗口
    plt.pause(2)  # 暂停 2 秒
    plt.close()  # 关闭图窗


    # 最终结果保存，带上 fitness_history
    result = {
        'recovery_order': best_ind,
        'number_of_nodes': len(best_ind),
        'fitness_history': fitness_history  # 新增：适应度随代数的变化
    }
    output_json_path = 'recovery_order_determined_based_on_GSCC_by_GA.json'
    with open(output_json_path, 'w') as f:
        json.dump(result, f, indent=4)

    # Update global data
    global_data["recovery_order_determined_based_on_GSCC_by_GA"] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(global_data, f, indent=4)

    return "The path to recovery order result has been saved in global_data.json"


# Usage example
global_json_path = 'Global_Data.json'
recovery_order_determined_based_on_GSCC_by_GA(global_json_path)
