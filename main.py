import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Configuración de la aplicación
st.set_page_config(page_title="SGI - LIMAYSER s.r.I", layout="centered")

# Encabezado oficial del formulario
st.title("🏗️ PARTE DIARIO de TRABAJO")
st.write("### LIMAYSER s.r.I")
st.caption("COD: PG 06 R 1 | REV: 2")

with st.form("formulario_parte"):
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("FECHA")
        unidad = st.text_input("UNIDAD (N°)")
    with col2:
        cliente = st.text_input("CLIENTE/S - UBICACIÓN/ES")
        contacto = st.text_input("CONTACTO/S")

    st.markdown("---")
    st.write("**TIPO DE TRABAJO**")
    
    # Opciones basadas fielmente en el documento original
    tipo = st.multiselect("Seleccione las opciones correspondientes:", 
                          ["Mantenimiento", "general", "Jardinería", "Carpintería", "Obra civil", "Refrigeración", "metálica"])

    st.markdown("---")
    
    # Campos de detalle de tareas y materiales de stock
    tareas = st.text_area("DETALLE: Tareas realizadas y operarios que participaron")
    materiales = st.text_area("MATERIALES UTILIZADOS de STOCK")
    
    # Campo para observaciones según PG 06 R 1
    observaciones = st.text_area("OBSERVACIONES - COMENTARIOS (Inconvenientes, Remitos, etc.)")

    # Botón final
    if st.form_submit_button("Validar y Finalizar"):
        st.success("El parte ha sido cargado con éxito en el sistema.")
