import heapq
"""
# Encontrar la posición de destino en el mapa
def lugar_llegada(mapa,final):
    for i in range(len(mapa)):
        for j in range(len(mapa[0])):
            if mapa[i][j] == final:
                destino = (i, j)
                print("destino:",destino)
                return destino
    print("No existe ese lugar")
    return None
"""
# Encontrar la posición de inicial en el mapa en caso de haber dos parkings coge la primera P y si no hay comienza en el (0,0)
def lugar_inicio(mapa):
    for i in range(len(mapa)):
        for j in range(len(mapa[0])):
            if mapa[i][j] == "P":
                inicio = (i, j)
                return inicio
    print("No hay parkings en el mapa")
    return None
"""
# Inicializar nodo inicial
inicio = lugar_inicio()
destino=lugar_llegada("CN")

if inicio==None or destino==None:
    print("error inicializando")
"""

def a_star_search(mapa,inicio,destino):
    # Definir las direcciones posibles: arriba, abajo, izquierda, derecha
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def heuristica(pos_actual, pos_final):
        # Heurística de distancia Manhattan
        return 1

    def obtener_sucesores(pos_actual):
        sucesores = []
        for dir_x, dir_y in direcciones:
            nueva_pos = (pos_actual[0] + dir_x, pos_actual[1] + dir_y)
            if 0 <= nueva_pos[0] < len(mapa) and 0 <= nueva_pos[1] < len(mapa[0]) and mapa[nueva_pos[0]][nueva_pos[1]] != 'X':
                sucesores.append(nueva_pos)
        return sucesores

    # Inicializar conjuntos ABIERTA y CERRADA
    ABIERTA = []
    CERRADA = set()

    nodo_inicial = (heuristica(inicio, destino), 0, inicio, [])
    heapq.heappush(ABIERTA, nodo_inicial)

    # Inicializar variables adicionales
    EXITO = False

    # Bucle principal
    while ABIERTA and not EXITO:
        _, costo, pos_actual, camino = heapq.heappop(ABIERTA)
        if pos_actual == destino:
            EXITO = True
        else:
            CERRADA.add(pos_actual)
            sucesores = obtener_sucesores(pos_actual)
            for sucesor in sucesores:
                if sucesor not in CERRADA:
                    nuevo_costo = costo + 1  # Suponemos que cada movimiento tiene un costo de 1
                    nuevo_nodo = (heuristica(sucesor, destino) + nuevo_costo, nuevo_costo, sucesor, camino + [pos_actual])
                    if sucesor not in (nodo[2] for nodo in ABIERTA):
                        heapq.heappush(ABIERTA, nuevo_nodo)
                    else:
                        indice = next((i for i, nodo in enumerate(ABIERTA) if nodo[2] == sucesor), None)
                        if nuevo_costo < ABIERTA[indice][1]:
                            ABIERTA[indice] = nuevo_nodo

    # Comprobar si se encontró una solución
    if EXITO:
        return camino + [destino]
    else:
        return None
    
def buscar_camino_a_todos(mapa, posicion_ambulancia, pacientes_por_recoger):
    caminos = {}

    for paciente in pacientes_por_recoger:
        camino = a_star_search(mapa, posicion_ambulancia, paciente)
        caminos[paciente] = camino
    caminos = {paciente: camino for paciente, camino in caminos.items() if camino is not None}
    return caminos

def recoger_paciente(mapa, estado_actual, paciente, caminos_a_pacientes):
    camino = caminos_a_pacientes[paciente]
    costo_energia = obtener_costo_energia(mapa, estado_actual['posicion_ambulancia'], camino)
    costo_ir_a_parking = obtener_costo_energia(mapa, camino[-1], a_star_search(mapa, camino[-1], lugar_inicio(mapa)))
    if costo_energia+costo_ir_a_parking <= estado_actual['energia']:
        estado_actual['energia'] -= costo_energia
        if camino:
            estado_actual['posicion_ambulancia'] = camino[-1]
            estado_actual['pacientes_por_recoger'].remove(paciente)
            estado_actual['pacientes_recogidos'].append(paciente)
            estado_actual['espacio_ambulancia'].append(mapa[paciente[0]][paciente[1]])
            estado_actual['paciente_ambulancia'].append(paciente)
        else:
            raise Exception(f"No se pudo encontrar un camino para recoger al paciente {paciente}")
    else:
        # Ir al parking para recargar
        try:
            ir_recargar_parking(mapa,estado_actual,costo_ir_a_parking)
        except Exception as e:
            print(f"No se pudoir al parking: {e}")
            return None

