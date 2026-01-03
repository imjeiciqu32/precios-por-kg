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
   "DT - MAÍZ": [
        {"Producto": "MINI TAKIS 35G", "Fabricante": "BARCEL", "Ocasión": "BITES", "Precio ($)": 10.0, "Gramaje (g)": 35, "SOM (%)": 0.7},
        {"Producto": "DORITOS 41G", "Fabricante": "SABRITAS", "Ocasión": "BITES", "Precio ($)": 15.0, "Gramaje (g)": 41, "SOM (%)": 0.7},
        {"Producto": "CHURRUMAIS 70G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 17.0, "Gramaje (g)": 70, "SOM (%)": 1.9},
        {"Producto": "TOSTACHOS 75G", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 18.0, "Gramaje (g)": 75, "SOM (%)": 0.7},
        {"Producto": "RUNNERS 72G", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 18.0, "Gramaje (g)": 72, "SOM (%)": 4.7},
        {"Producto": "FRITOS 70G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 18.0, "Gramaje (g)": 70, "SOM (%)": 8.1},
        {"Producto": "CHIPOTLES 65G", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 18.0, "Gramaje (g)": 65, "SOM (%)": 1.4},
        {"Producto": "RANCHERITOS 58G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 18.0, "Gramaje (g)": 58, "SOM (%)": 3.9},
        {"Producto": "TAKIS 70G", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 70, "SOM (%)": 13.8},
        {"Producto": "DORITOS DINAMITA 70G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 70, "SOM (%)": 9.0},
        {"Producto": "TOSTITOS 62G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 62, "SOM (%)": 6.7},
        {"Producto": "DORITOS 58G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 58, "SOM (%)": 22.4},
        {"Producto": "DORITOS DINAMITA 120G", "Fabricante": "SABRITAS", "Ocasión": "HAMBRE", "Precio ($)": 25.0, "Gramaje (g)": 120, "SOM (%)": 0.6},
        {"Producto": "TOSTITOS 110G", "Fabricante": "SABRITAS", "Ocasión": "HAMBRE", "Precio ($)": 25.0, "Gramaje (g)": 110, "SOM (%)": 0.0},
        {"Producto": "DORITOS 100G", "Fabricante": "SABRITAS", "Ocasión": "HAMBRE", "Precio ($)": 25.0, "Gramaje (g)": 100, "SOM (%)": 3.6},
        {"Producto": "DORITOS NACHO 146G", "Fabricante": "SABRITAS", "Ocasión": "COMPARTIR", "Precio ($)": 40.0, "Gramaje (g)": 146, "SOM (%)": 0.9},
        {"Producto": "RANCHERITOS 145G", "Fabricante": "SABRITAS", "Ocasión": "COMPARTIR", "Precio ($)": 40.0, "Gramaje (g)": 145, "SOM (%)": 0.2},
        {"Producto": "RUNNERS 200G", "Fabricante": "BARCEL", "Ocasión": "FAMILIAR", "Precio ($)": 40.0, "Gramaje (g)": 200, "SOM (%)": 0.0},
        {"Producto": "CHURRUMAIS 185G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 40.0, "Gramaje (g)": 185, "SOM (%)": 0.1},
        {"Producto": "TOSTITOS 175G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 40.0, "Gramaje (g)": 175, "SOM (%)": 0.7},
        {"Producto": "FRITOS 170G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 40.0, "Gramaje (g)": 170, "SOM (%)": 0.1},
        {"Producto": "TAKIS 200G", "Fabricante": "BARCEL", "Ocasión": "FAMILIAR", "Precio ($)": 45.0, "Gramaje (g)": 200, "SOM (%)": 0.2},
        {"Producto": "DORITOS 245G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 56.0, "Gramaje (g)": 245, "SOM (%)": 0.3}
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

st.title("📊 Análisis de Escalera y Participación (SOM)")

# --- EDITOR DE DATOS ---
st.subheader("📝 Tabla de Datos")
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = calcular_pkg(edited_df)
    st.session_state.data.to_csv(DB_FILE, index=False)
    st.rerun()

# --- 6. LÓGICA DEL GRÁFICO ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    ord_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df_p["O_Oca"] = df_p["Ocasión"].str.upper().map(ord_oca).fillna(99)
    df_p = df_p.sort_values(by=["O_Oca", "Precio ($)"]).reset_index(drop=True)

    # Cálculo de SOM por Ocasión
    som_por_ocasion = df_p.groupby("Ocasión")["SOM (%)"].sum().to_dict()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.3, 0.7])

    # 1. LÍNEA SOM (Etiquetas normales)
    fig.add_trace(go.Scatter(
        x=df_p["Producto"], 
        y=df_p["SOM (%)"], 
        mode="lines+markers",
        line=dict(color="#D3D3D3", width=2),
        marker=dict(size=6, color="#424242")
    ), row=1, col=1)

    for i, row in df_p.iterrows():
        fig.add_annotation(
            x=i, y=row["SOM (%)"],
            text=f"{row['SOM (%)']}%", 
            showarrow=False, yshift=15,
            font=dict(size=12, color="black"),
            row=1, col=1
        )

    # 2. BARRAS DE PRECIO
    colors = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    fig.add_trace(go.Bar(
        x=df_p["Producto"], 
        y=df_p["Precio ($)"],
        marker_color=[colors.get(str(f).upper(), "#B0B0B0") for f in df_p["Fabricante"]],
        text=[f"<b>${p}</b>" for p in df_p["Precio ($)"]], 
        textposition='outside',
        textfont=dict(size=14, color="black")
    ), row=2, col=1)

    # 3. INDEX ($/KG) DENTRO DE LAS BARRAS
    for i, row in df_p.iterrows():
        fig.add_annotation(
            x=i, y=row["Precio ($)"] * 0.15, # Lo pone en la base de la barra
            text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
            showarrow=False,
            font=dict(size=12, color="white" if row['Fabricante']=="BARCEL" else "black"),
            bgcolor="rgba(0,0,0,0.5)" if row['Fabricante']=="BARCEL" else "rgba(255,255,255,0.6)",
            row=2, col=1
        )

    # 4. OCASIONES Y SUMA SOM (ESTILO EXCEL)
    categorias_unicas = df_p["Ocasión"].unique()
    last_idx = -0.5
    for cat in categorias_unicas:
        indices = df_p.index[df_p["Ocasión"] == cat].tolist()
        start_idx = indices[0]
        end_idx = indices[-1]
        center_idx = (start_idx + end_idx) / 2
        
        # Nombre de Ocasión y % debajo
        fig.add_annotation(
            x=center_idx, y=-0.25, 
            xref="x2", yref="paper",
            text=f"{cat}<br><b>{som_por_ocasion[cat]:.1f}%</b>",
            showarrow=False,
            font=dict(size=13, color="black"),
            align="center"
        )
        
        # Línea divisoria vertical
        fig.add_vline(x=end_idx + 0.5, line_width=1, line_color="#D3D3D3", row=2, col=1)

    # CONFIGURACIÓN FINAL
    fig.update_layout(
        height=850,
        margin=dict(t=50, b=200, l=60, r=60),
        template="plotly_white",
        showlegend=False
    )
    
    fig.update_yaxes(showgrid=True, gridcolor="#F0F0F0", row=2, col=1, title="Precio ($)")
    fig.update_yaxes(showticklabels=False, row=1, col=1, range=[0, df_p["SOM (%)"].max() * 1.5])
    
    # Eje X sin negritas para los productos
    fig.update_xaxes(
        tickangle=-90,
        tickfont=dict(size=11, color="#444444", family="Arial"),
        row=2, col=1
    )
    
    st.plotly_chart(fig, use_container_width=True)
