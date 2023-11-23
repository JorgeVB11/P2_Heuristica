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
from constraint import Problem, AllDifferentConstraint

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


"""
def resolver_problema(filas, columnas, plazas_conexion, vehiculos):
    problem = Problem()

    plazas = [(i, j) for i in range(1, filas + 1) for j in range(1, columnas + 1)]

    problem.addVariables(plazas, vehiculos)

    # Restricciones
    problem.addConstraint(AllDifferentConstraint(), plazas)

    # Otras restricciones según las reglas del problema

    # Obtener la solución
    solucion = problem.getSolution()

    print("Solución encontrada:", solucion)

    return solucion

def guardar_solucion(solucion, path_salida):
    with open(path_salida, 'w') as file:
        # Escribir el número de soluciones encontradas
        file.write(f'"N. Sol:", {len(solucion)}\n')

        # Escribir la ocupación del parking
        for i in range(1, filas + 1):
            for j in range(1, columnas + 1):
                plaza = (i, j)
                ocupacion = solucion.get(plaza, '−')
                file.write(f'"{ocupacion}",')
            file.write('\n')

            """
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
"""
    solucion = resolver_problema(filas, columnas, plazas_conexion, vehiculos)

    if solucion:
        path_salida = path_parking.replace('.txt', '.csv')
        guardar_solucion(solucion, path_salida)
        print(f"Solución guardada en {path_salida}")
    else:
        print("No se encontró una solución.")

"""
