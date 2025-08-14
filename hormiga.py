import pygame
import random

GRID_SIZE = 100
CELL_SIZE = 6


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ANT_COLOR = (255, 0, 0)

DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

pygame.init()
screen = pygame.display.set_mode((GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE))
pygame.display.set_caption("Hormiga de Langton")

grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
dir_idx = random.randint(0, 3)

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if grid[y][x] == 0:
        grid[y][x] = 1
        dir_idx = (dir_idx + 1) % 4
    else:
        grid[y][x] = 0
        dir_idx = (dir_idx - 1) % 4

    dx, dy = DIRECTIONS[dir_idx]
    x = (x + dx) % GRID_SIZE
    y = (y + dy) % GRID_SIZE

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            color = WHITE if grid[row][col] == 0 else BLACK
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    pygame.draw.rect(screen, ANT_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    pygame.display.flip()

pygame.quit()
