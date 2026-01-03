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
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1).replace(0, 1)
    df["SOM (%)"] = pd.to_numeric(df["SOM (%)"], errors='coerce').fillna(0)
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(0)
    return df

if "data" not in st.session_state:
    if os.path.exists(DB_FILE):
        st.session_state.data = calcular_pkg(pd.read_csv(DB_FILE))
    else:
        st.session_state.data = pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])

# --- 3. BARRA LATERAL ---
st.sidebar.header("📁 Gestión")
nombre_plantilla = st.sidebar.selectbox("Cargar Plantilla:", ["-- Seleccionar --"] + list(PLANTILLAS.keys()))

if st.sidebar.button("Cargar Escalera"):
    if nombre_plantilla != "-- Seleccionar --":
        st.session_state.data = calcular_pkg(pd.DataFrame(PLANTILLAS[nombre_plantilla]))
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Reset"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.data = pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])
    st.rerun()

st.title("📊 Análisis de Escalera y Participación (SOM)")

# --- 4. AGREGAR SKU ---
with st.expander("➕ Agregar nuevo producto manualmente"):
    with st.form("nuevo_sku_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        f_nom = c1.text_input("Nombre del Producto").upper()
        f_fab = c2.selectbox("Fabricante", ["BARCEL", "SABRITAS", "OTROS"])
        f_oca = c3.selectbox("Ocasión", ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"])
        c4, c5, c6 = st.columns(3)
        f_pre = c4.number_input("Precio ($)", min_value=0.0, step=0.5)
        f_gra = c5.number_input("Gramaje (g)", min_value=1.0, step=1.0)
        f_som = c6.number_input("SOM (%)", min_value=0.0, max_value=100.0, step=0.1)
        if st.form_submit_button("Añadir"):
            nuevo = pd.DataFrame([{"Producto": f_nom, "Fabricante": f_fab, "Ocasión": f_oca, "Precio ($)": f_pre, "Gramaje (g)": f_gra, "SOM (%)": f_som}])
            st.session_state.data = calcular_pkg(pd.concat([st.session_state.data, nuevo], ignore_index=True))
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

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.3, 0.7])

    # SOM con Etiquetas Flotantes
    fig.add_trace(go.Scatter(x=[df_p["Ocasión"], df_p["Producto"]], y=df_p["SOM (%)"], mode="lines+markers", line=dict(color="#D3D3D3", width=2)), row=1, col=1)
    for i, row in enumerate(df_p.itertuples(index=False)):
        fig.add_annotation(x=i, y=row._5, text=f"<b>{row._5}%</b>", showarrow=False, yshift=15, font=dict(size=12), bgcolor="#E0E0E0", bordercolor="#BDBDBD", borderwidth=1, row=1, col=1)

    # Barras Precio
    colors = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    fig.add_trace(go.Bar(x=[df_p["Ocasión"], df_p["Producto"]], y=df_p["Precio ($)"], marker_color=[colors.get(f.upper(), "#B0B0B0") for f in df_p["Fabricante"]],
                         text=[f"<b>${p}</b>" for p in df_p["Precio ($)"]], textposition='outside', textfont=dict(size=15)), row=2, col=1)

    # $/Kg en base
    for i, row in enumerate(df_p.itertuples(index=False)):
        fig.add_annotation(x=i, y=2.5, text=f"<b>${int(row._6)}</b>", showarrow=False, font=dict(size=13, color="white" if row.Fabricante=="BARCEL" else "black"),
                           bgcolor="rgba(0,0,0,0.6)" if row.Fabricante=="BARCEL" else "rgba(255,255,255,0.7)", row=2, col=1)

    fig.update_layout(height=700, template="plotly_white", showlegend=False, margin=dict(t=30, b=50))
    fig.update_xaxes(tickfont=dict(size=11, color="black", family="Arial Black"), row=2, col=1)
    st.plotly_chart(fig, use_container_width=True)

    # --- 7. MULTI-INDEX PRO (CON FONDOS Y TENDENCIAS) ---
    st.divider()
    st.subheader("📈 Comparativas Index $/Kg (Barcel vs Competencia)")
    
    barcel_list = df_p[df_p["Fabricante"]=="BARCEL"]["Producto"].unique()
    comp_list = df_p[df_p["Fabricante"]!="BARCEL"]["Producto"].unique()

    if len(barcel_list) > 0 and len(comp_list) > 0:
        idx_cols = st.columns(4)
        for i in range(4):
            with idx_cols[i]:
                p_b = st.selectbox(f"B{i}", barcel_list, key=f"sb{i}", label_visibility="collapsed")
                p_c = st.selectbox(f"C{i}", comp_list, key=f"sc{i}", label_visibility="collapsed")
                
                v_b = df_p[df_p["Producto"]==p_b]["Precio por Kg ($)"].values[0]
                v_c = df_p[df_p["Producto"]==p_c]["Precio por Kg ($)"].values[0]
                index_val = int((v_b / v_c) * 100)
                
                # Lógica de color y flecha
                bg_color = "#0B3C8C" if index_val <= 100 else "#D32F2F"
                icon = "🔽" if index_val <= 100 else "🔼"
                label_trend = "EFICIENTE" if index_val <= 100 else "PREMIUM"

                st.markdown(f"""
                    <div style="background-color: {bg_color}; color: white; padding: 12px; border-radius: 10px; text-align: center; box-shadow: 2px 2px 8px rgba(0,0,0,0.2);">
                        <div style="font-size: 0.7rem; font-weight: bold; opacity: 0.9;">INDEX $/KG</div>
                        <div style="font-size: 2.2rem; font-weight: 900; margin: -5px 0;">{index_val}</div>
                        <div style="font-size: 0.7rem; font-weight: bold; margin-bottom: 8px;">{icon} {label_trend}</div>
                        <div style="display: flex; justify-content: space-between; background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 5px;">
                            <div style="text-align: left;"><small>Barcel</small><br><b>${int(v_b)}</b></div>
                            <div style="text-align: right;"><small>Comp.</small><br><b>${int(v_c)}</b></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
