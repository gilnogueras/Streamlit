import streamlit as st
import json
import fitz  # PyMuPDF
import tempfile

st.title("Test de Función Hepática")

# Función para extraer texto del PDF
def extraer_preguntas(pdf_path):
    doc = fitz.open(pdf_path)
    preguntas = []
    for page in doc:
        text = page.get_text("text")
        preguntas.extend(text.split("\n"))  # Dividir por líneas
    return preguntas

# Subir archivo PDF
uploaded_file = st.file_uploader("Sube un archivo PDF con preguntas de test", type=["pdf"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_pdf_path = temp_file.name
    
    st.success("Archivo subido con éxito. Procesando...")
    preguntas_extraidas = extraer_preguntas(temp_pdf_path)
    st.write("Preguntas extraídas:")
    for p in preguntas_extraidas[:10]:  # Mostrar solo algunas preguntas
        st.write(p)

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

st.success("Archivo subido con éxito. Procesando...")
preguntas_extraidas = extraer_preguntas(temp_pdf_path)
st.write(f"Se han extraído {len(preguntas_extraidas)} líneas de texto.")

