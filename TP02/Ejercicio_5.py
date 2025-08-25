import heapq
from collections import deque

# Grafo representado como diccionario de adyacencia
# Cada clave es un nodo y el valor es otro diccionario con sus vecinos y el costo de ir hacia ellos
graph = {
    "A": {"B": 1, "C": 1},
    "B": {"A": 1, "D": 1},
    "C": {"A": 1, "K": 1},
    "D": {"B": 1, "M": 1},
    "E": {"N": 1},
    "G": {"I": 1, "P": 1},
    "I": {"G": 1, "Q": 1, "W": 1},
    "W": {"I": 30, "K": 30},  # pesos altos simulan que este camino no es ideal
    "K": {"W": 1, "M": 1, "T": 1, "C": 1},
    "M": {"K": 1, "N": 1, "F": 1, "D": 1},
    "N": {"M": 1, "E": 1},
    "P": {"G": 1, "Q": 1},
    "Q": {"I": 1, "P": 1, "R": 1},
    "R": {"Q": 1, "T": 1},
    "T": {"K": 1, "R": 1},
    "F": {"M": 1},
}

goal = "F"

# Conjunto de "paredes": aristas que existen en el grafo pero que no deben usarse
# Se agregan como restricciones para los algoritmos de búsqueda
walls = {("C","D"), ("D","E"), ("W","R"), ("T","F")}


def maze_distance(start, goal):
    """
    Calcula la distancia real más corta entre 'start' y 'goal'
    usando BFS, considerando las paredes como prohibidas.
    Esto se usa como heurística para Avara y A*.
    """
    queue = deque([(start, 0)])  # Cola para BFS (nodo, distancia)
    visited = {start}            # Conjunto de visitados para no repetir nodos
    
    while queue:
        node, dist = queue.popleft()
        if node == goal:
            return dist  # Se encontró el objetivo, devolvemos la distancia
        
        for neighbor in graph[node]:
            # Ignorar vecinos que estén bloqueados por paredes
            if (node, neighbor) in walls or (neighbor, node) in walls:
                continue
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist+1))
    
    # Si no hay camino posible, devolvemos infinito
    return float("inf")

# Diccionario de heurística: para cada nodo precomputamos su distancia mínima al objetivo
heuristic = {n: maze_distance(n, goal) for n in graph}
print(heuristic)


def dfs(start, goal):
    """
    Algoritmo DFS clásico (con pila).
    Explora caminos hasta encontrar la meta.
    No garantiza ser el mas optimo.
    """
    stack = [(start, [start], 0)]  # (nodo actual, camino recorrido, costo acumulado)
    visited = set()
    
    while stack:
        node, path, cost = stack.pop()
        if node == goal:
            return path, cost   
        if node in visited: 
            continue
        visited.add(node)
        
        # Se recorre en orden alfabético invertido para mantener consistencia en el recorrido
        for neighbor, w in sorted(graph[node].items(), reverse=True):
            stack.append((neighbor, path + [neighbor], cost + w))
    return None

def avara(start, goal):
    """
    Algoritmo avara.
    Siempre expande el nodo cuya heurística es menor.
    NO garantiza el camino óptimo porque ignora el costo real recorrido.
    """
    frontier = [(heuristic[start], start, [start], 0)]  # (h(n), nodo, camino, costo real)
    visited = set()
    
    while frontier:
        _, node, path, cost = heapq.heappop(frontier)  # Elige siempre el de menor heurística
        if node == goal:
            return path, cost
        
        if node in visited: 
            continue
        visited.add(node)
        
        for neighbor, w in graph[node].items():
            heapq.heappush(frontier, (heuristic[neighbor], neighbor, path+[neighbor], cost+w))
    return None

def astar(start, goal):
    """
    Algoritmo A*.
    Combina el costo real g(n) con la heurística h(n).
    Siempre expande el nodo con menor f(n) = g(n) + h(n).
    Garantiza ser el mas optimo si la heurística es admisible.
    """
    frontier = [(heuristic[start], 0, start, [start])]  # (f, g, nodo, camino)
    visited = {}  # Guarda el costo g más bajo con el que se visitó un nodo
    
    while frontier:
        f, g, node, path = heapq.heappop(frontier)
        if node == goal:
            return path, g
        
        # Si ya encontramos un camino más barato antes, no seguimos este
        if node in visited and visited[node] <= g:
            continue
        visited[node] = g
        
        for neighbor, w in graph[node].items():
            g2 = g + w
            f2 = g2 + heuristic[neighbor]
            heapq.heappush(frontier, (f2, g2, neighbor, path+[neighbor]))
    return None

print("DFS:", dfs("I", "F"))
print("Avara:", avara("I", "F"))
print("A*:", astar("I", "F"))