def recoger_paciente_contagioso(mapa, estado_actual, paciente, caminos_a_pacientes,CC):
        camino = caminos_a_pacientes[paciente]
        costo_energia = obtener_costo_energia(mapa, estado_actual['posicion_ambulancia'], camino)
        costo_ir_a_parking = obtener_costo_energia(mapa, camino[-1], a_star_search(mapa, camino[-1], lugar_inicio(mapa)))
        if costo_energia+costo_ir_a_parking <= estado_actual['energia']:
            estado_actual['energia'] -= costo_energia

            if paciente == CC:
                if camino:
                    estado_actual['posicion_ambulancia'] = camino[-1]
                    estado_actual['espacio_ambulancia'].remove("C")
                    estado_actual['pacientes_en_CC'].append(estado_actual['paciente_ambulancia'][-1])
                    estado_actual['paciente_ambulancia'].remove(estado_actual['paciente_ambulancia'][-1])
                else:
                    raise Exception(f"No se pudo encontrar un camino para llegar al CC {paciente}")
            else:
                if camino:
                    estado_actual['posicion_ambulancia'] = camino[-1]
                    estado_actual['pacientes_recogidos'].append(paciente)
                    estado_actual['espacio_ambulancia'].append(mapa[paciente[0]][paciente[1]])
                    estado_actual['paciente_ambulancia'].append(paciente)
                else:
                    raise Exception(f"No se pudo encontrar un camino para recoger al paciente contagioso {paciente}")
        else:
            # Ir al parking para recargar
            try:
                ir_recargar_parking(mapa,estado_actual,costo_ir_a_parking)
            except Exception as e:
                print(f"No se pudoir al parking: {e}")
                return None


def ir_a_centro(mapa, estado_actual, centro, X):
    camino = a_star_search(mapa, estado_actual['posicion_ambulancia'], centro)
    costo_energia = obtener_costo_energia(mapa, estado_actual['posicion_ambulancia'], camino)
    costo_ir_a_parking = obtener_costo_energia(mapa, camino[-1], a_star_search(mapa, camino[-1], lugar_inicio(mapa)))
    if costo_energia+costo_ir_a_parking <= estado_actual['energia']:
        estado_actual['energia'] -= costo_energia
        sitio="CN"
        if camino:
            if X=="C":
                sitio="CC"
            estado_actual['posicion_ambulancia'] = camino[-1]
            n_pacientes = estado_actual['espacio_ambulancia'].count(X)
            for i in range(n_pacientes):
                estado_actual['espacio_ambulancia'].remove(X)
                estado_actual[f'pacientes_en_{sitio}'].append(estado_actual['paciente_ambulancia'][-1])
                estado_actual['paciente_ambulancia'].remove(estado_actual['paciente_ambulancia'][-1])
        else:
            raise Exception(f"No se pudo encontrar un camino para llegar al centro {centro}")
    else:
        # Ir al parking para recargar
        try:
            ir_recargar_parking(mapa,estado_actual,costo_ir_a_parking)
        except Exception as e:
            print(f"No se pudoir al parking: {e}")
            return None

def ir_recargar_parking(mapa,estado_actual,costo_ir_a_parking):
    camino_a_parking = a_star_search(mapa, estado_actual['posicion_ambulancia'], lugar_inicio(mapa))
    if camino_a_parking is not None:
        estado_actual['posicion_ambulancia'] = camino_a_parking[-1]
        print(f"Ir al parking para recarga de energía")
        estado_actual['energia'] = 50  # Recarga instantánea
    else:
        raise Exception("No se pudo encontrar un camino al parking para recargar")
    
