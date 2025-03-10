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
    respuesta_correcta = None

    for page in doc:
        for line in page.get_text("text").split("\n"):
            line = line.strip()
            if patron_pregunta.match(line):  # Si la línea parece una pregunta
                if pregunta_actual:
                    preguntas.append({"pregunta": pregunta_actual, "opciones": opciones, "respuesta_correcta": respuesta_correcta})
                pregunta_actual = line
                opciones = []
                respuesta_correcta = None
            elif line.startswith(("A)", "B)", "C)", "D)")) or line.startswith("*"):
                if line.startswith("*"):
                    respuesta_correcta = line[1:].strip()  # Eliminar el asterisco para mostrar la opción limpia
                opciones.append(line.lstrip("*"))  # Eliminar asterisco si existe
    
    if pregunta_actual:
        preguntas.append({"pregunta": pregunta_actual, "opciones": opciones, "respuesta_correcta": respuesta_correcta})
    
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

        for i, q in enumerate(preguntas_extraidas):
            with st.expander(q["pregunta"]):
                respuesta = st.radio("Selecciona una respuesta:", q["opciones"], key=f"radio_{i}")
                if st.button("Verificar", key=f"btn_{i}"):
                    if q["respuesta_correcta"]:
                        if respuesta == q["respuesta_correcta"]:
                            st.success("¡Correcto!")
                        else:
                            st.error(f"Incorrecto. La respuesta correcta es: {q['respuesta_correcta']}")
                    else:
                        st.warning("No se encontró la respuesta correcta en los datos extraídos.")
    else:
        st.error("No se pudieron extraer preguntas del archivo.")
