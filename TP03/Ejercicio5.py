import pygame
import sys
import random
import math

# ======== Configuración inicial ========
WIDTH, HEIGHT = 300, 300
LINE_WIDTH = 5          # Grosor de las líneas del tablero
CELL_SIZE = WIDTH // 3      # Tamaño de cada celda

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.init()
FONT = pygame.font.SysFont(None, 60)        # Fuente para dibujar X y O

# ======== Funciones básicas del Ta-te-ti ========
def draw_board(screen, board):
    screen.fill(WHITE)
    # Dibujar líneas horizontales y verticales
    for i in range(1, 3):
        pygame.draw.line(screen, BLACK, (0, CELL_SIZE*i), (WIDTH, CELL_SIZE*i), LINE_WIDTH)
        pygame.draw.line(screen, BLACK, (CELL_SIZE*i, 0), (CELL_SIZE*i, HEIGHT), LINE_WIDTH)
    # Dibujar X y O en las celdas
    for i in range(9):
        row, col = divmod(i, 3)
        # Calcula coordenadas centrales de la celda
        x = col * CELL_SIZE + CELL_SIZE // 2
        y = row * CELL_SIZE + CELL_SIZE // 2
         # Dibuja X si la celda contiene "X"
        if board[i] == "X":
            text = FONT.render("X", True, BLACK)
            screen.blit(text, text.get_rect(center=(x, y)))
         # Dibuja O si la celda contiene "O"
        elif board[i] == "O":
            text = FONT.render("O", True, BLACK)            #Crea texto "X" en negro
            screen.blit(text, text.get_rect(center=(x, y)))     # Dibuja texto centrado
    pygame.display.flip()           # Actualiza la pantalla

def check_winner(board, player):
    
    
     # Todas las combinaciones ganadoras posibles (filas, columnas, diagonales)
    win_states = [
        [0,1,2],[3,4,5],[6,7,8],  # filas
        [0,3,6],[1,4,7],[2,5,8],  # columnas
        [0,4,8],[2,4,6]           # diagonales
    ]
    return any(all(board[pos] == player for pos in line) for line in win_states)   # Verifica si el jugador o la IA han ganado

def is_full(board):
    return all(cell != " " for cell in board) #Esta parte retorna un true si hay un empate

def evaluate(board):        #Evalúa si gano la IA, si gano el jugador, o si hay empate
    if check_winner(board, "O"):
        return 1
    elif check_winner(board, "X"):
        return -1
    else:
        return 0

def neighbors(board, player):   #Genera tableros vecinos: todos los posibles movimientos legales del jugador actual.
    neigh = []                  # Lista para almacenar los estados vecinos
     # Itera por todas las celdas del tablero (0-8)
    for i in range(9):
        if board[i] == " ":                 # Si la celda está vacía
            new_board = board[:]            # Crea una copia del tablero actual
            new_board[i] = player           # Realiza el movimiento del jugador
            neigh.append((new_board, i))    # Agrega el nuevo estado y el índice del movimiento
    return neigh

# ======== Recocido Simulado ========
def simulated_annealing(board, player, T_init=10, alpha=0.95, steps=50):
    
    """
    Algoritmo de Recocido Simulado para encontrar el mejor movimiento
    board: estado actual del tablero
    player: jugador que realiza el movimiento (siempre "O" para la IA)
    T_init: temperatura inicial (controla la exploración inicial)
    alpha: factor de enfriamiento (0-1, controla la reducción de temperatura)
    steps: número de iteraciones del algoritmo
    return: índice del movimiento seleccionado
    """
    current_board = board[:]            # Copia del tablero actual (estado inicial)
    current_eval = evaluate(current_board)      # Evaluación del estado inicial
    move_index = None                       # Almacena el índice del movimiento seleccionado

    T = T_init                                  # Inicializa la temperatura
     # Bucle principal del algoritmo (steps iteraciones)
    for _ in range(steps):
        neighs = neighbors(current_board, player)       # Genera movimientos posibles
        if not neighs:                                   #Si no hay movimientos posibles, termina
            break
        # Selecciona un movimiento aleatorio de los disponibles
        new_board, idx = random.choice(neighs)
        new_eval = evaluate(new_board)              #Evalúa el nuevo estado
        delta = new_eval - current_eval            # Calcula la diferencia de evaluación (mejora o empeora)
        
        
        # Criterio de aceptación:
        # - Siempre acepta si mejora (delta > 0)
        # - Acepta con probabilidad exp(delta/T) si empeora (permite exploración)
        if delta > 0 or random.random() < math.exp(delta / T):
            current_board = new_board       # Actualiza el estado actual
            current_eval = new_eval         # Actualiza la evaluación
            move_index = idx                # Guarda el movimiento aceptado

        T = max(T * alpha, 0.01)            # Reduce la temperatura (enfriamiento), con mínimo 0.01
        
 # Retorna el movimiento seleccionado o un movimiento aleatorio válido si no se encontró ninguno
    return move_index if move_index is not None else random.choice([i for i in range(9) if board[i] == " "]) #

# ======== Juego principal ========
def play_game(T_init):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ta-te-ti con Recocido Simulado")

    board = [" "] * 9
    turn = "X"  # Turno inicial: jugador ("X") empieza
    running = True      # Controla si el juego está activo
    game_over = False   # Indica si el juego ha terminado
    winner = None       # Almacena el ganador ("Humano", "IA", o "Empate")

    while running:
        draw_board(screen, board)
 # Procesa eventos (clic del mouse, cierre de ventana, etc.)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:       # Si el usuario cierra la ventana
                running = False                 # Termina el juego
# Turno del jugador: detecta clic del mouse
            if not game_over and turn == "X" and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos            # Obtiene coordenadas del clic
                col = x // CELL_SIZE            # Calcula columna (0-2)
                row = y // CELL_SIZE            # Calcula fila (0-2)
                move = row * 3 + col            # Convierte a índice lineal (0-8)
                if board[move] == " ":          # Si la celda está vacía
                    board[move] = "X"           # Coloca "X" (movimiento humano)
                    
     # Verifica si el humano ganó
                    if check_winner(board, "X"):
                        game_over = True
                        winner = "Humano (X)"
                    elif is_full(board):  # Verifica si hay empate
                        game_over = True
                        winner = "Empate"
                    else:                   # Cambia turno a la IA
                        turn = "O"

        # Turno de la IA
        if not game_over and turn == "O":
            pygame.time.delay(500)         # Pequeña pausa para ver el movimiento
            
            # La IA decide su movimiento usando Recocido Simulado
            move = simulated_annealing(board, "O", T_init=T_init)
            board[move] = "O"           # Coloca "O"
            if check_winner(board, "O"):    # Verifica si la IA ganó
                game_over = True
                winner = "IA (O)"
            elif is_full(board):    # Verifica si hay empate
                game_over = True
                winner = "Empate"
            else:
                turn = "X"          # Cambia turno al humano
# Si el juego terminó, muestra el resultado
        if game_over:
            draw_board(screen, board)
            pygame.time.delay(1000)
            screen.fill(WHITE)
            msg = FONT.render(f"Ganador: {winner}", True, BLACK)
            screen.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2)))
            pygame.display.flip()

    pygame.quit()
    sys.exit()
# Punto de entrada del programa
if __name__ == "__main__":
    try:
        # Solicita temperatura inicial al usuario
        T_init = float(input("Temperatura inicial (recomendado 1 a 100): "))
        if T_init <= 0:         # Valida
            print("Se usará temperatura por defecto (10).")
            T_init = 10
    except:
        T_init = 10
 # Inicia el juego con la temperatura especificada
    play_game(T_init)