def traslado_pacientes(mapa, inicio_ambulancia, pacientes,pacientes_CC,pacientes_CN,CC,CN):
    # Estado Inicial
    estado_actual = {
        'posicion_ambulancia': inicio_ambulancia,
        'espacio_ambulancia':[],
        'paciente_ambulancia':[],
        'pacientes_por_recoger': pacientes.copy(),
        'pacientes_recogidos': [],
        'pacientes_contagiosos_por_recoger': pacientes_CC.copy(),
        'pacientes_no_contagiosos_por_recoger': pacientes_CN.copy(),
        'pacientes_en_CN': [],
        'pacientes_en_CC': [],
        'energia': 50
    }
    # Estado Objetivo
    #El estado objetivo debe tener la ambulancia en el parking y los pacientes en sus respectivos centros lo contagiosos en el centro de contagiosos y los no contagiosos en el de no contagiosos
    estado_objetivo = {
        'posicion_ambulancia': inicio_ambulancia,
        'espacio_ambulancia':[],
        'paciente_ambulancia':[],
        'pacientes_por_recoger': [],
        'pacientes_recogidos': pacientes.copy(),
        'pacientes_contagiosos_por_recoger': [],
        'pacientes_no_contagiosos_por_recoger': [],
        'pacientes_en_CN': pacientes_CN.copy(),
        'pacientes_en_CC': pacientes_CC.copy(),
        'energia': 50
    }
    # Bucle principal
    while not son_estados_iguales(estado_actual, estado_objetivo):

        if len(estado_actual['espacio_ambulancia'])==0 and estado_actual['pacientes_por_recoger']:
            caminos_a_pacientes = buscar_camino_a_todos(mapa, estado_actual['posicion_ambulancia'], estado_actual['pacientes_por_recoger'])

            # Asegurémonos de que haya caminos disponibles
            if all(caminos_a_pacientes.get(paciente) is not None and None not in caminos_a_pacientes[paciente] for paciente in estado_actual['pacientes_por_recoger']):
                paciente_mas_cercano = min(estado_actual['pacientes_por_recoger'], key=lambda paciente: len(caminos_a_pacientes[paciente]))
                try:
                    recoger_paciente(mapa, estado_actual, paciente_mas_cercano, caminos_a_pacientes)
                except Exception as e:
                    print(f"No se pudo recoger al paciente: {e}")
                    return None
            else:
                return None
            
        #comprobamos si se ha recogido a un paciente contagioso    
        if "C" in estado_actual['espacio_ambulancia']:
            if estado_actual['espacio_ambulancia'].count("C")<2: #tenemos al menos un paciente contagioso más que se pueda recoger
                if estado_actual['posicion_ambulancia'] in estado_actual["pacientes_contagiosos_por_recoger"]:
                    estado_actual["pacientes_contagiosos_por_recoger"].remove(estado_actual['posicion_ambulancia'])
                caminos_a_pacientes = buscar_camino_a_todos(mapa, estado_actual['posicion_ambulancia'],estado_actual["pacientes_contagiosos_por_recoger"]+[CC])
                if all(caminos_a_pacientes.get(paciente) is not None and None not in caminos_a_pacientes[paciente] for paciente in estado_actual['pacientes_contagiosos_por_recoger'] + [CC]):
                    paciente_mas_cercano = min(estado_actual['pacientes_contagiosos_por_recoger']+[CC], key=lambda paciente: len(caminos_a_pacientes[paciente]))
                    try:
                        recoger_paciente_contagioso(mapa, estado_actual, paciente_mas_cercano, caminos_a_pacientes,CC)
                    except Exception as e:
                        print(f"No se pudo acceder a: {e}")
                        return None
                    
                else:
                    return None

            if estado_actual['espacio_ambulancia'].count("C")==2:
                if estado_actual['posicion_ambulancia'] in estado_actual["pacientes_contagiosos_por_recoger"]:
                    estado_actual["pacientes_contagiosos_por_recoger"].remove(estado_actual['posicion_ambulancia'])
                    estado_actual["pacientes_por_recoger"].remove(estado_actual['posicion_ambulancia'])
                try:
                    ir_a_centro(mapa, estado_actual, CC, "C")
                except Exception as e:
                    print(f"No se pudo acceder a: {e}")
                    return None
                    
        if "N" in estado_actual['espacio_ambulancia']:
            if estado_actual['posicion_ambulancia']!=CC and estado_actual['posicion_ambulancia']!=CN and estado_actual['posicion_ambulancia'] in estado_actual["pacientes_no_contagiosos_por_recoger"]:
                estado_actual["pacientes_no_contagiosos_por_recoger"].remove(estado_actual['posicion_ambulancia'])
            if  len(estado_actual['espacio_ambulancia']) < 9: #si no esta llena la ambulancia busca a otro paciente o va a CN
                caminos_a_pacientes = buscar_camino_a_todos(mapa, estado_actual['posicion_ambulancia'],estado_actual["pacientes_por_recoger"]+[CN])
                if all(caminos_a_pacientes.get(paciente) is not None and None not in caminos_a_pacientes[paciente] for paciente in estado_actual['pacientes_por_recoger'] + [CN]):
                    paciente_mas_cercano = min(estado_actual['pacientes_por_recoger']+[CN], key=lambda paciente: len(caminos_a_pacientes[paciente]))
                    if paciente_mas_cercano == CN:#vamos al centro de no contagiados
                        try:
                            ir_a_centro(mapa, estado_actual, CN, "N")
                        except Exception as e:
                            print(f"No se pudo acceder a: {e}")
                            return None

                    else:
                        try:
                            recoger_paciente(mapa, estado_actual, paciente_mas_cercano, caminos_a_pacientes)
                        except Exception as e:
                            print(f"No se pudo recoger al paciente: {e}")
                            return None
                        
            if  len(estado_actual['espacio_ambulancia']) == 9 and estado_actual['espacio_ambulancia'][-1]=="N": #Caso de que haya 9N no puede ir a por C solo a por N o a vaciar
                if estado_actual['posicion_ambulancia'] in estado_actual["pacientes_no_contagiosos_por_recoger"]:
                    estado_actual["pacientes_no_contagiosos_por_recoger"].remove(estado_actual['posicion_ambulancia'])
                caminos_a_pacientes = buscar_camino_a_todos(mapa, estado_actual['posicion_ambulancia'],estado_actual["pacientes_no_contagiosos_por_recoger"]+[CN])
                if all(caminos_a_pacientes.get(paciente) is not None and None not in caminos_a_pacientes[paciente] for paciente in estado_actual['pacientes_no_contagiosos_por_recoger'] + [CN]):
                    paciente_mas_cercano = min(estado_actual['pacientes_no_contagiosos_por_recoger']+[CN], key=lambda paciente: len(caminos_a_pacientes[paciente]))
                    if paciente_mas_cercano == CN:#vamos al centro de no contagiados
                        try:
                            ir_a_centro(mapa, estado_actual, CN, "N")
                        except Exception as e:
                            print(f"No se pudo acceder a: {e}")
                            return None
                    else:
                        try:
                            recoger_paciente(mapa, estado_actual, paciente_mas_cercano, caminos_a_pacientes)
                        except Exception as e:
                            print(f"No se pudo recoger al paciente: {e}")
                            return None
            
        if  len(estado_actual['espacio_ambulancia']) > 9 : #caso de que haya 10 N vaya a CN
            if estado_actual['posicion_ambulancia'] in estado_actual["pacientes_no_contagiosos_por_recoger"]:
                estado_actual["pacientes_no_contagiosos_por_recoger"].remove(estado_actual['posicion_ambulancia'])
            try:
                ir_a_centro(mapa, estado_actual, CN, "N")
            except Exception as e:
                print(f"No se pudo acceder a: {e}")
                return None

        #si hay 8 N y se añade otra N
        #empieza si esta vacia ambulancia recoge un paciente, si es contagioso busca si prefiere ir al CC o a por otro contagioso,
        # si no es contagioso puede ir a por otro paciente sea cual sea o al cn,
        # Verificar si hay suficiente energía para continuar
        if estado_actual['energia'] <= 0:
            # Ir al parking para recargar
            camino_a_parking = a_star_search(mapa, estado_actual['posicion_ambulancia'], lugar_inicio(mapa))
            if camino_a_parking is not None:
                estado_actual['posicion_ambulancia'] = camino_a_parking[-1]
                estado_actual['energia'] = 50  # Recarga instantánea
            else:
                raise Exception("No se pudo encontrar un camino al parking para recargar")
            
        #si esta en el parking recarga enrgia
        if estado_actual['posicion_ambulancia']==lugar_inicio(mapa):
            estado_actual['energia'] = 50  # Recarga instantánea

        #cuando no haya pacientes a recoger y la mabulancia este vacia que vuelva al parking
        if len(estado_actual['espacio_ambulancia'])==0 and not estado_actual['pacientes_por_recoger']:
            camino = a_star_search(mapa, estado_actual['posicion_ambulancia'], lugar_inicio(mapa))
            if camino is None:
                return None
            estado_actual['posicion_ambulancia'] = camino[-1]
            costo_energia = obtener_costo_energia(mapa, estado_actual['posicion_ambulancia'], camino)
            estado_actual['energia'] -= costo_energia
            estado_actual['energia'] = 50 

    return estado_actual

