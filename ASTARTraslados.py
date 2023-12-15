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



def a_star(pos_inicial, heuristic_func, goal_test_func, actions_func, transition_func, cost_func, map_info):
    frontier = [(0, pos_inicial, [initial_state])]
    #print("initial_statee4grgwrgtrtg", initial_state)
    explored = []
    #print("hola")
    while frontier:
        current_cost, pos_actual, current_path = heapq.heappop(frontier)
        #print("pos actual", pos_actual)
        #print("pos_inicial_original", pos_inicial)
        if goal_test_func(map_info):
            #print("ENTREEEEERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
            return pos_actual, current_path, current_cost  # Devuelve el costo actual
        
        #print("antes explored:", explored)
        if pos_actual not in explored:
            explored.append(pos_actual)
        #print("despues del explored:", explored)
        #print("CURRENT_STATE", current_state)
        #print("pos actual452352345423", pos_actual)
        state, actions = actions_func(pos_actual, map_info)
        explored.append(state)
        for action in actions:
            nuevo_estado, map_info = transition_func(state, action, map_info["ambulance"], current_path)
            new_cost = current_cost + cost_func(state, action, map_info)
            total_cost = new_cost + heuristic_func( map_info)
            new_path = current_path + [nuevo_estado]  # Actualiza el camino recorrido
            
            print("Dora la exploradora:", explored)
            if tuple(nuevo_estado) not in explored:
                
                print("Dora la encontró", explored)
                #print("tuputostado", state)
                #print("tuputafrontera: ", frontier)
                heapq.heappush(frontier, (total_cost, nuevo_estado, new_path))
                #print("new state:",nuevo_estado,"\n")
            else:
                #comprueba si el coste es menor al que tenemos guardado en frontier
                for state in frontier:
                    if state[1] == nuevo_estado and total_cost < state[0]:
                        print("entreaqi")
                        frontier.remove(state)
                        #print("nuevo_estado:", nuevo_estado)
                        heapq.heappush(frontier, (total_cost, nuevo_estado, new_path))
                        #print("new state:",new_state,"\n")
    
    return None  # Si no se encuentra una solución


def heuristic(map_info):
    # Obtener las ubicaciones de los pacientes que aún no han sido trasladados
    remaining_patients = set(map_info['patient_locations']) - set(map_info['treatment_centers']['CC']) - set(map_info['treatment_centers']['CN'])

    # Calcular la distancia manhattan total entre la ambulancia y los pacientes restantes
    total_distance = 0
    for patient in remaining_patients:
        total_distance += abs(map_info['current_location'][0] - patient[0]) + abs(map_info['current_location'][1] - patient[1])

    return total_distance


def goal_test(map_info): 
    # Verificar si todos los pacientes están en sus centros de atención y la ambulancia está en el estacionamiento
    contagious_patients_in_contagious_center = all(patient in map_info['treatment_centers']['CC'] for patient in map_info['contagious_locations'])
    non_contagious_patients_in_non_contagious_center = all(patient in map_info['treatment_centers']['CN'] for patient in map_info['patient_locations'] if patient not in map_info['contagious_locations'])
    ambulance_at_parking = map_info['current_location'] == map_info['parking_location']

    return contagious_patients_in_contagious_center and non_contagious_patients_in_non_contagious_center and ambulance_at_parking



