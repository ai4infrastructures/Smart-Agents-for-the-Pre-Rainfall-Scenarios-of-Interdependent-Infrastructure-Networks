import json
import random
import math
import matplotlib.pyplot as plt

def initial_solution(nodes):
    solution = nodes[:]
    random.shuffle(solution)
    return solution


def generate_neighbor(solution):
    neighbor = solution[:]
    i, j = random.sample(range(len(neighbor)), 2)
    neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
    return neighbor


def fitness(individual, code_to_areas, id_to_population):
    restored_areas = set()
    total_fitness = 0
    current_population = 0      # ← 用来累加已恢复区域的人口
    weight = len(individual)

    for node in individual:
        # 找到本次节点新增恢复到的区域
        new_areas = set(code_to_areas.get(node, [])) - restored_areas
        # 将新增区域加入已恢复集合
        restored_areas |= new_areas

        # 将新增区域的人口加到 current_population
        for area in new_areas:
            current_population += id_to_population.get(area, 0)

        # 用增量后的一致人口数计算带权得分
        total_fitness += current_population * weight
        weight -= 1

    return total_fitness


def acceptance_probability(current_fitness, neighbor_fitness, temperature):
    if neighbor_fitness > current_fitness:
        return 1.0
    else:
        return math.exp((neighbor_fitness - current_fitness) / temperature)


def recovery_order_determined_based_on_population_by_SA(global_json_path, initial_temp=1000,
                                          cooling_rate=0.995,
                                          temperature_min=1e-3, max_iterations=100000):
    global_json_path = global_json_path.strip().replace('\n', '')

    # Load global data
    with open(global_json_path, 'r') as f:
        global_data = json.load(f)

    network_path = global_data["interdependent_critical_infrastructures_networks"]
    population_data_path = global_data["population_data"]
    failure_file = global_data.get('failure_node_after_HECRAS_simulations')

    with open(network_path, 'r') as f:
        network_data = json.load(f)
    with open(population_data_path, 'r') as f:
        population_data = json.load(f)

    # Load the failed nodes data
    with open(failure_file, 'r') as f:
        failure_data = json.load(f)

    failed_nodes = failure_data.get("all_failed_nodes", [])

    code_to_areas = {}
    for n in network_data["nodes"]:
        sa = n.get("Service Area") or ""  # 如果是 None，就用空串
        areas = [a.strip() for a in sa.split(',') if a.strip()]
        code_to_areas[n["Code"]] = areas

    id_to_population = {
        d["Id"]: d["Population"]
        for d in population_data
    }
    # Initialize solution with only failed nodes
    current_solution = initial_solution(failed_nodes)
    current_fitness = fitness(current_solution, code_to_areas, id_to_population)

    best_solution = current_solution[:]
    best_fitness = current_fitness

    # —— 性能监控数据结构 —— #
    fitness_history = [current_fitness]
    temperature_history = [initial_temp]
    iteration_history = [0]

    temperature = initial_temp
    iteration = 0

    while temperature > temperature_min and iteration < max_iterations:
        neighbor_solution = generate_neighbor(current_solution)
        neighbor_fitness = fitness(neighbor_solution, code_to_areas, id_to_population)
        ap = acceptance_probability(current_fitness, neighbor_fitness, temperature)

        if random.random() < ap:
            current_solution = neighbor_solution
            current_fitness = neighbor_fitness
            if current_fitness > best_fitness:
                best_solution = current_solution[:]
                best_fitness = current_fitness

        temperature *= cooling_rate
        iteration += 1

        # —— 记录当前迭代数据 —— #
        fitness_history.append(best_fitness)
        temperature_history.append(temperature)
        iteration_history.append(iteration)

    # Temperature decay curve (English labels, show only 2 seconds)
    plt.figure()
    plt.plot(iteration_history, temperature_history)
    plt.xlabel("Iteration")
    plt.ylabel("Temperature")
    plt.title("Simulated Annealing: Temperature Decay Curve")
    plt.tight_layout()

    # 非阻塞显示，暂停两秒，然后关闭窗口
    plt.show(block=False)
    plt.pause(2)
    plt.close()

    # —— 写结果到 JSON，更新 global_json_path —— #
    recovery_order = best_solution
    result = {
        'recovery_order': recovery_order,
        'number_of_nodes': len(recovery_order),
    }
    output_json_path = 'recovery_order_determined_based_on_population_by_SA.json'
    with open(output_json_path, 'w') as f:
        json.dump(result, f, indent=4)
    global_data["recovery_order_determined_based_on_population_by_SA"] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(global_data, f, indent=4)

    return "The path to recovery order result has been saved in global_data.json"


# Usage example
global_json_path = 'Global_Data.json'
recovery_order_determined_based_on_population_by_SA(global_json_path)
