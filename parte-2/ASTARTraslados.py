import heapq
import time
import sys
import networkx as nx



map_info = []
nodos_expandidos = 0

#Funcion que obtiene los valores del mapa
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
    non_contagious_locations = []
    mapa = []
    treatment_centers_cc = []
    treatment_centers_cn = []
    parking_location = None
    obstacles = set()

    for i, line in enumerate(lines):
        cells = line.strip().split(';')
        mapa.append([])
        for j, cell in enumerate(cells):
            mapa[i].append(cell)
            if cell == 'N':
                patient_locations.append((i, j))
                non_contagious_locations.append((i,j))
            elif cell == 'C':
                patient_locations.append((i, j))
                contagious_locations.append((i, j))
            elif cell == 'CC':
                treatment_centers_cc.append((i, j))
            elif cell == 'CN':
                treatment_centers_cn.append((i, j))
            elif cell == 'P':
                parking_location = (i, j)
            elif cell == 'X':
                obstacles.add((i, j))

    return {
        'mapa':mapa,
        'rows': rows,
        'cols': cols,
        'map': map_data,
        'patient_locations': patient_locations,
        'contagious_locations': contagious_locations,
        'non_contagious_locations': non_contagious_locations,
        'treatment_centers_cc': treatment_centers_cc,
        'treatment_centers_cn': treatment_centers_cn,
        'parking_location': parking_location,
        'obstacles': obstacles,
        'current_energy': 50,
        'ambulance': [],
        'current_location': parking_location
    }

# Encontrar la posición de inicial en el mapa en caso de haber dos parkings coge la primera P y si no hay comienza en el (0,0)
def lugar_inicio(mapa):
    for i in range(len(mapa)):
        for j in range(len(mapa[0])):
            if mapa[i][j] == "P":
                inicio = (i, j)
                return inicio
    print("No hay parkings en el mapa")
    return None

#función para calcular el Minimum Spanning k-Trees
def calcular_mst_k(aristas, k):
    # Creamos un grafo no dirigido ponderado
    grafo = nx.Graph()

    # Agregamos aristas al grafo con sus respectivos pesos
    for arista, peso in aristas.items():
        grafo.add_edge(arista[0], arista[1], weight=peso)

    # Inicializamos una lista para almacenar los MST-k
    mst_k_list = []

    # Calculamos k MST utilizando el algoritmo de Kruskal
    for _ in range(k):
        mst_k = nx.minimum_spanning_tree(grafo, algorithm='kruskal')
        mst_k_list.append(mst_k)

        # Removemos las aristas del MST-k actual del grafo para calcular el siguiente
        for edge in mst_k.edges:
            grafo.remove_edge(edge[0], edge[1])

    return mst_k_list

#función para calcular las aristas del grafo
def calcular_aristas(estado,mapa):
    aristas = {}

    # las ubicaciones relevantes del estado actual
    ubicacion_vehiculo = estado.ubicacion_vehiculo
    pacientes_sin_trasladar = estado.pacientes_sin_trasladar

    # Considera la ubicación del vehículo como parte del grafo
    nodos = [ubicacion_vehiculo] + pacientes_sin_trasladar

    # Calcula las aristas entre todos los nodos posibles
    for i in range(len(nodos)):
        for j in range(i + 1, len(nodos)):
            nodo_a, nodo_b = nodos[i], nodos[j]

            # Supongamos que la función costo_entre_estados devuelve el costo entre dos ubicaciones
            costo = costo_entre_estados(nodo_b,mapa)
            
            # Añade la arista al diccionario de aristas
            aristas[(nodo_a, nodo_b)] = costo

    return aristas


# Función de heurística utilizando MST-k
def heuristica_mst_k(estado_actual,mapa):
    aristas = calcular_aristas(estado_actual,mapa)
    mst_k_costo = calcular_mst_k(aristas, k=1)[0]  # Tomar el primer MST-k de la lista
    
    # Obtener las aristas del grafo y sumar sus pesos
    costo_total_mst_k = sum(d['weight'] for u, v, d in mst_k_costo.edges(data=True)) * 0.5
    
    return costo_total_mst_k

