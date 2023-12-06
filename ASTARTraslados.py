import heapq
import sys
import time

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
        'current_energy': 50,
        'ambulance': [],
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

        if goal_test_func(current_state, map_info):
            return current_state, current_path, current_cost  # Devuelve el costo actual

        explored.add(tuple(current_state))

        for action in actions_func(current_state, current_state['ambulance']):
            new_state = transition_func(current_state, action, current_state['ambulance'])
            new_cost = current_cost + cost_func(current_state, action, map_info)
            total_cost = new_cost + heuristic_func(new_state, map_info)
            new_path = current_path + [new_state]  # Actualiza el camino recorrido
            if tuple(new_state) not in explored:
                heapq.heappush(frontier, (total_cost, new_state, new_path))

    print("FRONTIER",frontier)
    print("new state:",new_state,"new cost",new_cost)
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


def goal_test(state, map_info): 
    # Verificar si todos los pacientes están en sus centros de atención y la ambulancia está en el estacionamiento
    contagious_patients_in_contagious_center = all(patient in state['treatment_centers']['CC'] for patient in map_info['contagious_locations'])
    non_contagious_patients_in_non_contagious_center = all(patient in state['treatment_centers']['CN'] for patient in map_info['patient_locations'] if patient not in map_info['contagious_locations'])
    ambulance_at_parking = state['current_location'] == map_info['parking_location']

    return contagious_patients_in_contagious_center and non_contagious_patients_in_non_contagious_center and ambulance_at_parking



def actions(state, ambulancia):
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
                # Verificar si la ambulancia tiene suficiente energía para realizar el movimiento
                required_energy = cost(state, ('MOVE', move), map_info)
                if state['current_energy'] >= required_energy:
                    # La ambulancia tiene suficiente energía, realizar el movimiento
                    # Reducir la energía disponible según el costo del movimiento
                    new_state = state.copy()
                    new_state['current_location'] = new_location
                    new_state['current_energy'] -= required_energy

                    # Verificar si hay pacientes en la nueva ubicación y recogerlos si es posible
                    patients_to_pickup = [patient for patient in map_info['patient_locations'] if
                                           patient == new_location]
                    if patients_to_pickup and len(ambulancia) < 10:
                        # Crear una acción que recoja a los pacientes en la nueva ubicación
                        pickup_action = ('PICKUP', patients_to_pickup)
                        possible_actions.append(pickup_action)
                        if any(patient in map_info['contagious_locations'] for patient in patients_to_pickup):
                            # Si hay pacientes contagiosos, ponerlos al final de la lista
                            ambulancia.extend(patients_to_pickup)
                        else:
                            # Si no hay contagiosos, ponerlos al principio de la lista
                            ambulancia = patients_to_pickup + ambulancia
                        map_info['patient_locations'].remove(patients_to_pickup)

                    # Verificar si estamos en un centro de contagiosos y en caso de tener pacientes contagiosos dejarlos
                    dejar_pacientes_contagiosos = [
                        centro_contagioso for centro_contagioso in map_info['treatment_centers']['CC'] if
                        new_location == centro_contagioso]
                    if dejar_pacientes_contagiosos and any(patient in ambulancia for patient in
                                                            map_info['contagious_locations']):
                        # Dejar pacientes contagiosos en las primeras dos plazas si es posible
                        pacientescc = ambulancia[:2]
                        if pacientescc:
                            dejar_action = ('DEJAR', pacientescc)
                            possible_actions.append(dejar_action)
                            ambulancia = ambulancia[2:]  # Quitar los pacientes contagiosos de la ambulancia

                            # Actualizar la ubicación de los pacientes en el mapa después de dejarlos en el centro
                            map_info['patient_locations'].extend(pacientescc)

                    # Agregar el movimiento como una acción
                    move_action = ('MOVE', move)
                    possible_actions.append(move_action)

        # Verificar si es necesario recargar y agregar la acción de recargar en el estacionamiento
        if state['current_energy'] < 50:
            recharge_action = ('RECHARGE', map_info['parking_location'])
            possible_actions.append(recharge_action)

        return possible_actions
    else:
        # Manejar el caso en el que 'current_location' no está presente en el estado
        print("Error: 'current_location' no está presente en el estado.")


