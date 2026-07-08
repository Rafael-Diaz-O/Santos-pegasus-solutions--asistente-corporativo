import fitz  # PyMuPDF: la herramienta que "lee" los PDF
import re 

#Almacena todos los datos en un string 
def limpiador_archivos_pdf_con_tablas(ruta):
    doc =  fitz.open(ruta)
    contenido_estructurado = ""

    for pagina in doc:
        # Extraer el texto de la página
        contenido_estructurado += pagina.get_text("text") + "\n"  

        #Estracion de tablas de forma estruturada 
        tabs = pagina.find_tables()
        for tab in tabs: 
            # Extraer el contenido de la tabla
            # Convierte la tabla a formato tabla Markdown para la IA
                 contenido_estructurado += "\n" + tab.to_markdown() + "\n"
    
    return contenido_estructurado


def limpiar_y_dividir_archivos(texto,tamano_chunk=1000, overlap=100):
      # 1. LIMPIEZA
    # Quitar saltos de línea, espacios extra y caracteres raros
    texto_limpio = re.sub(r'\s+', ' ', texto).strip()
    
    # 2. DIVISIÓN (CHUNKING)
    # Creamos trozos de 'tamano_chunk' caracteres
    chunks = []
    for i in range(0, len(texto_limpio), tamano_chunk - overlap):
        fragmento = texto_limpio[i:i + tamano_chunk]
        chunks.append(fragmento)
        
    return chunks