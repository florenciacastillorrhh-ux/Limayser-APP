import streamlit as st
import pandas as pd
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Configuración visual
st.set_page_config(page_title="SGI - LIMAYSER", layout="centered")

# 1. Carga de la lista de operarios desde tu Excel
try:
    df_nomina = pd.read_excel("nomina.xlsx")
    # Asumimos que la primera columna tiene los nombres
    lista_operarios = df_nomina.iloc[:, 0].dropna().tolist()
except:
    # Lista de respaldo por si el Excel no carga
    lista_operarios = ["Operario 1", "Operario 2", "Operario 3"]

# Estado para evitar doble envío
if 'enviado' not in st.session_state:
    st.session_state.enviado = False

def crear_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Encabezado Formato PG 06 R 1
    pdf.cell(190, 10, "PARTE DIARIO de TRABAJO", border=1, ln=1, align='C')
    pdf.set_font("Arial", "B", 12)
    pdf.cell(95, 10, "LIMAYSER s.r.l", border=1, align='L')
    pdf.cell(95, 10, "COD: PG 06 R 1 - REV: 2", border=1, ln=1, align='R')
    
    pdf.set_font("Arial", "", 10)
    pdf.ln(5)
    pdf.cell(95, 10, f"FECHA: {datos['fecha']}", border=1)
    pdf.cell(95, 10, f"UNIDAD (N°): {datos['unidad']}", border=1, ln=1)
    pdf.cell(190, 10, f"CLIENTE / UBICACIÓN: {datos['cliente']}", border=1, ln=1)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 10, "PERSONAL EN SITIO:", border=1, ln=1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(190, 10, datos['personal'], border=1)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 10, "DETALLE DE TAREAS:", border=1, ln=1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(190, 10, datos['tareas'], border=1)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 10, "MATERIALES UTILIZADOS de STOCK:", border=1, ln=1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(190, 10, datos['materiales'], border=1)

    return pdf.output(dest='S').encode('latin-1')

def enviar_email(pdf_cont, nombre_archivo):
    try:
        remitente = st.secrets["EMAIL_PRUEBA"]
        password = st.secrets["EMAIL_PASS"]
        
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = remitente
        msg['Subject'] = f"SGI LIMAYSER - Nuevo Parte: {nombre_archivo}"
        
        adj = MIMEBase('application', 'octet-stream')
        adj.set_payload(pdf_cont)
        encoders.encode_base64(adj)
        adj.add_header('Content-Disposition', f"attachment; filename={nombre_archivo}")
        msg.attach(adj)
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error técnico en el envío: {e}")
        return False

# --- INTERFAZ ---
st.title("🏗️ Registro Digital PG 06 R 1")

if st.session_state.enviado:
    st.success("✅ ¡PDF enviado correctamente a tu mail!")
    if st.button("Cargar otro Parte"):
        st.session_state.enviado = False
        st.rerun()
else:
    with st.form("form_limayser", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            f_fecha = st.date_input("FECHA", value=datetime.now())
            f_unidad = st.text_input("UNIDAD (N°)")
        with col2:
            f_cliente = st.text_input("CLIENTE / UBICACIÓN")
            f_personal = st.multiselect("OPERARIOS:", options=lista_operarios)
        
        f_tareas = st.text_area("DETALLE DE TAREAS REALIZADAS")
        f_materiales = st.text_area("MATERIALES DE STOCK UTILIZADOS")
        
        enviar = st.form_submit_button("VALIDAR Y ENVIAR PARTE")
        
        if enviar:
            if f_unidad and f_cliente and f_personal:
                personal_str = ", ".join(f_personal)
                datos = {
                    'fecha': f_fecha, 'unidad': f_unidad, 'cliente': f_cliente,
                    'personal': personal_str, 'tareas': f_tareas, 'materiales': f_materiales
                }
                archivo_pdf = crear_pdf(datos)
                if enviar_email(archivo_pdf, f"Parte_{f_unidad}.pdf"):
                    st.session_state.enviado = True
                    st.rerun()
            else:
                st.warning("⚠️ Por favor, completá los campos de Unidad, Cliente y seleccioná al menos un Operario.")
