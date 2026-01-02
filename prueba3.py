import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- Configuración y Persistencia ---
st.set_page_config(page_title="Price Ladder Pro", layout="wide")
DB_FILE = "historico_productos.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # Limpieza profunda: Convertir a numérico y llenar vacíos con 0
            df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
            df["Precio por Kg ($)"] = pd.to_numeric(df["Precio por Kg ($)"], errors='coerce').fillna(0)
            return df
        except:
            return pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)"])
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
            if prod:
                pkg = round(pre / (gra / 1000), 0)
                nuevo = pd.DataFrame([{
                    "Producto": prod.upper().strip(), 
                    "Fabricante": fab, 
                    "Ocasión": oca, 
                    "Precio ($)": pre, 
                    "Gramaje (g)": gra, 
                    "Precio por Kg ($)": pkg
                }])
                st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
                st.session_state.data.to_csv(DB_FILE, index=False)
                st.rerun()

# --- Tabla de Gestión ---
# Al editar la tabla, nos aseguramos de que los cálculos se mantengan
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    # Recalcular Precio por Kg si el usuario cambió Precio o Gramaje en la tabla
    edited_df["Precio ($)"] = pd.to_numeric(edited_df["Precio ($)"], errors='coerce').fillna(0)
    edited_df["Gramaje (g)"] = pd.to_numeric(edited_df["Gramaje (g)"], errors='coerce').fillna(1)
    edited_df["Precio por Kg ($)"] = (edited_df["Precio ($)"] / (edited_df["Gramaje (g)"] / 1000)).round(0)
    
    st.session_state.data = edited_df
    edited_df.to_csv(DB_FILE, index=False)
    st.rerun()

# --- GRÁFICO ---
if not st.session_state.data.empty:
    df = st.session_state.data.copy()
    
    # 1. Orden lógico
    mapa_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df["Orden_Oca"] = df["Ocasión"].map(mapa_oca)
    
    # 2. Ordenar: Ocasión -> Precio -> Precio/kg (Mezclando fabricantes)
    df = df.sort_values(by=["Orden_Oca", "Precio ($)", "Precio por Kg ($)"], ascending=[True, True, True])

    # 3. Colores
    colores_map = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    df["Color"] = df["Fabricante"].map(colores_map).fillna("#B0B0B0")

    fig = go.Figure()

    # Traza principal de barras
    fig.add_trace(go.Bar(
        x=[df["Ocasión"], df["Producto"]],
        y=df["Precio ($)"],
        marker_color=df["Color"],
        text=df["Precio ($)"].apply(lambda x: f"${x}"),
        textposition='outside',
        showlegend=False
    ))

    # Leyenda Manual
    for fab, col in colores_map.items():
        fig.add_trace(go.Bar(name=fab, x=[None], y=[None], marker_color=col))

    # 4. Anotaciones de Precio/Kg con validación para evitar el TypeError
    for i, row in df.iterrows():
        try:
            val_kg = int(row['Precio por Kg ($)'])
        except:
            val_kg = 0
            
        fig.add_annotation(
            x=[row["Ocasión"], row["Producto"]],
            y=0,
            yshift=15,
            text=f"<b>${val_kg}</b>",
            showarrow=False,
            font=dict(color="white" if row["Fabricante"]=="BARCEL" else "black", size=10),
            bgcolor="rgba(255,255,255,0.2)" if row["Fabricante"]=="SABRITAS" else None
        )

    fig.update_layout(
        title="Escalera de Precios: Desembolso y $/Kg",
        xaxis=dict(title=None),
        yaxis=dict(title="Precio Desembolso ($)", showgrid=True, gridcolor="#f0f0f0"),
        plot_bgcolor="white",
        height=600,
        margin=dict(t=80, b=120)
    )

    st.plotly_chart(fig, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📂 Descargar Excel (CSV)", csv, "escalera.csv", "text/csv")
else:
    st.info("Añade productos para ver la escalera de precios.")
