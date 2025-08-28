import pygame
import sys
import random
import math
import time

# ======== Configuración inicial ========
WIDTH, HEIGHT = 300, 300
LINE_WIDTH = 5
CELL_SIZE = WIDTH // 3

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

pygame.init()
FONT = pygame.font.SysFont(None, 40)
SMALL_FONT = pygame.font.SysFont(None, 30)

# ======== Funciones básicas del Ta-te-ti ========
def draw_board(screen, board):
    screen.fill(WHITE)
    for i in range(1, 3):
        pygame.draw.line(screen, BLACK, (0, CELL_SIZE*i), (WIDTH, CELL_SIZE*i), LINE_WIDTH)
        pygame.draw.line(screen, BLACK, (CELL_SIZE*i, 0), (CELL_SIZE*i, HEIGHT), LINE_WIDTH)
    
    for i in range(9):
        row, col = divmod(i, 3)
        x = col * CELL_SIZE + CELL_SIZE // 2
        y = row * CELL_SIZE + CELL_SIZE // 2
        if board[i] == "X":
            text = FONT.render("X", True, BLUE)
            screen.blit(text, text.get_rect(center=(x, y)))
        elif board[i] == "O":
            text = FONT.render("O", True, RED)
            screen.blit(text, text.get_rect(center=(x, y)))
    
    pygame.display.flip()

def check_winner(board, player):
    win_states = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    return any(all(board[pos] == player for pos in line) for line in win_states)

def is_full(board):
    return all(cell != " " for cell in board)

def enhanced_evaluate(board):
    # Evaluación mejorada
    if check_winner(board, "O"): 
        return 1000  # victoria IA
    if check_winner(board, "X"): 
        return -1000  # derrota IA
    if is_full(board): 
        return 0  # empate

    score = 0
    lines = [
        [0,1,2],[3,4,5],[6,7,8],  # filas
        [0,3,6],[1,4,7],[2,5,8],  # columnas
        [0,4,8],[2,4,6]           # diagonales
    ]

    for line in lines:
        values = [board[i] for i in line]

        # Jugada ganadora inminente
        if values.count("O") == 2 and values.count(" ") == 1:
            score += 100  # Mayor prioridad a movimientos ganadores
        if values.count("X") == 2 and values.count(" ") == 1:
            score -= 90   # Bloquear al oponente es crucial

        # Posiciones intermedias
        if values.count("O") == 1 and values.count(" ") == 2:
            score += 5
        if values.count("X") == 1 and values.count(" ") == 2:
            score -= 4

    # Bonificación por centro (la posición más fuerte)
    if board[4] == "O":
        score += 50
    elif board[4] == "X":
        score -= 75

    # Bonificación por esquinas
    for i in [0, 2, 6, 8]:
        if board[i] == "O":
            score += 7
        elif board[i] == "X":
            score -= 5

    return score

def neighbors(board, player):
    neigh = []
    for i in range(9):
        if board[i] == " ":
            new_board = board[:]
            new_board[i] = player
            neigh.append((new_board, i))
    return neigh

# ======== Recocido Simulado Mejorado ========
def simulated_annealing(board, player, T_init=10, alpha=0.95, steps=500):
    current_board = board[:]
    current_eval = enhanced_evaluate(current_board)
    
    # Mejor estado global encontrado
    best_board = current_board[:]
    best_eval = current_eval
    best_move = None
    
    T = T_init
    
    for step in range(steps):
        # Generar vecinos (movimientos posibles)
        neighs = neighbors(current_board, player)
        if not neighs:
            break
        
        # Seleccionar un vecino aleatorio
        new_board, move_idx = random.choice(neighs)
        new_eval = enhanced_evaluate(new_board)
        
        # Calcular la diferencia de evaluación
        delta = new_eval - current_eval
        
        # Criterio de aceptación
        if delta > 0:
            # Siempre aceptar mejoras
            current_board, current_eval = new_board, new_eval
            # Actualizar el mejor global si es necesario
            if new_eval > best_eval:
                best_board, best_eval = new_board[:], new_eval
                best_move = move_idx
        else:
            # Aceptar empeoras con probabilidad basada en temperatura
            probability = math.exp(delta / T) if T > 0 else 0
            if random.random() < probability:
                current_board, current_eval = new_board, new_eval
        
        # Enfriar la temperatura
        T = max(T * alpha, 0.01)
    
    # Si encontramos un movimiento bueno, usarlo
    if best_move is not None:
        return best_move
    
    # Si no se encontró un movimiento, elegir aleatoriamente
    empty_cells = [i for i in range(9) if board[i] == " "]
    if empty_cells:
        return random.choice(empty_cells)
    
    return -1  # No hay movimientos posibles

