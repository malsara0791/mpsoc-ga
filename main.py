import random
import math

# example data for building the core.
S_RATE = [0.15, 0.4, 0.6, 0.8, 1.0]  # Speed rates of processors
C_UTIL = [0.45, 0.4, 0.4, 0.16]  # Core utilization after allocation
C_RATE = [0.6, 0.4, 0.4, 0.4]  # Core rate after allocation
T_UTIL = [0.45, 0.4, 0.2, 0.2, 0.16]  # Task utilization
T_CORE_NUM = [1, 2, 3, 3, 4]  # Core where each task is located
P = [80, 170, 400, 900, 1600]  # Power per speed rate

class Population:
    def __init__(self):
        self.chromosome = []
        self.fitness = []
        self.FLM = []

def init_population():
    pop = Population()
    pop_size = sum(int(tu / 0.01) for tu in T_UTIL)

    for TASK in range(5):
        t1 = int(T_UTIL[TASK] / 0.01)
        x = 0.0
        for _ in range(t1):
            y = T_UTIL[TASK] - x
            RANDOM_CORE = random.randint(0, 3)
            RANDOM_RATE = random.randint(0, 4)
            chromo = f"{TASK} {y:.2f} {RANDOM_CORE} {RANDOM_RATE}"
            pop.chromosome.append(chromo)
            pop.fitness.append(0)
            pop.FLM.append(0)
            x += 0.01

    return pop

def fitness_calc(pop):
    for i, chromo in enumerate(pop.chromosome):
        TASK, Ui1, RANDOM_CORE, RANDOM_RATE = map(float, chromo.split())
        TASK, RANDOM_CORE, RANDOM_RATE = int(TASK), int(RANDOM_CORE), int(RANDOM_RATE)

        m = T_CORE_NUM[TASK] - 1
        Sy = S_RATE[RANDOM_RATE]
        Sx = C_RATE[m]
        Uj = C_UTIL[RANDOM_CORE]
        Ui = T_UTIL[TASK]
        Ui2 = Ui - Ui1
        Syo = C_RATE[RANDOM_CORE]

        Syn = S_RATE.index(Sy)
        Sxn = S_RATE.index(Sx)
        Syoo = S_RATE.index(Syo)

        R = (Sx * (Sx - Ui)) / (Sx - Sy)
        L = Sy - Uj
        y = min(L, R)

        Pnew = ((Uj + Ui1) / Sy * P[Syn]) + (Ui2 / Sx * P[Sxn])
        Pold = (Uj / Syo * P[Syoo]) + (Ui / Sx * P[Sxn])
        diff = Pold - Pnew
        savings = int((diff / Pold) * 100)

        if y <= Ui1 and y > 0.00 and diff > 0:
            pop.fitness[i] = diff
            pop.FLM[i] = savings
        else:
            pop.fitness[i] = 10

    return pop

def crossover(pop):
    pop2 = Population()
    POP_SIZE = len(pop.chromosome)
    
    for _ in range(POP_SIZE):
        parentA = roulette(pop)
        parentB = roulette(pop)

        TASK1, Ui11, RANDOM_CORE1, RANDOM_RATE1 = map(float, parentA.split())
        TASK1, RANDOM_CORE1, RANDOM_RATE1 = int(TASK1), int(RANDOM_CORE1), int(RANDOM_RATE1)
        TASK2, Ui12, RANDOM_CORE2, RANDOM_RATE2 = map(float, parentB.split())
        TASK2, RANDOM_CORE2, RANDOM_RATE2 = int(TASK2), int(RANDOM_CORE2), int(RANDOM_RATE2)

        if random.randint(0, 1) == 0:
            child = f"{TASK1} {Ui11:.2f} {RANDOM_CORE2} {RANDOM_RATE2}"
        else:
            child = f"{TASK2} {Ui12:.2f} {RANDOM_CORE1} {RANDOM_RATE1}"

        mutant = mutate(child)
        pop2.chromosome.append(mutant)
        pop2.fitness.append(0)
        pop2.FLM.append(0)

    return pop2

def roulette(pop):
    tot_fitness = sum(pop.fitness)
    slice = random.random() * tot_fitness
    fit_so_far = 0.0

    for i in range(len(pop.chromosome)):
        fit_so_far += pop.fitness[i]
        if fit_so_far >= slice:
            return pop.chromosome[i]

    return ""

def mutate(chromo):
    if random.random() < MUTATE_RATE:
        TASK, Ui1, RANDOM_CORE, RANDOM_RATE = map(float, chromo.split())
        TASK, RANDOM_CORE, RANDOM_RATE = int(TASK), int(RANDOM_CORE), int(RANDOM_RATE)

        NEW_CORE = random.choice([c for c in range(4) if c != RANDOM_CORE])
        NEW_RATE = random.choice([r for r in range(5) if r != RANDOM_RATE])

        return f"{TASK} {Ui1:.2f} {NEW_CORE} {NEW_RATE}"
    else:
        return chromo

def print_stuff(pop):
    print("#chrom\tChromosome\tFitness")
    for i in range(len(pop.chromosome)):
        print(f"{i}\t{pop.chromosome[i]}\t{pop.fitness[i]}\t{pop.FLM[i]}")

# Main function
if __name__ == "__main__":
    iterr = int(input("ENTER ITERRATIONS: "))
    MUTATE_RATE = float(input("ENTER MUTATE RATE: "))

    pop = init_population()
    pop = fitness_calc(pop)

    print("INITIAL POPULATION")
    print_stuff(pop)

    for i in range(iterr):
        pop = crossover(pop)
        pop = fitness_calc(pop)

        print("\n\nGENERATION:", i + 1)
        print_stuff(pop)

    print("\n\nBEST CHROMOSOME:", pop.chromosome[-1])
    print("BEST SAVING:", pop.fitness[-1], "mW", pop.FLM[-1], "%")
