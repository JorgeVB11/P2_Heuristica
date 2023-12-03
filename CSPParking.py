#Archivo para hacer el programa
#------------------------------------
#-------------INFO GENERAL---------------------
#Cada vehiculo una plaza
#vehiculos congelador->enchufe
#vehiculo TSU no tiene nada delante
#vehiculo tiene hueco a la izq o dcha
#---------------------------------------
#---------------DATOS ENTRADA-----------
#1ª línea: filas x columnas del parking
#2ª línea: listado de plazas con conexi´on el´ectrica
#3ª y posteriores: c´odigo de identificaci´on de los
#vehículos [ID-TIPO-CONGELADOR]
#ID: nº secuencial
#TIPO: TSU/TNU (Urgente/No urgente)
#CONGELADOR: C/X (Con congelador/Sin congelador)
#----------------------------------------
#---------------SE PIDE------------------
# Modelar este problema como un problema de satisfaccion de restricciones CSP
#Generar archivo de salida .csv
#Crear test con casos de prueba
#----------------------------------------
#------------A investigar-----------------------
#Averiguar cómo abrir y leer ficheros txt
#Averiguar cómo generar archivos csv
#Mirarse bien los distintos metodos de busqueda ya que necesitamos el nº total de soluciones. Lo que es seguro es que necesitamos un algoritmo que sea completo,
#no nos vale uno incompleto por muy eficiente que sea para llegar a lo optimo.
#------------PASOS----------------
#Crear clase parking
#Crear ns si clase o struct Parametros de inicio para que el parking reciba los datos del archivo
#Crear método crear mapa parking para inicializar los campos
#Para colocar ambulancias, 1º habrá que colocar las que son con refrigerador, no preferentes al final y después 
#preferentes pq sabremos que en esa fila no van más cosas
#a continuación si en la fila no hay ambulancias preferentes se meten no preferentes sin refrigerador y por ultimo prederentes sin refrigerador
#esto sería para encontrar una solución, para encontrar todas las que hay habria que pensar que tipo de metodo heuristico usamos

#!/usr/bin/env python
from constraint import Problem, AllDifferentConstraint, InSetConstraint
import csv

vacio = "-"

def cargar_datos(path):
    with open(path, 'r') as file:
        lines = file.readlines()

    # Obtener filas y columnas
    filas, columnas = map(int, lines[0].strip().split('x'))

    # Obtener plazas de conexión
    plazas_conexion_line = lines[1][3:].strip()  # Obtener la línea de las plazas de conexión
    plazas_conexion = [tuple(map(int, coord.strip('()').split(','))) for coord in plazas_conexion_line.split(')(')]

    # Obtener vehículos
    vehiculos = [line.strip() for line in lines[2:]]

    return filas, columnas, plazas_conexion, vehiculos



def resolver_problema(filas, columnas, plazas_conexion, vehiculos):
    problem = Problem()
    
    plazas = [(i, j) for i in range(1, filas + 1) for j in range(1, columnas + 1)]

    for vehiculo in vehiculos:
        vehiculo_id, tipo, congelador = vehiculo.split('-')
        problem.addVariable(vehiculo_id,plazas)

        # Restricción de conexión eléctrica para vehículos con congelador
        if congelador=='C':
            problem.addConstraint(InSetConstraint(plazas_conexion), [vehiculo_id])

        # Restricción para TSU que no puede tener TNU por delante
        if tipo == 'TSU':  
            for vehiculo2 in vehiculos:
                vehiculo2_id, tipo2, _ = vehiculo2.split('-')
                if tipo2 == 'TNU':
                    problem.addConstraint(lambda tsu, tnu: tsu[0] != tnu[0] or tsu[1] >= tnu[1], (vehiculo_id, vehiculo2_id))

        # Restricción de maniobrabilidad
        # Verifica que las plazas a la izquierda y a la derecha estén libres
        for vehiculo2 in vehiculos:
                vehiculo2_id, tipo2, _ = vehiculo2.split('-')
                problem.addConstraint(lambda v1, v2: v1[0]-1!=v2[0]  and v1[0]+1!=v2[0], (vehiculo_id, vehiculo2_id))

    problem.addConstraint(AllDifferentConstraint())

    # Obtener la solución
    solucion = problem.getSolution()

    print("Solución encontrada:", solucion)

    return solucion