def actions(state, map_info):
    #print("skkfnmnfgeakorfgnaoe\n",state)
    # Obtener las acciones posibles para el estado actual
    possible_actions = []

    # Definir movimientos posibles (derecha, izquierda, arriba, abajo)
    movements = [(0, 1), (0, -1), (-1, 0), (1, 0)]

    # Obtener las acciones posibles para el estado actual
    current_location = state  # Obtener la ubicación actual o None si no está presente
    if current_location is not None:
        for move in movements:
            print("pos\n", current_location)
            new_location = current_location[0] + move[0], current_location[1] + move[1]
            print("mimov\n", new_location)
            # Verificar si la nueva ubicación está dentro de los límites del mapa y no es un obstáculo
            if (
                0 <= new_location[0] < map_info['rows'] and
                0 <= new_location[1] < map_info['cols'] and
                new_location not in map_info['obstacles']
            ):
                print("columnas",map_info['cols'])
                # Verificar si la ambulancia tiene suficiente energía para realizar el movimiento
                required_energy = cost(state, ('MOVE', move), map_info)
                if map_info['current_energy'] >= required_energy:
                    # La ambulancia tiene suficiente energía, realizar el movimiento
                    # Reducir la energía disponible según el costo del movimiento
                    new_state = map_info.copy()
                    new_state['current_location'] = new_location
                    state = new_location
                    #print("reuired energy",required_energy)
                    new_state['current_energy'] -= required_energy
                    #print("energy",new_state['current_energy'])

                    # Verificar si hay pacientes en la nueva ubicación y recogerlos si es posible
                    patients_to_pickup = [patient for patient in map_info['patient_locations'] if
                                           patient == new_location]

                    if patients_to_pickup and len(map_info["ambulance"]) < 10:
                        # Crear una acción que recoja a los pacientes en la nueva ubicación
                        pickup_action = ('PICKUP', patients_to_pickup)
                        possible_actions.append(pickup_action)
                        if any(patient in map_info['contagious_locations'] for patient in patients_to_pickup):
                            # Si hay pacientes contagiosos, ponerlos al final de la lista
                            map_info["ambulance"].extend(patients_to_pickup)
                        else:
                            # Si no hay contagiosos, ponerlos al principio de la lista
                            map_info["ambulance"] = patients_to_pickup + map_info["ambulance"]
                        #print("p:",patients_to_pickup)
                        for patient in patients_to_pickup:
                            if patient in map_info['patient_locations']:
                                    map_info['patient_locations'].remove(patient)


                    # Verificar si estamos en un centro de contagiosos y en caso de tener pacientes contagiosos dejarlos
                    dejar_pacientes_contagiosos = [
                        centro_contagioso for centro_contagioso in map_info['treatment_centers']['CC'] if
                        new_location == centro_contagioso]
                    if dejar_pacientes_contagiosos and any(patient in map_info["ambulance"] for patient in
                                                            map_info['contagious_locations']):
                        # Dejar pacientes contagiosos en las primeras dos plazas si es posible
                        pacientescc = map_info["ambulance"][:2]
                        if pacientescc:
                            dejar_action = ('DEJAR', pacientescc)
                            possible_actions.append(dejar_action)
                            map_info["ambulance"] = map_info["ambulance"][2:]  # Quitar los pacientes contagiosos de la ambulancia

                            # Actualizar la ubicación de los pacientes en el mapa después de dejarlos en el centro
                            map_info['patient_locations'].extend(pacientescc)

                    # Agregar el movimiento como una acción
                    move_action = ('MOVE', move)
                    possible_actions.append(move_action)
                    # Verificar si es necesario recargar y agregar la acción de recargar en el estacionamiento
                    if map_info['current_energy'] < 1:
                        recharge_action = ('RECHARGE', map_info['parking_location'])
                        possible_actions.append(recharge_action)
            else:
                # Manejar el caso en el que 'current_location' no está presente en el estado
                print("Error: 'current_location' no está presente en el estado.")       
            return state, None
        
    
        

