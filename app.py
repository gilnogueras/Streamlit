import streamlit as st
import fitz  # PyMuPDF
import tempfile
import re

st.title("Test de Función Hepática")

# Función para extraer preguntas del PDF y estructurarlas
def extraer_preguntas(pdf_path):
    doc = fitz.open(pdf_path)
    preguntas = []
    patron_pregunta = re.compile(r"^\d+\..+")  # Detecta líneas que parecen preguntas (ej: "1. ¿Cuál es...?")

    pregunta_actual = None
    opciones = []

    for page in doc:
        for line in page.get_text("text").split("\n"):
            line = line.strip()
            if patron_pregunta.match(line):  # Si la línea parece una pregunta
                if pregunta_actual:
                    preguntas.append({"pregunta": pregunta_actual, "opciones": opciones})
                pregunta_actual = line
                opciones = []
            elif line.startswith(("A)", "B)", "C)", "D)")):  # Si es una opción de respuesta
                opciones.append(line)

    if pregunta_actual:
        preguntas.append({"pregunta": pregunta_actual, "opciones": opciones})  # Añadir última pregunta

    return preguntas

# Subir archivo PDF
uploaded_file = st.file_uploader("Sube un archivo PDF con preguntas de test", type=["pdf"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_pdf_path = temp_file.name

    st.success("Archivo subido con éxito. Procesando...")
    preguntas_extraidas = extraer_preguntas(temp_pdf_path)

    if preguntas_extraidas:
        st.success("Procesamiento completado. Ahora puedes responder las preguntas.")

        for q in preguntas_extraidas:
            respuesta = st.radio(q["pregunta"], q["opciones"])
            if st.button(f"Verificar {q['pregunta'][:10]}..."):
                st.write(f"Has seleccionado: {respuesta}")
    else:
        st.error("No se pudieron extraer preguntas del archivo.")

# Preguntas de ejemplo (esto se reemplazará con las extraídas del PDF)
questions_data = [
    {
        "pregunta": "¿Cuál de estas pruebas no es una prueba funcional hepática?",
        "opciones": ["A) Prueba de Mac-Lagan", "B) Prueba de rosa de Bengala", "C) Prueba de Schales-Schales", "D) Prueba de Hanger"],
        "respuesta_correcta": "C) Prueba de Schales-Schales"
    },
    {
        "pregunta": "¿Cuál de las siguientes enzimas es más específica del hígado?",
        "opciones": ["A) Lactato deshidrogenasa", "B) GOT", "C) GPT", "D) Fosfatasa alcalina"],
        "respuesta_correcta": "C) GPT"
    }
]

score = 0

def mostrar_pregunta(pregunta, opciones, respuesta_correcta):
    respuesta = st.radio(pregunta, opciones)
    if st.button(f"Verificar {pregunta[:10]}..."):
        if respuesta == respuesta_correcta:
            st.success("¡Correcto!")
        else:
            st.error(f"Incorrecto. La respuesta correcta es: {respuesta_correcta}")

for q in questions_data:
    mostrar_pregunta(q["pregunta"], q["opciones"], q["respuesta_correcta"])
