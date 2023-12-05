import heapq

def parse_map(map_str):
    with open(map_str, 'r') as archivo:
        lines = archivo.readlines()
    rows = len(lines)
    cols = len(lines[0].split(';'))

    map_data = []
    for line in lines:
        cells = line.strip().split(';')
        map_data.append(cells)

    patient_locations = []
    contagious_locations = []
    treatment_centers = {'CC': set(), 'CN': set()}
    parking_location = None
    obstacles = set()

    for i, line in enumerate(lines):
        cells = line.strip().split(';')
        for j, cell in enumerate(cells):
            if cell == 'N':
                patient_locations.append((i, j))
            elif cell == 'C':
                patient_locations.append((i, j))
                contagious_locations.append((i, j))
            elif cell == 'CC':
                treatment_centers['CC'].add((i, j))
            elif cell == 'CN':
                treatment_centers['CN'].add((i, j))
            elif cell == 'P':
                parking_location = (i, j)
            elif cell == 'X':
                obstacles.add((i, j))

    return {
        'rows': rows,
        'cols': cols,
        'map': map_data,
        'patient_locations': patient_locations,
        'contagious_locations': contagious_locations,
        'treatment_centers': treatment_centers,
        'parking_location': parking_location,
        'obstacles': obstacles,
        'current_location': parking_location
    }

# Ejemplo de uso
map_str = 'mapa.csv'

map_info = parse_map(map_str)
print(map_info)


def a_star(initial_state, heuristic_func, goal_test_func, actions_func, transition_func, cost_func):
    frontier = [(0, initial_state, [initial_state])]
    explored = set()
    map_info = parse_map(map_str)
    while frontier:
        current_cost, current_state, current_path = heapq.heappop(frontier)

        if goal_test_func(current_state, map_info['patient_locations'], map_info['parking_location']):
            return current_state, current_path, total_cost  # o cualquier otra cosa que necesites

        explored.add(tuple(current_state))

        for action in actions_func(current_state):
            new_state = transition_func(current_state, action)
            new_cost = current_cost + cost_func(current_state, action, map_info)
            total_cost = new_cost + heuristic_func(new_state, map_info)
            new_path = current_path + [new_state]  # Actualiza el camino recorrido
            if tuple(new_state) not in explored:
                heapq.heappush(frontier, (total_cost, new_state, new_path))

    return None  # Si no se encuentra una solución



# Definir funciones específicas para tu problema
def heuristic(state, map_info):
    # Obtener las ubicaciones de los pacientes que aún no han sido trasladados
    remaining_patients = set(map_info['patient_locations']) - set(state['treatment_centers']['CC']) - set(state['treatment_centers']['CN'])

    # Calcular la distancia manhattan total entre la ambulancia y los pacientes restantes
    total_distance = 0
    for patient in remaining_patients:
        total_distance += abs(state['current_location'][0] - patient[0]) + abs(state['current_location'][1] - patient[1])

    return total_distance


def goal_test(state, patient_locations, ambulance_parking):
    # Verificar si todos los pacientes están en sus centros de atención y la ambulancia está en el estacionamiento
    return all(patient in state['treatment_centers'].values() for patient in patient_locations) and state['current_location'] == ambulance_parking


def actions(state):
    # Obtener las acciones posibles para el estado actual
    possible_actions = []

    # Definir movimientos posibles (derecha, izquierda, arriba, abajo)
    movements = [(0, 1), (0, -1), (-1, 0), (1, 0)]

    # Obtener las acciones posibles para el estado actual
    current_location = state.get('current_location')  # Obtener la ubicación actual o None si no está presente
    if current_location is not None:
        for move in movements:
            new_location = (current_location[0] + move[0], current_location[1] + move[1])

            # Verificar si la nueva ubicación está dentro de los límites del mapa y no es un obstáculo
            if (
                0 <= new_location[0] < map_info['rows'] and
                0 <= new_location[1] < map_info['cols'] and
                new_location not in map_info['obstacles']
            ):
                possible_actions.append(move)

        return possible_actions
    else:
        # Manejar el caso en el que 'current_location' no está presente en el estado
        print("Error: 'current_location' no está presente en el estado.")

def transition(state, action):
    # Obtener el nuevo estado después de realizar una acción
    new_location = (state['current_location'][0] + action[0], state['current_location'][1] + action[1])

    # Verificar si la nueva ubicación está dentro de los límites del mapa y no es un obstáculo
    if (
        0 <= new_location[0] < map_info['rows'] and
        0 <= new_location[1] < map_info['cols'] and
        new_location not in map_info['obstacles']
    ):
        # Crear una copia del estado actual y actualizar la ubicación de la ambulancia
        new_state = state.copy()
        new_state['current_location'] = new_location

        return new_state
    else:
        # Si la nueva ubicación no es válida, devolver el estado actual sin cambios
        return state

def cost(state, action, map_info):
    # Obtener la ubicación después de realizar la acción
    new_location = (state['current_location'][0] + action[0], state['current_location'][1] + action[1])

    # Verificar si la nueva ubicación está dentro de los límites del mapa y no es un obstáculo
    if (
        0 <= new_location[0] < map_info['rows'] and
        0 <= new_location[1] < map_info['cols'] and
        new_location not in map_info['obstacles']
    ):
        # Obtener el tipo de celda en la nueva ubicación
        cell_type = map_info['map'][new_location[0]][new_location[1]]

        # Asignar costos según el tipo de celda
        if cell_type.isdigit():
            # Si es un número, utilizar ese valor como costo
            return int(cell_type)
        elif cell_type == 'N' or cell_type == 'C':
            # Costo 1 para pacientes no contagiosos y contagiosos
            return 1
        elif cell_type == 'P':
            # Costo 0 para el estacionamiento
            return 0
        else:
            # Otros tipos de celdas (por ejemplo, centros de atención) pueden tener costos específicos
            return 2  # Ajusta según tus necesidades
    else:
        # Si la nueva ubicación no es válida, devolver un costo alto
        return float('inf')

# Luego, puedes llamar al algoritmo A* con tus funciones específicas
initial_state = map_info.copy()
solution = a_star(initial_state, heuristic, goal_test, actions, transition, cost)

print("Solución encontrada:", solution)

"""
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python ASTARTraslados.py <path mapa.csv> <num-h>")
        sys.exit(1)

    file_path = sys.argv[1]
    num_h = int(sys.argv[2])

    map_info = parse_map('mapa.csv')

    start_time = time.time()
    solution = a_star(map_info, num_h)
    end_time = time.time()

    cost =  # Calcula el costo de la solución
    plan_length =  # Calcula la longitud del plan
    expanded_nodes =  # Calcula el número de nodos expandidos

    save_solution(solution, map_info, num_h)
    save_statistics(end_time - start_time, cost, plan_length, expanded_nodes, map_info, num_h)
"""