# Función de heurística teniendo en cuenta cuantos pacientes quedan por recoger
def heuristica_pacientes_sin_trasladar(estado_actual):
    # Cantidad total de pacientes sin trasladar
    pacientes_sin_trasladar = len(estado_actual.pacientes_sin_trasladar)

    # Ponderación del factor
    peso_pacientes = 0.5

    # Combinamos los factores con la ponderación
    heuristica = (peso_pacientes * pacientes_sin_trasladar)

    return heuristica

# Clase para representar el estado del problema
class Estado:
    def __init__(self, ubicacion_vehiculo, pacientes_sin_trasladar, energia_restante,plazas_vehiculo,paciente_vehiculo):
        self.ubicacion_vehiculo = ubicacion_vehiculo    # Se guarda la posicion actual del vehiculo
        self.pacientes_sin_trasladar = pacientes_sin_trasladar # Lista con los pacientes por recoger
        self.energia_restante = energia_restante    # Valor de la energia que tiene la ambulancia
        self.plazas_vehiculo = plazas_vehiculo  # Lista que rastrea el tipo de paciente en cada plaza
        self.paciente_vehiculo = paciente_vehiculo # Lista que guarda la posicion de los pacientes de la ambulancia

    def __lt__(self, other):
        # Define la comparación en base a el costo total
        return self.costo_total < other.costo_total if hasattr(self, 'costo_total') and hasattr(other, 'costo_total') else False
    
    def __hash__(self):
        # Utiliza una tupla que incluye la ubicación del vehículo, la lista de pacientes sin trasladar y la energía restante.
        return hash((self.ubicacion_vehiculo, tuple(self.pacientes_sin_trasladar), self.energia_restante))

    def __eq__(self, other):
        # Dos objetos son iguales si tienen la misma ubicación del vehículo, la misma lista de pacientes sin trasladar  y los mismos pacientes en la ambulancia.
        return (
            self.ubicacion_vehiculo == other.ubicacion_vehiculo and
            self.pacientes_sin_trasladar == other.pacientes_sin_trasladar and
            self.plazas_vehiculo == other.plazas_vehiculo and
            self.paciente_vehiculo == other.paciente_vehiculo
        )

    def __str__(self):
        # Devuelve una cadena formateada que incluye la ubicación del vehículo, el tipo de celda en esa ubicación y la energía restante.
        return f"({self.ubicacion_vehiculo[0] + 1},{self.ubicacion_vehiculo[1] + 1}):{map_info['mapa'][self.ubicacion_vehiculo[0]][self.ubicacion_vehiculo[1]]}:{self.energia_restante}"


# Implementación del algoritmo A* con MST-k
def a_estrella(mapa, estado_inicial,nombre_archivo, n_heuristica):

    cola_prioridad = [(0, estado_inicial, [estado_inicial.ubicacion_vehiculo])]  # (costo_total, estado, camino)
    visitados = set()
    global nodos_expandidos

    while cola_prioridad:
        costo_actual, estado_actual, camino = heapq.heappop(cola_prioridad)
        nodos_expandidos += 1
        if mapa[estado_actual.ubicacion_vehiculo[0]][estado_actual.ubicacion_vehiculo[1]] == 'P':
            estado_actual.energia_restante = 50

        if estado_actual in visitados:
            continue
            
        visitados.add(estado_actual)

        # Verificar si alcanzamos el estado objetivo
        if es_estado_objetivo(mapa, estado_actual):
            imprimir_output(mapa, camino, nombre_archivo)
            return costo_actual, camino, nodos_expandidos

        # Generar sucesores
        sucesores = generar_sucesores(mapa, estado_actual)

        for sucesor in sucesores:
            costo_sucesor = costo_actual + costo_entre_estados(sucesor.ubicacion_vehiculo, mapa)

            if n_heuristica == 1:
                heuristica_sucesor = heuristica_pacientes_sin_trasladar(sucesor)

            elif n_heuristica == 2:
                heuristica_sucesor = heuristica_mst_k(sucesor,mapa)

            elif n_heuristica == 3: 
                #Heuristica que se basa en utilizar la heruistica mas rentable en cada momento
                heuristica_sucesor = max(heuristica_mst_k(sucesor,mapa), heuristica_pacientes_sin_trasladar(sucesor))
            else:
                heuristica_sucesor = 0
            costo_total_sucesor = costo_sucesor + heuristica_sucesor
            if not sucesor in visitados:
                heapq.heappush(cola_prioridad, (costo_total_sucesor, sucesor, camino + [sucesor.ubicacion_vehiculo]))


    return costo_actual, None, nodos_expandidos  # No se encontró una solución

