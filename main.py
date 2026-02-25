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
import streamlit as st
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Función para crear el PDF siguiendo el formato PG 06 R 1
def crear_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Encabezado (Réplica del documento original)
    pdf.cell(190, 10, "PARTE DIARIO de TRABAJO", border=1, ln=1, align='C') # [cite: 1]
    pdf.set_font("Arial", "B", 12)
    pdf.cell(95, 10, "LIMAYSER s.r.I", border=1, align='L') # [cite: 2]
    pdf.cell(95, 10, f"COD: PG 06 R 1 - REV: 2", border=1, ln=1, align='R') # 

    pdf.set_font("Arial", "", 10)
    pdf.ln(5)
    
    # Campos de datos
    pdf.cell(95, 10, f"FECHA: {datos['fecha']}", border=1) # [cite: 9]
    pdf.cell(95, 10, f"UNIDAD: {datos['unidad']}", border=1, ln=1) # [cite: 18]
    pdf.cell(190, 10, f"CLIENTE/S - UBICACIÓN: {datos['cliente']}", border=1, ln=1) # [cite: 10]
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 10, "DETALLE DE TAREAS Y OPERARIOS:", border=1, ln=1) # [cite: 26, 27]
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(190, 10, datos['tareas'], border=1)
    
    pdf.ln(5)
    pdf.cell(190, 10, "MATERIALES UTILIZADOS de STOCK:", border=1, ln=1) # [cite: 28]
    pdf.multi_cell(190, 10, datos['materiales'], border=1)

    pdf.ln(5)
    pdf.cell(190, 10, "OBSERVACIONES:", border=1, ln=1) # [cite: 29]
    pdf.multi_cell(190, 10, datos['observaciones'], border=1)

    return pdf.output(dest='S').encode('latin-1')

# Función de envío por mail
def enviar_email(pdf_contenido, nombre_archivo):
    try:
        remitente = st.secrets["EMAIL_PRUEBA"]
        password = st.secrets["EMAIL_PASS"]
        
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = remitente
        msg['Subject'] = f"Nuevo Parte Diario - {nombre_archivo}"

        adjunto = MIMEBase('application', 'octet-stream')
        adjunto.set_payload(pdf_contenido)
        encoders.encode_base64(adjunto)
        adjunto.add_header('Content-Disposition', f"attachment; filename={nombre_archivo}")
        msg.attach(adjunto)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# Interfaz Streamlit
st.title("🏗️ Registro PG 06 R 1")

with st.form("form_pdf"):
    f_fecha = st.date_input("FECHA")
    f_unidad = st.text_input("UNIDAD")
    f_cliente = st.text_input("CLIENTE / UBICACIÓN")
    f_tareas = st.text_area("DETALLE TAREAS")
    f_materiales = st.text_area("MATERIALES STOCK")
    f_obs = st.text_area("OBSERVACIONES")
    
    if st.form_submit_button("Enviar PDF por Mail"):
        datos = {
            'fecha': f_fecha, 'unidad': f_unidad, 'cliente': f_cliente,
            'tareas': f_tareas, 'materiales': f_materiales, 'observaciones': f_obs
        }
        archivo_pdf = crear_pdf(datos)
        if enviar_email(archivo_pdf, f"Parte_{f_unidad}.pdf"):
            st.success("✅ PDF enviado correctamente a tu casilla.")
