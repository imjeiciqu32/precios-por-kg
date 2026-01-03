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
    "Escalera DT- MAÍZ": [
        {"Producto": "MINI TAKIS 35G", "Fabricante": "BARCEL", "Ocasión": "BITES", "Precio ($)": 10.0, "Gramaje (g)": 35, "SOM (%)": 1.4},
        {"Producto": "DORITOS 41G", "Fabricante": "SABRITAS", "Ocasión": "BITES", "Precio ($)": 15.0, "Gramaje (g)": 41, "SOM (%)": 0.7},
        {"Producto": "TAKIS 70G", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 70, "SOM (%)": 8.2},
        {"Producto": "DORITOS 58G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 58, "SOM (%)": 12.1},
        {"Producto": "TAKIS 200G", "Fabricante": "BARCEL", "Ocasión": "FAMILIAR", "Precio ($)": 45.0, "Gramaje (g)": 200, "SOM (%)": 1.2},
        {"Producto": "DORITOS 245G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 56.0, "Gramaje (g)": 245, "SOM (%)": 3.2}
    ],
    "Escalera Super - Familiar": [
        {"Producto": "TAKIS 200G", "Fabricante": "BARCEL", "Ocasión": "FAMILIAR", "Precio ($)": 45.0, "Gramaje (g)": 200, "SOM (%)": 1.2},
        {"Producto": "DORITOS 245G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 56.0, "Gramaje (g)": 245, "SOM (%)": 3.2}
    ]
}

def calcular_pkg(df):
    """Garantiza que todas las columnas necesarias existan y tengan datos válidos"""
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
st.sidebar.header("📁 Repositorio")
nombre_plantilla = st.sidebar.selectbox("Cargar Plantilla:", ["-- Seleccionar --"] + list(PLANTILLAS.keys()))

if st.sidebar.button("Cargar Escalera"):
    if nombre_plantilla != "-- Seleccionar --":
        nuevos_datos = pd.DataFrame(PLANTILLAS[nombre_plantilla])
        st.session_state.data = calcular_pkg(nuevos_datos)
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Reset Total"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.data = pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])
    st.rerun()

st.title("📊 Análisis de Escalera y Participación (SOM)")

# --- 4. EDITOR DE DATOS ---
st.subheader("📝 Tabla de Datos")
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = calcular_pkg(edited_df)
    st.session_state.data.to_csv(DB_FILE, index=False)
    st.rerun()

# --- 5. GRÁFICO (SOLUCIÓN DEFINITIVA DE ETIQUETAS) ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    ord_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df_p["O_Oca"] = df_p["Ocasión"].str.upper().map(ord_oca).fillna(99)
    df_p = df_p.sort_values(by=["O_Oca", "Precio ($)"])

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.3, 0.7])

    # Gráfico superior: SOM %
    fig.add_trace(go.Scatter(
        x=[df_p["Ocasión"], df_p["Producto"]], 
        y=df_p["SOM (%)"], 
        mode="lines+markers+text",
        text=[f"<b>{v}%</b>" for v in df_p["SOM (%)"]],
        textposition="top center",
        line=dict(color="#BDBDBD", width=2),
        marker=dict(size=8, color="#424242"),
        textfont=dict(size=11)
    ), row=1, col=1)

    # Gráfico inferior: Escalera de Precios
    colors = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    fig.add_trace(go.Bar(
        x=[df_p["Ocasión"], df_p["Producto"]], 
        y=df_p["Precio ($)"],
        marker_color=[colors.get(str(f).upper(), "#B0B0B0") for f in df_p["Fabricante"]],
        text=[f"<b>${p}</b>" for p in df_p["Precio ($)"]], 
        textposition='outside',
        textfont=dict(size=14, color="black")
    ), row=2, col=1)

    # ETIQUETAS $/KG (Posicionadas manualmente para evitar errores)
    for i in range(len(df_p)):
        row = df_p.iloc[i]
        fig.add_annotation(
            x=i, y=2, # Cerca de la base
            text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
            showarrow=False,
            font=dict(size=13, color="white" if row['Fabricante']=="BARCEL" else "black"),
            bgcolor="rgba(0,0,0,0.5)" if row['Fabricante']=="BARCEL" else "rgba(255,255,255,0.6)",
            row=2, col=1
        )

    fig.update_layout(height=700, template="plotly_white", showlegend=False, margin=dict(t=20, b=50))
    fig.update_yaxes(showgrid=False, showticklabels=False, row=1, col=1, range=[0, df_p["SOM (%)"].max() * 1.5])
    fig.update_yaxes(title="Precio Desembolso", row=2, col=1)
    fig.update_xaxes(tickfont=dict(size=11, color="black", family="Arial Black"), row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)

    # --- 6. MULTI-INDEX (DISEÑO PRO) ---
    st.divider()
    st.subheader("📈 Comparativas de Índice $/Kg (Market Intel)")
    
    # Filtros para Barcel y Competencia
    barcel_list = df_p[df_p["Fabricante"]=="BARCEL"]["Producto"].unique()
    comp_list = df_p[df_p["Fabricante"]!="BARCEL"]["Producto"].unique()

    if len(barcel_list) > 0 and len(comp_list) > 0:
        # Fila 1
        c1, c2 = st.columns(2)
        # Fila 2
        c3, c4 = st.columns(2)
        all_cols = [c1, c2, c3, c4]

        for i in range(4):
            with all_cols[i]:
                # El diseño "Pro": Contenedor con estilo Card
                with st.container(border=True):
                    sc1, sc2 = st.columns(2)
                    p_b = sc1.selectbox(f"Barcel {i+1}", barcel_list, key=f"sel_b{i}")
                    p_c = sc2.selectbox(f"Competencia {i+1}", comp_list, key=f"sel_c{i}")
                    
                    val_b = df_p[df_p["Producto"]==p_b]["Precio por Kg ($)"].values[0]
                    val_c = df_p[df_p["Producto"]==p_c]["Precio por Kg ($)"].values[0]
                    index_val = int((val_b / val_c) * 100)
                    
                    # HTML/CSS para un look profesional
                    color_index = "#0B3C8C" if index_val <= 100 else "#D32F2F"
                    
                    st.markdown(f"""
                        <div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border-left: 8px solid #0B3C8C; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="text-align: left;">
                                    <span style="color: #666; font-size: 0.8rem; font-weight: bold;">BARCEL $/KG</span><br>
                                    <span style="font-size: 1.2rem; font-weight: 800; color: #0B3C8C;">${val_b}</span>
                                </div>
                                <div style="text-align: center; background-color: {color_index}; color: white; padding: 10px 15px; border-radius: 10px;">
                                    <span style="font-size: 0.7rem; display: block; margin-bottom: -5px;">INDEX</span>
                                    <span style="font-size: 1.8rem; font-weight: 900;">{index_val}</span>
                                </div>
                                <div style="text-align: right;">
                                    <span style="color: #666; font-size: 0.8rem; font-weight: bold;">COMPETENCIA</span><br>
                                    <span style="font-size: 1.2rem; font-weight: 800; color: #F5C400;">${val_c}</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
