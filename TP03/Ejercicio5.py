import math
import random

# ======== Funciones básicas del Ta-te-ti ========

def print_board(board):
    print("\n")
    for i in range(3):
        print(" | ".join(board[i*3:(i+1)*3]))
        if i < 2:
            print("---------")
    print("\n")

def check_winner(board, player):
    win_states = [
        [0,1,2],[3,4,5],[6,7,8],  # filas
        [0,3,6],[1,4,7],[2,5,8],  # columnas
        [0,4,8],[2,4,6]           # diagonales
    ]
    return any(all(board[pos] == player for pos in line) for line in win_states)

def is_full(board):
    return all(cell != " " for cell in board)

# ======== Función de evaluación para la IA ========
def evaluate(board):
    if check_winner(board, "O"):
        return 1
    elif check_winner(board, "X"):
        return -1
    else:
        return 0

# ======== Vecinos: todas las jugadas posibles ========
def neighbors(board, player):
    neigh = []
    for i in range(9):
        if board[i] == " ":
            new_board = board[:]
            new_board[i] = player
            neigh.append((new_board, i))
    return neigh

# ======== Recocido Simulado para elegir jugada ========
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

        T = max(T * alpha, 0.01)  # enfriamiento

    return move_index if move_index is not None else random.choice([i for i in range(9) if board[i] == " "])

# ======== Juego principal ========
def play_game():
    print("Bienvenido al Ta-te-ti con IA (Recocido Simulado).")
    print("Elegí la temperatura inicial (rango recomendado: 1 a 100).")
    
    try:
        T_init = float(input("Temperatura inicial: "))
        if T_init <= 0:
            print("La temperatura debe ser positiva. Se usará 10 por defecto.")
            T_init = 10
    except:
        T_init = 10

    board = [" "] * 9
    turn = "X"  # humano empieza

    while True:
        print_board(board)

        if turn == "X":  # humano
            move = int(input("Elegí posición (0-8): "))
            if board[move] != " ":
                print("Casilla ocupada, probá otra.")
                continue
            board[move] = "X"
        else:  # IA
            print("Turno de la IA...")
            move = simulated_annealing(board, "O", T_init=T_init)
            board[move] = "O"

        # chequeo fin de partida
        if check_winner(board, turn):
            print_board(board)
            print(f"Ganó {turn}!")
            break
        if is_full(board):
            print_board(board)
            print("Empate!")
            break

        turn = "O" if turn == "X" else "X"

if __name__ == "__main__":
    play_game()