# Funcion objetivo
def es_estado_objetivo(mapa,estado):
    #Cuando la ambulancia este vacia en el parking y no queden pacientes por recoger llegamos al estado final

    if ((estado.ubicacion_vehiculo == lugar_inicio(mapa)) and
        (len(estado.pacientes_sin_trasladar) == 0) and
        (len(estado.paciente_vehiculo) == 0) and
        (estado.energia_restante == 50)):
        return True
    return False


# Funcion que genera los nodos sucesores
def generar_sucesores(mapa, estado):
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    sucesores = []

    for dir_x, dir_y in direcciones:
        nueva_pos = (estado.ubicacion_vehiculo[0] + dir_x, estado.ubicacion_vehiculo[1] + dir_y)

        #Siempre y cuando haya energia puede generar sucesores
        if estado.energia_restante > 0:

            #Si esta en una casilla valida dentro del mapa y no es un obstaculo
            if 0 <= nueva_pos[0] < len(mapa) and 0 <= nueva_pos[1] < len(mapa[0]) and mapa[nueva_pos[0]][nueva_pos[1]] != 'X':
                nuevos_pacientes = estado.pacientes_sin_trasladar.copy()    #Pacientes a recoger
                nuevas_plazas = estado.plazas_vehiculo.copy()             #Tipo de paciente en la ambulancia
                paciente_vehiculo = estado.paciente_vehiculo.copy()         #posicion de los pacientes en la ambulancia

                tipo = mapa[nueva_pos[0]][nueva_pos[1]]     #Guardamos el valor de la celda actual

                #Si la nueva posicion esta entre los pacientes a recoger
                if nueva_pos in nuevos_pacientes:
                    # Verifica si es un no contagioso
                    if tipo == 'N':
                        if 'C' in nuevas_plazas or len(nuevas_plazas)==10:
                            continue  # Ignora si hay pacientes contagiosos en el vehículo

                        # Actualiza la información de las plazas
                        nuevas_plazas.append(tipo)
                        paciente_vehiculo.insert(0, nueva_pos)
                        # Actualiza la información de la ambulancia
                    
                    # Verifica si es un contagios
                    elif tipo == 'C':
                        if nuevas_plazas.count('C') == 2 or nuevas_plazas.count('N') == 9:
                            continue
                        # Si es contagioso, añádelo al final de la lista de pacientes en la ambulancia
                        nuevas_plazas.append(tipo)
                        paciente_vehiculo.append(nueva_pos)

                    #Actualiza la lista de pacientes por recoger
                    nuevos_pacientes.remove(nueva_pos)

                elif tipo == 'CC' and ('C' in nuevas_plazas):
                    # Elimina todas las posiciones de pacientes contagiosos
                    nuevas_plazas = [plaza for plaza in nuevas_plazas if plaza != 'C']
                    paciente_vehiculo = [pos for pos in paciente_vehiculo if mapa[pos[0]][pos[1]] != 'C']
                elif tipo == 'CN' and ('C' not in nuevas_plazas) and ('N' in nuevas_plazas):
                    # Elimina todas las posiciones de pacientes no contagiosos
                    nuevas_plazas = [plaza for plaza in nuevas_plazas if plaza != 'N']
                    paciente_vehiculo = [pos for pos in paciente_vehiculo if mapa[pos[0]][pos[1]] != 'N']

                gasto = costo_entre_estados(nueva_pos,mapa)

                nuevo_estado = Estado(
                    ubicacion_vehiculo=nueva_pos,
                    pacientes_sin_trasladar=nuevos_pacientes,
                    energia_restante=estado.energia_restante-gasto,
                    plazas_vehiculo=nuevas_plazas,
                    paciente_vehiculo=paciente_vehiculo
                )

                sucesores.append(nuevo_estado)

    return sucesores

