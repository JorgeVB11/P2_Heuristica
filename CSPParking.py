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