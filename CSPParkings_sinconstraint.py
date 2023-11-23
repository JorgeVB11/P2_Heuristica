class PlazaDeGaraje:
    def __init__(self, fila, columna):
        self.ubicacion_fila = fila
        self.ubicacion_columna = columna
        self.congelador = False
        self.ocupada = None
        self.coche = Coche()



class Coche:
    def __init__(self) -> None:
        self.nombre = ""
        self.ubicacion = None
        self.id = None
        self.prioritario = "X"
        self.tengo_congelador = False



class Parking:  
    def __init__(self, path):
        self.plazas = []
        self.filas, self.columnas, self.plazas_conexion, self.vehiculos = self.cargar_datos(path)
    def cargar_datos(self, path):
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



    def crear_parking(self):
        for i in range(self.filas):
            for j in range(self.columnas):
                plaza = PlazaDeGaraje(i+1,j+1) 
                self.plazas.append(plaza)
        for i in self.plazas_conexion:
            for j in self.plazas:
                if i[0] == j.ubicacion_fila and i[1] == j.ubicacion_columna:
                    j.congelador = True
        return

    def comprobar_parking_asignado(self):
        #1. Todo vehículo tiene que tener asignada una plaza y solo una. Dos coches no pueden tener la misma
        for i in self.plazas:
            if i.coche.ubicacion == None:
                return -1 #control de que todos tienen plaza
            for j in self.plazas:
                if i.coche.ubicacion == j.coche.ubicacion and i != j: #control de que no son la misma
                    return -1
        return 0

    def comprobar_electricidad(self):
        for item in self.plazas:
            if item.congelador == True and item.coche.tengo_congelador == False or item.congelador == False and item.coche.tengo_congelador == True:
                return -1
        return 0

    def vehiculo_prioritario(self):
        pass