#Coste de ir a una ubicacion en el mapa
def costo_entre_estados(ubicacion, mapa):

    # Obtener el valor del estado al que se mueve
    cell_type = mapa[ubicacion[0]][ubicacion[1]]

    # Asignar costos según el tipo de celda
    if cell_type.isdigit():
        # Si es un número, utilizar ese valor como costo
        coste=int(cell_type)
    else:
        coste=1
        # Costo 1 para el resto de casillas

    return coste

#Funcion para imprimir correctamente el proceso seguido
def imprimir_output(mapa, camino, nombre_archivo):
    with open(nombre_archivo, 'w') as archivo_solucion:
        for posicion in camino:
            x, y = posicion[0] + 1, posicion[1] + 1
            valor_celda = mapa[posicion[0]][posicion[1]]
            if valor_celda == 'P':
                gasolina = 50
            elif valor_celda in ['C','N','CC','CN']:
                gasolina -= 1
            else:
                gasolina -= int(valor_celda)
            archivo_solucion.write(f"({x},{y}):{valor_celda}:{gasolina}\n")

#Funcion para imprimir las estadisticas
def imprimir_stats(tiempo, dir_output, dir_stats, n_nodos_expandidos):
    coste_total = 0
    longitud_plan = 0
    primero = True
    with open(dir_output, 'r') as archivo:
        for linea in archivo:
            elementos = linea.split(':')
            valor = elementos[1]
            if valor == 'P':
                if primero:
                    primero = False
                else:
                    coste_total+=1
            elif valor in ["CC", "CN","C","N"]:
                coste_total += 1
            else:
                coste_total += int(valor)
            longitud_plan +=1
    with open(dir_stats, 'a') as archivo:
           archivo.write('Tiempo total: ' + str(tiempo) + '\n')
           archivo.write('Coste total: ' + str(coste_total) + '\n')
           archivo.write('Longitud del plan: ' + str(longitud_plan) + '\n')
           archivo.write('Nodos expandidos: ' + str(n_nodos_expandidos) + '\n')

#Funcion main
def  main():
    if len(sys.argv) != 3:
        print("Uso: python ASTARTraslados.py <path mapa.csv> <num-h>")
        sys.exit(1)

    file_path = sys.argv[1]
    num_h = int(sys.argv[2])
    n_mapa = file_path.split('.')
    output = n_mapa[0]+".output"
    stat = n_mapa[0]+".stat"
    with open (stat, 'w') as archivo:
        archivo.write('')

    global map_info
    map_info = parse_map(file_path)
    start_time = time.time()

    # Llama a la función A* con el estado inicial del problema
    _ , resultado, nodos_expandidos = a_estrella(map_info['mapa'],Estado(map_info['parking_location'],map_info['patient_locations'],map_info['current_energy'],[],[]),output,num_h)
    
    end_time = time.time()
    total_time = end_time - start_time
    imprimir_stats(total_time,output, stat, nodos_expandidos)

    if resultado:
        print("Solución encontrada y guardada")
    else:
        print("No se encontró una solución.")


if __name__ == "__main__":
    main()