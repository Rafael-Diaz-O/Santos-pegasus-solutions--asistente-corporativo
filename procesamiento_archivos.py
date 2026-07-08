import os  #Manipulacion de rutas de archivo 
import fitz # PyMuPDF: la herramienta que "lee" los PDF
from funciones_limpieza_archivos import limpiador_archivos_pdf_con_tablas  # Importamos la función que limpia los archivos PDF con tablas
from funciones_limpieza_archivos import limpiar_y_dividir_archivos  # Importamos la función que limpia y divide el texto en chunks

#from openai import OpenAI

#Lectura de Archivo 

# Definimos dónde está nuestra "biblioteca" de documentos
carpeta = "Informacion_de_la_empresa"

biblioteca_de_archivos = []  # Lista para almacenar los nombres de los archivos que vamos a procesar

# 1. os.listdir(carpeta) crea una lista con todos los nombres de archivos dentro de esa carpeta.
# 2. El 'for' hace que el programa tome un nombre a la vez y lo guarde en 'nombre_archivo'.
for nombre_archivo in os.listdir(carpeta):
    
    # 3. os.path.join une el nombre de la carpeta con el nombre del archivo.
    # Resultado: "Informacion_de_la_empresa/archivo.pdf" (la ruta exacta que Python necesita). 
    #El path garantiza que funcione en cualquier sistema operativo (Windows, Linux, Mac).
    ruta_completa = os.path.join(carpeta, nombre_archivo)
    
    # 4. Verificamos que sea un archivo y no una subcarpeta.
    # Es un paso de seguridad para evitar errores.
    if os.path.isfile(ruta_completa):
        
        # 5. Imprimimos el nombre para que tú, como programador, veas el progreso.
        print(f"Procesando: {nombre_archivo}")
        
        # 6. Clasificación según la extensión del archivo.
        # Aquí le das instrucciones distintas a la computadora según el formato.
        if nombre_archivo.endswith(".pdf"):
            # Aquí pondrías la lógica: abrir con fitz, extraer texto, enviar a la IA.
            #Prueba
            #print(f"--> Detectado archivo PDF: {nombre_archivo}")

            #Procesamiento de archvos PDF con tablas 
            contenido_crudo  = limpiador_archivos_pdf_con_tablas(ruta_completa)

            #Limpiar y divdir archivos
            fragmentos = limpiar_y_dividir_archivos(contenido_crudo, tamano_chunk=1000, overlap=100)

            for i,fragmento in enumerate(fragmentos):
                # Guardar cada fragmento en la lista de archivos procesados
                biblioteca_de_archivos.append({
                    "nombre_archivo": nombre_archivo,
                    "fragmento_id":i,
                    "contenido": fragmento
                })
            
            
        elif nombre_archivo.endswith(".txt"):
            # Aquí pondrías la lógica: abrir con open(), leer el texto, enviar a la IA.
            print(f"--> Detectado archivo de texto: {nombre_archivo}")
            print("Se encuentra en desarrollo por favor cargue solo pdf ")
        
        elif nombre_archivo.endswith(".csv"):
            # Aquí pondrías la lógica: abrir con pandas, procesar datos, enviar a la IA.
            print(f"--> Detectado archivo CSV: {nombre_archivo}")   
            print("Se encuentra en desarrollo por favor cargue solo pdf ")

        else:
            # Si es un formato que no has programado aún, lo saltamos.
            print(f"--> Formato no soportado: {nombre_archivo}")





#Testeo para verificar que la informacion se haya guardado de forma correcta 
print(f"se han procesado {len(biblioteca_de_archivos)} archivos correctamente.")

#Me muestra la psocion en la que se encunetra mi archivo con el respetivo nombre 
print("----Contenido de los archivos procesados----")
for i ,item in enumerate(biblioteca_de_archivos):
    print(f"posicion {i}: {item['nombre_archivo']}")
    






#Descomentar y comentar con control + / 
# #Creando el cliente de OpenAI
# client = OpenAI(

#     base_url = "http://127.0.0.1:1234",
#     api_key = "google/gemma-3-1b"

# )

# #Pasando info a archivos JSON 

# lista_de_informacion = []

# def pasar_archivos_a_json(archivos):    

