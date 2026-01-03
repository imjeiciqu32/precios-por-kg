import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Price Ladder Expert", layout="wide")
DB_FILE = "historico_productos.csv"

# --- 2. REPOSITORIO DE PLANTILLAS (Configúralo aquí) ---
# Puedes añadir tantas como quieras siguiendo este formato
PLANTILLAS = {
    "Escalera Oxxo - Individual": [
        {"Producto": "MINI TAKIS 35G", "Fabricante": "BARCEL", "Ocasión": "BITES", "Precio ($)": 10.0, "Gramaje (g)": 35, "SOM (%)": 1.4},
        {"Producto": "DORITOS 41G", "Fabricante": "SABRITAS", "Ocasión": "BITES", "Precio ($)": 15.0, "Gramaje (g)": 41, "SOM (%)": 0.7},
        {"Producto": "TAKIS 70G", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 70, "SOM (%)": 8.2},
        {"Producto": "DORITOS 58G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 58, "SOM (%)": 12.1}
    ],
    "Escalera Supermercado - Familiar": [
        {"Producto": "TAKIS 200G", "Fabricante": "BARCEL", "Ocasión": "FAMILIAR", "Precio ($)": 45.0, "Gramaje (g)": 200, "SOM (%)": 1.2},
        {"Producto": "DORITOS 245G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 56.0, "Gramaje (g)": 245, "SOM (%)": 3.2},
        {"Producto": "CHURRUMAIS 185G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 40.0, "Gramaje (g)": 185, "SOM (%)": 0.9}
    ],
    "Escalera Mayoreo - Compartir": [
        {"Producto": "RUNNERS 200G", "Fabricante": "BARCEL", "Ocasión": "COMPARTIR", "Precio ($)": 40.0, "Gramaje (g)": 200, "SOM (%)": 0.2},
        {"Producto": "DORITOS 146G", "Fabricante": "SABRITAS", "Ocasión": "COMPARTIR", "Precio ($)": 40.0, "Gramaje (g)": 146, "SOM (%)": 1.1}
    ]
}

# --- 3. FUNCIONES DE DATOS ---
def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # Forzar tipos de datos
        df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
        df["SOM (%)"] = pd.to_numeric(df["SOM (%)"], errors='coerce').fillna(0)
        df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1)
        df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(0)
        return df
    return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])

if "data" not in st.session_state:
    st.session_state.data = load_data()

# --- 4. BARRA LATERAL (CONTROL DE PLANTILLAS) ---
st.sidebar.header("📁 Repositorio de Escaleras")
nombre_plantilla = st.sidebar.selectbox("Selecciona una configuración:", ["-- Seleccionar --"] + list(PLANTILLAS.keys()))

if st.sidebar.button("Cargar Escalera"):
    if nombre_plantilla != "-- Seleccionar --":
        # Cargar los datos de la plantilla y calcular el precio/kg
        nuevos_datos = pd.DataFrame(PLANTILLAS[nombre_plantilla])
        nuevos_datos["Precio por Kg ($)"] = (nuevos_datos["Precio ($)"] / (nuevos_datos["Gramaje (g)"] / 1000)).round(0)
        
        st.session_state.data = nuevos_datos
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Borrar Histórico"):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    st.session_state.data = pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])
    st.rerun()

# --- 5. INTERFAZ PRINCIPAL ---
st.title("📊 Análisis de Escalera y Participación (SOM)")

# Editor de datos dinámico
st.subheader("📝 Editor de Datos")
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)

# Actualizar si hay cambios en el editor
if not edited_df.equals(st.session_state.data):
    edited_df["Precio por Kg ($)"] = (edited_df["Precio ($)"] / (edited_df["Gramaje (g)"].replace(0, 1) / 1000)).round(0)
    st.session_state.data = edited_df
    edited_df.to_csv(DB_FILE, index=False)