# ======== Juego principal ========
def play_game(T_init, alpha=0.95, steps=500):  # Corregido: usar steps=500 consistentemente
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Ta-te-ti - Recocido Simulado (T={T_init}, Steps={steps})")

    board = [" "] * 9
    turn = "X"  # Jugador empieza
    running = True
    game_over = False
    winner = None

    while running:
        # Dibujar información de temperatura
        screen.fill(WHITE)
        info_text = SMALL_FONT.render(f"Temperatura: {T_init}", True, BLACK)
        screen.blit(info_text, (10, 10))
        steps_text = SMALL_FONT.render(f"Steps: {steps}", True, BLACK)
        screen.blit(steps_text, (10, 40))
        
        draw_board(screen, board)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if not game_over and turn == "X" and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                col = x // CELL_SIZE
                row = y // CELL_SIZE
                move = row * 3 + col
                
                if 0 <= move < 9 and board[move] == " ":
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
            pygame.time.delay(500)  # Pausa para ver el turno
            
            move = simulated_annealing(board, "O", T_init, alpha, steps)
            
            if move != -1:  # Si hay movimientos válidos
                board[move] = "O"
                
                if check_winner(board, "O"):
                    game_over = True
                    winner = "IA (O)"
                elif is_full(board):
                    game_over = True
                    winner = "Empate"
                else:
                    turn = "X"
            else:
                # No hay movimientos posibles
                game_over = True
                winner = "Empate"

        # Mostrar resultado final
        if game_over:
            draw_board(screen, board)
            pygame.time.delay(1000)
            
            # Pantalla de resultado
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 200))
            screen.blit(overlay, (0, 0))
            
            if winner == "Empate":
                msg = FONT.render("¡Empate!", True, BLACK)
            else:
                msg = FONT.render(f"¡{winner} gana!", True, BLACK)
            
            screen.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2 - 30)))
            
            restart_msg = SMALL_FONT.render("Clic para jugar otra vez", True, BLACK)
            screen.blit(restart_msg, restart_msg.get_rect(center=(WIDTH//2, HEIGHT//2 + 30)))
            
            pygame.display.flip()
            
            # Esperar clic para reiniciar
            waiting_for_click = True
            while waiting_for_click and running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting_for_click = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        waiting_for_click = False
                        return True  # Indicar que se debe reiniciar
    
    pygame.quit()
    return False

# ======== Función principal ========
def main():
    # Configuración de parámetros
    temperatures = [1, 10, 100]  # Diferentes temperaturas a probar
    current_temp_index = 0
    alpha = 0.95  # Factor de enfriamiento
    steps = 500   # Número de iteraciones (ahora consistentemente 500)
    
    restart = True
    while restart:
        try:
            # Solicitar temperatura al usuario
            T_init = float(input(f"Temperatura inicial ({temperatures[current_temp_index]} por defecto): ") or temperatures[current_temp_index])
            if T_init <= 0:
                print("La temperatura debe ser positiva. Usando valor por defecto.")
                T_init = temperatures[current_temp_index]
        except ValueError:
            print("Entrada no válida. Usando valor por defecto.")
            T_init = temperatures[current_temp_index]
        
        # Jugar con la temperatura seleccionada
        restart = play_game(T_init, alpha, steps)
        
        # Cambiar a la siguiente temperatura para la próxima partida
        if restart:
            current_temp_index = (current_temp_index + 1) % len(temperatures)
            print(f"\nPróxima partida con temperatura: {temperatures[current_temp_index]}")
            print("Observaciones:")
            if temperatures[current_temp_index] < 10:
                print("- Temperatura baja: la IA será más conservadora y predecible")
            else:
                print("- Temperatura alta: la IA explorará más movimientos, pudiendo ser más creativa o cometer más errores")

if __name__ == "__main__":
    main()