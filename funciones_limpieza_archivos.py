import fitz  # PyMuPDF: la herramienta que "lee" los PDF


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