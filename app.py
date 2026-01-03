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
    "Escalera Oxxo - Individual": [
        {"Producto": "MINI TAKIS 35G", "Fabricante": "BARCEL", "Ocasión": "BITES", "Precio ($)": 10.0, "Gramaje (g)": 35, "SOM (%)": 1.4},
        {"Producto": "DORITOS 41G", "Fabricante": "SABRITAS", "Ocasión": "BITES", "Precio ($)": 15.0, "Gramaje (g)": 41, "SOM (%)": 0.7},
        {"Producto": "TAKIS 70G", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 70, "SOM (%)": 8.2},
        {"Producto": "DORITOS 58G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 58, "SOM (%)": 12.1}
    ],
    "Escalera Super - Familiar": [
        {"Producto": "TAKIS 200G", "Fabricante": "BARCEL", "Ocasión": "FAMILIAR", "Precio ($)": 45.0, "Gramaje (g)": 200, "SOM (%)": 1.2},
        {"Producto": "DORITOS 245G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 56.0, "Gramaje (g)": 245, "SOM (%)": 3.2}
    ]
}

def calcular_pkg(df):
    """Función de seguridad para garantizar que $/Kg siempre sea correcto"""
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1).replace(0, 1)
    df["SOM (%)"] = pd.to_numeric(df["SOM (%)"], errors='coerce').fillna(0)
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(0)
    return df

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        return calcular_pkg(df)
    return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])

if "data" not in st.session_state:
    st.session_state.data = load_data()

# --- 3. BARRA LATERAL ---
st.sidebar.header("📁 Gestión de Datos")
nombre_plantilla = st.sidebar.selectbox("Cargar Plantilla:", ["-- Seleccionar --"] + list(PLANTILLAS.keys()))

if st.sidebar.button("Cargar Escalera"):
    if nombre_plantilla != "-- Seleccionar --":
        # CARGA Y CÁLCULO INMEDIATO
        nuevos_datos = pd.DataFrame(PLANTILLAS[nombre_plantilla])
        st.session_state.data = calcular_pkg(nuevos_datos)
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Borrar Todo"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.data = pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])
    st.rerun()

st.title("📊 Análisis de Escalera y Participación (SOM)")

# --- 4. FORMULARIO AGREGAR ---
with st.expander("➕ Agregar nuevo producto manualmente"):
    with st.form("add_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        p_nom = c1.text_input("Nombre")
        p_fab = c2.selectbox("Fabricante", ["BARCEL", "SABRITAS", "OTROS"])
        p_oca = c3.selectbox("Ocasión", ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"])
        c4, c5, c6 = st.columns(3)
        p_pre = c4.number_input("Precio ($)", min_value=0.0)
        p_gra = c5.number_input("Gramaje (g)", min_value=1.0)
        p_som = c6.number_input("SOM (%)", min_value=0.0)
        
        if st.form_submit_button("Añadir"):
            nuevo = pd.DataFrame([{"Producto": p_nom.upper(), "Fabricante": p_fab, "Ocasión": p_oca, 
                                   "Precio ($)": p_pre, "Gramaje (g)": p_gra, "SOM (%)": p_som}])
            st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
            st.session_state.data = calcular_pkg(st.session_state.data) # Forzar cálculo
            st.session_state.data.to_csv(DB_FILE, index=False)
            st.rerun()

# --- 5. EDITOR ---
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = calcular_pkg(edited_df)
    st.session_state.data.to_csv(DB_FILE, index=False)
    st.rerun()

# --- 6. GRÁFICO ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    ord_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df_p["O_Oca"] = df_p["Ocasión"].str.upper().map(ord_oca).fillna(99)
    df_p = df_p.sort_values(by=["O_Oca", "Precio ($)"])

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.3, 0.7])

    # SOM
    fig.add_trace(go.Scatter(x=[df_p["Ocasión"], df_p["Producto"]], y=df_p["SOM (%)"], 
                             mode="lines+markers", line=dict(color="#D3D3D3", width=2), marker=dict(size=1)), row=1, col=1)

    for i, row in enumerate(df_p.itertuples(index=False)):
        fig.add_annotation(x=i, y=row._6, # _6 es SOM (%) en itertuples
                           text=f"<b>{row._6}%</b>", showarrow=False, 
                           bgcolor="white", bordercolor="#BDBDBD", borderwidth=1, row=1, col=1)

    # Barras
    colors = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    fig.add_trace(go.Bar(x=[df_p["Ocasión"], df_p["Producto"]], y=df_p["Precio ($)"],
                         marker_color=[colors.get(str(f).upper(), "#B0B0B0") for f in df_p["Fabricante"]],
                         text=[f"<b>${p}</b>" for p in df_p["Precio ($)"]], textposition='outside',
                         textfont=dict(size=16, color="black")), row=2, col=1)

    # $/Kg Etiquetas (CORREGIDO: Llamada directa a columna)
    for i, row in enumerate(df_p.itertuples(index=False)):
        # Accedemos por nombre para evitar el error de los "ceros"
        valor_kg = int(row._5) # _5 suele ser Precio por Kg ($)
        fig.add_annotation(x=i, y=3, text=f"<b>${valor_kg}</b>", showarrow=False,
                           font=dict(size=14, color="white" if row.Fabricante=="BARCEL" else "black"),
                           bgcolor="rgba(0,0,0,0.6)" if row.Fabricante=="BARCEL" else "rgba(255,255,255,0.7)", row=2, col=1)

    fig.update_layout(height=800, template="plotly_white", showlegend=False, margin=dict(t=50, b=100))
    fig.update_yaxes(showgrid=False, showticklabels=False, row=1, col=1, range=[-1, df_p["SOM (%)"].max()*2])
    fig.update_xaxes(tickfont=dict(size=12, color="black", family="Arial Black"), row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)

    # --- 7. MULTI-INDEX (4 ESPACIOS) ---
    st.divider()
    st.subheader("📈 Comparativas de Índice $/Kg")
    
    # Creamos una cuadrícula de 2x2
    f1c1, f1c2 = st.columns(2)
    f2c1, f2c2 = st.columns(2)
    slots = [f1c1, f1c2, f2c1, f2c2]

    prods_barcel = df_p[df_p["Fabricante"]=="BARCEL"]["Producto"].unique()
    prods_comp = df_p[df_p["Fabricante"]!="BARCEL"]["Producto"].unique()

    if len(prods_barcel) > 0 and len(prods_comp) > 0:
        for j in range(4):
            with slots[j]:
                with st.container(border=True):
                    c_sel1, c_sel2 = st.columns(2)
                    b_p = c_sel1.selectbox(f"Barcel:", prods_barcel, key=f"b_{j}")
                    c_p = c_sel2.selectbox(f"Competencia:", prods_comp, key=f"c_{j}")
                    
                    v_b = df_p[df_p["Producto"]==b_p]["Precio por Kg ($)"].values[0]
                    v_c = df_p[df_p["Producto"]==c_p]["Precio por Kg ($)"].values[0]
                    res = int((v_b / v_c) * 100)
                    
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-around; background: #f9f9f9; padding: 10px; border-radius: 8px; border: 1px solid #eee;">
                        <div style="text-align: center;"><small>Barcel</small><br><b style="color:#0B3C8C;">${v_b}</b></div>
                        <div style="background: #0B3C8C; color: white; padding: 10px 20px; border-radius: 5px; font-size: 22px; font-weight: bold;">{res}</div>
                        <div style="text-align: center;"><small>Comp.</small><br><b style="color:#F5C400;">${v_c}</b></div>
                    </div>
                    """, unsafe_allow_html=True)
