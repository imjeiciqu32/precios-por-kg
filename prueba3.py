import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- Configuración y Datos ---
st.set_page_config(page_title="Price Ladder Pro", layout="wide")
DB_FILE = "historico_productos.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
        df["Precio por Kg ($)"] = pd.to_numeric(df["Precio por Kg ($)"], errors='coerce').fillna(0)
        return df
    return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)"])

if "data" not in st.session_state:
    st.session_state.data = load_data()

# --- Formulario ---
st.title("📊 Escalera de Precios Multimarca")
with st.expander("➕ Añadir o Editar SKUs", expanded=False):
    with st.form("form_registro", clear_on_submit=True):
        c1, c2, c3, c4, c5 = st.columns(5)
        prod = c1.text_input("Producto (ej: Takis 70g)")
        fab = c2.selectbox("Fabricante", ["SABRITAS", "BARCEL", "OTROS"])
        oca = c3.selectbox("Ocasión", ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"])
        pre = c4.number_input("Precio ($)", min_value=0.0)
        gra = c5.number_input("Gramaje (g)", min_value=1.0)
        
        if st.form_submit_button("Guardar"):
            pkg = round(pre / (gra / 1000), 0)
            nuevo = pd.DataFrame([{"Producto": prod.upper(), "Fabricante": fab, "Ocasión": oca, "Precio ($)": pre, "Gramaje (g)": gra, "Precio por Kg ($)": pkg}])
            st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
            st.session_state.data.to_csv(DB_FILE, index=False)
            st.rerun()

# --- Tabla de Gestión ---
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = edited_df
    edited_df.to_csv(DB_FILE, index=False)

# --- GRÁFICO: LA ESCALERA PERFECTA ---
if not st.session_state.data.empty:
    df = st.session_state.data.copy()
    
    # 1. Definir orden lógico
    mapa_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df["Orden_Oca"] = df["Ocasión"].map(mapa_oca)
    
    # 2. ORDENAR TODO (Aquí es donde se mezclan los fabricantes)
    df = df.sort_values(by=["Orden_Oca", "Precio ($)", "Precio por Kg ($)"], ascending=[True, True, True])

    # 3. Asignar colores manualmente para evitar que Plotly los separe
    colores_map = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    df["Color"] = df["Fabricante"].map(colores_map)

    # 4. Construcción del gráfico
    fig = go.Figure()

    # Añadimos una sola traza de barras para que el orden sea absoluto
    fig.add_trace(go.Bar(
        x=[df["Ocasión"], df["Producto"]],
        y=df["Precio ($)"],
        marker_color=df["Color"], # Color individual por barra
        text=df["Precio ($)"].apply(lambda x: f"${x}"),
        textposition='outside',
        showlegend=False # Ocultamos leyenda automática para crear una personalizada
    ))

    # Añadir Leyenda Manual (para que aparezca Barcel y Sabritas arriba)
    for fab, col in colores_map.items():
        fig.add_trace(go.Bar(name=fab, x=[None], y=[None], marker_color=col))

    # Etiquetas de Precio/Kg dentro de la barra (como en tu ejemplo)
    for i, row in df.iterrows():
        fig.add_annotation(
            x=[row["Ocasión"], row["Producto"]],
            y=0,
            yshift=20, # Un poco arriba de la base
            text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
            showarrow=False,
            font=dict(color="white" if row["Fabricante"]=="BARCEL" else "black", size=11),
            bgcolor="rgba(255,255,255,0.3)" if row["Fabricante"]=="SABRITAS" else None
        )

    fig.update_layout(
        title="Escalera de Precios: Desembolso y $/Kg (Mezclado)",
        xaxis=dict(title=None, tickfont=dict(size=10)),
        yaxis=dict(title="Precio Desembolso ($)", showgrid=True, gridcolor="lightgrey"),
        plot_bgcolor="white",
        height=600,
        margin=dict(t=50, b=100)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Botones de Exportación ---
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📂 Descargar Datos (Excel/CSV)", csv, "escalera_precios.csv", "text/csv")
    with col_dl2:
        st.info("📸 Tip: Usa el icono de cámara en el gráfico para descargar como imagen PNG.")

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aún no hay datos para graficar.")
