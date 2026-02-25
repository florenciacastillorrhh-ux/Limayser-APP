import streamlit as st
import pandas as pd
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

st.set_page_config(page_title="SGI - LIMAYSER", layout="centered")

# 1. Carga de Nómina
try:
    df_nomina = pd.read_excel("nomina.xlsx")
    lista_operarios = df_nomina.iloc[:, 0].dropna().tolist()
except:
    lista_operarios = ["Operario 1", "Operario 2", "Operario 3"]

if 'enviado' not in st.session_state:
    st.session_state.enviado = False

def crear_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    # Encabezado oficial PG 06 R 1 [cite: 2, 5, 6]
    pdf.cell(190, 10, "PARTE DIARIO de TRABAJO", border=1, ln=1, align='C')
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 8, "LIMAYSER s.r.l", border=1, align='L')
    pdf.cell(95, 8, "COD: PG 06 R 1 - REV: 2", border=1, ln=1, align='R')
    
    pdf.set_font("Arial", "", 9)
    pdf.ln(4)
    # Fila: Fecha, Unidad y Presupuesto [cite: 12, 15, 18]
    pdf.cell(63, 8, f"FECHA: {datos['fecha']}", border=1)
    pdf.cell(63, 8, f"UNIDAD N°: {datos['unidad']}", border=1)
    pdf.cell(64, 8, f"PRESUPUESTO N°: {datos['presupuesto']}", border=1, ln=1)
    
    # Fila: Cliente y Tipo de Trabajo [cite: 8, 10]
    pdf.cell(126, 8, f"CLIENTE / UBICACIÓN: {datos['cliente']}", border=1)
    pdf.cell(64, 8, f"TIPO: {datos['tipo']}", border=1, ln=1)
    
    # Fila: Horarios [cite: 16]
    pdf.cell(63, 8, f"HS. INICIO: {datos['h_in']}", border=1)
    pdf.cell(63, 8, f"HS. VIAJE: {datos['h_viaje']}", border=1)
    pdf.cell(64, 8, f"HS. FINAL: {datos['h_fin']}", border=1, ln=1)

    pdf.ln(4)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(190, 8, "DETALLE: Tareas y Operarios participantes", border=1, ln=1)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(190, 8, f"PERSONAL: {datos['personal']}\nTAREAS: {datos['tareas']}", border=1)
    
    pdf.ln(4)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(190, 8, "MATERIALES UTILIZADOS de STOCK", border=1, ln=1)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(190, 8, datos['materiales'], border=1)
    
    pdf.ln(4)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(190, 8, "OBSERVACIONES - COMENTARIOS", border=1, ln=1)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(190, 8, datos['obs'], border=1)
    
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
        st.error(f"Error: {e}")
        return False

# --- INTERFAZ ---
st.title("🏗️ Registro Digital PG 06 R 1")

if st.session_state.enviado:
    st.success("✅ Parte enviado con éxito.")
    if st.button("Cargar otro"):
        st.session_state.enviado = False
        st.rerun()
else:
    with st.form("form_limayser"):
        c1, c2, c3 = st.columns(3)
        with c1: f_fecha = st.date_input("FECHA")
        with c2: f_unidad = st.text_input("UNIDAD N°") # [cite: 18]
        with c3: f_presupuesto = st.text_input("PRESUPUESTO N°") # [cite: 15]
        
        f_cliente = st.text_input("CLIENTE / UBICACIÓN / CONTACTOS") # [cite: 10]
        f_tipo = st.multiselect("TIPO DE TRABAJO", ["Mantenimiento", "Jardinería", "Carpintería", "Obra civil", "Refrigeración", "Metálica", "General"]) # [cite: 8, 10]
        
        h1, h2, h3 = st.columns(3)
        with h1: f_h_in = st.time_input("Inicio") # [cite: 16]
        with h2: f_h_viaje = st.number_input("Hs. Viaje", min_value=0.0, step=0.5) # [cite: 16]
        with h3: f_h_fin = st.time_input("Final") # [cite: 16]
        
        f_personal = st.multiselect("OPERARIOS:", options=lista_operarios) # [cite: 27]
        f_tareas = st.text_area("DETALLE TAREAS") # [cite: 26, 27]
        f_materiales = st.text_area("MATERIALES STOCK") # [cite: 28]
        f_obs = st.text_area("OBSERVACIONES") # [cite: 29]
        
        submit = st.form_submit_button("VALIDAR Y ENVIAR") # El botón que faltaba
        
        if submit:
            if f_unidad and f_cliente and f_personal:
                datos = {
                    'fecha': f_fecha, 'unidad': f_unidad, 'presupuesto': f_presupuesto,
                    'cliente': f_cliente, 'tipo': ", ".join(f_tipo),
                    'h_in': f_h_in, 'h_viaje': f_h_viaje, 'h_fin': f_h_fin,
                    'personal': ", ".join(f_personal), 'tareas': f_tareas,
                    'materiales': f_materiales, 'obs': f_obs
                }
                archivo_pdf = crear_pdf(datos)
                if enviar_email(archivo_pdf, f"Parte_{f_unidad}.pdf"):
                    st.session_state.enviado = True
                    st.rerun()
            else:
                st.warning("Completá Unidad, Cliente y Operarios.")
