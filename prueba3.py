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
modo = st.sidebar.radio("Seleccionar Herramienta:", ["Price Ladder", "Price Pack"])

# Configuración de variables según el modo
if modo == "Price Ladder":
    DB_FILE = "historico_productos.csv"
    label_agru = "Ocasión"
    opciones_agru = ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR", "REUNIÓN", "FIESTA", "TRANSFORMADOR"]
    fuente_plantillas = PLANTILLAS
    columnas_tabla = ["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "SOM (%)"]
else:
    DB_FILE = "historico_price_pack.csv"
    label_agru = "Canal"
    # Jerarquía de canales para Price Pack
    opciones_agru = ["INSTITUCIONALES", "MAYOREO", "CLUBES", "DETALLE", "AUTOSERVICIO", "CONVENIENCIA"]
    fuente_plantillas = PLANTILLAS_PP
    columnas_tabla = ["Producto", "Familia", "Canal", "Precio ($)", "Gramaje (g)"]

# --- 2. FUNCIONES CORE ---
def calcular_pkg(df, modo_actual):
    if df.empty: return df
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1).replace(0, 1)
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(1)
    
    if modo_actual == "Price Ladder":
        if "SOM (%)" not in df.columns: df["SOM (%)"] = 0.0
        if "Fabricante" not in df.columns: df["Fabricante"] = "OTROS"
    return df

# --- 3. GESTIÓN DE ESTADO ---
if "data" not in st.session_state or st.session_state.get("last_modo") != modo:
    if os.path.exists(DB_FILE):
        st.session_state.data = calcular_pkg(pd.read_csv(DB_FILE), modo)
    else:
        st.session_state.data = pd.DataFrame(columns=columnas_tabla)
    st.session_state.last_modo = modo

# --- 4. BARRA LATERAL ---
st.sidebar.header("📁 Gestión de Datos")
nombre_plantilla = st.sidebar.selectbox("Cargar Plantilla:", ["-- Seleccionar --"] + list(fuente_plantillas.keys()))

if st.sidebar.button("Cargar Datos"):
    if nombre_plantilla != "-- Seleccionar --":
        st.session_state.data = calcular_pkg(pd.DataFrame(fuente_plantillas[nombre_plantilla]), modo)
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Reset"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.data = pd.DataFrame(columns=columnas_tabla)
    st.rerun()

st.title(f"📊 {modo.upper()}")

