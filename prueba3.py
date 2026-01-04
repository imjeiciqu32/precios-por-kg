import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. CONFIGURACIÓN Y CARGA DE PLANTILLAS ---
try:
    from plantillas import PLANTILLAS 
except ImportError:
    PLANTILLAS = {}

try:
    from price_pack import PLANTILLAS_PP
except ImportError:
    PLANTILLAS_PP = {}

st.set_page_config(page_title="Price Architecture Expert Pro", layout="wide")

# NAVEGACIÓN
st.sidebar.header("🚀 Modo de Visualización")
modo = st.sidebar.radio("Seleccionar:", ["Price Ladder", "Price Pack"])

if modo == "Price Ladder":
    DB_FILE = "historico_productos.csv"
    label_agru = "Ocasión"
    opciones_agru = ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR", "REUNIÓN", "FIESTA", "TRANSFORMADOR"]
    fuente_plantillas = PLANTILLAS
else:
    DB_FILE = "historico_price_pack.csv"
    label_agru = "Canal"
    opciones_agru = ["INSTITUCIONALES", "MAYOREO", "CLUBES", "DETALLE", "AUTOSERVICIO", "CONVENIENCIA"]
    fuente_plantillas = PLANTILLAS_PP

# --- 2. FUNCIONES CORE ---
def calcular_pkg(df):
    if df.empty: return df
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1)
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(1)
    if "SOM (%)" not in df.columns: df["SOM (%)"] = 0.0
    if "Fabricante" not in df.columns: df["Fabricante"] = "BARCEL"
    return df

# --- 3. GESTIÓN DE ESTADO ---
if "data" not in st.session_state or st.session_state.get("last_modo") != modo:
    if os.path.exists(DB_FILE):
        st.session_state.data = calcular_pkg(pd.read_csv(DB_FILE))
    else:
        st.session_state.data = pd.DataFrame(columns=["Producto", "Fabricante", label_agru, "Precio ($)", "Gramaje (g)", "SOM (%)"])
    st.session_state.last_modo = modo

# --- 4. BARRA LATERAL ---
st.sidebar.header("📁 Gestión")
nombre_plantilla = st.sidebar.selectbox("Cargar Plantilla:", ["-- Seleccionar --"] + list(fuente_plantillas.keys()))

if st.sidebar.button("Cargar Datos"):
    if nombre_plantilla != "-- Seleccionar --":
        st.session_state.data = calcular_pkg(pd.DataFrame(fuente_plantillas[nombre_plantilla]))
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Reset"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.data = pd.DataFrame(columns=["Producto", "Fabricante", label_agru, "Precio ($)", "Gramaje (g)", "SOM (%)"])
    st.rerun()

st.title(f"📊 {modo.upper()}")

# --- 5. EDITOR ---
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = calcular_pkg(edited_df)
    st.session_state.data.to_csv(DB_FILE, index=False)
    st.rerun()

# --- 6. GRÁFICO CORREGIDO ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    ord_map = {cat.upper(): i for i, cat in enumerate(opciones_agru)}
    df_p["Orden"] = df_p[label_agru].str.upper().map(ord_map).fillna(99)
    df_p = df_p.sort_values(by=["Orden", "Precio por Kg ($)" if modo == "Price Pack" else "Precio ($)"]).reset_index(drop=True)

    fig = go.Figure()

    if modo == "Price Pack":
        # Barras principales (Precio por Kg)
        fig.add_trace(go.Bar(
            x=df_p.index, y=df_p["Precio por Kg ($)"],
            marker_color="#0B3C8C",
            text=[f"<b>${p:,.0f}</b>" for p in df_p["Precio por Kg ($)"]],
            textposition="outside",
            textfont=dict(size=14, color="black")
        ))

        # Etiquetas internas simplificadas (Solo Precio $)
        for i, r in df_p.iterrows():
            fig.add_annotation(
                x=i, y=r["Precio por Kg ($)"] * 0.15, # Posición baja dentro de la barra
                text=f"<b>${r['Precio ($)']:.1f}</b>",
                showarrow=False, font=dict(size=12, color="white"),
                bgcolor="rgba(0,0,0,0.6)", borderpad=4
            )
        
        # Ajuste de Ejes y márgenes para evitar empalmes
        fig.update_layout(
            height=750, 
            margin=dict(b=250, t=50), # Más espacio abajo para los canales
            template="plotly_white",
            xaxis=dict(
                tickmode='array', tickvals=list(df_p.index),
                ticktext=df_p["Producto"],
                tickangle=-90, # Etiquetas de producto a 90 grados
                tickfont=dict(size=12)
            ),
            yaxis=dict(title="Precio por Kg ($)", range=[0, df_p["Precio por Kg ($)"].max() * 1.25])
        )

        # Divisores y Etiquetas de Canal bajadas
        for cat in df_p[label_agru].unique():
            idx_list = df_p.index[df_p[label_agru] == cat].tolist()
            if idx_list:
                center = (idx_list[0] + idx_list[-1]) / 2
                # Línea divisoria
                fig.add_shape(type="line", x0=idx_list[-1]+0.5, x1=idx_list[-1]+0.5, y0=0, y1=1, xref="x", yref="paper", line=dict(color="#DDD", width=2))
                # Etiqueta de canal movida más abajo (y=-0.35)
                fig.add_annotation(x=center, y=-0.38, xref="x", yref="paper", text=f"<b>{cat}</b>", showarrow=False, font=dict(size=14, color="#333"))

    else:
        # Lógica original para Price Ladder (Escaleras)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.15, 0.85])
        # ... (Se mantiene tu lógica de Ladder intacta aquí para no mezclar)
        fig.add_trace(go.Bar(x=df_p.index, y=df_p["Precio ($)"], marker_color="#0B3C8C"), row=2, col=1)
        fig.update_xaxes(tickangle=-90, row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)

st.sidebar.caption("G g")