def transition(state, action, ambulancia):
    action_type, action_value = action

    if action_type == 'MOVE':
        # Obtener el nuevo estado después de realizar un movimiento
        new_location = (
            state['current_location'][0] + action_value[0],
            state['current_location'][1] + action_value[1]
        )

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
    elif action_type == 'PICKUP':
         return perform_pickup(state, action_value, ambulancia, map_info)
    elif action_type == 'DEJAR':
        return perform_leave(state, action_value, ambulancia, map_info)
    elif action_type == 'RECHARGE':
        return perform_recharge(state, action_value, ambulancia, map_info)
    else:
        # Manejar otros tipos de acciones según sea necesario
        return state

def perform_pickup(state, action_value, ambulancia, map_info):
    new_state = state.copy()

    # Verificar la capacidad del vehículo antes de recoger a los pacientes
    if len(new_state['patients_on_board']) + len(action_value) <= 10:
        # Verificar si se están recogiendo pacientes contagiosos
        contagious_patients = [patient for patient in action_value if patient in map_info['contagious_locations']]

        if contagious_patients:
            # Si hay pacientes contagiosos, verificar si hay espacio en las plazas habilitadas
            if len(new_state['contagious_seats']) + len(contagious_patients) <= 2:
                new_state['patients_on_board'].extend(action_value)
                new_state['contagious_seats'].extend(contagious_patients)
            else:
                # No hay espacio en las plazas habilitadas, devolver el estado actual sin cambios
                return state
        else:
            # No hay pacientes contagiosos, recoger a todos los pacientes no contagiosos
            new_state['patients_on_board'].extend(action_value)

        # Actualizar el estado de la ambulancia (puedes ajustar según tus necesidades)
        new_state['ambulance_state'] = 'PICKING_UP'

        return new_state
    else:
        # No hay capacidad suficiente para recoger a todos los pacientes, devolver el estado actual sin cambios
        return state

def perform_leave(state, action_value, ambulancia, map_info):
    new_state = state.copy()

    # Remover a los pacientes dejados de las ubicaciones de pacientes y de la ambulancia
    for patient in action_value:
        if patient in new_state['patient_locations']:
            new_state['patient_locations'].remove(patient)
        if patient in new_state['patients_on_board']:
            new_state['patients_on_board'].remove(patient)

    # Actualizar el estado de la ambulancia (puedes ajustar según tus necesidades)
    new_state['ambulance_state'] = 'DROPPING_OFF'

    return new_state

def perform_recharge(state, action_value, ambulancia, map_info):
    new_state = state.copy()
    new_state['current_energy'] = 50  # Establecer la energía en la carga máxima
    new_state['current_location'] = action_value  # Mover la ambulancia al estacionamiento

    return new_state

def move_cost(new_location, map_info):
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

def cost(state, action, map_info):
    action_type, action_value = action

    if action_type == 'MOVE':
        # Obtener la ubicación después de realizar la acción
        new_location = (
            state['current_location'][0] + action_value[0],
            state['current_location'][1] + action_value[1]
        )

        return move_cost(new_location, map_info)
    elif action_type == 'RECHARGE':
        # Costo de recarga en el estacionamiento (0)
        return 0
    else:
        # Manejar otros tipos de acciones según sea necesario
        return float('inf')

"""
# Luego, puedes llamar al algoritmo A* con tus funciones específicas
initial_state = map_info.copy()
solution = a_star(initial_state, heuristic, goal_test, actions, transition, cost)

print("Solución encontrada:", solution)"""


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python ASTARTraslados.py <path mapa.csv> <num-h>")
        sys.exit(1)

    file_path = sys.argv[1]
    num_h = int(sys.argv[2])

    map_info = parse_map('mapa.csv')
    initial_state = map_info.copy()

    start_time = time.time()
    """solution = a_star(map_info, num_h)"""
    solution = a_star(initial_state, heuristic, goal_test, actions, transition, cost)
    print("Solución encontrada:", solution)
    end_time = time.time()
    print (end_time - start_time)

    """
    save_solution(solution, map_info, num_h)
    save_statistics(end_time - start_time, cost, plan_length, expanded_nodes, map_info, num_h)"""