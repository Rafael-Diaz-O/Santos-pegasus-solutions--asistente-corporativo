"""
backend.py
==========
Aquí va la lógica real de tu agente (RAG). El frontend (app.py) NO sabe nada
de cómo funciona esto por dentro: solo llama a `get_answer(pregunta, historial)`
y espera de vuelta una respuesta con sus fuentes.

Esto separa "interfaz" de "cerebro", así puedes cambiar de vector store, LLM o
framework (LangChain, LlamaIndex, API directa de Claude, etc.) sin tocar la UI.

------------------------------------------------------------------------------
CÓMO CONECTAR TU RAG REAL
------------------------------------------------------------------------------
1. Reemplaza la función `retrieve_documents()` para que consulte tu índice
   vectorial real (Chroma, FAISS, Pinecone, Weaviate, etc.) en vez del
   diccionario de ejemplo `FAKE_KNOWLEDGE_BASE`.

2. Reemplaza `call_llm()` para que llame a tu modelo real (por ejemplo la API
   de Anthropic) pasándole la pregunta + los fragmentos recuperados como
   contexto.

3. `get_answer()` ya orquesta el flujo típico de RAG:
      pregunta -> recuperar documentos -> armar prompt -> LLM -> respuesta + fuentes
   No debería necesitar cambios grandes, solo ajustar el prompt si quieres.

4. Todo lo que pase por `log_unanswered()` y `log_feedback()` alimenta el
   "Monitoreo de calidad" y el "Ciclo de mejora" que pide el proyecto:
   preguntas sin respuesta y feedback negativo quedan guardados en CSV para
   que luego los revises y decidas qué documentos añadir o qué prompt ajustar.
------------------------------------------------------------------------------
"""

import csv
import os
from datetime import datetime

FEEDBACK_LOG = os.path.join(os.path.dirname(__file__), "feedback_log.csv")
UNANSWERED_LOG = os.path.join(os.path.dirname(__file__), "unanswered_log.csv")

# --------------------------------------------------------------------------
# EJEMPLO / MOCK - Bórralo cuando conectes tu índice vectorial real.
# Simula una base de conocimiento con "documentos" y permite que el demo
# funcione de inmediato sin dependencias externas.
# --------------------------------------------------------------------------
FAKE_KNOWLEDGE_BASE = [
    {
        "id": "doc_vacaciones",
        "title": "Política de Vacaciones 2025.pdf",
        "category": "RH",
        "content": "Los colaboradores tienen derecho a 15 días hábiles de "
                    "vacaciones por año, acumulables hasta por 6 meses.",
    },
    {
        "id": "doc_reembolsos",
        "title": "Manual de Reembolsos.docx",
        "category": "Financiero",
        "content": "Los reembolsos de gastos de viaje deben presentarse dentro "
                    "de los 15 días posteriores al viaje, con factura original.",
    },
    {
        "id": "doc_home_office",
        "title": "Política de Home Office.pdf",
        "category": "RH",
        "content": "Los colaboradores pueden trabajar de forma remota hasta "
                    "3 días por semana, previa autorización de su líder.",
    },
]


def retrieve_documents(question: str, top_k: int = 3):
    """
    TODO: Reemplazar por una búsqueda real en tu índice vectorial.
    Ejemplo con Chroma:

        results = vector_store.similarity_search(question, k=top_k)
        return [{"title": r.metadata["title"], "content": r.page_content,
                 "category": r.metadata.get("category", "General")} for r in results]

    Por ahora, hace un match muy simple por palabras clave sobre el mock.
    """
    question_lower = question.lower()
    scored = []
    for doc in FAKE_KNOWLEDGE_BASE:
        score = sum(1 for word in question_lower.split()
                    if word in doc["content"].lower())
        if score > 0:
            scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]


def call_llm(question: str, context_docs: list, history: list) -> str:
    """
    TODO: Reemplazar por una llamada real a tu LLM (por ejemplo la API de
    Anthropic), pasando el `question`, los `context_docs` recuperados y el
    `history` de la conversación para mantener contexto multi-turno.

    Ejemplo (pseudo-código):

        context_text = "\\n\\n".join(d["content"] for d in context_docs)
        response = client.messages.create(
            model="claude-sonnet-5",
            messages=[
                *history,
                {"role": "user", "content": f"Contexto:\\n{context_text}\\n\\nPregunta: {question}"}
            ],
        )
        return response.content[0].text

    Por ahora, devuelve una respuesta simulada basada en los documentos.
    """
    if not context_docs:
        return None  # None = "no encontré nada" -> se registra como sin respuesta

    partes = [d["content"] for d in context_docs]
    return (
        "Según la documentación disponible: " + " ".join(partes)
    )


def get_answer(question: str, history: list):
    """
    Orquesta el flujo de RAG. Devuelve un dict:
        {
            "answer": str,
            "sources": [{"title": str, "category": str}, ...]
        }
    """
    context_docs = retrieve_documents(question)
    answer = call_llm(question, context_docs, history)

    if answer is None:
        log_unanswered(question)
        return {
            "answer": (
                "No encontré información suficiente en la base de documentos "
                "para responder esto con confianza. Voy a registrar tu pregunta "
                "para que el equipo la revise y, si corresponde, se agregue "
                "documentación nueva."
            ),
            "sources": [],
        }

    sources = [{"title": d["title"], "category": d["category"]} for d in context_docs]
    return {"answer": answer, "sources": sources}


# --------------------------------------------------------------------------
# Logging para monitoreo de calidad y ciclo de mejora
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
