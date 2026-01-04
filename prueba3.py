import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from plantillas import PLANTILLAS 

# Carga de plantillas Price Pack
try:
    from price_pack import PLANTILLAS_PP
except ImportError:
    PLANTILLAS_PP = {}

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Price Architecture Expert Pro", layout="wide")

st.sidebar.header("🚀 Modo de Visualización")
modo = st.sidebar.radio("Seleccionar:", ["Price Ladder", "Price Pack"])

# Variables de entorno según el modo
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

# --- 2. FUNCIONES DE PROCESAMIENTO ---
def calcular_pkg(df):
    if df.empty: return df
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1)
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(1)
    if "SOM (%)" not in df.columns: df["SOM (%)"] = 0.0
    if "Fabricante" not in df.columns: df["Fabricante"] = "BARCEL"
    return df

# --- 3. GESTIÓN DE DATOS ---
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

# --- 6. GRÁFICO DINÁMICO ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    ord_map = {cat.upper(): i for i, cat in enumerate(opciones_agru)}
    df_p["Orden"] = df_p[label_agru].str.upper().map(ord_map).fillna(99)
    df_p = df_p.sort_values(by=["Orden", "Precio por Kg ($)" if modo == "Price Pack" else "Precio ($)"]).reset_index(drop=True)

    if modo == "Price Ladder":
        # Gráfico original con SOM arriba
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.0, row_heights=[0.15, 0.85])
        fig.add_trace(go.Scatter(
            x=df_p.index, y=df_p["SOM (%)"], mode="lines+markers+text",
            marker=dict(size=30, color="#EEE", symbol="square"),
            text=[f"<b>{s}%</b>" for s in df_p["SOM (%)"]], textposition="middle center",
        ), row=1, col=1)
        
        fig.add_trace(go.Bar(
            x=df_p.index, y=df_p["Precio ($)"],
            marker_color=["#0B3C8C" if f == "BARCEL" else "#F5C400" for f in df_p["Fabricante"]],
            text=[f"<b>${int(p)}</b>" for p in df_p["Precio ($)"]], textposition="outside"
        ), row=2, col=1)

        for i, r in df_p.iterrows():
            fig.add_annotation(x=i, y=2, text=f"<b>${int(r['Precio por Kg ($)'])}</b>", showarrow=False, font=dict(color="white" if r["Fabricante"]=="BARCEL" else "black"), bgcolor="rgba(0,0,0,0.4)" if r["Fabricante"]=="BARCEL" else "rgba(255,255,255,0.7)", row=2, col=1)

    else:
        # MODO PRICE PACK: Eje Y es Precio x Kg
        fig = make_subplots(rows=1, cols=1)
        
        fig.add_trace(go.Bar(
            x=df_p.index, y=df_p["Precio por Kg ($)"],
            marker_color="#0B3C8C",
            text=[f"<b>${p:,.0f}</b>" for p in df_p["Precio por Kg ($)"]], # Etiqueta Superior: PxKg
            textposition="outside",
            textfont=dict(size=14, color="black")
        ))

        # Etiqueta Interna: Desembolso (Precio $)
        for i, r in df_p.iterrows():
            fig.add_annotation(
                x=i, y=r["Precio por Kg ($)"] * 0.5,
                text=f"Desembolso:<br><b>${r['Precio ($)']}</b><br>{int(r['Gramaje (g)'])}g",
                showarrow=False, font=dict(size=11, color="white"),
                bgcolor="rgba(0,0,0,0.3)", borderpad=4
            )

    # Líneas divisorias de categorías y nombres de Canal/Ocasión
    for cat in df_p[label_agru].unique():
        idx_list = df_p.index[df_p[label_agru] == cat].tolist()
        center = (idx_list[0] + idx_list[-1]) / 2
        fig.add_shape(type="line", x0=idx_list[-1]+0.5, x1=idx_list[-1]+0.5, y0=0, y1=1, xref="x", yref="paper", line=dict(color="#DDD", width=2))
        fig.add_annotation(x=center, y=-0.15 if modo == "Price Pack" else -0.3, xref="x", yref="paper", text=f"<b>{cat}</b>", showarrow=False, font=dict(size=14))

    fig.update_layout(height=700, margin=dict(b=150), template="plotly_white", showlegend=False)
    fig.update_xaxes(tickmode='array', tickvals=list(df_p.index), ticktext=df_p["Producto"], tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# --- 7. COMPARATIVAS (SOLO EN PRICE LADDER) ---
if modo == "Price Ladder" and not st.session_state.data.empty:
    st.divider()
    st.subheader("📈 Comparativas Index $/Kg")
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
                st.metric(f"{p1} vs {p2}", f"Index {int((v1/v2)*100)}")

st.sidebar.caption("G g")
