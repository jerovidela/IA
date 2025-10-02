# Librerías necesarias
import numpy as np                      # Para trabajar con matrices y operaciones numéricas
import matplotlib.pyplot as plt         # Para graficar la política óptima
import networkx as nx                   # Para construir y visualizar grafos (salas conectadas)
import random                           # Para elegir acciones aleatorias durante el aprendizaje
from sklearn.preprocessing import MinMaxScaler  # Para normalizar la matriz Q entre 0 y 1
import pandas as pd                     # Para mostrar resultados en forma de tabla


# Cada fila representa un estado (sala) y cada columna una posible acción (ir a otra sala)
# -1 significa que no se puede ir de un estado a otro
# 0 es una transición válida pero sin recompensa
# 100 es la recompensa por llegar al estado del TESORO

R = np.array([
    [-1,  0, -1,  0, -1, -1],  # 0
    [ 0, -1,  0, -1, -1, -1],  # 1
    [-1,  0, -1,  0,100, -1],  # 2
    [ 0, -1,  0, -1, -1,  0],  # 3
    [-1, -1,  0, -1,100,  0],  # 4 
    [-1, -1, -1,  0,100, -1],  # 5
])


# Parámetros
gamma = 0.9   # Factor de descuento: valora más las recompensas cercanas en el tiempo
alpha = 0.8   # Tasa de aprendizaje: cuánto se actualiza la Q cada vez
n_states = R.shape[0]  # Cantidad de estados (6 en este caso)


# Inicializamos Q
Q = np.zeros_like(R, dtype=float)  # Matriz Q, del mismo tamaño que R, inicializada en ceros

# Q-Learning
episodes = 10000  # Cantidad de episodios (iteraciones de entrenamiento)

for _ in range(episodes):
    state = random.randint(0, n_states - 1)  # Elegimos un estado inicial al azar
    possible_actions = np.where(R[state] >= 0)[0]  # Acciones posibles desde ese estado
    if len(possible_actions) == 0:
        continue  # Si no hay acciones válidas, salteamos

    action = random.choice(possible_actions)  # Elegimos una acción al azar
    next_possible = np.where(R[action] >= 0)[0]  # Acciones posibles desde el siguiente estado

    # Elegimos el máximo valor Q del siguiente estado (para la fórmula de actualización)
    max_q = max(Q[action, next_possible]) if len(next_possible) > 0 else 0

    # Fórmula de actualización Q-learning:
    # Q(s, a) = Q(s, a) + α * [ R(s, a) + γ * max(Q(s', a')) - Q(s, a) ]
    Q[state, action] = Q[state, action] + alpha * (R[state, action] + gamma * max_q - Q[state, action])

# Normalizar la matriz Q
# Para hacer más visual la política, normalizamos los valores entre 0 y 1
scaler = MinMaxScaler()
Q_norm = scaler.fit_transform(Q)

# Política óptima: mejor acción desde cada estado
# Para cada estado, elegimos la acción con mayor valor Q
policy = np.argmax(Q, axis=1)


# Creamos un grafo dirigido donde los nodos son las salas y las flechas las transiciones
G = nx.DiGraph()

# Etiquetas legibles para los nodos
labels = {0: "0 (robot)", 1: "1", 2: "2", 3: "3", 4: "4 (tesoro)", 5: "5"}

# Creamos todas las aristas posibles basadas en R (acciones válidas)
edges = [(i, j) for i in range(n_states) for j in range(n_states) if R[i][j] >= 0]

# Posiciones de los nodos para una mejor visualización
pos = {
    0: (0, 0),   # robot
    1: (0, 1),
    2: (1, 1),
    3: (1, 0),
    4: (2, 1),   # tesoro
    5: (2, 0)
}

plt.figure(figsize=(8, 6))
nx.draw_networkx_nodes(G, pos, node_size=800, node_color='lightblue')     # Nodos azules
nx.draw_networkx_labels(G, pos, labels, font_size=10)                     # Etiquetas de nodos

# Dibujamos sólo las transiciones que forman parte de la política óptima
policy_edges = [(s, policy[s]) for s in range(n_states) if R[s][policy[s]] != -1]
nx.draw_networkx_edges(G, pos, edgelist=policy_edges, edge_color='red', width=2, arrows=True)

plt.title("Política óptima aprendida con Q-Learning")
plt.axis('off')
plt.show()

import ace_tools as tools
tools.display_dataframe_to_user(
    name="Matriz Q Normalizada",
    dataframe=pd.DataFrame(Q_norm, columns=[f"A{i}" for i in range(n_states)])
)
