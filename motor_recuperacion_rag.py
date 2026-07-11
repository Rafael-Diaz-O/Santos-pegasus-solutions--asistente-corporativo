import chromadb
from sentence_transformers import SentenceTransformer

"""Sistema RAG (Recuperación Augmentada de Información) para responder preguntas sobre documentos de la empresa.
Este sistema utiliza un modelo de embeddings para convertir preguntas en vectores y busca en una base de datos de 
documentos previamente indexados para encontrar los fragmentos más relevantes que respondan a la pregunta del usuario. Luego, estos fragmentos 
se pueden utilizar para generar respuestas más precisas y contextuales."""

#Se carga el mismo modelo que se uso en la indexacion 
modelo_embeddings = SentenceTransformer('all-MiniLM-L6-v2')

def buscador_en_base_de_datos(pregunta, n_resultados=3): # en el segundo parametro al poner el 3 le decimo a la funcion si no sele pasa un segundo parametro pon que sea 3 

    #Conecion con la base de datos chromadb
    client = chromadb.PersistentClient(path="./base_de_datos_inteligente") #Busca  informacion dentro d ela carpeta 
    coleccion = client.get_collection(name="documentos_empresa") # Con esto lo que hago es traer informacion de la carpeta de la base de datos 

    #Pasar la pregunta a vector(embedding)
    vector_pregunta = modelo_embeddings.encode(pregunta).tolist() #Resivimos la pregunta la volvemos un vector de numeros y lo pasamos a una lista para que pueda ser leida por la base de datos

    #Buscamos los N resultados mas cercanos (similitud de coseno interna)
    resultados = coleccion.query( #Hago una consulta a la base de datos para que me busque los resultados mas cercanos a la pregunta que le estoy haciendo
            query_embeddings=[vector_pregunta],#Se hace la pregunta y se busca similitudes es una lisa para poder almacenar mas preguntas 
            n_results=n_resultados
    )

    return resultados #Me devuelve fragmentos de texto que son los mas cercanos a la pregunta que le hice a la base de datos 

