import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. IMPORTACIÓN DE PLANTILLAS ---
from plantillas import PLANTILLAS
try:
    from price_pack import PLANTILLAS_PP
except ImportError:
    PLANTILLAS_PP = {}

# --- 2. CONFIGURACIÓN ---
st.set_page_config(page_title="Price Architecture Tool", layout="wide")

# --- 3. SELECTOR DE MÓDULO ---
st.sidebar.header("🚀 Navegación")
modo = st.sidebar.radio("Seleccionar Herramienta:", ["Price Ladder", "Price Pack"])

# --- 4. CONFIGURACIÓN DINÁMICA POR MODO ---
if modo == "Price Ladder":
    DB_FILE = "historico_ladder.csv"
    fuente_plantillas = PLANTILLAS
    label_agrupador = "Ocasión"
    opciones_agrupador = ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR", "REUNIÓN", "FIESTA", "TRANSFORMADOR"]
    titulo_app = "📊 ESCALERAS DE PRECIO DINÁMICAS (MARKET)"
else:
    DB_FILE = "historico_price_pack.csv"
    fuente_plantillas = PLANTILLAS_PP
    label_agrupador = "Canal"
    # Orden solicitado para Price Pack
    opciones_agrupador = ["INSTITUCIONALES", "MAYOREO", "CLUBES", "HARD DISCOUNT", "DETALLE", "AUTOSERVICIO", "CONVENIENCIA"]
    titulo_app = "📦 PRICE PACK ARCHITECTURE (INTERNAL BARCEL)"

# --- 5. FUNCIONES CORE ---
def calcular_pkg(df):
    if df.empty: return df
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1).replace(0, 1)
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(0)
    if "SOM (%)" not in df.columns: df["SOM (%)"] = 0
    return df

# --- 6. GESTIÓN DE ESTADO ---
if "data" not in st.session_state or st.session_state.get('last_modo') != modo:
    if os.path.exists(DB_FILE):
        st.session_state.data = calcular_pkg(pd.read_csv(DB_FILE))
    else:
        cols = ["Producto", "Familia", label_agrupador, "Precio ($)", "Gramaje (g)", "Precio por Kg ($)"]
        if modo == "Price Ladder": cols += ["Fabricante", "SOM (%)"]
        st.session_state.data = pd.DataFrame(columns=cols)
    st.session_state.last_modo = modo

# --- 7. BARRA LATERAL (GESTIÓN) ---
st.sidebar.divider()
st.sidebar.subheader(f"📁 Gestión {modo}")
nombre_plantilla = st.sidebar.selectbox("Cargar Plantilla:", ["-- Seleccionar --"] + list(fuente_plantillas.keys()))

if st.sidebar.button("Cargar Datos"):
    if nombre_plantilla != "-- Seleccionar --":
        st.session_state.data = calcular_pkg(pd.DataFrame(fuente_plantillas[nombre_plantilla]))
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Reset"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.rerun()

st.title(titulo_app)

