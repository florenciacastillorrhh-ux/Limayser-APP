import streamlit as st
import pandas as pd
from datetime import datetime
import io

# [cite_start]Configuración de la aplicación basada en el documento PG 06 R 1 [cite: 5]
st.set_page_config(page_title="SGI - LIMAYSER s.r.I", layout="centered")

# [cite_start]Encabezado oficial [cite: 1, 2, 5, 6]
st.title("🏗️ PARTE DIARIO de TRABAJO")
st.write("### LIMAYSER s.r.I")
st.caption("COD: PG 06 R 1 | REV: 2")

with st.form("formulario_parte"):
    col1, col2 = st.columns(2)
    with col1:
        [cite_start]fecha = st.date_input("FECHA") [cite: 9]
        [cite_start]unidad = st.text_input("UNIDAD") [cite: 18]
    with col2:
        [cite_start]cliente = st.text_input("CLIENTE/S - UBICACIÓN/ES") [cite: 10]
        [cite_start]contacto = st.text_input("CONTACTO/S") [cite: 10]

    st.markdown("---")
    # [cite_start]Tipos de trabajo según el formulario [cite: 8, 11, 19, 21, 23, 24, 25]
    st.write("**TIPO DE TRABAJO**")
    tipo = st.multiselect("Seleccione las opciones correspondientes:", 
                          ["Mantenimiento", "general", "Jardinería", "Carpintería", "Obra civil", "Refrigeración", "metálica"])

    # [cite_start]Campos de detalle y stock [cite: 27, 28, 29]
    st.write("---")
    [cite_start]tareas = st.text_area("DETALLE: Tareas realizadas y operarios que participaron") [cite: 26, 27]
    [cite_start]materiales = st.text_area("MATERIALES UTILIZADOS de STOCK") [cite: 28]
    [cite_start]observaciones = st.text_area("OBSERVACIONES - COMENTARIOS (Inconvenientes, Remitos, etc.)") [cite: 29]

    if st.form_submit_button("Validar y Cargar"):
        st.success("El parte ha sido validado correctamente.")
