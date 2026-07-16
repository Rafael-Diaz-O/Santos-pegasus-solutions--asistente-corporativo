# Asistente Interno — Frontend (Streamlit)

Interfaz de chat simple y funcional para el agente de IA, pensada para uso interno.

## Cómo correrlo

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abre en `http://localhost:8501`.

## Qué incluye

- **`app.py`** — Interfaz: campo de pregunta, historial de conversación,
  aviso de "estás hablando con un agente de IA", fuentes citadas por
  respuesta y botones de feedback 👍👎.
- **`backend.py`** — Punto de integración con tu RAG real. Trae un mock
  (`FAKE_KNOWLEDGE_BASE`) para que el demo funcione sin dependencias, con
  comentarios `TODO` indicando exactamente dónde conectar tu vector store y
  tu LLM real.
- **`feedback_log.csv`** — Se genera automáticamente cuando alguien vota
  una respuesta. Sirve para el monitoreo de calidad.
- **`unanswered_log.csv`** — Se genera automáticamente cada vez que el
  agente no encuentra información suficiente. Sirve para detectar vacíos
  en la base documental.

## Conectar tu RAG real

En `backend.py`, reemplaza:

1. `retrieve_documents()` → tu búsqueda real en el índice vectorial
   (Chroma, FAISS, Pinecone, etc.).
2. `call_llm()` → tu llamada real al LLM (por ejemplo, la API de Anthropic),
   pasando la pregunta + los documentos recuperados + el historial.

El resto de `app.py` no necesita cambios: solo consume `get_answer()`.

## Cómo esto se conecta con el mantenimiento continuo del proyecto

Este frontend no reemplaza los procesos de mantenimiento que describiste,
pero les da la data que necesitan:

| Proceso | De dónde sale la data |
|---|---|
| Monitoreo de calidad (preguntas sin respuesta) | `unanswered_log.csv` |
| Monitoreo de calidad (feedback negativo) | `feedback_log.csv` (columna `rating`) |
| Ciclo de mejora (qué documentos faltan) | Revisar preguntas recurrentes en `unanswered_log.csv` |
| Ciclo de mejora (ajustes de prompt/recuperación) | Revisar respuestas con `rating = negative` |

El **pipeline de actualización de documentos**, la **curaduría de contenido**
y la **actualización del modelo** son procesos externos a este frontend
(normalmente un job/cron o un pipeline separado que reprocesa documentos y
actualiza el índice vectorial); este chat solo consume ese índice a través
de `backend.py`, así que cualquier mejora ahí se refleja automáticamente
sin tocar la interfaz.

## Alternativas de canal

Si en tu empresa ya usan Slack o Microsoft Teams a diario, considera migrar
esta misma lógica de `backend.py` a un bot de esas plataformas en vez de
mantener el chat web — la ventaja es que la gente no tiene que abrir un
sistema adicional. Los elementos clave (aviso de IA, fuentes, feedback,
historial) se pueden replicar igual usando botones/reacciones nativos de
Slack o tarjetas adaptativas de Teams.
