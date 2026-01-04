import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from plantillas import PLANTILLAS 

# Intentamos cargar price_pack, si no existe creamos un diccionario vacío
try:
    from price_pack import PLANTILLAS_PP
except ImportError:
    PLANTILLAS_PP = {}

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Price Architecture Expert Pro", layout="wide")

# NAVEGACIÓN ENTRE MODOS
st.sidebar.header("🚀 Modo de Visualización")
modo = st.sidebar.radio("Seleccionar:", ["Price Ladder", "Price Pack"])

if modo == "Price Ladder":
    DB_FILE = "historico_productos.csv"
    label_agru = "Ocasión"
    opciones_agru = ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR","REUNIÓN", "FIESTA","TRANSFORMADOR"]
    fuente_plantillas = PLANTILLAS
else:
    DB_FILE = "historico_price_pack.csv"
    label_agru = "Canal"
    # Jerarquía basada en tus capturas (INST, MAY, CLUB, DT, AS, CNV)
    opciones_agru = ["INSTITUCIONALES", "MAYOREO", "CLUBES", "DETALLE", "AUTOSERVICIO", "CONVENIENCIA"]
    fuente_plantillas = PLANTILLAS_PP

# --- 2. FUNCIONES CORE ---
def calcular_pkg(df):
    if df.empty: return df
    # Asegurar que las columnas existan antes de operar
    for col in ["Precio ($)", "Gramaje (g)", "SOM (%)"]:
        if col not in df.columns: df[col] = 0.0
    
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1).replace(0, 1)
    df["SOM (%)"] = pd.to_numeric(df["SOM (%)"], errors='coerce').fillna(0)
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(1)
    
    # SOLUCIÓN AL NAMEERROR: Asegurar columna Fabricante
    if "Fabricante" not in df.columns:
        df["Fabricante"] = "BARCEL"
    return df

def procesar_datos_piramide(df, agrupador="Ocasión"):
    if df.empty: return df
    temp = df.copy()
    def get_base(g):
        if g["SOM (%)"].max() > 0:
            return g.loc[g["SOM (%)"].idxmax(), "Precio por Kg ($)"]
        return g["Precio por Kg ($)"].mean() if not g.empty else 1
    
    bases = temp.groupby(agrupador).apply(lambda x: get_base(x)).reset_index()
    bases.columns = [agrupador, "P_Ref"]
    temp = temp.merge(bases, on=agrupador, how="left")
    temp["Idx_P"] = (temp["Precio por Kg ($)"] / temp["P_Ref"] * 100).round(0)
    
    def asignar_t(i):
        if i >= 170: return "PREMIUM"
        elif 120 <= i < 170: return "UPPER MAINSTREAM"
        elif 95 <= i < 120: return "MAINSTREAM"
        elif 80 <= i < 95: return "MAINSTREAM LOW"
        else: return "VALUE"
    temp["Tier"] = temp["Idx_P"].apply(asignar_t)
    return temp

# --- 3. ESTADO DE SESIÓN ---
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
        nuevos_datos = pd.DataFrame(fuente_plantillas[nombre_plantilla])
        st.session_state.data = calcular_pkg(nuevos_datos)
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

# --- 6. GRÁFICO (MODIFICADO PARA PRICE PACK) ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    ord_map = {cat.upper(): i for i, cat in enumerate(opciones_agru)}
    df_p["Orden"] = df_p[label_agru].str.upper().map(ord_map).fillna(99)
    df_p = df_p.sort_values(by=["Orden", "Precio ($)"]).reset_index(drop=True)
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.0, row_heights=[0.15, 0.85])

    # SOM superior
    fig.add_trace(go.Scatter(
        x=df_p.index, y=df_p["SOM (%)"], mode="lines+markers+text",
        marker=dict(size=25, color="#EEE", symbol="square"),
        text=[f"<b>{s}%</b>" for s in df_p["SOM (%)"]], textposition="middle center",
    ), row=1, col=1)

    # Barras de Precio
    fig.add_trace(go.Bar(
        x=df_p.index, y=df_p["Precio ($)"],
        marker_color=["#0B3C8C" if f == "BARCEL" else "#7F8C8D" for f in df_p["Fabricante"]],
        text=[f"<b>${p}</b>" for p in df_p["Precio ($)"]], textposition="outside"
    ), row=2, col=1)

    # $/Kg Annotations
    for i, row in df_p.iterrows():
        fig.add_annotation(
            x=i, y=row["Precio ($)"]*0.5, text=f"<b>${row['Precio por Kg ($)']:,.0f}</b>",
            showarrow=False, font=dict(color="white"), bgcolor="rgba(0,0,0,0.5)", row=2, col=1
        )

    fig.update_layout(height=800, template="plotly_white", showlegend=False)
    fig.update_xaxes(tickmode='array', tickvals=list(df_p.index), ticktext=df_p["Producto"], tickangle=-90, row=2, col=1)
    st.plotly_chart(fig, use_container_width=True)

# --- 7. COMPARATIVAS (SOLUCIÓN AL ERROR) ---
st.divider()
st.subheader("📈 Comparativas Index $/Kg")

# Verificación de seguridad para evitar el NameError
if not st.session_state.data.empty:
    df_c = st.session_state.data
    barcel_list = df_c[df_c["Fabricante"] == "BARCEL"]["Producto"].unique()
    comp_list = df_c[df_c["Fabricante"] != "BARCEL"]["Producto"].unique()

    if len(barcel_list) > 0 and len(comp_list) > 0:
        cols = st.columns(4)
        for i in range(min(4, len(barcel_list))):
            with cols[i]:
                p1 = st.selectbox(f"Barcel {i}", barcel_list, key=f"b{i}")
                p2 = st.selectbox(f"Comp {i}", comp_list, key=f"c{i}")
                v1 = df_c[df_c["Producto"] == p1]["Precio por Kg ($)"].values[0]
                v2 = df_c[df_c["Producto"] == p2]["Precio por Kg ($)"].values[0]
                idx = int((v1/v2)*100)
                st.metric(f"{p1} vs {p2}", f"Index {idx}")

st.sidebar.caption("G g")
