import pygame
import sys
import random
import math

# ======== Configuración inicial ========
WIDTH, HEIGHT = 300, 300
LINE_WIDTH = 5
CELL_SIZE = WIDTH // 3

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.init()
FONT = pygame.font.SysFont(None, 60)

# ======== Funciones básicas del Ta-te-ti ========
def draw_board(screen, board):
    screen.fill(WHITE)
    # Dibujar líneas
    for i in range(1, 3):
        pygame.draw.line(screen, BLACK, (0, CELL_SIZE*i), (WIDTH, CELL_SIZE*i), LINE_WIDTH)
        pygame.draw.line(screen, BLACK, (CELL_SIZE*i, 0), (CELL_SIZE*i, HEIGHT), LINE_WIDTH)
    # Dibujar X y O
    for i in range(9):
        row, col = divmod(i, 3)
        x = col * CELL_SIZE + CELL_SIZE // 2
        y = row * CELL_SIZE + CELL_SIZE // 2
        if board[i] == "X":
            text = FONT.render("X", True, BLACK)
            screen.blit(text, text.get_rect(center=(x, y)))
        elif board[i] == "O":
            text = FONT.render("O", True, BLACK)
            screen.blit(text, text.get_rect(center=(x, y)))
    pygame.display.flip()

def check_winner(board, player):
    win_states = [
        [0,1,2],[3,4,5],[6,7,8],  # filas
        [0,3,6],[1,4,7],[2,5,8],  # columnas
        [0,4,8],[2,4,6]           # diagonales
    ]
    return any(all(board[pos] == player for pos in line) for line in win_states)

def is_full(board):
    return all(cell != " " for cell in board)

def evaluate(board):
    if check_winner(board, "O"):
        return 1
    elif check_winner(board, "X"):
        return -1
    else:
        return 0

def neighbors(board, player):
    neigh = []
    for i in range(9):
        if board[i] == " ":
            new_board = board[:]
            new_board[i] = player
            neigh.append((new_board, i))
    return neigh

# ======== Recocido Simulado ========
def simulated_annealing(board, player, T_init=10, alpha=0.95, steps=50):
    current_board = board[:]
    current_eval = evaluate(current_board)
    move_index = None

    T = T_init
    for _ in range(steps):
        neighs = neighbors(current_board, player)
        if not neighs:
            break
        new_board, idx = random.choice(neighs)
        new_eval = evaluate(new_board)
        delta = new_eval - current_eval

        if delta > 0 or random.random() < math.exp(delta / T):
            current_board = new_board
            current_eval = new_eval
            move_index = idx

        T = max(T * alpha, 0.01)

    return move_index if move_index is not None else random.choice([i for i in range(9) if board[i] == " "])

# ======== Juego principal ========
def play_game(T_init):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ta-te-ti con Recocido Simulado")

    board = [" "] * 9
    turn = "X"  # humano empieza
    running = True
    game_over = False
    winner = None

    while running:
        draw_board(screen, board)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not game_over and turn == "X" and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                col = x // CELL_SIZE
                row = y // CELL_SIZE
                move = row * 3 + col
                if board[move] == " ":
                    board[move] = "X"
                    if check_winner(board, "X"):
                        game_over = True
                        winner = "Humano (X)"
                    elif is_full(board):
                        game_over = True
                        winner = "Empate"
                    else:
                        turn = "O"

        # Turno de la IA
        if not game_over and turn == "O":
            pygame.time.delay(500)
            move = simulated_annealing(board, "O", T_init=T_init)
            board[move] = "O"
            if check_winner(board, "O"):
                game_over = True
                winner = "IA (O)"
            elif is_full(board):
                game_over = True
                winner = "Empate"
            else:
                turn = "X"

        if game_over:
            draw_board(screen, board)
            pygame.time.delay(1000)
            screen.fill(WHITE)
            msg = FONT.render(f"Ganador: {winner}", True, BLACK)
            screen.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2)))
            pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        T_init = float(input("Temperatura inicial (recomendado 1 a 100): "))
        if T_init <= 0:
            print("Se usará temperatura por defecto (10).")
            T_init = 10
    except:
        T_init = 10

    play_game(T_init)