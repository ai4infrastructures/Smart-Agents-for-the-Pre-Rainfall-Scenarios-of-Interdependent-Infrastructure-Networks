import json
import random
import math
import matplotlib.pyplot as plt

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


def fitness(individual, code_to_areas, population_map):
    """
    计算一条恢复序列的适应度：
    - remaining_steps：剩余恢复步骤数（影响权重）
    - new_population_sum：本步新恢复的人口总和
    """
    restored = set()
    total_fitness = 0
    remaining_steps = len(individual)

    for node in individual:
        # 1. 计算本步新恢复的区域
        new_areas = set(code_to_areas.get(node, [])) - restored
        if new_areas:
            restored |= new_areas
            # 2. 本步新增人口 × 剩余步骤数
            new_population_sum = sum(population_map.get(str(a), 0) for a in new_areas)
            total_fitness += new_population_sum * remaining_steps
        remaining_steps -= 1

    return total_fitness


def selection(population, fitness_scores, k):
    """
    按轮盘赌法选出 k 个个体（允许重复）。
    """
    total = sum(fitness_scores)
    if total <= 0:
        return random.choices(population, k=k)  # 均匀采样
    probs = [f / total for f in fitness_scores]
    return random.choices(population, weights=probs, k=k)

def order_crossover(parent1, parent2):
    """
    顺序交叉（OX）确保子代仍是合法全排列。
    """
    n = len(parent1)
    i, j = sorted(random.sample(range(n), 2))
    # 1. 在子代对应位置复制 parent1[i:j]
    child = [None] * n
    child[i:j] = parent1[i:j]
    # 2. 按 parent2 的顺序，将剩余基因依次填入
    pos = j
    for gene in parent2[j:] + parent2[:j]:
        if gene not in child:
            child[pos] = gene
            pos = (pos + 1) % n
    return child


def mutation(individual):
    """
    Perform mutation by randomly swapping two nodes in the individual.
    :param individual: The individual to mutate
    :return: Mutated individual
    """
    i, j = random.sample(range(len(individual)), 2)
    individual[i], individual[j] = individual[j], individual[i]
    return individual


def recovery_order_determined_based_on_population_by_GA(global_json_path, population_size=50, generations=100,crossover_rate=0.8,mutation_rate=0.1):
    """
    Solve the node recovery order using Genetic Algorithm, but only for failed nodes.
    :param global_json_path: Path to the global data JSON file
    :param population_size: Size of the population
    :param generations: Number of generations to run the algorithm
    :return: Path to the recovery strategy result
    """
    global_json_path = global_json_path.strip().replace('\n', '')

    # Load global data
    with open(global_json_path, 'r') as f:
        global_data = json.load(f)

    # Load network and population data paths from the global data
    network_path = global_data["interdependent_critical_infrastructures_networks"]
    population_data_path = global_data["population_data"]
    failure_file = global_data.get('failure_node_after_HECRAS_simulations')

    with open(network_path, 'r') as f:
        network_data = json.load(f)
    with open(population_data_path, 'r') as f:
        population_data = json.load(f)

    # Load failed nodes information from the failure file
    with open(failure_file, 'r') as f:
        failure_data = json.load(f)

    # Get the list of failed nodes
    failed_nodes = failure_data.get("all_failed_nodes", [])

    # Only keep the failed nodes from the network
    nodes = [node["Code"] for node in network_data["nodes"] if node["Code"] in failed_nodes]

    fitness_history = []

    # 在读取完 network_data/population_data 后：
    code_to_areas = {}
    for n in network_data["nodes"]:
        sa = n.get("Service Area")
        if sa:
            areas = [area.strip() for area in sa.split(',') if area.strip()]
            code_to_areas[str(n["Code"])] = areas
        else:
            code_to_areas[str(n["Code"])] = []
            # population_data 中的 Id 同样转为字符串
    population_map = {str(d["Id"]): d["Population"] for d in population_data}

    population = initialize_population(nodes, population_size)
    fitness_scores = [fitness(ind, code_to_areas, population_map)
                      for ind in population]
    # 初始化 best_individual 为首代最优
    best_idx = max(range(len(population)), key=lambda i: fitness_scores[i])
    best_individual = population[best_idx]
    best_fitness = fitness_scores[best_idx]
    fitness_history.append(best_fitness)
    for gen in range(1,generations):
        # 1. 精英保留
        elite_count = max(1, int(0.05 * population_size))
        elite_idx = sorted(
            range(len(population)),
            key=lambda i: fitness_scores[i],
            reverse=True
        )[:elite_count]
        elites = [population[i] for i in elite_idx]

        # 2. 选择 + OX 交叉 + 变异 生成 others
        offspring_count = population_size - elite_count

        # 从轮盘赌中选出 2*ceil(offspring_count/2) 个父本，以保证能配对出足够子代
        pair_count = math.ceil(offspring_count / 2)
        selected = selection(population, fitness_scores, k=pair_count * 2)

        others = []
        for i in range(0, len(selected), 2):
            p1, p2 = selected[i], selected[i + 1]
            # 按交叉率决定是否交叉
            if random.random() < crossover_rate:
                c1 = order_crossover(p1, p2)
                c2 = order_crossover(p2, p1)
            else:
                c1, c2 = p1[:], p2[:]
            # 按变异率决定是否变异
            if random.random() < mutation_rate:
                c1 = mutation(c1)
            if random.random() < mutation_rate:
                c2 = mutation(c2)
            others.extend([c1, c2])

        # 截断到 offspring_count
        others = others[:offspring_count]

        new_population = elites + others

        # 4. 评估新一代
        new_fitness = [
            fitness(ind, code_to_areas, population_map)
            for ind in new_population
        ]
        gen_best = max(new_fitness)
        fitness_history.append(gen_best)

        # 5. 更新全局最优
        idx = max(range(len(new_population)), key=lambda k: new_fitness[k])
        if new_fitness[idx] > best_fitness:
            best_fitness, best_individual = new_fitness[idx], new_population[idx]

        # 6. 准备下一代
        population, fitness_scores = new_population, new_fitness

    plt.figure(figsize=(8, 5))
    plt.plot(range(1, generations + 1), fitness_history, marker='o')
    plt.title('GA Recovery: Best Population-Service Fitness')
    plt.xlabel('Generation')
    plt.ylabel('Weighted Service‐Pop Fitness')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show(block=False)  # 非阻塞地弹出窗口
    plt.pause(2)  # 暂停 2 秒
    plt.close()


    recovery_order = best_individual

    result = {
        'recovery_order': recovery_order,
        'number_of_nodes': len(recovery_order),
        'fitness_history': fitness_history
    }

    output_json_path = 'recovery_order_determined_based_on_population_by_GA.json'
    with open(output_json_path, 'w') as f:
        json.dump(result, f, indent=4)

    # Update global data with new recovery strategy
    global_data["recovery_order_determined_based_on_population_by_GA"] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(global_data, f, indent=4)

    return "The path to recovery order result has been saved in global_data.json"


# Usage example
global_json_path = 'Global_Data.json'
recovery_order_determined_based_on_population_by_GA(global_json_path)
