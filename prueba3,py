import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ----------------------------
# 1. Configuración y Persistencia
# ----------------------------
st.set_page_config(page_title="Analytics de Precios Pro", layout="wide")

DB_FILE = "historico_productos.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if "data" not in st.session_state:
    st.session_state.data = load_data()

# ----------------------------
# 2. Interfaz de Usuario
# ----------------------------
st.title("📊 Monitor Estratégico de Precios")

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
                    "Producto": producto.upper(),
                    "Fabricante": fabricante,
                    "Ocasión": ocasion,
                    "Precio ($)": precio,
                    "Gramaje (g)": gramaje,
                    "Precio por Kg ($)": precio_kg
                }])
                st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
                save_data(st.session_state.data)
                st.success(f"✅ {producto} guardado.")
            else:
                st.error("Escribe un nombre de producto.")

# ----------------------------
# 3. Gestión de Datos y Exportación
# ----------------------------
st.subheader("🧾 Inventario de Precios")

# Editor de datos con guardado automático al editar
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = edited_df
    save_data(edited_df)
    st.rerun()

# Botones de exportación
col_exp1, col_exp2, _ = st.columns([1, 1, 4])
with col_exp1:
    csv = st.session_state.data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar CSV", data=csv, file_name="precios_snacks.csv", mime="text/csv")
with col_exp2:
    # Nota: Para Excel real se requiere openpyxl, usamos este truco rápido:
    st.caption("Tip: El CSV abre directo en Excel.")

# ----------------------------
# 4. Lógica de Ordenamiento y Visualización
# ----------------------------
if not st.session_state.data.empty:
    df = st.session_state.data.copy()
    
    # Definimos el orden categórico
    orden_ocasion = ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"]
    df["Ocasión"] = pd.Categorical(df["Ocasión"], categories=orden_ocasion, ordered=True)
    
    # ORDEN SOLICITADO: Ocasión -> Precio Desembolso -> Precio Kg
    df = df.sort_values(by=["Ocasión", "Precio ($)", "Precio por Kg ($)"])

    # Mapeo de Colores
    color_map = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}

    # Creación del gráfico con Eje X Multicapa (Excel Style)
    fig = px.bar(
        df,
        x=["Ocasión", "Producto"], # <--- Esto crea la jerarquía visual abajo
        y="Precio ($)",
        color="Fabricante",
        color_discrete_map=color_map,
        title="Escalera de Precios por Ocasión de Consumo",
        text_auto='.2f'
    )

    # Configuración estética
    fig.update_layout(
        height=650,
        xaxis_title=None,
        yaxis_title="Precio de Desembolso ($)",
        legend_title="Fabricante",
        uniformtext_minsize=8, 
        uniformtext_mode='hide',
        # Configuración para que el gráfico sea exportable como imagen limpia
        paper_bgcolor="white",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    # Añadir el Precio por Kg como etiqueta flotante dentro de las barras
    for i, row in df.iterrows():
        fig.add_annotation(
            x=[row["Ocasión"], row["Producto"]],
            y=row["Precio ($)"] / 2, # Posición a mitad de la barra
            text=f"${int(row['Precio por Kg ($)'])}/kg",
            showarrow=False,
            font=dict(color="white" if row["Fabricante"] == "BARCEL" else "black", size=9)
        )

    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 **Tip de exportación:** Pasa el mouse sobre el gráfico y haz clic en la 📷 (cámara) para descargar como PNG de alta calidad.")

else:
    st.info("El histórico está vacío. Agrega productos arriba para comenzar.")
