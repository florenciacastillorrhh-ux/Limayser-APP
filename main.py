import streamlit as st
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Configuración de la App
st.set_page_config(page_title="SGI - LIMAYSER", layout="centered")

# Inicializamos un estado para evitar el doble envío
if 'enviado' not in st.session_state:
    st.session_state.enviado = False

def crear_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "PARTE DIARIO de TRABAJO", border=1, ln=1, align='C')
    pdf.set_font("Arial", "B", 12)
    pdf.cell(95, 10, "LIMAYSER s.r.I", border=1, align='L')
    pdf.cell(95, 10, "COD: PG 06 R 1 - REV: 2", border=1, ln=1, align='R')
    pdf.set_font("Arial", "", 10)
    pdf.ln(5)
    pdf.cell(95, 10, f"FECHA: {datos['fecha']}", border=1)
    pdf.cell(95, 10, f"UNIDAD: {datos['unidad']}", border=1, ln=1)
    pdf.cell(190, 10, f"CLIENTE: {datos['cliente']}", border=1, ln=1)
    pdf.ln(5)
    pdf.multi_cell(190, 10, f"TAREAS REALIZADAS:\n{datos['tareas']}", border=1)
    pdf.multi_cell(190, 10, f"MATERIALES DE STOCK:\n{datos['materiales']}", border=1)
    return pdf.output(dest='S').encode('latin-1')

def enviar_email(pdf_cont, nombre_archivo):
    try:
        remitente = st.secrets["EMAIL_PRUEBA"]
        password = st.secrets["EMAIL_PASS"]
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = remitente
        msg['Subject'] = f"Nuevo Parte Diario - {nombre_archivo}"
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
    except Exception
