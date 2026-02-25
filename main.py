import streamlit as st
import pandas as pd
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os

# Configuración de página
st.set_page_config(page_title="SGI - LIMAYSER", layout="centered")

# --- LECTURA DE NÓMINA ---
def obtener_ruta_nomina():
    # Buscamos el archivo en la carpeta principal
    for root, dirs, files in os.walk("."):
        if "nomina.xlsx" in files:
            return os.path.join(root, "nomina.xlsx")
    return None

def cargar_nomina():
    ruta = obtener_ruta_nomina()
    if ruta:
        try:
            df = pd.read_excel(ruta, engine='openpyxl')
            return df.iloc[:, 0].dropna().astype(str).tolist()
        except Exception as e:
            st.sidebar.error(f"Error al leer: {e}")
            return []
    return []

lista_operarios = cargar_nomina()

if 'enviado' not in st.session_state:
    st.session_state.enviado = False

# --- GENERADOR DE PDF (Formato PG 06 R 1 Rev. 2) ---
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
    pdf.cell(63, 8, f"UNIDAD N°: {datos['unidad']}", border=1)
    pdf.cell(64, 8, f"PRESUPUESTO N°: {datos['presupuesto']}", border=1, ln=1)
    
    pdf.cell(190, 8, f"CLIENTE/UBICACIÓN/CONTACTO: {datos['cliente']}", border=1, ln=1)
    pdf.cell(190, 8, f"TIPO DE TRABAJO: {datos['tipo']}", border=1, ln=1)
    
    # Horarios
    pdf.cell(63, 8, f"HS. INICIO: {datos['h_in']}", border=1)
    pdf.cell(63, 8, f"HS. VIAJE: {datos['h_viaje']}", border=1)
    pdf.cell(64, 8, f"HS. FINAL: {datos['h_fin']}", border=1, ln=1)

    pdf.ln(4)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(190, 8, "DETALLE: Tareas realizadas y operarios participantes", border=1, ln=1)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(190, 8, f"OPERARIOS: {datos['personal']}\n\nTAREAS: {datos['tareas']}", border=1)
    
    pdf.ln(4)
    pdf.cell(190, 8, "MATERIALES UTILIZADOS de STOCK:", border=1, ln=1)
    pdf.multi_cell(190, 8, datos['materiales'], border=1)
    
    pdf.ln(4)
    pdf.cell(190, 8, "OBSERVACIONES - COMENTARIOS:", border=1, ln=1)
    pdf.multi_cell(190, 8, datos['obs'], border=1)
    
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
    st.success("✅ ¡Parte enviado con éxito!")
    if st.button("Cargar nuevo Parte Diario"):
        st.session_state.enviado = False
        st.rerun()
else:
    if not lista_operarios:
        st.warning("⚠️ No se detectó 'nomina.xlsx'. Revisa GitHub.")
        lista_operarios = ["Cargar nomina.xlsx para ver personal"]

    with st.form("form_oficial"):
        c1, c2, c3 = st.columns(3)
        with c1: f_fecha = st.date_input("FECHA")
        with c2: f_unidad = st.text_input("UNIDAD N°")
        with c3: f_presupuesto = st.text_input("PRESUPUESTO N°")
        
        f_cliente = st.text_input("CLIENTE / UBICACIÓN / CONTACTOS")
        f_tipo = st.multiselect("TIPO DE TRABAJO", ["Mantenimiento", "Jardinería", "Carpintería", "Obra civil", "Refrigeración", "Metálica", "General"])
        
        h1, h2, h3 = st.columns(3)
        with h1: f_h_in = st.time_input("Hs. Inicio")
        with h2: f_h_viaje = st.number_input("Hs. Viaje", min_value=0.0, step=0.5)
        with h3: f_h_fin = st.time_input("Hs. Final")
        
        f_personal = st.multiselect("OPERARIOS PARTICIPANTES:", options=lista_operarios)
        f_tareas = st.text_area("DETALLE TAREAS REALIZADAS")
        f_materiales = st.text_area("MATERIALES STOCK")
        f_obs = st.text_area("OBSERVACIONES (Remitos, inconvenientes, etc.)")
        
        if st.form_submit_button("VALIDAR Y ENVIAR PARTE"):
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
                st.error("⚠️ Unidad, Cliente y Operarios son obligatorios.")
import streamlit as st
import pandas as pd
import os

# --- CARGA DE NÓMINA REFORZADA ---
def cargar_personal():
    archivo_nombre = "nomina.xlsx"
    # Verificamos si el archivo existe físicamente en el servidor
    if os.path.exists(archivo_nombre):
        try:
            # Leemos sin usar caché para asegurar que tome los cambios
            df = pd.read_excel(archivo_nombre, engine='openpyxl')
            # Tomamos la primera columna y limpiamos nombres vacíos
            nombres = df.iloc[:, 0].dropna().astype(str).tolist()
            if len(nombres) > 0:
                return nombres
        except Exception as e:
            st.sidebar.error(f"Error al abrir el archivo: {e}")
    return []

lista_operarios = cargar_personal()

# Si la lista sigue vacía, mostramos el aviso
if not lista_operarios:
    st.warning("⚠️ No se detectaron nombres en 'nomina.xlsx'.")
    lista_operarios = ["Cargar personal en nomina.xlsx"]
