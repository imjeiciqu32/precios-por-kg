import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Price Ladder Expert Pro", layout="wide")
DB_FILE = "historico_productos.csv"

# --- 2. REPOSITORIO DE PLANTILLAS ---
PLANTILLAS = {
    "Escalera DT - MAÍZ": [
        {"Producto": "MINI TAKIS 35G", "Fabricante": "BARCEL", "Ocasión": "BITES", "Precio ($)": 10.0, "Gramaje (g)": 35, "SOM (%)": 1.4},
        {"Producto": "DORITOS 41G", "Fabricante": "SABRITAS", "Ocasión": "BITES", "Precio ($)": 15.0, "Gramaje (g)": 41, "SOM (%)": 0.7},
        {"Producto": "TAKIS 70G", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 70, "SOM (%)": 8.2},
        {"Producto": "DORITOS 58G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 58, "SOM (%)": 12.1},
        {"Producto": "TAKIS 200G", "Fabricante": "BARCEL", "Ocasión": "FAMILIAR", "Precio ($)": 45.0, "Gramaje (g)": 200, "SOM (%)": 1.2},
        {"Producto": "DORITOS 245G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 56.0, "Gramaje (g)": 245, "SOM (%)": 3.2}
    ],
    "Escalera DT - PAPA": [
        {"Producto": "TAKIS 200G", "Fabricante": "BARCEL", "Ocasión": "FAMILIAR", "Precio ($)": 45.0, "Gramaje (g)": 200, "SOM (%)": 1.2},
        {"Producto": "DORITOS 245G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 56.0, "Gramaje (g)": 245, "SOM (%)": 3.2}
    ]
}

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
        df["SOM (%)"] = pd.to_numeric(df["SOM (%)"], errors='coerce').fillna(0)
        df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1)
        df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(0)
        return df
    return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])

if "data" not in st.session_state:
    st.session_state.data = load_data()

# --- 3. BARRA LATERAL ---
st.sidebar.header("📁 Gestión de Datos")
nombre_plantilla = st.sidebar.selectbox("Cargar Plantilla:", ["-- Seleccionar --"] + list(PLANTILLAS.keys()))

if st.sidebar.button("Cargar Escalera"):
    if nombre_plantilla != "-- Seleccionar --":
        nuevos_datos = pd.DataFrame(PLANTILLAS[nombre_plantilla])
        nuevos_datos["Precio por Kg ($)"] = (nuevos_datos["Precio ($)"] / (nuevos_datos["Gramaje (g)"] / 1000)).round(0)
        st.session_state.data = nuevos_datos
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Borrar Todo"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.data = pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])
    st.rerun()

st.title("📊 Análisis de Escalera y Participación (SOM)")

