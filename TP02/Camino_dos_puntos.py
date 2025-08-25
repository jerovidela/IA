import pygame
import heapq
import time

# Configuración
WIDTH, HEIGHT = 600, 600    # Dimensiones de la ventana
ROWS, COLS = 17, 17          # Filas y columnas de la cuadrícula
CELL_SIZE = WIDTH // COLS       # Tamaño de cada celda

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))  # Inicializar ventana
pygame.display.set_caption("Camino mas corto A*")   # Título de la ventana


grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]  # Crear cuadrícula vacía



# Obstáculos según la imagen
obstacles = [
   (2, 9), (3, 8), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (11, 7),
    (12, 8), (12, 9), (12, 10), (12, 11), (12, 11)
]                                   #Crea los obstáculos punto a punto (Revisar)
for r, c in obstacles:   # Agregar obstáculos a la cuadrícula
    grid[r][c] = 1

start, end = None, None

# --- Algoritmo A* ---
def heuristic(a, b):            # Heurística de Manhattan
    return abs(a[0] - b[0]) + abs(a[1] - b[1])      # Calcula la distancia Manhattan entre dos puntos

def astar(start, goal):             # Algoritmo A*
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:                             # Mientras haya nodos por explorar
        _, current = heapq.heappop(open_set)       # Obtiene el nodo con menor costo
        if current == goal:                        # Si se llega al objetivo....
            path = []                               # Lista para almacenar el camino
            while current in came_from:             # Retrocede por el camino
                path.append(current)                # Se agrega el nodo actual al camino
                current = came_from[current]        # Obtener el nodo anterior
            return path[::-1]                       # Retornar el camino invertido

        neighbors = [(0,1),(1,0),(0,-1),(-1,0)]     # Indica cuales son los mov válidos
        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < ROWS and 0 <= neighbor[1] < COLS:     # Verifica los límites de la cuadrícula
                if grid[neighbor[0]][neighbor[1]] == 1:             # Si es pared, se salta
                    continue
                tentative_g = g_score[current] + 1                  # Costo del movimiento
                # Si encontramos un camino más barato hacia 'neighbor'...
                if tentative_g < g_score.get(neighbor, float("inf")): 
                    came_from[neighbor] = current                    # Se guarda el nodo actual como el anterior
                    g_score[neighbor] = tentative_g                  # Se actualiza el costo g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)     # Se actualiza el costo f  (f = g + h)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))  # Se agrega el vecino a la lista abierta
    return None  # (Si no se encontró un camino)

# --- Dibujo ---
def draw_grid():
    for r in range(ROWS):
        for c in range(COLS):
            color = WHITE
            if grid[r][c] == 1:
                color = BLACK                   # Se dibujan los obstáculo
             # Rectángulo de la celda
            pygame.draw.rect(win, color, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            # Líneas de la cuadrícula
            pygame.draw.rect(win, GRAY, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    if start:
        # Celda inicio en azul (nota: (x,y) en pantalla = (col, fila))
        pygame.draw.rect(win, BLUE, (start[1]*CELL_SIZE, start[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    if end:
         # Celda fin en amarillo
        pygame.draw.rect(win, YELLOW, (end[1]*CELL_SIZE, end[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_path(path):
    if not path:
        return

    for i, (row, col) in enumerate(path):
        # Saltamos el primer nodo (inicio) y el último (destino),
        # para que sigan mostrándose con sus colores originales
        if (row, col) == start or (row, col) == end:
            continue

        # El último del camino lo pintamos amarillo
        if i == len(path) - 1:
            color = (255, 255, 0)  # Amarillo
        else:
            color = (0, 255, 0)    # Verde

        pygame.draw.rect(win, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# --- Loop principal ---
running = True
path = []
while running:
    draw_grid()          # Dibuja el tablero y (si existen) inicio/fin...
    if path:
        time.sleep(0.1)  # Pausa para visualizar el camino
        draw_path(path)
    pygame.display.update() # Actualiza la ventana

    for event in pygame.event.get():     # Procesa eventos de la ventana
        if event.type == pygame.QUIT:   # Cerrar ventana
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN: # Click del mouse
            x, y = pygame.mouse.get_pos()       # Posición en píxeles
            r, c = y // CELL_SIZE, x // CELL_SIZE   # Lo convierte a (fila, columna)
            if not start:
                start = (r, c)      # Primer click: fija el inicio
            elif not end:           # Segundo click: fija el final
                end = (r, c)
                path = astar(start, end)  # Llama a A* y guarda el camino resultante

pygame.quit()
# Fin del programa