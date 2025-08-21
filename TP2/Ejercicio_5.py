import heapq
from collections import deque

graph = {
    "A": {"B": 1, "C": 1},
    "B": {"A": 1, "D": 1},
    "C": {"A": 1, "K": 1},
    "D": {"B": 1, "M": 1},
    "E": {"N": 1},
    "G": {"I": 1, "P": 1},
    "I": {"G": 1, "Q": 1, "W": 1},
    "W": {"I": 30, "K": 30},
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
walls = {("C","D"),("D","E"),("W","R"),("T","F")}

def maze_distance(start, goal):
    queue = deque([(start,0)])
    visited = {start}
    while queue:
        node, dist = queue.popleft()
        if node == goal:
            return dist
        for neighbor in graph[node]:
            if (node,neighbor) in walls or (neighbor,node) in walls:
                continue
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor,dist+1))
    return float("inf")
heuristic = {n: maze_distance(n, goal) for n in graph}
print(heuristic)


def dfs(start, goal):
    stack = [(start, [start], 0)]
    visited = set()
    while stack:
        node, path, cost = stack.pop()
        if node == goal:
            return path, cost
        if node in visited: 
            continue
        visited.add(node)
        for neighbor, w in sorted(graph[node].items(), reverse=True): # alfabético
            stack.append((neighbor, path + [neighbor], cost + w))
    return None

def avara(start, goal):
    frontier = [(heuristic[start], start, [start], 0)]
    visited = set()
    while frontier:
        _, node, path, cost = heapq.heappop(frontier)
        if node == goal:
            return path, cost
        if node in visited: 
            continue
        visited.add(node)
        for neighbor, w in graph[node].items():
            heapq.heappush(frontier, (heuristic[neighbor], neighbor, path+[neighbor], cost+w))
    return None

def astar(start, goal):
    frontier = [(heuristic[start], 0, start, [start])]
    visited = {}
    while frontier:
        f, g, node, path = heapq.heappop(frontier)
        if node == goal:
            return path, g
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
