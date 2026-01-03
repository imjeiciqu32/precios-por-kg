import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Price Ladder Expert Pro", layout="wide")
DB_FILE = "historico_productos.csv"

# --- 2. REPOSITORIO DE PLANTILLAS ---
PLANTILLAS = {
   "DT - MAÍZ": [
        {"Producto": "MINI TAKIS 35G", "Fabricante": "BARCEL", "Ocasión": "BITES", "Precio ($)": 10.0, "Gramaje (g)": 35, "SOM (%)": 0.7},
        {"Producto": "DORITOS 41G", "Fabricante": "SABRITAS", "Ocasión": "BITES", "Precio ($)": 15.0, "Gramaje (g)": 41, "SOM (%)": 0.7},
        {"Producto": "CHURRUMAIS 70G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 17.0, "Gramaje (g)": 70, "SOM (%)": 1.9},
        {"Producto": "TOSTACHOS 75G", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 18.0, "Gramaje (g)": 75, "SOM (%)": 0.7},
        {"Producto": "RUNNERS 72G", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 18.0, "Gramaje (g)": 72, "SOM (%)": 4.7},
        {"Producto": "FRITOS 70G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 18.0, "Gramaje (g)": 70, "SOM (%)": 8.1},
        {"Producto": "CHIPOTLES 65G", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 18.0, "Gramaje (g)": 65, "SOM (%)": 1.4},
        {"Producto": "RANCHERITOS 58G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 18.0, "Gramaje (g)": 58, "SOM (%)": 3.9},
        {"Producto": "TAKIS 70G", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 70, "SOM (%)": 13.8},
        {"Producto": "DORITOS DINAMITA 70G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 70, "SOM (%)": 9.0},
        {"Producto": "TOSTITOS 62G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 62, "SOM (%)": 6.7},
        {"Producto": "DORITOS 58G", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 58, "SOM (%)": 22.4},
        {"Producto": "DORITOS DINAMITA 120G", "Fabricante": "SABRITAS", "Ocasión": "HAMBRE", "Precio ($)": 25.0, "Gramaje (g)": 120, "SOM (%)": 0.6},
        {"Producto": "TOSTITOS 110G", "Fabricante": "SABRITAS", "Ocasión": "HAMBRE", "Precio ($)": 25.0, "Gramaje (g)": 110, "SOM (%)": 0.0},
        {"Producto": "DORITOS 100G", "Fabricante": "SABRITAS", "Ocasión": "HAMBRE", "Precio ($)": 25.0, "Gramaje (g)": 100, "SOM (%)": 3.6},
        {"Producto": "DORITOS NACHO 146G", "Fabricante": "SABRITAS", "Ocasión": "COMPARTIR", "Precio ($)": 40.0, "Gramaje (g)": 146, "SOM (%)": 0.9},
        {"Producto": "RANCHERITOS 145G", "Fabricante": "SABRITAS", "Ocasión": "COMPARTIR", "Precio ($)": 40.0, "Gramaje (g)": 145, "SOM (%)": 0.2},
        {"Producto": "RUNNERS 200G", "Fabricante": "BARCEL", "Ocasión": "FAMILIAR", "Precio ($)": 40.0, "Gramaje (g)": 200, "SOM (%)": 0.0},
        {"Producto": "CHURRUMAIS 185G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 40.0, "Gramaje (g)": 185, "SOM (%)": 0.1},
        {"Producto": "TOSTITOS 175G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 40.0, "Gramaje (g)": 175, "SOM (%)": 0.7},
        {"Producto": "FRITOS 170G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 40.0, "Gramaje (g)": 170, "SOM (%)": 0.1},
        {"Producto": "TAKIS 200G", "Fabricante": "BARCEL", "Ocasión": "FAMILIAR", "Precio ($)": 45.0, "Gramaje (g)": 200, "SOM (%)": 0.2},
        {"Producto": "DORITOS 245G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 56.0, "Gramaje (g)": 245, "SOM (%)": 0.3}
   ],
   "Escalera Super - Familiar": [
        {"Producto": "TAKIS 200G", "Fabricante": "BARCEL", "Ocasión": "FAMILIAR", "Precio ($)": 45.0, "Gramaje (g)": 200, "SOM (%)": 1.2},
        {"Producto": "DORITOS 245G", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 56.0, "Gramaje (g)": 245, "SOM (%)": 3.2}
   ]
}

def calcular_pkg(df):
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1).replace(0, 1)
    df["SOM (%)"] = pd.to_numeric(df["SOM (%)"], errors='coerce').fillna(0)
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(0)
    return df

if "data" not in st.session_state:
    if os.path.exists(DB_FILE):
        st.session_state.data = calcular_pkg(pd.read_csv(DB_FILE))
    else:
        st.session_state.data = pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])

# --- 3. BARRA LATERAL ---
st.sidebar.header("📁 Gestión")
nombre_plantilla = st.sidebar.selectbox("Cargar Plantilla:", ["-- Seleccionar --"] + list(PLANTILLAS.keys()))

if st.sidebar.button("Cargar Escalera"):
    if nombre_plantilla != "-- Seleccionar --":
        nuevos_datos = pd.DataFrame(PLANTILLAS[nombre_plantilla])
        st.session_state.data = calcular_pkg(nuevos_datos)
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Reset"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.data = pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])
    st.rerun()

st.title("📊 ESCALERAS DE PRECIO DINÁMICAS")

# --- 4. FORMULARIO AGREGAR SKU ---
with st.expander("➕ Agregar nuevo producto manualmente", expanded=False):
    with st.form("nuevo_sku_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        f_nom = c1.text_input("Nombre del Producto").upper()
        f_fab = c2.selectbox("Fabricante", ["BARCEL", "SABRITAS", "OTROS"])
        f_oca = c3.selectbox("Ocasión", ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"])
        
        c4, c5, c6 = st.columns(3)
        f_pre = c4.number_input("Precio ($)", min_value=0.0, step=0.5)
        f_gra = c5.number_input("Gramaje (g)", min_value=1.0, step=1.0)
        f_som = c6.number_input("SOM (%)", min_value=0.0, max_value=100.0, step=0.1)
        
        if st.form_submit_button("Añadir a la lista"):
            nuevo_sku = pd.DataFrame([{"Producto": f_nom, "Fabricante": f_fab, "Ocasión": f_oca, 
                                       "Precio ($)": f_pre, "Gramaje (g)": f_gra, "SOM (%)": f_som}])
            st.session_state.data = pd.concat([st.session_state.data, nuevo_sku], ignore_index=True)
            st.session_state.data = calcular_pkg(st.session_state.data)
            st.session_state.data.to_csv(DB_FILE, index=False)
            st.rerun()

# --- 5. EDITOR ---
st.subheader("📝 Tabla de Datos")
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = calcular_pkg(edited_df)
    st.session_state.data.to_csv(DB_FILE, index=False)
    st.rerun()

# --- 6. GRÁFICO ACTUALIZADO ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    ord_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df_p["O_Oca"] = df_p["Ocasión"].str.upper().map(ord_oca).fillna(99)
    df_p = df_p.sort_values(by=["O_Oca", "Precio ($)"])

    # --- Cálculo de SOM por Ocasión ---
    som_por_ocasion = df_p.groupby("Ocasión")["SOM (%)"].sum().to_dict()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.3, 0.7])

    # Línea SOM (Sin negritas)
    fig.add_trace(go.Scatter(
        x=[df_p["Ocasión"], df_p["Producto"]], 
        y=df_p["SOM (%)"], 
        mode="lines+markers",
        line=dict(color="#D3D3D3", width=2),
        marker=dict(size=4, color="#424242")
    ), row=1, col=1)

    for i in range(len(df_p)):
        row = df_p.iloc[i]
        fig.add_annotation(
            x=i, y=row["SOM (%)"],
            text=f"{row['SOM (%)']}%", 
            showarrow=False,
            yshift=15,
            font=dict(size=18, color="black"),
            bgcolor="rgba(224, 224, 224, 0.8)",
            bordercolor="#BDBDBD", borderwidth=1,
            row=1, col=1
        )

    # Barras de Precio
    colors = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    fig.add_trace(go.Bar(
        x=[df_p["Ocasión"], df_p["Producto"]], 
        y=df_p["Precio ($)"],
        marker_color=[colors.get(str(f).upper(), "#B0B0B0") for f in df_p["Fabricante"]],
        text=[f"<b>${p}</b>" for p in df_p["Precio ($)"]], 
        textposition='outside',
        textfont=dict(size=18, color="black")
    ), row=2, col=1)

    # Etiquetas $/Kg
    for i in range(len(df_p)):
        row = df_p.iloc[i]
        fig.add_annotation(
            x=i, y=2.5,
            text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
            showarrow=False,
            font=dict(size=16, color="white" if row['Fabricante']=="BARCEL" else "black"),
            bgcolor="rgba(0,0,0,0.6)" if row['Fabricante']=="BARCEL" else "rgba(255,255,255,0.7)",
            row=2, col=1
        )

    # --- Anotaciones de peso total por Ocasión ---
    # Posicionamos el total debajo de los nombres de las categorías
    categorias_unicas = df_p["Ocasión"].unique()
    for cat in categorias_unicas:
        # Buscamos la posición central de los productos en esa categoría
        indices = df_p.index[df_p["Ocasión"] == cat].tolist()
        df_indices = [df_p.index.get_loc(idx) for idx in indices]
        pos_x_central = sum(df_indices) / len(df_indices)
        
        fig.add_annotation(
            x=pos_x_central, y=-0.22, # Ajustado para que no choque con los nombres
            xref="x2", yref="paper",
            text=f"<b>Total SOM: {som_por_ocasion[cat]:.1f}%</b>", # Corregido de .1st a .1f
            showarrow=False,
            font=dict(size=14, color="#424242", family="Arial"),
            row=2, col=1
        )

    # Ajustes finales de layout
    fig.update_layout(
        height=850, # Un poco más alto para que quepa todo el texto inferior
        template="plotly_white", 
        showlegend=False, 
        margin=dict(t=50, b=180, l=50, r=50) # Margen inferior amplio para las etiquetas
    )
    
    fig.update_yaxes(showgrid=False, showticklabels=False, row=1, col=1, range=[0, df_p["SOM (%)"].max() * 2.5])
    
    # Eje X sin negritas
    fig.update_xaxes(
        tickfont=dict(size=12, color="black", family="Arial"), 
        row=2, col=1
    )
    
    st.plotly_chart(fig, use_container_width=True)
