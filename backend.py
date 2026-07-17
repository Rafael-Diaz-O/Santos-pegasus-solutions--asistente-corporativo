"""
backend.py
==========
Conecta el frontend (app.py) con tu motor RAG real (motor_recuperacion_rag.py).

IMPORTANTE SOBRE UBICACION DE ARCHIVOS:
Este archivo hace `from motor_recuperacion_rag import ...`, así que debe
vivir en la MISMA carpeta (o tener en el PYTHONPATH) que:
    - motor_recuperacion_rag.py
    - almacenamiento.py
    - procesamiento_archivos.py
Es decir: mueve app.py y backend.py a la raíz de tu proyecto, junto a esos
archivos (la carpeta "unificada" de la que hablamos antes), o el import
va a fallar con ModuleNotFoundError.

La lógica de retrieval + reranking + umbral de confianza + generación es
la misma que ya tenías probada en tu main.py; aquí solo se reorganiza en
una función get_answer() para que la use la interfaz de Streamlit.
"""

import csv
import os
from datetime import datetime

from motor_recuperacion_rag import buscador_en_base_de_datos
from motor_recuperacion_rag import reclasificar_resultados
from motor_recuperacion_rag import generar_respuesta

FEEDBACK_LOG = os.path.join(os.path.dirname(__file__), "feedback_log.csv")
UNANSWERED_LOG = os.path.join(os.path.dirname(__file__), "unanswered_log.csv")

# Mismo umbral que usabas en main.py
UMBRAL_CONFIANZA = 0.5


def get_answer(question: str, history: list):
    """
    Orquesta el flujo de RAG real: recupera, reclasifica, valida confianza
    y genera la respuesta. Devuelve:
        {
            "answer": str,
            "sources": [{"title": str}, ...]
        }

    Nota: `history` (la conversación previa) todavía NO se le pasa a
    generar_respuesta() porque tu función actual solo recibe
    (pregunta, contexto_final). Si más adelante quieres que el LLM tenga
    memoria de turnos anteriores, hay que ajustar generar_respuesta() en
    motor_recuperacion_rag.py para que acepte el historial también.
    """
    # 1. Recuperación
    candidatos = buscador_en_base_de_datos(question, n_resultados=10)
    documentos = candidatos["documents"][0]
    metadatos = candidatos["metadatas"][0]

    if not documentos:
        log_unanswered(question)
        return {
            "answer": "No encontré información suficiente en la base de "
                      "documentos para responder esto con confianza. Voy a "
                      "registrar tu pregunta para que el equipo la revise.",
            "sources": [],
        }

    # 2. Reclasificación
    top_resultados = reclasificar_resultados(question, documentos)

    # 3. Validación de calidad
    mejor_puntaje = top_resultados[0][0]

    if mejor_puntaje < UMBRAL_CONFIANZA:
        log_unanswered(question)
        return {
            "answer": "No encontré información suficientemente relevante "
                      "en la base de conocimientos para responder esto con "
                      "confianza. Voy a registrar tu pregunta para que el "
                      "equipo la revise.",
            "sources": [],
        }

    # 4. Ensamblaje con fuentes reales
    contexto_final = ""
    fuentes_usadas = []
    for i in range(min(3, len(top_resultados))):
        _puntaje, texto = top_resultados[i]
        nombre_archivo = metadatos[i].get("nombre_archivo", "Desconocido")
        contexto_final += f"--- FUENTE: {nombre_archivo} ---\nCONTENIDO: {texto}\n\n"
        if nombre_archivo not in [f["title"] for f in fuentes_usadas]:
            fuentes_usadas.append({"title": nombre_archivo})

    # 5. Generación de la respuesta
    respuesta_final = generar_respuesta(question, contexto_final)

    return {"answer": respuesta_final, "sources": fuentes_usadas}


# --------------------------------------------------------------------------
# Logging para monitoreo de calidad y ciclo de mejora (sin cambios)
# --------------------------------------------------------------------------
def log_unanswered(question: str):
    _append_csv(UNANSWERED_LOG, ["timestamp", "question"],
                [datetime.utcnow().isoformat(), question])


def log_feedback(question: str, answer: str, rating: str):
    """rating: 'positive' o 'negative'"""
    _append_csv(FEEDBACK_LOG, ["timestamp", "question", "answer", "rating"],
                [datetime.utcnow().isoformat(), question, answer, rating])


def _append_csv(path: str, header: list, row: list):
    file_exists = os.path.isfile(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(row)