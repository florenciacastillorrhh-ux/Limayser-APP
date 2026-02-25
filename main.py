import streamlit as st
import pandas as pd
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

st.set_page_config(page_title="SGI - LIMAYSER", layout="centered")

# --- LECTURA DE NÓMINA ---
def cargar_nomina():
    try:
        # Forzamos el motor openpyxl para evitar errores de lectura
        df = pd.read_excel("nomina.xlsx", engine='openpyxl')
        return df.iloc[:, 0].dropna().astype(str).tolist()
    except:
        return []

lista_operarios = cargar_nomina()

if 'enviado' not in st.session_state:
    st.session_state.enviado = False

# --- GENERADOR DE PDF ---
def crear_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    # Encabezado
    pdf.cell(190, 10, "PARTE DIARIO de TRABAJO", border=1, ln=1, align='C')
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 8, "LIMAYSER s.r.l", border=1, align='L')
    pdf.cell(95, 8, "COD: PG 06 R 1 - REV: 2", border=1, ln=1, align='R')
    
    pdf.set_font("Arial", "", 9)
    pdf.ln(4)
    # Datos de Obra
    pdf.cell(63, 8, f"FECHA: {datos['fecha']}", border=1)
    pdf.cell(63, 8, f"UNIDAD: {datos['unidad']}", border=1)
    pdf.cell(64, 8, f"PRESUPUESTO: {datos['presupuesto']}", border=1, ln=1)
    
    pdf.cell(190, 8, f"CLIENTE / UBICACIÓN: {datos['cliente']}", border=1, ln=1)
    pdf.cell(190, 8, f"TIPO DE TRABAJO: {datos['tipo']}", border=1, ln=1)
    
    # Horarios
    pdf.cell(63, 8, f"HS. INICIO: {datos['h_in']}", border=1)
    pdf.cell(63, 8, f"HS. VIAJE: {datos['h_viaje']}", border=1)
    pdf.cell(64, 8, f"HS. FINAL: {datos['h_fin']}", border=1, ln=1)

    pdf.ln(4)
    pdf.multi_cell(190, 8, f"OPERARIOS PARTICIPANTES:\n{datos['personal']}", border=1)
    pdf.multi_cell(190, 8, f"DETALLE TAREAS:\n{datos['tareas']}", border=1)
    pdf.multi_cell(190, 8, f"MATERIALES UTILIZADOS:\n{datos['materiales']}", border=1)
    pdf.multi_cell(190, 8, f"OBSERVACIONES:\n{datos['obs']}", border=1)
    
    return pdf.output(dest='S').encode('latin-1')

def enviar_email(pdf_cont, nombre_archivo):
    try:
        remitente = st.secrets["EMAIL_PRUEBA"]
        password = st.secrets["EMAIL_PASS"]
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = remitente
        msg['Subject'] = f"SGI LIMAYSER - {nombre_archivo}"
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
        st.error(f"Error de envío: {e}")
        return False

# --- INTERFAZ ---
st.title("🏗️ Registro Digital PG 06 R 1")

if st.session_state.enviado:
    st.success("✅ Parte enviado correctamente.")
    if st.button("Cargar otro"):
        st.session_state.enviado = False
        st.rerun()
else:
    # Si la lista está vacía, mostramos una advertencia
    if not lista_operarios:
        st.warning("⚠️ No se cargó la nómina. Verifica que 'nomina.xlsx' esté en GitHub.")
    
    with st.form("form_limayser"):
        c1, c2, c3 = st.columns(3)
        with c1: f_fecha = st.date_input("FECHA")
        with c2: f_unidad = st.text_input("UNIDAD (N°)")
        with c3: f_presupuesto = st.text_input("PRESUPUESTO (N°)")
        
        f_cliente = st.text_input("CLIENTE / UBICACIÓN / CONTACTO")
        f_tipo = st.multiselect("TIPO DE TRABAJO", ["Mantenimiento", "Jardinería", "Carpintería", "Obra civil", "Refrigeración", "Metálica", "General"])
        
        h1, h2, h3 = st.columns(3)
        with h1: f_h_in = st.time_input("Inicio")
        with h2: f_h_viaje = st.number_input("Hs. Viaje", min_value=0.0)
        with h3: f_h_fin = st.time_input
