# 🤖 Asistente Corporativo — Santos Pegasus Solutions

## 🚀 App en vivo

### 👉 **[https://santos-pegasus-solutions--asistente-corporativo-3s4lmi5p3tbtx8.streamlit.app/](https://santos-pegasus-solutions--asistente-corporativo-3s4lmi5p3tbtx8.streamlit.app/)**

Agente de IA corporativo que responde preguntas basándose únicamente en los documentos internos indexados de la empresa (RAG: Retrieval-Augmented Generation).

---

## 📸 Capturas del funcionamiento

**Pregunta sin información en la base de conocimientos** — el agente reconoce que no tiene contexto suficiente en vez de inventar una respuesta, y la registra para revisión del equipo:

![Captura del agente indicando que no encontró información relevante](screenshots/captura_1_pregunta.png)

**Pregunta con contexto disponible** — el agente responde citando la fuente y muestra el documento utilizado en el expander "Fuentes utilizadas":

![Captura del agente respondiendo con fuentes citadas](screenshots/captura_2_respuesta.png)

---

## 🧪 Preguntas para probar el agente

Puedes copiar y pegar estas preguntas directamente en el chat para verificar que el sistema responde correctamente en base a los documentos indexados:

- ¿Qué políticas de seguridad se deben aplicar obligatoriamente al manejar tokens de autenticación para evitar vulnerabilidades como XSS?
- ¿Cuál es la diferencia fundamental entre los roles definidos durante la respuesta a un incidente SEV-1?
- ¿Cuál es el objetivo principal de fomentar una cultura "Blameless" al momento de redactar un Post-Mortem?

---

## ⚙️ Cómo correrlo localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Necesitas un archivo `.env` en la raíz del proyecto con:

```
GROQ_API_KEY=tu_clave_de_groq
```

Se abre en `http://localhost:8501`.

## 🧩 Qué incluye

- **`app.py`** — Interfaz: campo de pregunta, historial de conversación, aviso de "estás hablando con un agente de IA", fuentes citadas por respuesta y botones de feedback 👍👎.
- **`backend.py`** — Conecta la interfaz con el motor RAG real (`motor_recuperacion_rag.py`): recupera documentos relevantes, reclasifica por relevancia (re-ranking), valida un umbral de confianza y genera la respuesta con el LLM.
- **`motor_recuperacion_rag.py`** — Búsqueda semántica en ChromaDB + re-ranking con CrossEncoder + generación de respuesta vía Groq (compatible con la API de OpenAI).
- **`almacenamiento.py`** — Indexación de documentos procesados como embeddings en ChromaDB.
- **`procesamiento_archivos.py`** — Extracción y limpieza de texto (incluyendo tablas) desde PDFs, y división en fragmentos (chunking).
- **`main.py`** — Script de indexación: procesa los documentos de `Informacion_de_la_empresa/` y los guarda en la base de datos vectorial.
- **`feedback_log.csv`** — Se genera automáticamente cuando alguien vota una respuesta. Sirve para el monitoreo de calidad.
- **`unanswered_log.csv`** — Se genera automáticamente cada vez que el agente no encuentra información suficiente. Sirve para detectar vacíos en la base documental.

## 🔄 Mantenimiento continuo

| Proceso | De dónde sale la data |
|---|---|
| Monitoreo de calidad (preguntas sin respuesta) | `unanswered_log.csv` |
| Monitoreo de calidad (feedback negativo) | `feedback_log.csv` (columna `rating`) |
| Ciclo de mejora (qué documentos faltan) | Revisar preguntas recurrentes en `unanswered_log.csv` |
| Ciclo de mejora (ajustes de prompt/recuperación) | Revisar respuestas con `rating = negative` |

El pipeline de actualización de documentos, la curaduría de contenido y la actualización del modelo son procesos externos a este frontend (normalmente re-ejecutar `main.py` cuando cambian los documentos fuente); el chat solo consume el índice vectorial ya generado.