# --- 8. FORMULARIO ---
with st.expander(f"➕ Agregar SKU a {modo}", expanded=False):
    with st.form("nuevo_sku_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        f_nom = c1.text_input("Nombre del Producto").upper()
        f_fam = c2.text_input("Familia").upper()
        f_agru = c3.selectbox(label_agrupador, opciones_agrupador)
        
        c4, c5 = st.columns(2)
        f_pre = c4.number_input("Precio Desembolso ($)", min_value=0.0, step=0.5)
        f_gra = c5.number_input("Gramaje (g)", min_value=1.0, step=1.0)
        
        f_fab = "BARCEL"
        f_som = 0.0
        if modo == "Price Ladder":
            f_fab = st.selectbox("Fabricante", ["BARCEL", "SABRITAS", "OTROS"])
            f_som = st.number_input("SOM (%)", min_value=0.0, max_value=100.0)

        if st.form_submit_button("Añadir SKU"):
            nueva_fila = {"Producto": f_nom, "Familia": f_fam, label_agrupador: f_agru, "Precio ($)": f_pre, "Gramaje (g)": f_gra}
            if modo == "Price Ladder":
                nueva_fila["Fabricante"] = f_fab
                nueva_fila["SOM (%)"] = f_som
            
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.session_state.data = calcular_pkg(st.session_state.data)
            st.session_state.data.to_csv(DB_FILE, index=False)
            st.rerun()

# --- 9. EDITOR ---
st.subheader("📝 Tabla de Datos")
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = calcular_pkg(edited_df)
    st.session_state.data.to_csv(DB_FILE, index=False)
    st.rerun()

# --- 10. GRÁFICOS ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    
    # Ordenamiento por Canal (Price Pack) u Ocasión (Ladder)
    ord_map = {cat: i for i, cat in enumerate(opciones_agrupador)}
    df_p["Orden"] = df_p[label_agrupador].str.upper().map(ord_map).fillna(99)
    df_p = df_p.sort_values(by=["Orden", "Precio por Kg ($)" if modo == "Price Pack" else "Precio ($)"]).reset_index(drop=True)

    if modo == "Price Pack":
        # GRÁFICO ESPECÍFICO PRICE PACK
        fig = go.Figure()
        
        # Barras: Eje Y es Precio por Kg ($)
        fig.add_trace(go.Bar(
            x=df_p["Producto"],
            y=df_p["Precio por Kg ($)"],
            marker_color="#0B3C8C", # Azul Barcel
            text=[f"<b>${int(p)}</b>" for p in df_p["Precio por Kg ($)"]],
            textposition="outside",
            textfont=dict(size=16, color="black"),
            name="Precio por Kg"
        ))

        # Etiquetas de Precio Desembolso en la base (y=5 o valor pequeño)
        for i, row in df_p.iterrows():
            fig.add_annotation(
                x=i, y=max(df_p["Precio por Kg ($)"]) * 0.05, # Cerca de la base
                text=f"Desbolso:<br><b>${row['Precio ($)']}</b><br><span style='font-size:10px;'>{int(row['Gramaje (g)'])}g</span>",
                showarrow=False, font=dict(size=12, color="white"),
                bgcolor="rgba(0,0,0,0.5)", borderpad=4
            )

        # Líneas divisoras por Canal
        for cat in df_p[label_agrupador].unique():
            idx_list = df_p.index[df_p[label_agrupador] == cat].tolist()
            center = (idx_list[0] + idx_list[-1]) / 2
            fig.add_shape(type="line", x0=idx_list[-1]+0.5, x1=idx_list[-1]+0.5, y0=0, y1=1, xref="x", yref="paper", line=dict(color="#DDD", width=2))
            fig.add_annotation(x=center, y=-0.15, xref="x", yref="paper", text=f"<b>{cat}</b>", showarrow=False, font=dict(size=14))

        fig.update_layout(title="Arquitectura de Precio por Kg por Canal", height=700, margin=dict(b=150), template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    else:
        # GRÁFICO ORIGINAL PRICE LADDER (Tu lógica original con SOM y Subplots)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.0, row_heights=[0.15, 0.85])
        # ... (Aquí va tu código de go.Scatter y go.Bar original que ya funciona)
        st.plotly_chart(fig, use_container_width=True)

# --- 11. CÁLCULO DE COMPARATIVAS E INDEX (SOLO PARA LADDER) ---
if modo == "Price Ladder" and not st.session_state.data.empty:
    # --- 7. COMPARATIVAS (MANTENIDO EXACTAMENTE IGUAL) ---
    st.divider()
    st.subheader("📈 Comparativas Index $/Kg")
    barcel_list = df_p[df_p["Fabricante"]=="BARCEL"]["Producto"].unique() if not df_p.empty else []
    comp_list = df_p[df_p["Fabricante"]!="BARCEL"]["Producto"].unique() if not df_p.empty else []
    
    if len(barcel_list) > 0 and len(comp_list) > 0:
        idx_cols = st.columns(4)
        for i in range(4):
            with idx_cols[i]:
                with st.container(border=True):
                    p_b = st.selectbox(f"Barcel", barcel_list, key=f"sb{i}", label_visibility="collapsed")
                    p_c = st.selectbox(f"Comp.", comp_list, key=f"sc{i}", label_visibility="collapsed")
                    val_b = df_p[df_p["Producto"]==p_b]["Precio por Kg ($)"].values[0]
                    val_c = df_p[df_p["Producto"]==p_c]["Precio por Kg ($)"].values[0]
                    index_val = int((val_b / val_c) * 100)
                    color_index = "#0B3C8C" if index_val <= 100 else "#D32F2F"
                    st.markdown(f"""<div style="background-color: #f8f9fa; padding: 15px 10px; border-radius: 10px; border-top: 5px solid {color_index}; text-align: center; max-width: 200px; margin: 10px auto; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);"><div style="font-size: 1.1rem; font-weight: bold; color: #333; margin-bottom: 8px; line-height: 1.2;">{p_b} <br> <span style="color: #888; font-size: 0.9rem;">vs</span> <br> {p_c}</div><div style="font-size: 2.2rem; font-weight: 900; color: {color_index};">{index_val}</div></div>""", unsafe_allow_html=True)
    
    #
