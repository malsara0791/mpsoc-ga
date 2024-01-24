import random
from typing import List

# Example data for building the core.
S_RATE = [0.15, 0.4, 0.6, 0.8, 1.0]  # Speed rates of processors
C_UTIL = [0.45, 0.4, 0.4, 0.16]  # Core utilization after allocation
C_RATE = [0.6, 0.4, 0.4, 0.4]  # Core rate after allocation
T_UTIL = [0.45, 0.4, 0.2, 0.2, 0.16]  # Task utilization
T_CORE_NUM = [1, 2, 3, 3, 4]  # Core where each task is located
P = [80, 170, 400, 900, 1600]  # Power per speed rate


class Population:
    def __init__(self):
        self.chromosomes = []
        self.fitness = []
        self.flm = []


def init_population() -> Population:
    pop = Population()
    pop_size = sum(int(tu / 0.01) for tu in T_UTIL)

    for task in range(5):
        t1 = int(T_UTIL[task] / 0.01)
        x = 0.0
        for _ in range(t1):
            y = T_UTIL[task] - x
            random_core = random.randint(0, 3)
            random_rate = random.randint(0, 4)
            chromo = f"{task} {y:.2f} {random_core} {random_rate}"
            pop.chromosomes.append(chromo)
            pop.fitness.append(0)
            pop.flm.append(0)
            x += 0.01

    return pop


def fitness_calc(pop: Population) -> Population:
    for i, chromo in enumerate(pop.chromosomes):
        task, ui1, random_core, random_rate = map(float, chromo.split())
        task, random_core, random_rate = int(task), int(random_core), int(random_rate)

        m = T_CORE_NUM[task] - 1
        sy = S_RATE[random_rate]
        sx = C_RATE[m]
        uj = C_UTIL[random_core]
        ui = T_UTIL[task]
        ui2 = ui - ui1
        syo = C_RATE[random_core]

        syn = S_RATE.index(sy)
        sxn = S_RATE.index(sx)
        syoo = S_RATE.index(syo)

        r = (sx * (sx - ui)) / (sx - sy)
        l = sy - uj
        y = min(l, r)

        p_new = ((uj + ui1) / sy * P[syn]) + (ui2 / sx * P[sxn])
        p_old = (uj / syo * P[syoo]) + (ui / sx * P[sxn])
        diff = p_old - p_new
        savings = int((diff / p_old) * 100)

        if 0.00 < y <= ui1 and diff > 0:
            pop.fitness[i] = diff
            pop.flm[i] = savings
        else:
            pop.fitness[i] = 10

    return pop


def crossover(pop: Population) -> Population:
    pop2 = Population()
    pop_size = len(pop.chromosomes)

    for _ in range(pop_size):
        parent_a = roulette(pop)
        parent_b = roulette(pop)

        task1, ui11, random_core1, random_rate1 = map(float, parent_a.split())
        task1, random_core1, random_rate1 = int(task1), int(random_core1), int(random_rate1)
        task2, ui12, random_core2, random_rate2 = map(float, parent_b.split())
        task2, random_core2, random_rate2 = int(task2), int(random_core2), int(random_rate2)

        if random.randint(0, 1) == 0:
            child = f"{task1} {ui11:.2f} {random_core2} {random_rate2}"
        else:
            child = f"{task2} {ui12:.2f} {random_core1} {random_rate1}"

        mutant = mutate(child)
        pop2.chromosomes.append(mutant)
        pop2.fitness.append(0)
        pop2.flm.append(0)

    return pop2
