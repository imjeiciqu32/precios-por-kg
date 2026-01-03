import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# ----------------------------
# 1. Configuración y Datos
# ----------------------------
st.set_page_config(page_title="Escalera de Precios Pro", layout="wide")
DB_FILE = "historico_productos.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
        df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1)
        df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(0)
        return df
    return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)"])

if "data" not in st.session_state:
    st.session_state.data = load_data()

st.title("📊 Escalera de Precios (Desembolso y $/Kg)")

# ----------------------------
# 2. Entrada de Datos (Manual y Tabla)
# ----------------------------
with st.expander("➕ Agregar Producto Nuevo", expanded=False):
    with st.form("nuevo_producto", clear_on_submit=True):
        c1, c2, c3, c4, c5 = st.columns(5)
        p = c1.text_input("Producto")
        f = c2.selectbox("Fabricante", ["SABRITAS", "BARCEL", "OTROS"])
        o = c3.selectbox("Ocasión", ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"])
        pr = c4.number_input("Precio ($)", min_value=0.0)
        gr = c5.number_input("Gramaje (g)", min_value=1.0)
        
        if st.form_submit_button("Guardar"):
            pkg = round(pr / (gr / 1000), 0)
            nuevo = pd.DataFrame([{"Producto": p.upper(), "Fabricante": f, "Ocasión": o, "Precio ($)": pr, "Gramaje (g)": gr, "Precio por Kg ($)": pkg}])
            st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
            st.session_state.data.to_csv(DB_FILE, index=False)
            st.rerun()

# Tabla para editar/borrar
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = edited_df
    edited_df.to_csv(DB_FILE, index=False)
    st.rerun()

# ----------------------------
# 3. Gráfico de Escalera Ajustado
# ----------------------------
if not st.session_state.data.empty:
    df_plot = st.session_state.data.copy()
    
    # Ordenamiento Estricto
    mapa_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df_plot["Orden_Oca"] = df_plot["Ocasión"].str.upper().map(mapa_oca).fillna(99)
    df_plot = df_plot.sort_values(by=["Orden_Oca", "Precio ($)", "Precio por Kg ($)"])

    # Colores Sabritas/Barcel
    colores_map = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    
    fig = go.Figure()

    # Barras de Precio Desembolso
    fig.add_trace(go.Bar(
        x=[df_plot["Ocasión"], df_plot["Producto"]],
        y=df_plot["Precio ($)"],
        marker_color=[colores_map.get(str(fab).upper(), "#B0B0B0") for fab in df_plot["Fabricante"]],
        text=[f"<b>${p}</b>" for p in df_plot["Precio ($)"]], # Precios arriba en NEGRITA
        textposition='outside',
        textfont=dict(size=13, color="black"),
        showlegend=False
    ))

    # Anotaciones de $/Kg (Más GRANDES y en NEGRITA dentro de la barra)
    for i, row in df_plot.iterrows():
        fig.add_annotation(
            x=[row["Ocasión"], row["Producto"]],
            y=row["Precio ($)"] * 0.15, # Posicionado en la base
            text=f"<b>${int(row['Precio por Kg ($)'])}</b>", # $/kg en negrita y sin decimales
            showarrow=False,
            font=dict(
                size=16, # Tamaño un poco más grande
                color="white" if str(row["Fabricante"]).upper() == "BARCEL" else "black"
            ),
            bgcolor="rgba(0,0,0,0.3)" if str(row["Fabricante"]).upper() == "BARCEL" else "rgba(255,255,255,0.4)"
        )

    # Configuración del Layout para visibilidad de Ocasiones
    fig.update_layout(
        template="plotly_white",
        height=700,
        margin=dict(t=80, b=150, l=50, r=50), # Margen inferior amplio para las ocasiones
        xaxis=dict(
            title=None,
            tickfont=dict(size=12, family="Arial Black", color="black"),
            showgrid=True,
            gridcolor="#EEEEEE",
            automargin=True # Asegura que las etiquetas no se corten
        ),
        yaxis=dict(
            title="Precio Desembolso ($)",
            range=[0, df_plot["Precio ($)"].max() * 1.25] # Espacio para el texto de arriba
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # Opción de descarga
    csv = df_plot.to_csv(index=False).encode('utf-8')
    st.download_button("📂 Descargar Datos (CSV)", csv, "escalera_precios.csv", "text/csv")

else:
    st.info("Agrega productos para generar la escalera.")
