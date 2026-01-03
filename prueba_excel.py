import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- Configuración Inicial ---
st.set_page_config(page_title="Price Ladder & SOM Analysis", layout="wide")
DB_FILE = "historico_productos.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # Asegurar que todas las columnas necesarias existan
            for col in ["Precio ($)", "Gramaje (g)", "SOM (%)"]:
                if col not in df.columns: df[col] = 0
            df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
            df["SOM (%)"] = pd.to_numeric(df["SOM (%)"], errors='coerce').fillna(0)
            df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1)
            df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(0)
            return df
        except:
            return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])
    return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])

if "data" not in st.session_state:
    st.session_state.data = load_data()

st.title("📊 Análisis de Escalera y Participación (SOM)")

# --- Sección de entrada de datos (Mantenemos tu lógica) ---
with st.expander("➕ Agregar Producto Nuevo"):
    with st.form("nuevo_p", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        p = c1.text_input("Producto")
        f = c2.selectbox("Fabricante", ["SABRITAS", "BARCEL", "OTROS"])
        o = c3.selectbox("Ocasión", ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"])
        c4, c5, c6 = st.columns(3)
        pr = c4.number_input("Precio ($)", min_value=0.0)
        gr = c5.number_input("Gramaje (g)", min_value=1.0)
        sm = c6.number_input("SOM (%)", min_value=0.0, max_value=100.0)
        if st.form_submit_button("Guardar"):
            pkg = round(pr / (gr / 1000), 0)
            nuevo = pd.DataFrame([{"Producto": p.upper(), "Fabricante": f, "Ocasión": o, "Precio ($)": pr, "Gramaje (g)": gr, "Precio por Kg ($)": pkg, "SOM (%)": sm}])
            st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
            st.session_state.data.to_csv(DB_FILE, index=False)
            st.rerun()

st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True, key="editor_principal")

# --- GRÁFICO DOBLE (DESPEGADO) ---
if not st.session_state.data.empty:
    df = st.session_state.data.copy()
    
    # Ordenamiento por Ocasión
    mapa_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df["Orden"] = df["Ocasión"].str.upper().map(mapa_oca).fillna(99)
    df = df.sort_values(by=["Orden", "Precio ($)"])

    colores = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}

    # Crear Subplots con más espacio vertical para que parezcan "despegados"
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1, # Espacio entre los dos gráficos
        row_heights=[0.3, 0.7]
    )

    # 1. Gráfico Superior: SOM %
    fig.add_trace(
        go.Scatter(
            x=[df["Ocasión"], df["Producto"]],
            y=df["SOM (%)"],
            mode="lines+markers+text",
            name="Participación (SOM)",
            line=dict(color="#D3D3D3", width=2),
            marker=dict(size=10, color="#444"),
            text=[f"<b>{s}%</b>" for s in df["SOM (%)"]],
            textposition="top center",
            textfont=dict(size=12)
        ),
        row=1, col=1
    )

    # 2. Gráfico Inferior: Escalera de Precios
    fig.add_trace(
        go.Bar(
            x=[df["Ocasión"], df["Producto"]],
            y=df["Precio ($)"],
            marker_color=[colores.get(str(fab).upper(), "#B0B0B0") for fab in df["Fabricante"]],
            text=[f"<b>${p}</b>" for p in df["Precio ($)"]],
            textposition='outside',
            textfont=dict(size=20, color="black"), # PRECIO DESEMBOLSO GRANDE
            name="Desembolso"
        ),
        row=2, col=1
    )

    # Etiquetas de $/Kg dentro de las barras
    for i in range(len(df)):
        row = df.iloc[i]
        fig.add_annotation(
            x=i, # Posición indexada para evitar errores de coincidencia de nombres
            y=row["Precio ($)"] * 0.15,
            text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
            showarrow=False,
            font=dict(size=16, color="white" if str(row["Fabricante"]).upper() == "BARCEL" else "black"),
            bgcolor="rgba(0,0,0,0.3)" if str(row["Fabricante"]).upper() == "BARCEL" else "rgba(255,255,255,0.4)",
            row=2, col=1
        )

    # Ajustes finales de diseño
    fig.update_layout(
        template="plotly_white",
        height=900,
        showlegend=False,
        margin=dict(t=50, b=150, l=60, r=40)
    )

    # Personalizar Ejes
    fig.update_yaxes(title_text="SOM %", row=1, col=1, range=[0, df["SOM (%)"].max() * 1.4])
    fig.update_yaxes(title_text="Precio ($)", row=2, col=1, range=[0, df["Precio ($)"].max() * 1.3])
    fig.update_xaxes(tickfont=dict(size=12, family="Arial Black"), row=2, col=1, automargin=True)

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Agrega datos para generar el análisis visual.")