# --- 5. FORMULARIOS DE AGREGAR (DIFERENCIADOS) ---
with st.expander(f"➕ Agregar nuevo SKU a {modo}", expanded=False):
    with st.form("form_nuevo_sku", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        f_nom = col1.text_input("Nombre del Producto").upper()
        
        if modo == "Price Ladder":
            f_fab = col2.selectbox("Fabricante", ["BARCEL", "SABRITAS", "OTROS", "PROPUESTA"])
            f_cat = col3.selectbox("Ocasión de Consumo", opciones_agru)
            col4, col5, col6 = st.columns(3)
            f_pre = col4.number_input("Precio ($)", min_value=0.0, step=0.5)
            f_gra = col5.number_input("Gramaje (g)", min_value=1.0, step=1.0)
            f_som = col6.number_input("SOM (%)", min_value=0.0, max_value=100.0, step=0.1)
            
            if st.form_submit_button("Añadir a Escalera"):
                nuevo = pd.DataFrame([{"Producto": f_nom, "Fabricante": f_fab, "Ocasión": f_cat, "Precio ($)": f_pre, "Gramaje (g)": f_gra, "SOM (%)": f_som}])
                st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
                st.session_state.data = calcular_pkg(st.session_state.data, modo)
                st.session_state.data.to_csv(DB_FILE, index=False)
                st.rerun()
        else:
            f_fam = col2.text_input("Familia").upper()
            f_can = col3.selectbox("Canal", opciones_agru)
            col4, col5 = st.columns(2)
            f_pre = col4.number_input("Precio ($)", min_value=0.0, step=0.5)
            f_gra = col5.number_input("Gramaje (g)", min_value=1.0, step=1.0)
            
            if st.form_submit_button("Añadir a Price Pack"):
                nuevo = pd.DataFrame([{"Producto": f_nom, "Familia": f_fam, "Canal": f_can, "Precio ($)": f_pre, "Gramaje (g)": f_gra}])
                st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
                st.session_state.data = calcular_pkg(st.session_state.data, modo)
                st.session_state.data.to_csv(DB_FILE, index=False)
                st.rerun()

# --- 6. EDITOR DE TABLA ---
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = calcular_pkg(edited_df, modo)
    st.session_state.data.to_csv(DB_FILE, index=False)
    st.rerun()

# --- 7. GRÁFICOS ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    ord_map = {cat.upper(): i for i, cat in enumerate(opciones_agru)}
    df_p["Orden_Agru"] = df_p[label_agru].str.upper().map(ord_map).fillna(99)
    
    # ORDENAMIENTO: Ambos modos se ordenan por su bloque y luego por Precio Desembolso ($)
    df_p = df_p.sort_values(by=["Orden_Agru", "Precio ($)"], ascending=[True, True]).reset_index(drop=True)

    if modo == "Price Ladder":
        # GRÁFICO DE ESCALERAS (CON SOM Y COLORES POR MARCA)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.0, row_heights=[0.15, 0.85])
        
        fig.add_trace(go.Scatter(
            x=df_p.index, y=df_p["SOM (%)"], mode="lines+markers+text",
            marker=dict(size=30, color="#EEE", symbol="square"),
            text=[f"<b>{s}%</b>" for s in df_p["SOM (%)"]], textposition="middle center",
        ), row=1, col=1)
        
        colors = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D", "PROPUESTA": "#4B207E"}
        fig.add_trace(go.Bar(
            x=df_p.index, y=df_p["Precio ($)"],
            marker_color=[colors.get(str(f).upper(), "#999") for f in df_p["Fabricante"]],
            text=[f"<b>${int(p)}</b>" for p in df_p["Precio ($)"]], textposition="outside"
        ), row=2, col=1)

        for i, r in df_p.iterrows():
            fig.add_annotation(x=i, y=2, text=f"<b>${int(r['Precio por Kg ($)'])}</b>", showarrow=False, 
                               font=dict(color="white" if r["Fabricante"]=="BARCEL" else "black"), 
                               bgcolor="rgba(0,0,0,0.5)" if r["Fabricante"]=="BARCEL" else "rgba(255,255,255,0.7)", row=2, col=1)
        
        fig.update_layout(height=850, margin=dict(b=200), template="plotly_white", showlegend=False)
        fig.update_xaxes(tickmode='array', tickvals=list(df_p.index), ticktext=df_p["Producto"], tickangle=-90, row=2, col=1)

    else:
        # GRÁFICO PRICE PACK (EJE Y = $/KG)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_p.index, y=df_p["Precio por Kg ($)"],
            marker_color="#0B3C8C",
            text=[f"<b>${p:,.0f}</b>" for p in df_p["Precio por Kg ($)"]], # Etiqueta superior $/Kg
            textposition="outside",
            textfont=dict(size=14, color="black")
        ))

        for i, r in df_p.iterrows():
            fig.add_annotation(
                x=i, y=r["Precio por Kg ($)"] * 0.15,
                text=f"<b>${r['Precio ($)']:.1f}</b>", # Etiqueta interna Desembolso
                showarrow=False, font=dict(size=12, color="white"),
                bgcolor="rgba(0,0,0,0.6)", borderpad=4
            )

        fig.update_layout(
            height=750, margin=dict(b=250), template="plotly_white",
            xaxis=dict(tickmode='array', tickvals=list(df_p.index), ticktext=df_p["Producto"], tickangle=-90),
            yaxis=dict(title="Precio por Kg ($)", range=[0, df_p["Precio por Kg ($)"].max() * 1.2])
        )

    # Divisores y Etiquetas (Ocasión o Canal)
    for cat in df_p[label_agru].unique():
        indices = df_p.index[df_p[label_agru] == cat].tolist()
        if indices:
            center = (indices[0] + indices[-1]) / 2
            # Ajustamos la referencia del eje para que la línea salga bien en ambos modos
            xref_val = "x" if modo == "Price Pack" else "x2"
            fig.add_shape(type="line", x0=indices[-1]+0.5, x1=indices[-1]+0.5, y0=0, y1=1, xref=xref_val, yref="paper", line=dict(color="#DDD", width=2))
            fig.add_annotation(x=center, y=-0.4, xref=xref_val, yref="paper", text=f"<b>{cat}</b>", showarrow=False, font=dict(size=14))

    st.plotly_chart(fig, use_container_width=True)

# Sección de Comparativas solo para Ladder
if modo == "Price Ladder" and not st.session_state.data.empty:
    st.divider()
    st.subheader("📈 Comparativas Index $/Kg")
    barcel_list = df_p[df_p["Fabricante"]=="BARCEL"]["Producto"].unique()
    comp_list = df_p[df_p["Fabricante"]!="BARCEL"]["Producto"].unique()
    if len(barcel_list) > 0 and len(comp_list) > 0:
        c1, c2 = st.columns(2)
        p1 = c1.selectbox("Producto Barcel", barcel_list)
        p2 = c2.selectbox("Producto Competencia", comp_list)
        v1 = df_p[df_p["Producto"]==p1]["Precio por Kg ($)"].values[0]
        v2 = df_p[df_p["Producto"]==p2]["Precio por Kg ($)"].values[0]
        st.metric(f"Index {p1} vs {p2}", int((v1/v2)*100))