def guardar_solucion(solucion, path_salida, filas, columnas):
    with open(path_salida, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Escribir el número de soluciones encontradas
        writer.writerow(["N. Sol:", 1])

        # Escribir la ocupación del parking
        for i in range(1, filas + 1):
            fila = []
            for j in range(1, columnas + 1):
                plaza = (i, j)
                ocupacion = solucion.get(plaza, vacio)
                fila.append(ocupacion)
            writer.writerow(fila)
            
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python CSPParking.py <path_parking>")
        sys.exit(1)

    path_parking = sys.argv[1]
    filas, columnas, plazas_conexion, vehiculos = cargar_datos(path_parking)
    # Imprimir los valores obtenidos
    print(f"Filas: {filas}")
    print(f"Columnas: {columnas}")
    print(f"Plazas de Conexión: {plazas_conexion}")
    print(f"Vehículos: {vehiculos}")

    solucion = resolver_problema(filas, columnas, plazas_conexion, vehiculos)

    if solucion:
        path_salida = 'exit.csv'
        guardar_solucion(solucion, path_salida, filas, columnas)
        print(f"Solución guardada en {path_salida}")
    else:
        print("No se encontró una solución.")

    
        """
        # Restricción3: Vehículos con congelador solo pueden ocupar plazas con conexión a la red eléctrica
        if congelador == 'C':
            for plaza in plazas_conexion:
                problem.addConstraint(lambda v, p=plaza: v == f"{vehiculo_id}-{tipo}-{congelador}" if p == plaza else True, (plaza,))
    
        # Restricción4: Un vehículo de tipo TSU no puede tener aparcado por delante a ningún otro vehículo,
        # excepto si este es también de tipo TSU
        if tipo == 'TSU':
            for i in range(columnas):
                for j in range(1, filas):
                    plaza_actual = (j, i+1)
                    plaza_delante = (j+1, i+1)

                    problem.addConstraint(lambda v1, v2, t=tipo: (v1 != f"{vehiculo_id}-{t}" or v2 != f"{vehiculo_id}-{t}") if (v1, v2) == (plaza_actual, plaza_delante) else True, (plaza_actual, plaza_delante))

        # Restricción5: Todo vehículo debe tener libre una plaza a izquierda o derecha
        for i in range(1, filas + 1):
            for j in range(1, columnas + 1):
                plaza_actual = (i, j)

                # Asegurarse de que la plaza_izquierda esté dentro del rango
                if j > 1:
                    plaza_izquierda = (i, j - 1)
                    problem.addConstraint(lambda v1, v2: (v1 != f"{vehiculo_id}-{tipo}-{congelador}" or v2 != f"{vehiculo_id}-{tipo}-{congelador}") if (v1, v2) == (plaza_actual, plaza_izquierda) else True, (plaza_actual, plaza_izquierda))

                # Asegurarse de que la plaza_derecha esté dentro del rango
                if j < columnas:
                    plaza_derecha = (i, j + 1)
                    problem.addConstraint(lambda v1, v2: (v1 != f"{vehiculo_id}-{tipo}-{congelador}" or v2 != f"{vehiculo_id}-{tipo}-{congelador}") if (v1, v2) == (plaza_actual, plaza_derecha) else True, (plaza_actual, plaza_derecha))

    # Restricción2: No puede haber dos vehículos en la misma plaza
    for plaza in plazas:
        problem.addConstraint(AllDifferentConstraint(), [plaza])
    """