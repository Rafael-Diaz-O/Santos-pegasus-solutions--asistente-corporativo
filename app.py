"""
app.py
======
Interfaz de chat simple y funcional para el agente interno (RAG).
Ejecutar con:

    streamlit run app.py

No busca ser un diseño elaborado: cumple lo pedido (campo de pregunta,
historial de conversación, fuentes citadas, feedback, y aviso de que es un
agente de IA) con el mínimo de fricción.
"""

import streamlit as st
from backend import get_answer, log_feedback

st.set_page_config(page_title="Asistente Interno", page_icon="🤖", layout="centered")

# --------------------------------------------------------------------------
# Estado de sesión
# --------------------------------------------------------------------------
if "messages" not in st.session_state:
    # Cada mensaje: {"role": "user"/"assistant", "content": str,
    #                "sources": [...], "feedback": None/"positive"/"negative"}
    st.session_state.messages = []

# --------------------------------------------------------------------------
# Encabezado + aviso obligatorio de que es un agente de IA
# --------------------------------------------------------------------------
st.title("🤖 Asistente Interno")
st.caption("Estás conversando con un agente de IA, no con una persona.")

st.divider()

# --------------------------------------------------------------------------
# Historial de conversación
# --------------------------------------------------------------------------
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant":
            # Fuentes citadas
            if msg.get("sources"):
                with st.expander("📄 Fuentes utilizadas"):
                    for src in msg["sources"]:
                        st.markdown(f"- **{src['title']}**")
            else:
                st.caption("Sin fuentes específicas para esta respuesta.")

            # Botones de feedback (solo si aún no se han votado)
            col1, col2, col3 = st.columns([1, 1, 8])
            feedback = msg.get("feedback")

            with col1:
                if st.button("👍", key=f"up_{idx}", disabled=feedback is not None):
                    msg["feedback"] = "positive"
                    log_feedback(
                        question=st.session_state.messages[idx - 1]["content"],
                        answer=msg["content"],
                        rating="positive",
                    )
                    st.rerun()
            with col2:
                if st.button("👎", key=f"down_{idx}", disabled=feedback is not None):
                    msg["feedback"] = "negative"
                    log_feedback(
                        question=st.session_state.messages[idx - 1]["content"],
                        answer=msg["content"],
                        rating="negative",
                    )
                    st.rerun()
            with col3:
                if feedback == "positive":
                    st.caption("Gracias por tu feedback ✅")
                elif feedback == "negative":
                    st.caption("Gracias, lo tendremos en cuenta ✅")

# --------------------------------------------------------------------------
# Campo de pregunta
# --------------------------------------------------------------------------
question = st.chat_input("Escribe tu pregunta...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Historial en formato simple (role/content) para pasarle contexto al LLM
    history_for_llm = [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Buscando en la documentación..."):
            result = get_answer(question, history_for_llm)
        st.markdown(result["answer"])
        if result["sources"]:
            with st.expander("📄 Fuentes utilizadas"):
                for src in result["sources"]:
                    st.markdown(f"- **{src['title']}**")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
        "feedback": None,
    })
    st.rerun()

# --------------------------------------------------------------------------
# Barra lateral: utilidades rápidas
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("Opciones")
    if st.button("🗑️ Nueva conversación"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption(
        "Este chat conserva el historial solo durante la sesión actual. "
        "Las respuestas se generan a partir de documentos indexados; "
        "las preguntas sin respuesta y el feedback negativo quedan "
        "registrados para revisión del equipo (ver `feedback_log.csv` "
        "y `unanswered_log.csv`)."
    )