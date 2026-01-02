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
        df = pd.read_csv(DB_FILE)
        # Aseguramos tipos de datos correctos al cargar
        df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce')
        df["Precio por Kg ($)"] = pd.to_numeric(df["Precio por Kg ($)"], errors='coerce')
        return df
    return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if "data" not in st.session_state:
    st.session_state.data = load_data()

# ----------------------------
# 2. Formulario de Entrada
# ----------------------------
st.title("📊 Monitor de Precios (Versión Robusta)")

with st.expander("➕ Añadir Nuevo SKU", expanded=True):
    with st.form("form_producto", clear_on_submit=True):
        c1, c2, c3, c4, c5 = st.columns(5)
        producto = c1.text_input("Nombre del Producto")
        fabricante = c2.selectbox("Fabricante", ["SABRITAS", "BARCEL", "OTROS"])
        ocasion = c3.selectbox("Ocasión", ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"])
        precio = c4.number_input("Precio ($)", min_value=0.0, step=0.5)
        gramaje = c5.number_input("Gramaje (g)", min_value=1.0, step=1.0)
        
        if st.form_submit_button("Guardar en Histórico"):
            if producto:
                precio_kg = round(precio / (gramaje / 1000), 2)
                nuevo = pd.DataFrame([{
                    "Producto": producto.upper().strip(),
                    "Fabricante": fabricante,
                    "Ocasión": ocasion,
                    "Precio ($)": precio,
                    "Gramaje (g)": gramaje,
                    "Precio por Kg ($)": precio_kg
                }])
                st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
                save_data(st.session_state.data)
                st.success(f"✅ {producto} guardado.")
                st.rerun()

# ----------------------------
# 3. Gestión y Exportación
# ----------------------------
st.subheader("🧾 Inventario de Precios")

edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = edited_df
    save_data(edited_df)

# Exportar a CSV (Compatible con Excel)
csv = st.session_state.data.to_csv(index=False).encode('utf-8')
st.download_button("📥 Exportar Tabla a Excel (CSV)", data=csv, file_name="precios_chips.csv", mime="text/csv")

# ----------------------------
# 4. Gráfico Multi-Nivel (Solución al Error)
# ----------------------------
if not st.session_state.data.empty:
    df_plot = st.session_state.data.copy()
    
    # 1. Definir orden jerárquico
    orden_ocasion = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df_plot["Orden_Oc"] = df_plot["Ocasión"].map(orden_ocasion)
    
    # 2. ORDEN SOLICITADO: Ocasión -> Precio -> Precio/Kg
    df_plot = df_plot.sort_values(by=["Orden_Oc", "Precio ($)", "Precio por Kg ($)"])

    # 3. Crear el gráfico con Graph Objects (más estable que Express para ejes múltiples)
    fig = go.Figure()

    color_map = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}

    for fab in df_plot["Fabricante"].unique():
        df_sub = df_plot[df_plot["Fabricante"] == fab]
        
        fig.add_trace(go.Bar(
            name=fab,
            x=[df_sub["Ocasión"], df_sub["Producto"]], # Eje X multi-nivel
            y=df_sub["Precio ($)"],
            marker_color=color_map.get(fab, "#B0B0B0"),
            text=df_sub["Precio ($)"].apply(lambda x: f"${x:.1f}"),
            textposition='outside',
            customdata=df_sub["Precio por Kg ($)"],
            hovertemplate="<b>%{x}</b><br>Precio: $%{y}<br>Precio/Kg: $%{customdata}<extra></extra>"
        ))

    # 4. Diseño del Eje X para que parezca Excel
    fig.update_layout(
        title="Escalera de Precios por Ocasión (Desembolso)",
        xaxis=dict(title="Ocasión de Consumo / SKU", tickangle=0),
        yaxis=dict(title="Precio Desembolso ($)", gridcolor="LightGrey"),
        barmode='group',
        height=600,
        plot_bgcolor="white",
        legend_title="Fabricante"
    )

    # Añadir etiquetas de Precio por Kg dentro de las barras
    for i in range(len(df_plot)):
        row = df_plot.iloc[i]
        fig.add_annotation(
            x=[row["Ocasión"], row["Producto"]],
            y=row["Precio ($)"] / 2,
            text=f"${int(row['Precio por Kg ($)'])}/kg",
            showarrow=False,
            font=dict(color="white" if row["Fabricante"] == "BARCEL" else "black", size=10)
        )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("📸 Para guardar como imagen: Pasa el mouse sobre el gráfico y dale clic a la cámara.")

else:
    st.info("Agrega productos para generar el análisis.")
    
    st.info("💡 **Tip de exportación:** Pasa el mouse sobre el gráfico y haz clic en la 📷 (cámara) para descargar como PNG de alta calidad.")

else:
    st.info("El histórico está vacío. Agrega productos arriba para comenzar.")
