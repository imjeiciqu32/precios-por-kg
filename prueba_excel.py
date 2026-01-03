import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- Configuración ---
st.set_page_config(page_title="Price Ladder & SOM Analysis", layout="wide")
DB_FILE = "historico_productos.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
        df["SOM (%)"] = pd.to_numeric(df["SOM (%)"], errors='coerce').fillna(0.0)
        df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1)
        df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(0)
        return df
    return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])

if "data" not in st.session_state:
    st.session_state.data = load_data()

# --- Formulario y Tabla (Se mantiene igual para no perder tus datos) ---
st.title("📊 Análisis de Escalera y Participación (SOM)")

# ... (Aquí va tu sección de formulario y data_editor que ya tienes) ...

# --- GRÁFICO DE DOS NIVELES ---
if not st.session_state.data.empty:
    df_plot = st.session_state.data.copy()
    mapa_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df_plot["Orden_Oca"] = df_plot["Ocasión"].str.upper().map(mapa_oca).fillna(99)
    df_plot = df_plot.sort_values(by=["Orden_Oca", "Precio ($)"])

    colores_map = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}

    # CREAR SUBPLOTS: 2 filas, 1 columna
    # row_heights=[0.2, 0.8] hace que el de arriba sea pequeño y el de abajo el principal
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.05, 
        row_heights=[0.25, 0.75]
    )

    # 1. GRÁFICO SUPERIOR: Share of Market (Línea)
    fig.add_trace(
        go.Scatter(
            x=[df_plot["Ocasión"], df_plot["Producto"]],
            y=df_plot["SOM (%)"],
            mode="lines+markers+text",
            line=dict(color="#B0B0B0", width=1.5),
            marker=dict(size=8, color="#444"),
            text=[f"<b>{s}%</b>" for s in df_plot["SOM (%)"]],
            textposition="top center",
            name="SOM %",
        ),
        row=1, col=1
    )

    # 2. GRÁFICO INFERIOR: Escalera de Precios (Barras)
    fig.add_trace(
        go.Bar(
            x=[df_plot["Ocasión"], df_plot["Producto"]],
            y=df_plot["Precio ($)"],
            marker_color=[colores_map.get(str(fab).upper(), "#B0B0B0") for fab in df_plot["Fabricante"]],
            text=[f"<b>${p}</b>" for p in df_plot["Precio ($)"]],
            textposition='outside',
            textfont=dict(size=18, color="black"), # Tamaño grande solicitado antes
            name="Precio",
        ),
        row=2, col=1
    )

    # Anotaciones de $/Kg dentro de las barras (se anclan a la fila 2)
    for i, row in df_plot.iterrows():
        fig.add_annotation(
            x=[row["Ocasión"], row["Producto"]],
            y=row["Precio ($)"] * 0.2,
            text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
            showarrow=False,
            font=dict(size=16, color="white" if str(row["Fabricante"]).upper() == "BARCEL" else "black"),
            bgcolor="rgba(0,0,0,0.3)" if str(row["Fabricante"]).upper() == "BARCEL" else "rgba(255,255,255,0.4)",
            xref="x", yref="y2" # Esto le dice que use el eje del segundo gráfico
        )

    # Ajustes estéticos finales
    fig.update_layout(
        template="plotly_white",
        height=900,
        showlegend=False,
        margin=dict(t=50, b=150, l=60, r=40)
    )

    # Configurar ejes específicos
    fig.update_yaxes(title_text="SOM %", row=1, col=1, showgrid=True, gridcolor="#f0f0f0")
    fig.update_yaxes(title_text="Precio ($)", row=2, col=1, showgrid=True, gridcolor="#f0f0f0")
    fig.update_xaxes(tickfont=dict(size=12, family="Arial Black"), row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)