# Función para comparar dos estados ignorando el orden de las listas
def son_estados_iguales(estado1, estado2):
    for clave, valor in estado1.items():
        if clave in ['pacientes_recogidos', 'pacientes_en_CN', 'pacientes_en_CC']:
            if set(valor) != set(estado2.get(clave, [])):
                return False
        elif estado1[clave] != estado2.get(clave):
            return False
    return True

def obtener_costo_energia(mapa, posicion, camino):
    coste=0
    camino.remove(posicion)
    for posicion in camino:
        # Obtener el tipo de celda en la nueva ubicación
        cell_type = mapa[posicion[0]][posicion[1]]
        # Asignar costos según el tipo de celda
        if cell_type.isdigit():
            # Si es un número, utilizar ese valor como costo
            coste+=int(cell_type)
        elif cell_type == 'N' or cell_type == 'C' or cell_type == 'CN' or cell_type == 'CC':
            # Costo 1 para pacientes no contagiosos y contagiosos
            coste+=1
        else: 
            #cell_type == 'P':
            # Costo 0 para el estacionamiento
            coste+=0
    return coste


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
# Ejemplo de uso
map_info = parse_map('mapa.csv')
resultado = traslado_pacientes(map_info['mapa'], map_info['current_location'], map_info['patient_locations'],map_info['contagious_locations'],
                               map_info['non_contagious_locations'],map_info['treatment_centers_cc'][0],map_info['treatment_centers_cn'][0])
if resultado is None:
    print("No existe solución")
print("Resultado del traslado:", resultado) 