import streamlit as st
import fitz  # PyMuPDF
import tempfile
import re
import cv2
import numpy as np
from pdf2image import convert_from_path
import pytesseract

st.title("Test de Función Hepática")

# Función para extraer texto de imágenes con OCR
def extraer_texto_resaltado(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    result = cv2.bitwise_and(img, img, mask=mask)
    
    # Reducir tamaño de imagen para mejorar velocidad
    result = cv2.resize(result, (0, 0), fx=0.5, fy=0.5)
    
    gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    text = pytesseract.image_to_string(gray, config='--psm 6')
    return text.strip()

# Función para extraer preguntas y respuestas del PDF con OCR
def extraer_preguntas(pdf_path):
    images = convert_from_path(pdf_path)
    preguntas = []
    patron_pregunta = re.compile(r"^\d+\..+")
    
    pregunta_actual = None
    opciones = []
    respuesta_correcta = None
    respuestas_resaltadas = []
    
    for img in images:
        img_cv = np.array(img)
        texto_resaltado = extraer_texto_resaltado(img_cv)
        respuestas_resaltadas.extend(texto_resaltado.split("\n"))
        
        text = pytesseract.image_to_string(img_cv, config='--psm 6')
        for line in text.split("\n"):
            line = line.strip()
            if patron_pregunta.match(line):
                if pregunta_actual:
                    preguntas.append({"pregunta": pregunta_actual, "opciones": opciones, "respuesta_correcta": respuesta_correcta})
                pregunta_actual = line
                opciones = []
                respuesta_correcta = None
            elif line.startswith(("A)", "B)", "C)", "D)")):
                opciones.append(line)
                if any(line in res for res in respuestas_resaltadas):
                    respuesta_correcta = line
    
    if pregunta_actual:
        preguntas.append({"pregunta": pregunta_actual, "opciones": opciones, "respuesta_correcta": respuesta_correcta})
    
    return preguntas, respuestas_resaltadas

# Subir archivo PDF
uploaded_file = st.file_uploader("Sube un archivo PDF con preguntas de test", type=["pdf"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_pdf_path = temp_file.name

    st.success("Archivo subido con éxito. Procesando...")
    preguntas_extraidas, respuestas_resaltadas = extraer_preguntas(temp_pdf_path)

    # Mostrar respuestas resaltadas detectadas para depuración
    st.write("Respuestas resaltadas detectadas en el PDF:")
    st.write(respuestas_resaltadas)

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
