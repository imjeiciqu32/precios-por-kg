import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- Configuración y Persistencia ---
st.set_page_config(page_title="Price Ladder Pro v2", layout="wide")
DB_FILE = "historico_productos.csv"

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

# --- INTERFAZ: CARGA DE DATOS ---
st.title("📊 Escalera de Precios Avanzada")

col_input1, col_input2 = st.columns([2, 1])

with col_input1:
    with st.expander("📂 Cargar desde Excel", expanded=False):
        uploaded_file = st.file_uploader("Sube tu archivo .xlsx o .csv", type=["xlsx", "csv"])
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.xlsx'):
                    new_data = pd.read_excel(uploaded_file)
                else:
                    new_data = pd.read_csv(uploaded_file)
                
                # Validar columnas mínimas necesarias
                required = ["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)"]
                if all(col in new_data.columns for col in required):
                    new_data["Precio por Kg ($)"] = (new_data["Precio ($)"] / (new_data["Gramaje (g)"] / 1000)).round(0)
                    st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True).drop_duplicates()
                    st.session_state.data.to_csv(DB_FILE, index=False)
                    st.success("✅ ¡Excel cargado con éxito!")
                    st.rerun()
                else:
                    st.error(f"El Excel debe tener estas columnas: {required}")
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

with col_input2:
    if st.button("🗑️ Borrar Todo el Historial"):
        st.session_state.data = pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)"])
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()

# --- GESTIÓN DE TABLA ---
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = edited_df
    edited_df.to_csv(DB_FILE, index=False)
    st.rerun()

# --- GRÁFICO OPTIMIZADO ---
if not st.session_state.data.empty:
    df = st.session_state.data.copy()
    mapa_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df["Orden_Oca"] = df["Ocasión"].map(mapa_oca).fillna(99)
    df = df.sort_values(by=["Orden_Oca", "Precio ($)", "Precio por Kg ($)"])

    colores_map = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    df["Color"] = df["Fabricante"].map(colores_map).fillna("#B0B0B0")

    fig = go.Figure()

    # Barras principales
    fig.add_trace(go.Bar(
        x=[df["Ocasión"], df["Producto"]],
        y=df["Precio ($)"],
        marker_color=df["Color"],
        # Precios superiores en NEGRITA y más visibles
        text=df["Precio ($)"].apply(lambda x: f"<b>${x}</b>"),
        textposition='outside',
        textfont=dict(size=14), # Precio desembolso más grande
        showlegend=False
    ))

    # Anotaciones de $/Kg (MÁS GRANDES y posicionadas)
    for i, row in df.iterrows():
        fig.add_annotation(
            x=[row["Ocasión"], row["Producto"]],
            y=0,
            yshift=25,
            text=f"<b>${int(row['Precio por Kg ($)'])}</b>", # Negritas
            showarrow=False,
            font=dict(
                color="white" if row["Fabricante"]=="BARCEL" else "black", 
                size=13 # Precio por kg un poquito más grande
            ),
            bgcolor="rgba(255,255,255,0.3)" if row["Fabricante"]=="SABRITAS" else "rgba(0,0,0,0.1)"
        )

    # Leyenda Manual
    for fab, col in colores_map.items():
        fig.add_trace(go.Bar(name=fab, x=[None], y=[None], marker_color=col))

    # Ajustes de diseño para que las OCASIONES se vean bien
    fig.update_layout(
        title="Escalera de Precios Competitiva",
        xaxis=dict(
            title=None,
            tickangle=0, # Texto horizontal para legibilidad
            tickfont=dict(size=11),
            groupwidgets=True, # Mantiene las ocasiones agrupadas visualmente
            automargin=True
        ),
        yaxis=dict(title="Desembolso ($)", gridcolor="#f0f0f0", range=[0, df["Precio ($)"].max() * 1.2]),
        plot_bgcolor="white",
        height=700, # Aumentamos altura para dar aire a las etiquetas
        margin=dict(t=80, b=150) # Más margen inferior para las etiquetas del eje X
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Carga un Excel o añade productos para visualizar el gráfico.")
