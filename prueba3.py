import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. IMPORTACIÓN DE PLANTILLAS SEPARADAS ---
from plantillas import PLANTILLAS
try:
    from price_pack import PLANTILLAS_PP
except ImportError:
    PLANTILLAS_PP = {} # Por si aún no creas el archivo

# --- 2. CONFIGURACIÓN ---
st.set_page_config(page_title="Price Architecture Expert Pro", layout="wide")

# --- 3. SELECTOR DE MÓDULO (EL INTERRUPTOR) ---
st.sidebar.header("🚀 Navegación")
modo = st.sidebar.radio("Seleccionar Herramienta:", ["Price Ladder", "Price Pack"])

# Definición de archivos y fuentes según el modo
if modo == "Price Ladder":
    DB_FILE = "historico_ladder.csv"
    fuente_plantillas = PLANTILLAS
    label_agrupador = "Ocasión"
    opciones_agrupador = ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR","REUNIÓN", "FIESTA","TRANSFORMADOR"]
    titulo_app = "📊 ESCALERAS DE PRECIO DINÁMICAS"
else:
    DB_FILE = "historico_price_pack.csv"
    fuente_plantillas = PLANTILLAS_PP
    label_agrupador = "Canal"
    opciones_agrupador = ["CONVENIENCIA", "MAYOREO", "AUTOSERVICIO", "TRADICIONAL", "E-COMMERCE"]
    titulo_app = "📦 PRICE PACK ARCHITECTURE (BARCEL)"

# --- 4. FUNCIONES CORE ---
def calcular_pkg(df):
    if df.empty: return df
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1).replace(0, 1)
    df["SOM (%)"] = pd.to_numeric(df["SOM (%)"], errors='coerce').fillna(0)
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(0)
    return df

# --- 5. GESTIÓN DE ESTADO (SESSION STATE) ---
if "data" not in st.session_state or st.session_state.get('last_modo') != modo:
    if os.path.exists(DB_FILE):
        st.session_state.data = calcular_pkg(pd.read_csv(DB_FILE))
    else:
        columnas = ["Producto", "Fabricante", label_agrupador, "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"]
        st.session_state.data = pd.DataFrame(columns=columnas)
    st.session_state.last_modo = modo

# --- 6. BARRA LATERAL (GESTIÓN) ---
st.sidebar.divider()
st.sidebar.subheader(f"📁 Gestión {modo}")
nombre_plantilla = st.sidebar.selectbox("Cargar Plantilla:", ["-- Seleccionar --"] + list(fuente_plantillas.keys()))

if st.sidebar.button("Cargar Datos"):
    if nombre_plantilla != "-- Seleccionar --":
        nuevos_datos = pd.DataFrame(fuente_plantillas[nombre_plantilla])
        st.session_state.data = calcular_pkg(nuevos_datos)
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Reset"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.rerun()

st.title(titulo_app)

# --- 7. FORMULARIO DINÁMICO ---
with st.expander(f"➕ Agregar nuevo producto a {modo}", expanded=False):
    with st.form("nuevo_sku_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        f_nom = c1.text_input("Nombre del Producto").upper()
        # En Price Pack fijamos Barcel, en Ladder permitimos elegir
        if modo == "Price Pack":
            f_fab = "BARCEL"
            c2.info("Fabricante: BARCEL (Fijo)")
        else:
            f_fab = c2.selectbox("Fabricante", ["BARCEL", "SABRITAS", "OTROS","PROPUESTA"])
        
        f_agrupador = c3.selectbox(label_agrupador, opciones_agrupador)
        
        c4, c5, c6 = st.columns(3)
        f_pre = c4.number_input("Precio ($)", min_value=0.0, step=0.5)
        f_gra = c5.number_input("Gramaje (g)", min_value=1.0, step=1.0)
        f_som = c6.number_input("SOM (%)", min_value=0.0, max_value=100.0, step=0.1)
        
        if st.form_submit_button("Añadir a la lista"):
            nuevo_sku = pd.DataFrame([{"Producto": f_nom, "Fabricante": f_fab, label_agrupador: f_agrupador, "Precio ($)": f_pre, "Gramaje (g)": f_gra, "SOM (%)": f_som}])
            st.session_state.data = pd.concat([st.session_state.data, nuevo_sku], ignore_index=True)
            st.session_state.data = calcular_pkg(st.session_state.data)
            st.session_state.data.to_csv(DB_FILE, index=False)
            st.rerun()

# --- 8. EDITOR ---
st.subheader("📝 Tabla de Datos")
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = calcular_pkg(edited_df)
    st.session_state.data.to_csv(DB_FILE, index=False)
    st.rerun()

# --- 9. GRÁFICO (REUTILIZANDO LÓGICA) ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    
    # Ordenar por Agrupador (Ocasión o Canal)
    if modo == "Price Ladder":
        ord_map = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5,"REUNIÓN":6, "FIESTA":7,"TRANSFORMADOR":8}
    else:
        ord_map = {cat: i for i, cat in enumerate(opciones_agrupador)}
    
    df_p["Orden"] = df_p[label_agrupador].str.upper().map(ord_map).fillna(99)
    df_p = df_p.sort_values(by=["Orden", "Precio ($)"]).reset_index(drop=True)
    
    # Gráfica similar a la tuya pero usando label_agrupador
    # [Aquí se mantiene tu lógica de Plotly, solo asegúrate de cambiar 'Ocasión' por label_agrupador]
    st.info(f"Visualizando datos por {label_agrupador}")
    # (Resto de tu código de Plotly...)
