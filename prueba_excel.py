import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ----------------------------
# 1. Configuración y Datos
# ----------------------------
st.set_page_config(page_title="Price Ladder & SOM Pro", layout="wide")
DB_FILE = "historico_productos.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
        df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1)
        # Aseguramos que SOM exista y sea numérico
        if "SOM (%)" not in df.columns: df["SOM (%)"] = 0.0
        df["SOM (%)"] = pd.to_numeric(df["SOM (%)"], errors='coerce').fillna(0.0)
        df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(0)
        return df
    return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])

if "data" not in st.session_state:
    st.session_state.data = load_data()

st.title("📊 Escaleras de Precios Dinámicas")

# ----------------------------
# 2. Entrada de Datos Mejorada
# ----------------------------
with st.expander("➕ Agregar Producto Nuevo", expanded=False):
    with st.form("nuevo_producto", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        p = c1.text_input("Producto")
        f = c2.selectbox("Fabricante", ["SABRITAS", "BARCEL", "OTROS"])
        o = c3.selectbox("Ocasión", ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"])
        
        c4, c5, c6 = st.columns(3)
        pr = c4.number_input("Precio ($)", min_value=0.0)
        gr = c5.number_input("Gramaje (g)", min_value=1.0)
        som = c6.number_input("Share of Market (%)", min_value=0.0, max_value=100.0, step=0.1)
        
        if st.form_submit_button("Guardar"):
            pkg = round(pr / (gr / 1000), 0)
            nuevo = pd.DataFrame([{"Producto": p.upper(), "Fabricante": f, "Ocasión": o, 
                                   "Precio ($)": pr, "Gramaje (g)": gr, 
                                   "Precio por Kg ($)": pkg, "SOM (%)": som}])
            st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
            st.session_state.data.to_csv(DB_FILE, index=False)
            st.rerun()

# Tabla editable
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = edited_df
    edited_df.to_csv(DB_FILE, index=False)
    st.rerun()

# ----------------------------
# 3. Gráfico de Doble Eje (Barras + Línea SOM)
# ----------------------------
if not st.session_state.data.empty:
    df_plot = st.session_state.data.copy()
    
    # Ordenamiento
    mapa_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df_plot["Orden_Oca"] = df_plot["Ocasión"].str.upper().map(mapa_oca).fillna(99)
    df_plot = df_plot.sort_values(by=["Orden_Oca", "Precio ($)"])

    colores_map = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    
    # Crear figura con eje secundario
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. BARRAS: Precio Desembolso
    fig.add_trace(
        go.Bar(
            x=[df_plot["Ocasión"], df_plot["Producto"]],
            y=df_plot["Precio ($)"],
            marker_color=[colores_map.get(str(fab).upper(), "#B0B0B0") for fab in df_plot["Fabricante"]],
            text=[f"<b>${p}</b>" for p in df_plot["Precio ($)"]],
            textposition='outside',
            textfont=dict(size=18, color="black"),
            name="Precio Desembolso",
        ),
        secondary_y=False,
    )

    # 2. LÍNEA: Share of Market (SOM)
    fig.add_trace(
        go.Scatter(
            x=[df_plot["Ocasión"], df_plot["Producto"]],
            y=df_plot["SOM (%)"],
            mode="lines+markers+text",
            line=dict(color="#D3D3D3", width=2), # Línea gris tenue como en tu imagen
            marker=dict(size=8, symbol="circle"),
            text=[f"<b>{s}%</b>" for s in df_plot["SOM (%)"]],
            textposition="top center",
            textfont=dict(size=11, color="#444"),
            name="SOM (%)",
        ),
        secondary_y=True,
    )

    # Anotaciones de $/Kg (Dentro de la barra)
    for i, row in df_plot.iterrows():
        fig.add_annotation(
            x=[row["Ocasión"], row["Producto"]],
            y=row["Precio ($)"] * 0.15,
            text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
            showarrow=False,
            font=dict(size=15, color="white" if str(row["Fabricante"]).upper() == "BARCEL" else "black"),
            bgcolor="rgba(0,0,0,0.3)" if str(row["Fabricante"]).upper() == "BARCEL" else "rgba(255,255,255,0.4)",
            secondary_y=False
        )

    # Configuración de Layout
    fig.update_layout(
        template="plotly_white",
        height=750,
        margin=dict(t=80, b=150, l=50, r=50),
        xaxis=dict(tickfont=dict(size=12, family="Arial Black"), automargin=True),
        yaxis=dict(title="<b>Precio Desembolso ($)</b>", side="left", range=[0, df_plot["Precio ($)"].max() * 1.3]),
        yaxis2=dict(title="<b>Share of Market (%)</b>", side="right", showgrid=False, range=[0, df_plot["SOM (%)"].max() * 1.5]),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Agrega productos para visualizar el análisis.")
