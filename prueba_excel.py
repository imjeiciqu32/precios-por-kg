import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- Configuración Inicial ---
st.set_page_config(page_title="Price Ladder Pro", layout="wide")
DB_FILE = "historico_productos.csv"

# Función para cargar datos con limpieza
def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
            df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1)
            df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(0)
            return df
        except:
            return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)"])
    return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)"])

if "data" not in st.session_state:
    st.session_state.data = load_data()

st.title("📊 Escalera de Precios Avanzada")

# --- Sección de Carga (Excel/CSV) ---
with st.expander("📂 Cargar desde Excel o CSV", expanded=False):
    file = st.file_uploader("Sube tu archivo", type=["xlsx", "csv"])
    if file:
        try:
            if file.name.endswith('.xlsx'):
                # Intento de lectura con manejo de error de dependencia
                try:
                    df_new = pd.read_excel(file)
                except ImportError:
                    st.error("Falta la librería 'openpyxl'. Si estás en local, corre: pip install openpyxl")
                    df_new = None
            else:
                df_new = pd.read_csv(file)
            
            if df_new is not None:
                # Estandarizar columnas
                df_new.columns = [c.strip() for c in df_new.columns]
                st.session_state.data = pd.concat([st.session_state.data, df_new], ignore_index=True).drop_duplicates()
                st.session_state.data.to_csv(DB_FILE, index=False)
                st.success("✅ Datos integrados correctamente.")
                st.rerun()
        except Exception as e:
            st.error(f"Error técnico: {e}")

# --- Gráfico de Escalera ---
if not st.session_state.data.empty:
    df = st.session_state.data.copy()
    
    # Ordenar por Ocasión (Lógica de mercado) y Precio
    mapa_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df["Orden_Oca"] = df["Ocasión"].map(mapa_oca).fillna(99)
    df = df.sort_values(by=["Orden_Oca", "Precio ($)", "Precio por Kg ($)"])

    colores = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    
    fig = go.Figure()

    # Construcción de barras mezcladas
    fig.add_trace(go.Bar(
        x=[df["Ocasión"], df["Producto"]],
        y=df["Precio ($)"],
        marker_color=[colores.get(f, "#B0B0B0") for f in df["Fabricante"]],
        text=[f"<b>${p}</b>" for p in df["Precio ($)"]],
        textposition='outside',
        textfont=dict(size=14, color="black"),
    ))

    # Anotaciones de Precio por Kg (Más grandes y claras)
    for i, row in df.iterrows():
        fig.add_annotation(
            x=[row["Ocasión"], row["Producto"]],
            y=row["Precio ($)"] * 0.1, # Posicionado en la base de la barra
            text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
            showarrow=False,
            font=dict(
                size=13, # Un poco más grande como pediste
                color="white" if row["Fabricante"] == "BARCEL" else "black"
            ),
            bgcolor="rgba(0,0,0,0.4)" if row["Fabricante"] == "BARCEL" else "rgba(255,255,255,0.5)"
        )

    # Diseño para que se vean las Ocasiones (Eje X Multi-nivel)
    fig.update_layout(
        template="plotly_white",
        height=700,
        margin=dict(t=50, b=150, l=50, r=50),
        xaxis=dict(
            title=None,
            tickfont=dict(size=11),
            showgrid=True,
            gridcolor="lightgrey"
        ),
        yaxis=dict(title="Precio Desembolso ($)", showgrid=True, gridcolor="#f0f0f0"),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla editable abajo para ajustes rápidos
    st.subheader("📝 Editor de datos rápido")
    st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)

else:
    st.info("La base de datos está vacía. Sube un Excel o usa el editor.")
