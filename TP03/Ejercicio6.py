import random
import numpy as np
import matplotlib.pyplot as plt

# ========== DATOS DEL PROBLEMA ==========
# Lista de pesos de las 10 cajas (kg)
weights = [300, 200, 450, 145, 664, 90, 150, 355, 401, 395]
# Lista de precios de las 10 cajas ($)
prices = [100, 50, 115, 25, 200, 30, 40, 100, 100, 100]
# Capacidad máxima que soporta la grúa (kg)
MAX_CAPACITY = 1000
# Número total de cajas
N_BOXES = len(weights)

# ========== PARÁMETROS DEL ALGORITMO GENÉTICO ==========
POPULATION_SIZE = 20   # Tamaño de la población (número de individuos, debe ser par)
MUTATION_RATE = 0.1    # Probabilidad de mutación de cada gen
MAX_GENERATIONS = 100  # Número máximo de generaciones
ELITISM_COUNT = 2      # Número de mejores individuos que pasan directamente (elitismo)

# ========== REPRESENTACIÓN DE UN INDIVIDUO ==========
def create_individual():
    """
    Crea un individuo aleatorio representado como una lista de 0s y 1s:
    - 1: caja incluida en la grúa
    - 0: caja no incluida
    Asegura que el individuo no supere el límite de peso.
    """
    individual = [random.randint(0, 1) for _ in range(N_BOXES)]
    
    # Si el individuo supera la capacidad, se "repara" quitando cajas
    while calculate_weight(individual) > MAX_CAPACITY:
        for i in range(N_BOXES):
            if individual[i] == 1 and random.random() < 0.5:
                individual[i] = 0
                if calculate_weight(individual) <= MAX_CAPACITY:
                    break
    return individual

def calculate_weight(individual):                                                   #Devuelve el peso total de las cajas seleccionadas (los 1s del cromosoma)
    return sum(weights[i] for i in range(N_BOXES) if individual[i] == 1)

def calculate_price(individual):
    """Devuelve el precio total de las cajas seleccionadas."""
    return sum(prices[i] for i in range(N_BOXES) if individual[i] == 1)

# ========== POBLACIÓN INICIAL ==========
def create_population():
    """Genera una población inicial de individuos válidos."""
    return [create_individual() for _ in range(POPULATION_SIZE)]

# ========== FUNCIÓN DE FITNESS ==========
def evaluate_fitness(individual):
    """
    Calcula la idoneidad (fitness) del individuo:
    - Si el peso excede el límite → fitness = 0
    - Si no excede → fitness = precio total
    """
    total_weight = calculate_weight(individual)
    if total_weight > MAX_CAPACITY:
        return 0
    return calculate_price(individual)

# ========== SELECCIÓN POR RULETA ==========
def select_parents(population, fitnesses):
    """
    Selección por ruleta:
    - La probabilidad de cada individuo es proporcional a su fitness.
    - Si todos tienen fitness 0, se eligen al azar.
    """
    total_fitness = sum(fitnesses)
    if total_fitness == 0:
        return random.sample(population, 2)  # todos igual de malos

    # Probabilidades proporcionales al fitness
    probabilities = [f/total_fitness for f in fitnesses]

    # Elegir dos padres
    parents = []
    for _ in range(2):
        spin = random.random()
        cumulative_prob = 0
        for i, prob in enumerate(probabilities):
            cumulative_prob += prob
            if spin <= cumulative_prob:
                parents.append(population[i])
                break
    return parents

# ========== OPERADOR DE CRUCE ==========
def crossover(parent1, parent2):
    """
    Realiza cruce de un punto:
    - Se elige un punto aleatorio.
    - Se combinan las partes de los dos padres para formar dos hijos.
    """
    point = random.randint(1, N_BOXES - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

# ========== OPERADOR DE MUTACIÓN ==========
def mutate(individual):
    """
    Aplica mutación: con probabilidad MUTATION_RATE,
    invierte el valor de un gen (0→1 o 1→0).
    Después, repara al individuo si supera la capacidad.
    """
    for i in range(N_BOXES):
        if random.random() < MUTATION_RATE:
            individual[i] = 1 - individual[i]  # flip bit
    
    # Reparación: si excede peso, eliminar cajas hasta que sea válido
    total_weight = calculate_weight(individual)
    while total_weight > MAX_CAPACITY:
        loaded_boxes = [i for i in range(N_BOXES) if individual[i] == 1]
        if not loaded_boxes:
            break
        box_to_remove = random.choice(loaded_boxes)
        individual[box_to_remove] = 0
        total_weight = calculate_weight(individual)
    
    return individual

# ========== ALGORITMO GENÉTICO PRINCIPAL ==========
def genetic_algorithm():
    """Ejecuta el algoritmo genético completo."""
    # 1. Crear población inicial
    population = create_population()
    best_individual = None
    best_fitness = 0
    fitness_history = []

    # 2. Iterar sobre generaciones
    for generation in range(MAX_GENERATIONS):
        # Evaluar fitness
        fitnesses = [evaluate_fitness(ind) for ind in population]

        # Guardar mejor individuo de la generación
        current_best_fitness = max(fitnesses)
        current_best_index = fitnesses.index(current_best_fitness)
        
        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_individual = population[current_best_index].copy()

        fitness_history.append(best_fitness)

        if generation % 10 == 0:
            print(f"Generación {generation}: Mejor fitness = {best_fitness}")

        # 3. Crear nueva población
        new_population = []

        # Elitismo: mantener los mejores sin cambios
        sorted_indices = np.argsort(fitnesses)[::-1]
        for i in range(ELITISM_COUNT):
            new_population.append(population[sorted_indices[i]].copy())

        # Rellenar el resto con cruce y mutación
        while len(new_population) < POPULATION_SIZE:
            parents = select_parents(population, fitnesses)
            child1, child2 = crossover(parents[0], parents[1])
            new_population.append(mutate(child1))
            if len(new_population) < POPULATION_SIZE:
                new_population.append(mutate(child2))

        population = new_population
    
    return best_individual, best_fitness, fitness_history

# ========== EJECUCIÓN Y RESULTADOS ==========
if __name__ == "__main__":
    print("Ejecutando algoritmo genético para el problema de la grúa...")
    print(f"Capacidad máxima: {MAX_CAPACITY} kg")
    print(f"Número de cajas: {N_BOXES}")
    print(f"Pesos: {weights}")
    print(f"Precios: {prices}\n")
    
    # Ejecutar el algoritmo
    best_solution, best_value, history = genetic_algorithm()
    
    # Mostrar mejor solución
    print("\n" + "="*50)
    print("MEJOR SOLUCIÓN ENCONTRADA:")
    print("="*50)
    
    total_weight = calculate_weight(best_solution)
    total_price = calculate_price(best_solution)
    
    print(f"Cajas seleccionadas: {[i+1 for i in range(N_BOXES) if best_solution[i] == 1]}")
    print(f"Peso total: {total_weight} kg")
    print(f"Precio total: ${total_price}")
    
    print("\nDetalle de cajas seleccionadas:")
    for i in range(N_BOXES):
        if best_solution[i] == 1:
            print(f"Caja {i+1}: Peso = {weights[i]} kg, Precio = ${prices[i]}")

    # Graficar evolución del fitness
    plt.figure(figsize=(10, 6))
    plt.plot(history, linewidth=2)
    plt.title('Evolución del Mejor Fitness por Generación')
    plt.xlabel('Generación')
    plt.ylabel('Fitness (Precio Total $)')
    plt.grid(True, alpha=0.3)
    plt.show()