def transition(state, action, ambulancia, current_path):
    #print("yatusabe_stado",state)
    if action == None:
        return current_path[-1], map_info
    print("Transition - Action:", action)
    action_type, action_value = action

    if action_type == 'MOVE':
        # Obtener el nuevo estado después de realizar un movimiento
        #print("estadobrrr", state)
        new_location = (
            state[0] + action_value[0],
            state[1] + action_value[1]
        )

        # Verificar si la nueva ubicación está dentro de los límites del mapa y no es un obstáculo
        #print("Mueres o klk")
        if (0 <= new_location[0] < map_info['rows'] and
            0 <= new_location[1] < map_info['cols'] and
            new_location not in map_info['obstacles']):

            # Crear una copia del estado actual y actualizar la ubicación de la ambulancia
            new_state = map_info.copy()
            new_state['current_location'] = new_location
            state = new_location
            #print("movendome")
            return state, new_state
        else:
            # Si la nueva ubicación no es válida, devolver el estado actual sin cambios
            print("me sali we", state)
            #necesitamos pasarle el estado anterior
            print("currentpath",current_path[-1])
            return current_path[-1], map_info
    elif action_type == 'PICKUP':
         print("Performing Pickup")
         return state, perform_pickup(state, action_value, ambulancia, map_info)
    elif action_type == 'DEJAR':
        print("Performing Leave")
        return state, perform_leave(state, action_value, ambulancia, map_info)
    elif action_type == 'RECHARGE':
        print("Performing Recharge")
        return state, perform_recharge(state, action_value, ambulancia, map_info)
    else:
        # Manejar otros tipos de acciones según sea necesario
        print("Unknown action type:", action_type)
        return state, map_info

def perform_pickup(state, action_value, ambulancia, map_info):
    new_state = map_info.copy()

    # Verificar la capacidad del vehículo antes de recoger a los pacientes
    if len(new_state['ambulance']) + len(action_value) <= 10:
        # Verificar si se están recogiendo pacientes contagiosos
        contagious_patients = [patient for patient in action_value if patient in map_info['contagious_locations']]

        if contagious_patients:
            # Si hay pacientes contagiosos, verificar si hay espacio en las plazas habilitadas
            if len(new_state['contagious_seats']) + len(contagious_patients) <= 2:
                new_state['patients_on_board'].extend(action_value)
                new_state['contagious_seats'].extend(contagious_patients)
            else:
                # No hay espacio en las plazas habilitadas, devolver el estado actual sin cambios
                return new_state
        else:
            # No hay pacientes contagiosos, recoger a todos los pacientes no contagiosos
            new_state['ambulance'].extend(action_value)

        # Actualizar el estado de la ambulancia (puedes ajustar según tus necesidades)
        new_state['ambulance'] = 'PICKING_UP'

        return new_state
    else:
        # No hay capacidad suficiente para recoger a todos los pacientes, devolver el estado actual sin cambios
        return new_state

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
        #print("cell_type",cell_type)
        # Asignar costos según el tipo de celda
        if cell_type.isdigit():
            # Si es un número, utilizar ese valor como costo
            return int(cell_type)
        elif cell_type == 'N' or cell_type == 'C' or cell_type == 'CN' or cell_type == 'CC':
            # Costo 1 para pacientes no contagiosos y contagiosos
            return 1
        else: 
            #cell_type == 'P':
            # Costo 0 para el estacionamiento
            return 0
    else:
        # Si la nueva ubicación no es válida, devolver un costo alto
        return float('inf')

def cost(state, action, map_info):
    action_type, action_value = action
    #print("action_type",action_type)
    if action_type == 'MOVE':
        # Obtener la ubicación después de realizar la acción
        new_location = (
            state[0] + action_value[0],
            state[1] + action_value[1]
        )
        #print("new_location",new_location)
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

#print("Solución encontrada:", solution)"""


if __name__ == "__main__":
    if len(sys.argv) != 3:
        #print("Uso: python ASTARTraslados.py <path mapa.csv> <num-h>")
        sys.exit(1)
    #print("primer")
    file_path = sys.argv[1]
    num_h = int(sys.argv[2])

    map_info = parse_map('mapa-2.csv')
    initial_state = map_info["current_location"]
    #print("Estado inicial",initial_state)
    start_time = time.time()
    """solution = a_star(map_info, num_h)"""
    solution = a_star(initial_state, heuristic, goal_test, actions, transition, cost, map_info)
    print("Solución encontrada:", solution)
    end_time = time.time()
    #print (end_time - start_time)

    """
    save_solution(solution, map_info, num_h)
    save_statistics(end_time - start_time, cost, plan_length, expanded_nodes, map_info, num_h)"""