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
    resaltados_detectados = []

    for page in doc:
        highlights = []
        for annot in page.annots():
            if annot.type[0] == 8:  # Tipo 8 = Resaltado
                rect = annot.rect  # Obtener la posición del resaltado
                text_highlighted = page.get_text("text", clip=rect).strip()  # Extraer texto resaltado
                if text_highlighted:
                    highlights.append(text_highlighted)
                    resaltados_detectados.append(text_highlighted)  # Guardar para depuración

        for line in page.get_text("text").split("\n"):
            line = line.strip()
            if patron_pregunta.match(line):  # Si la línea parece una pregunta
                if pregunta_actual:
                    preguntas.append({"pregunta": pregunta_actual, "opciones": opciones, "respuesta_correcta": respuesta_correcta})
                pregunta_actual = line
                opciones = []
                respuesta_correcta = None
            elif line.startswith(("A)", "B)", "C)", "D)")):  # Si es una opción de respuesta
                opciones.append(line)
                for h in highlights:
                    if h in line:
                        respuesta_correcta = line

    if pregunta_actual:
        preguntas.append({"pregunta": pregunta_actual, "opciones": opciones, "respuesta_correcta": respuesta_correcta})  # Añadir última pregunta

    return preguntas, resaltados_detectados

# Subir archivo PDF
uploaded_file = st.file_uploader("Sube un archivo PDF con preguntas de test", type=["pdf"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_pdf_path = temp_file.name

    st.success("Archivo subido con éxito. Procesando...")
    preguntas_extraidas, resaltados_detectados = extraer_preguntas(temp_pdf_path)

    # Mostrar resaltados detectados para depuración
    st.write("Resaltados detectados en el PDF:")
    st.write(resaltados_detectados)

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
