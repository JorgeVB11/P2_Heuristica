from constraint import Problem, AllDifferentConstraint, InSetConstraint
import csv
import random


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

# Restricción para v1 sin vehículos a la izquierda y a la derecha al mismo tiempo
def restriccion_v1(v1, v2, v3):
                    if v1[0] == 1:  # en la primera fila
                         if (v1[0] + 1 == v2[0] and v1[1]==v2[1]) or (v1[0] + 1 == v3[0] and v1[1]==v3[1]):  # no tiene un vehículo adyacente a la derecha
                            return False
                    elif v1[0] == filas:  # en la ultima fila
                         if (v1[0] - 1 == v2[0] and v1[1]==v2[1]) or (v1[0] - 1 == v3[0] and v1[1]==v3[1]):  # no tiene un vehículo adyacente a la izquierda
                            return False
                    else:
                        if (v1[0] + 1 == v2[0] and v1[1] == v2[1]) and (v1[0] - 1 == v3[0] and v1[1] == v3[1]): #no puede tener uno a la izquierda y a la derecha a la vez
                                return False
                    return True

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
        for vehiculo2 in vehiculos:
            vehiculo2_id, tipo2, _ = vehiculo2.split('-')
            if tipo == 'TSU'  and  tipo2 == 'TNU':
                problem.addConstraint(lambda tsu, tnu: tsu[0] != tnu[0] or tsu[1] >= tnu[1], (vehiculo_id, vehiculo2_id))

            # Restricción de maniobrabilidad
            # Verifica que las plazas a la izquierda y a la derecha estén libres
            for vehiculo3 in vehiculos:
                vehiculo3_id, _ , _ = vehiculo3.split('-')
            
                problem.addConstraint(restriccion_v1, (vehiculo_id, vehiculo2_id, vehiculo3_id))
                
    problem.addConstraint(AllDifferentConstraint())

    # Obtener las soluciones
    soluciones = problem.getSolutions()

    return soluciones


def guardar_soluciones(soluciones, path_salida, filas, columnas):
    with open(path_salida, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Escribir el número de soluciones encontradas
        writer.writerow(["N. Sol:", len(soluciones)])
        writer.writerow([ ])

        if len(soluciones) > 2:
            soluciones = random.sample(soluciones, 2)
        
        for index, solucion in enumerate(soluciones):
            # Escribe una línea indicando la solución actual
            writer.writerow([f"Solución {index + 1}"])

            # Crear una matriz para representar el parking
            parking = [['-'] * columnas for i in range(filas)]
            # Rellenar la matriz con los vehículos de la solución
            for vehiculo, plaza in solucion.items():
                info_vehiculo = next((v for v in vehiculos if v.startswith(vehiculo)), None)
                if info_vehiculo:
                    parking[plaza[0]-1][plaza[1]-1] = f"{info_vehiculo}"
            
            # Escribir la matriz en el archivo
            for fila in parking:
                writer.writerow(fila)
            
            # Agregar una fila de espacio si no es la última solución
            if index < len(soluciones) - 1:
                writer.writerow([ ])
        
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

    soluciones = resolver_problema(filas, columnas, plazas_conexion, vehiculos)

    if soluciones:
        # Barajar las soluciones para mostrar algunas de forma aleatoria
        random.shuffle(soluciones)
        path_salida = 'exit.csv'
        guardar_soluciones(soluciones, path_salida, filas, columnas)
        print(f"Soluciones guardadas en {path_salida}")
    else:
        print("No se encontraron soluciones.")

    