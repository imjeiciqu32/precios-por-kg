import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# ----------------------------
# 1. Configuración y Persistencia
# ----------------------------
st.set_page_config(page_title="Analytics de Precios Pro", layout="wide")

DB_FILE = "historico_productos.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # Limpieza básica para evitar errores de tipo
            df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
            df["Precio por Kg ($)"] = pd.to_numeric(df["Precio por Kg ($)"], errors='coerce').fillna(0)
            return df
        except:
            return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)"])
    return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if "data" not in st.session_state:
    st.session_state.data = load_data()

# ----------------------------
# 2. Interfaz de Usuario
# ----------------------------
st.title("📊 Monitor de Precios")

with st.expander("➕ Añadir Nuevo SKU", expanded=True):
    with st.form("form_producto", clear_on_submit=True):
        c1, c2, c3, c4, c5 = st.columns(5)
        prod_input = c1.text_input("Nombre del Producto")
        fab_input = c2.selectbox("Fabricante", ["SABRITAS", "BARCEL", "OTROS"])
        oca_input = c3.selectbox("Ocasión", ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"])
        pre_input = c4.number_input("Precio ($)", min_value=0.0, step=0.5)
        gra_input = c5.number_input("Gramaje (g)", min_value=1.0, step=1.0)
        
        if st.form_submit_button("Guardar en Histórico"):
            if prod_input:
                pkg = round(pre_input / (gra_input / 1000), 2)
                nuevo = pd.DataFrame([{
                    "Producto": prod_input.upper().strip(),
                    "Fabricante": fab_input,
                    "Ocasión": oca_input,
                    "Precio ($)": pre_input,
                    "Gramaje (g)": gra_input,
                    "Precio por Kg ($)": pkg
                }])
                st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
                save_data(st.session_state.data)
                st.rerun()

# ----------------------------
# 3. Tabla y Exportación
# ----------------------------
st.subheader("🧾 Inventario")
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)

if not edited_df.equals(st.session_state.data):
    st.session_state.data = edited_df
    save_data(edited_df)

# Exportación
csv = st.session_state.data.to_csv(index=False).encode('utf-8')
st.download_button("📥 Descargar Excel (CSV)", data=csv, file_name="precios.csv", mime="text/csv")

# ----------------------------
# 4. Gráfico de Escalera (Lógica Robusta)
# ----------------------------
if not st.session_state.data.empty:
    df_plot = st.session_state.data.copy()
    
    # Orden jerárquico solicitado
    mapa_orden = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df_plot["Orden_Oca"] = df_plot["Ocasión"].map(mapa_orden)
    
    # ORDEN: Ocasión -> Precio -> Precio/Kg
    df_plot = df_plot.sort_values(by=["Orden_Oca", "Precio ($)", "Precio por Kg ($)"])

    fig = go.Figure()
    colores = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}

    # Agrupar por fabricante para la leyenda
    for f in df_plot["Fabricante"].unique():
        d = df_plot[df_plot["Fabricante"] == f]
        fig.add_trace(go.Bar(
            name=f,
            x=[d["Ocasión"], d["Producto"]],
            y=d["Precio ($)"],
            marker_color=colores.get(f, "#B0B0B0"),
            text=d["Precio ($)"].apply(lambda x: f"${x}"),
            textposition='outside',
            customdata=d["Precio por Kg ($)"],
            hovertemplate="SKU: %{x}<br>Precio: $%{y}<br>Precio/Kg: $%{customdata}<extra></extra>"
        ))

    fig.update_layout(
        title="Escalera de Precios (Desembolso por Ocasión)",
        xaxis=dict(title="Ocasión / Producto"),
        yaxis=dict(title="Precio ($)"),
        barmode='group',
        height=600,
        template="plotly_white"
    )
    
    # Etiquetas de Precio/Kg dentro de las barras
    for i, row in df_plot.iterrows():
        fig.add_annotation(
            x=[row["Ocasión"], row["Producto"]],
            y=row["Precio ($)"] * 0.5,
            text=f"${int(row['Precio por Kg ($)'])}/kg",
            showarrow=False,
            font=dict(color="white" if row["Fabricante"] == "BARCEL" else "black", size=9)
        )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aún no hay datos para graficar.")
