import pygame
import random
import sys

# --- Configuración ---
CELL_SIZE = 100
GRID_SIZE = 4
WINDOW_SIZE = CELL_SIZE * GRID_SIZE
FPS = 10

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
BROWN = (139, 69, 19)
RED = (200, 0, 0)
GRAY = (200, 200, 200)
BLUE = (50, 50, 255)

pygame.init()
font = pygame.font.SysFont(None, 24)
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 50))
pygame.display.set_caption("Wumpus World")

clock = pygame.time.Clock()

# --- Clases ---
class Game:
    def __init__(self):
        self.player_pos = [GRID_SIZE-1, 0]
        self.player_alive = True
        self.has_gold = False
        self.arrow = True

        # Inicializamos como None para evitar errores
        self.wumpus = None
        self.gold = None
        self.pits = []

        # Ahora sí, generamos posiciones
        self.wumpus = self.random_empty()
        self.gold = self.random_empty()
        self.pits = [self.random_empty() for _ in range(3)]

    
    def random_empty(self):
        while True:
            r, c = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if [r, c] != self.player_pos:
                if (self.wumpus is None or [r, c] != self.wumpus) and \
                (self.gold is None or [r, c] != self.gold) and \
                [r, c] not in self.pits:
                    return [r, c]

    
    def in_bounds(self, pos):
        return 0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE
    
    def percepts(self):
        r, c = self.player_pos
        adj = [(r-1,c),(r+1,c),(r,c-1),(r,c+1)]
        msgs = []
        for rr, cc in adj:
            if not self.in_bounds([rr,cc]): continue
            if [rr,cc] == self.wumpus: msgs.append("Stench")
            if [rr,cc] in self.pits: msgs.append("Breeze")
        if [r,c] == self.gold: msgs.append("Glitter")
        return msgs
    
    def move(self, dr, dc):
        nr, nc = self.player_pos[0]+dr, self.player_pos[1]+dc
        if self.in_bounds([nr,nc]):
            self.player_pos = [nr,nc]
            self.check_status()
    
    def check_status(self):
        if self.player_pos == self.wumpus:
            self.player_alive = False
        elif self.player_pos in self.pits:
            self.player_alive = False
        elif self.player_pos == self.gold:
            self.has_gold = True
    
    def draw(self):
        # fondo
        screen.fill(BLACK)
        # celdas
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                pygame.draw.rect(screen, GRAY, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
        # oro
        pygame.draw.circle(screen, GOLD, (self.gold[1]*CELL_SIZE+CELL_SIZE//2, self.gold[0]*CELL_SIZE+CELL_SIZE//2), 15)
        # pozos
        for pit in self.pits:
            pygame.draw.circle(screen, BROWN, (pit[1]*CELL_SIZE+CELL_SIZE//2, pit[0]*CELL_SIZE+CELL_SIZE//2), 20)
        # wumpus
        pygame.draw.circle(screen, RED, (self.wumpus[1]*CELL_SIZE+CELL_SIZE//2, self.wumpus[0]*CELL_SIZE+CELL_SIZE//2), 20)
        # jugador
        pygame.draw.rect(screen, BLUE, (self.player_pos[1]*CELL_SIZE+25, self.player_pos[0]*CELL_SIZE+25, 50, 50))
        # percepciones
        percept_text = " | ".join(self.percepts())
        msg = font.render(percept_text, True, WHITE)
        screen.blit(msg, (10, WINDOW_SIZE+10))
        
        pygame.display.flip()

# --- Main Loop ---
def main():
    game = Game()
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: game.move(-1,0)
                elif event.key == pygame.K_DOWN: game.move(1,0)
                elif event.key == pygame.K_LEFT: game.move(0,-1)
                elif event.key == pygame.K_RIGHT: game.move(0,1)
        
        game.draw()
        
        if not game.player_alive:
            print("Game Over!")
            running = False
    
    pygame.quit()

if __name__ == "__main__":
    main()
