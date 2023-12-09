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
        return abs(pos_actual[0] - pos_final[0]) + abs(pos_actual[1] - pos_final[1])

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

    return caminos

def traslado_pacientes(mapa, inicio_ambulancia, pacientes,pacientes_CC,pacientes_CN,CC,CN):
    # Estado Inicial
    estado_actual = {
        'posicion_ambulancia': inicio_ambulancia,
        'espacio_ambulancia':[],
        'paciente_ambulancia':[],
        'pacientes_por_recoger': pacientes.copy(),
        'pacientes_contagiosos_por_recoger': pacientes_CC.copy(),
        'pacientes_no_contagiosos_por_recoger': pacientes_CN.copy(),
        'pacientes_recogidos': [],
        'pacientes_en_CN': [],
        'pacientes_en_CC': [],
    }

    # Estado Objetivo
    #El estado objetivo debe tener la ambulancia en el parking y los pacientes en sus respectivos centros lo contagiosos en el centro de contagiosos y los no contagiosos en el de no contagiosos
    estado_objetivo = {
        'posicion_ambulancia': inicio_ambulancia,
        'espacio_ambulancia':[],
        'pacientes_por_recoger': [],
        'pacientes_recogidos': pacientes.copy(),
        'pacientes_en_CN': pacientes_CN.copy(),
        'pacientes_en_CC': pacientes_CC.copy(),
    }
    # Bucle principal
    while estado_actual != estado_objetivo:
        #pregunta que hay en la ambulancia? y si quedan pacientes por recoger?
        #Cuando esta vacia la ambulancia y queden pacientes por recoger ir a por un paciente
        #Cuando se recoge a un paciente contagioso o se recoge a otro siempre que haya espacio en la ambulancia o se le deja en el centro de contagiosos
        #Cuando se recoge a un paciente no contagioso puede recoger a otro paciente de cualquier tipo si la mbulancia no esta llena o ir al centro de no contagiosos
        if len(estado_actual['espacio_ambulancia'])<10 and estado_actual['pacientes_por_recoger']:
            caminos_a_pacientes = buscar_camino_a_todos(mapa, estado_actual['posicion_ambulancia'], estado_actual['pacientes_por_recoger'])
            
            paciente_mas_cercano = min(estado_actual['pacientes_por_recoger'], key=lambda paciente: len(caminos_a_pacientes[paciente]))

            camino = caminos_a_pacientes[paciente_mas_cercano]
            #recoja al paciente mas cercano
            if camino:
                # Simula recoger al paciente
                estado_actual['posicion_ambulancia'] = camino[-1]
                print("ESTOY AQUI:",estado_actual['posicion_ambulancia'])
                estado_actual['pacientes_por_recoger'].remove(paciente_mas_cercano)
                estado_actual['pacientes_recogidos'].append(paciente_mas_cercano)
                estado_actual['espacio_ambulancia'].append(mapa[paciente_mas_cercano[0]][paciente_mas_cercano[1]])#se puede guardar como c on cogiendo el valor que pone en el mapa
                estado_actual['paciente_ambulancia'].append(paciente_mas_cercano)
                #print("estado de ambulancia: ",estado_actual['espacio_ambulancia'])
                  # Mueve al siguiente paso del bucle principal
        #comprobamos si se ha recogido a un paciente contagioso

        print(estado_actual["pacientes_contagiosos_por_recoger"])
        if "C" in estado_actual['espacio_ambulancia']:
            print("siuu")
            estado_actual["pacientes_contagiosos_por_recoger"].remove(estado_actual['posicion_ambulancia'])
            if len(estado_actual["pacientes_contagiosos_por_recoger"])>0 and estado_actual['espacio_ambulancia'].count("C")<2: #tenemos al menos un paciente contagioso más que se pueda recoger
                caminos_a_pacientes = buscar_camino_a_todos(mapa, estado_actual['posicion_ambulancia'],estado_actual["pacientes_contagiosos_por_recoger"])
                paciente_mas_cercano = min(estado_actual['pacientes_contagiosos_por_recoger'], key=lambda paciente: len(caminos_a_pacientes[paciente]))
                camino = caminos_a_pacientes[paciente_mas_cercano]
                if camino:
                # Simula recoger al paciente
                    estado_actual['posicion_ambulancia'] = camino[-1]
                    estado_actual['pacientes_por_recoger'].remove(paciente_mas_cercano)
                    estado_actual["pacientes_contagiosos_por_recoger"].remove(estado_actual['posicion_ambulancia'])
                    estado_actual['pacientes_recogidos'].append(paciente_mas_cercano)
                    estado_actual['espacio_ambulancia'].append(mapa[paciente_mas_cercano[0]][paciente_mas_cercano[1]])#se puede guardar como c on cogiendo el valor que pone en el mapa
                    estado_actual['paciente_ambulancia'].append(paciente_mas_cercano)


            if len(estado_actual["pacientes_contagiosos_por_recoger"])==0 or estado_actual['espacio_ambulancia'].count("C")==2:
                print("no way")
                camino = a_star_search(mapa, estado_actual['posicion_ambulancia'], (CC))
                print("este es mi camino", camino)
                print("este es CC:\n", CC)
                estado_actual['posicion_ambulancia'] = (CC)
                n_pacientes = estado_actual['espacio_ambulancia'].count("C")
                for i in range(n_pacientes):
                    estado_actual['espacio_ambulancia'].remove("C")
                    estado_actual['pacientes_en_CC'].append(estado_actual['paciente_ambulancia'][-1])
                    estado_actual['paciente_ambulancia'].remove(estado_actual['paciente_ambulancia'][-1])
        elif "N" in estado_actual['espacio_ambulancia']:
            print("cr7")
            
            estado_actual["pacientes_no_contagiosos_por_recoger"].remove(estado_actual['posicion_ambulancia'])
            if len(estado_actual["pacientes_por_recoger"])==0 or estado_actual['espacio_ambulancia'].count("N")==10: #si terminamos de buscar vamos al hospital CN
                camino = a_star_search(mapa, estado_actual['posicion_ambulancia'], CN)
                print("deberia estar_aqui", camino[-1])
                estado_actual['posicion_ambulancia'] = camino[-1]
                n_pacientes = estado_actual['espacio_ambulancia'].count("N")
                for i in range(n_pacientes):
                    estado_actual['espacio_ambulancia'].remove("N")
                    estado_actual['pacientes_en_CN'].append(estado_actual['paciente_ambulancia'][-1])
                    estado_actual['paciente_ambulancia'].remove(estado_actual['paciente_ambulancia'][-1])
        #estado_actual['posicion_ambulancia']=lugar_inicio(mapa)

    return estado_actual

# Ejemplo de uso
mapa_ejemplo = [
    ['P', 'N', '1', 'C'],
    ['2', 'X', 'CC', 'N'],
    ['C', '3', '1', 'CN'],
    ['N', 'X', 'C', 'X']
]

inicio_ambulancia = (0, 0)
pacientes_a_recoger = [(0,3),(2,0),(3,2),(0,1),(1,3),(3,0)]
pacientes_contagiosos =[(0,3),(2,0),(3,2)]
pacientes_no_contagiosos=[(0,1),(1,3),(3,0)]
CN= ([2,3])
CC=([1,2])

resultado = traslado_pacientes(mapa_ejemplo, inicio_ambulancia, pacientes_a_recoger,pacientes_contagiosos,pacientes_no_contagiosos,CC,CN)

#print("Resultado del traslado:", resultado)
"""
# Ejemplo de uso
mapa_ejemplo = [
    ['P', 'N', '1', 'C'],
    ['2', 'X', 'CC', 'N'],
    ['C', '3', 'X', 'CN'],
    ['N', 'X', 'C', 'X']
]

camino_solucion = a_star_search(mapa_ejemplo)

if camino_solucion:
    print("Camino de la solución:", camino_solucion)
else:
    print("No se encontró una solución.")
"""