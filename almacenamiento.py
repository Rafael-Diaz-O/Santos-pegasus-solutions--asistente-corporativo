import chromadb 
from sentence_transformers import SentenceTransformer


#Almacenamiento de archivos procesados y transformacion en vectores 

modelo_embedding = SentenceTransformer('all-MiniLM-L6-v2')

def indexar_con_embeddings_explicitos(lista_de_chunks):
     print("Estoy entrando en la funcion idexacion")
     cliente = chromadb.PersistentClient(path="./base_de_datos_inteligente") #Me crea un nuevo archivo 
     coleccion = cliente.get_or_create_collection(name="documentos_empresa")

     #Convertimos cada texto en vectores(embendding) manualmente 
     for i, item in enumerate(lista_de_chunks):
        texto = item["contenido"]
        nombre = item["nombre_archivo"]


        #Genero el vector usando el modelo 
        vector = modelo_embedding.encode(texto).tolist()

        #Genero un ID unico que combine el nombre y el fragmento, esto para poder identificar de que archiv biene el texto y evitar conflitos de info repetida
        id_unico = f"{nombre}_{item['fragmento_id']}"

        # Guardamos en la base de datos el vector y su texto 
        coleccion.upsert( #Me rescribe la base datos varias veces cada que ejecute 
             ids=[id_unico],
             embeddings=[vector],#Pasamos el vector calculado manualmente 
             documents=[texto],
             metadatas=[{"archivo": nombre}]
        )    
    