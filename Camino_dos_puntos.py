import pygame
import heapq

# Configuración
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 15, 15
CELL_SIZE = WIDTH // COLS

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A* Pathfinding")

# Construcción del grid vacío
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# Obstáculos según la imagen
obstacles = [
    (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7),
    (10, 8), (10, 9), (10, 10), (10, 11)
]
for r, c in obstacles:
    grid[r][c] = 1

start, end = None, None

# --- Algoritmo A* ---
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        neighbors = [(0,1),(1,0),(0,-1),(-1,0)]
        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < ROWS and 0 <= neighbor[1] < COLS:
                if grid[neighbor[0]][neighbor[1]] == 1:
                    continue
                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return None

# --- Dibujo ---
def draw_grid():
    for r in range(ROWS):
        for c in range(COLS):
            color = WHITE
            if grid[r][c] == 1:
                color = BLACK
            pygame.draw.rect(win, color, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(win, GRAY, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    if start:
        pygame.draw.rect(win, BLUE, (start[1]*CELL_SIZE, start[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    if end:
        pygame.draw.rect(win, YELLOW, (end[1]*CELL_SIZE, end[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_path(path):
    for r, c in path:
        pygame.draw.rect(win, GREEN, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))

# --- Loop principal ---
running = True
path = []
while running:
    draw_grid()
    if path:
        draw_path(path)
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            r, c = y // CELL_SIZE, x // CELL_SIZE
            if not start:
                start = (r, c)
            elif not end:
                end = (r, c)
                path = astar(start, end)

pygame.quit()
