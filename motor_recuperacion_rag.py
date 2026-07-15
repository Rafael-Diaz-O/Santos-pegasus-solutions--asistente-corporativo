import chromadb
import os #Trabajar con variables de entorno
from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder 
from openai  import OpenAI
from dotenv import load_dotenv 


"""Sistema RAG (Recuperación Augmentada de Información) para responder preguntas sobre documentos de la empresa.
Este sistema utiliza un modelo de embeddings para convertir preguntas en vectores y busca en una base de datos de 
documentos previamente indexados para encontrar los fragmentos más relevantes que respondan a la pregunta del usuario. Luego, estos fragmentos 
se pueden utilizar para generar respuestas más precisas y contextuales."""

#Se carga el mismo modelo que se uso en la indexacion 
modelo_embeddings = SentenceTransformer('all-MiniLM-L6-v2')

def buscador_en_base_de_datos(pregunta, n_resultados=10,): # en el segundo parametro al poner el 3 le decimo a la funcion si no sele pasa un segundo parametro pon que sea 3 

    #Conecion con la base de datos chromadb
    client = chromadb.PersistentClient(path="./base_de_datos_inteligente") #Busca  informacion dentro d ela carpeta 
    coleccion = client.get_collection(name="documentos_empresa") # Con esto lo que hago es traer informacion de la carpeta de la base de datos 

    #Pasar la pregunta a vector(embedding)
    vector_pregunta = modelo_embeddings.encode(pregunta).tolist() #Resivimos la pregunta la volvemos un vector de numeros y lo pasamos a una lista para que pueda ser leida por la base de datos


    resultados = coleccion.query( #Hago una consulta a la base de datos para que me busque los resultados mas cercanos a la pregunta que le estoy haciendo
        query_embeddings=[vector_pregunta],#Se hace la pregunta y se busca similitudes es una lisa para poder almacenar mas preguntas 
        n_results=n_resultados,    
    )

    return resultados #Me devuelve fragmentos de texto que son los mas cercanos a la pregunta que le hice a la base de datos 


#se carga el modelo de re-ranking que es un modelo que me va a ayudar a ordenar los resultados que me devuelve la base de datos
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2') 

def reclasificar_resultados(pregunta,documentos_resultados):
    #Se hace una lista de listas donde cada lista contiene la pregunta y un documento de los resultados
    pares = [[pregunta, doc] for doc in documentos_resultados]  # Con el for recrror los documentos que me devuevo y eso se guarda en una lista [pregunta ,doc] que a su vez se guarda en una lista externa siendo una lista dentro de otra lista 

    puntajes = reranker.predict(pares) #Se hace la prediccion de los puntajes de cada par pregunta-documento

    
    resultados_ordenados = sorted(zip(puntajes,documentos_resultados), key=lambda x: x[0], reverse=True) #Se ordenan los resultados por puntaje de mayor a menor
    #Con el zip se une porcentaje con pregunta 
    #Con x 0 le decimos que ordene por el primer elemento de la tupla que es el puntaje
    #Con reverse=True le decimos que ordene de mayor a menor 

    return resultados_ordenados #Se devuelven los resultados ordenados por puntaje



#Generando respuesta con el lllm 

load_dotenv()  # Cargar variables de entorno desde el archivo .env

def generar_respuesta(pregunta,contexto):
    #Configurando groq (compatible con openai) para generar la respuesta
    client = OpenAI(

        api_key=os.getenv("GROQ_API_KEY"), # Obtener la clave de la API desde las variables de entorno
        base_url="https://api.groq.com/openai/v1"
    )

    completion = client.chat.completions.create(
        model="llama3-70b-8192", # Es un modelo excelente y muy rápido en Groq
        messages=[{

            "role": "user", 

            "content": f"""Eres un asistente experto de la empresa Santo Pegasus.
            Tu trabajo es responder preguntas basándote ESTRICTAMENTE en el contexto proporcionado abajo.
            Si la información no aparece en el contexto, di que no tienes suficiente información para responder.
    
            CONTEXTO:
            {contexto}

            PREGUNTA:
            {pregunta}"""
            
            }],
        temperature=0.1
    )

    return completion.choices[0].message.content #Solo devolvera el texto del mensaje 