# --- 6. GRÁFICO PROFESIONAL ---
if not st.session_state.data.empty:
    df_plot = st.session_state.data.copy()
    mapa_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df_plot["Orden_Oca"] = df_plot["Ocasión"].str.upper().map(mapa_oca).fillna(99)
    df_plot = df_plot.sort_values(by=["Orden_Oca", "Precio ($)"])

    # Subplots: SOM arriba, Barras abajo
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.25, 0.75])

    # 6a. SOM (Capas)
    fig.add_trace(go.Scatter(
        x=[df_plot["Ocasión"], df_plot["Producto"]], 
        y=df_plot["SOM (%)"], 
        mode="lines+markers", 
        line=dict(color="#D3D3D3", width=1.5), 
        marker=dict(size=1)
    ), row=1, col=1)

    for i, row in enumerate(df_plot.itertuples()):
        fig.add_annotation(
            x=i, y=row._7, text=f"<b>{row._7}%</b>", showarrow=False,
            yshift=0, font=dict(size=11), bgcolor="#F0F0F0", 
            bordercolor="#BDBDBD", borderwidth=1, row=1, col=1
        )

    # 6b. BARRAS (Escalera)
    colores = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    fig.add_trace(go.Bar(
        x=[df_plot["Ocasión"], df_plot["Producto"]], 
        y=df_plot["Precio ($)"],
        marker_color=[colores.get(str(f).upper(), "#B0B0B0") for f in df_plot["Fabricante"]],
        text=[f"<b>${p}</b>" for p in df_plot["Precio ($)"]], 
        textposition='outside',
        textfont=dict(size=18, color="black")
    ), row=2, col=1)

    # 6c. $/Kg ALINEADOS EN BASE (Y FIJO)
    for i, row in enumerate(df_plot.itertuples()):
        fig.add_annotation(
            x=i, y=2.5, text=f"<b>${int(row._6)}</b>", showarrow=False,
            font=dict(size=14, color="white" if row.Fabricante == "BARCEL" else "black"),
            bgcolor="rgba(0,0,0,0.4)" if row.Fabricante == "BARCEL" else "rgba(255,255,255,0.5)", 
            row=2, col=1
        )

    fig.update_layout(height=800, template="plotly_white", showlegend=False, margin=dict(t=20, b=100))
    fig.update_yaxes(showgrid=False, showticklabels=False, row=1, col=1, range=[0, df_plot["SOM (%)"].max()*2.5])
    st.plotly_chart(fig, use_container_width=True)

    # --- 7. SECCIÓN INDEX $/KG (ESTILO COMPARATIVA) ---
    st.divider()
    st.subheader("📈 Cálculo de Index vs Competencia")
    
    # Solo mostrar si hay al menos un producto de Barcel y otro de competencia
    if "BARCEL" in df_plot["Fabricante"].values and len(df_plot["Fabricante"].unique()) > 1:
        c1, c2, c3 = st.columns([1, 1, 2])
        
        with c1:
            b_prod = st.selectbox("Producto Barcel:", df_plot[df_plot["Fabricante"]=="BARCEL"]["Producto"].unique())
        with c2:
            c_prod = st.selectbox("Producto Competencia:", df_plot[df_plot["Fabricante"]!="BARCEL"]["Producto"].unique())
        
        val_b = df_plot[df_plot["Producto"]==b_prod]["Precio por Kg ($)"].values[0]
        val_c = df_plot[df_plot["Producto"]==c_prod]["Precio por Kg ($)"].values[0]
        idx = int((val_b / val_c) * 100)
        
        with c3:
            st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: center; background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6;">
                <div style="text-align: center; margin-right: 20px;">
                    <span style="color: #666; font-size: 0.8em;">{b_prod}</span><br>
                    <span style="font-weight: bold; color: #0B3C8C;">${val_b} Kg</span>
                </div>
                <div style="background-color: #0B3C8C; color: white; padding: 10px 20px; border-radius: 5px; font-size: 22px; font-weight: bold;">
                    INDEX: {idx}
                </div>
                <div style="text-align: center; margin-left: 20px;">
                    <span style="color: #666; font-size: 0.8em;">{c_prod}</span><br>
                    <span style="font-weight: bold; color: #F5C400;">${val_c} Kg</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