# --- 4. FORMULARIO PARA AGREGAR MANUALMENTE ---
with st.expander("➕ Agregar nuevo producto a la lista actual", expanded=False):
    with st.form("add_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        p_nom = col1.text_input("Nombre del Producto")
        p_fab = col2.selectbox("Fabricante", ["BARCEL", "SABRITAS", "OTROS"])
        p_oca = col3.selectbox("Ocasión", ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"])
        
        col4, col5, col6 = st.columns(3)
        p_pre = col4.number_input("Precio ($)", min_value=0.0, step=0.5)
        p_gra = col5.number_input("Gramaje (g)", min_value=1.0, step=1.0)
        p_som = col6.number_input("SOM (%)", min_value=0.0, max_value=100.0, step=0.1)
        
        if st.form_submit_button("Añadir a la tabla"):
            pkg = round(p_pre / (p_gra / 1000), 0)
            nuevo = pd.DataFrame([{"Producto": p_nom.upper(), "Fabricante": p_fab, "Ocasión": p_oca, 
                                   "Precio ($)": p_pre, "Gramaje (g)": p_gra, "Precio por Kg ($)": pkg, "SOM (%)": p_som}])
            st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
            st.session_state.data.to_csv(DB_FILE, index=False)
            st.rerun()

# --- 5. EDITOR DE TABLA ---
st.subheader("📝 Editor de Datos")
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    edited_df["Precio por Kg ($)"] = (edited_df["Precio ($)"] / (edited_df["Gramaje (g)"].replace(0, 1) / 1000)).round(0)
    st.session_state.data = edited_df
    edited_df.to_csv(DB_FILE, index=False)

# --- 6. GRÁFICO ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    ord_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df_p["O_Oca"] = df_p["Ocasión"].str.upper().map(ord_oca).fillna(99)
    df_p = df_p.sort_values(by=["O_Oca", "Precio ($)"])

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.25, 0.75])

    # Línea SOM
    fig.add_trace(go.Scatter(x=[df_p["Ocasión"], df_p["Producto"]], y=df_p["SOM (%)"], 
                             mode="lines+markers", line=dict(color="#D3D3D3", width=1.5), marker=dict(size=1)), row=1, col=1)

    for i, r in enumerate(df_p.itertuples()):
        fig.add_annotation(x=i, y=r._7, text=f"<b>{r._7}%</b>", showarrow=False, bgcolor="#F0F0F0", 
                           bordercolor="#BDBDBD", borderwidth=1, row=1, col=1)

    # Barras Precio
    colors = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    fig.add_trace(go.Bar(x=[df_p["Ocasión"], df_p["Producto"]], y=df_p["Precio ($)"],
                         marker_color=[colors.get(str(f).upper(), "#B0B0B0") for f in df_p["Fabricante"]],
                         text=[f"<b>${p}</b>" for p in df_p["Precio ($)"]], textposition='outside',
                         textfont=dict(size=16, color="black")), row=2, col=1)

    # $/Kg Etiquetas fijas en la base
    for i, r in enumerate(df_p.itertuples()):
        fig.add_annotation(x=i, y=3, text=f"<b>${int(r._6)}</b>", showarrow=False,
                           font=dict(size=14, color="white" if r.Fabricante=="BARCEL" else "black"),
                           bgcolor="rgba(0,0,0,0.5)" if r.Fabricante=="BARCEL" else "rgba(255,255,255,0.6)", row=2, col=1)

    fig.update_layout(height=750, template="plotly_white", showlegend=False, margin=dict(t=10, b=80))
    fig.update_yaxes(showgrid=False, showticklabels=False, row=1, col=1, range=[0, df_p["SOM (%)"].max()*2.5])
    # Eje X con Negritas
    fig.update_xaxes(tickfont=dict(size=12, color="black", family="Arial Black"), row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)

    # --- 7. SECCIÓN MULTI-INDEX (4 CUADROS) ---
    st.divider()
    st.subheader("📈 Comparativas de Índice $/Kg")
    
    idx_cols = st.columns(2) # Dos filas de dos columnas
    for j in range(4):
        with idx_cols[j % 2]:
            with st.container(border=True):
                c1, c2 = st.columns(2)
                b_p = c1.selectbox(f"Barcel {j+1}:", df_p[df_p["Fabricante"]=="BARCEL"]["Producto"].unique(), key=f"b{j}")
                c_p = c2.selectbox(f"Competencia {j+1}:", df_p[df_p["Fabricante"]!="BARCEL"]["Producto"].unique(), key=f"c{j}")
                
                if b_p and c_p:
                    v_b = df_p[df_p["Producto"]==b_p]["Precio por Kg ($)"].values[0]
                    v_c = df_p[df_p["Producto"]==c_p]["Precio por Kg ($)"].values[0]
                    res = int((v_b / v_c) * 100)
                    
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; background: #fdfdfd; padding: 10px; border-radius: 8px;">
                        <div style="text-align: center;"><small>Barcel</small><br><b>${v_b}</b></div>
                        <div style="background: #0B3C8C; color: white; padding: 8px 15px; border-radius: 5px; font-size: 20px; font-weight: bold;">INDEX: {res}</div>
                        <div style="text-align: center;"><small>Comp.</small><br><b>${v_c}</b></div>
                    </div>
                    """, unsafe_allow_html=True)
