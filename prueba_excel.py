import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Price Ladder & SOM Analysis", layout="wide")
DB_FILE = "historico_productos.csv"

# --- 2. FUNCIONES DE DATOS ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # Asegurar existencia de columnas clave
            columnas_necesarias = ["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "SOM (%)"]
            for col in columnas_necesarias:
                if col not in df.columns:
                    df[col] = 0 if col in ["Precio ($)", "Gramaje (g)", "SOM (%)"] else "S/D"
            
            # Limpieza y cálculos
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

# --- 3. ENTRADA DE DATOS (FORMULARIO) ---
with st.expander("➕ Agregar Producto Nuevo", expanded=False):
    with st.form("nuevo_producto", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        p = c1.text_input("Producto (Nombre y Gramaje)")
        f = c2.selectbox("Fabricante", ["SABRITAS", "BARCEL", "OTROS"])
        o = c3.selectbox("Ocasión", ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"])
        
        c4, c5, c6 = st.columns(3)
        pr = c4.number_input("Precio Desembolso ($)", min_value=0.0, step=0.5)
        gr = c5.number_input("Gramaje Real (g)", min_value=1.0, step=1.0)
        sm = c6.number_input("Share of Market (%)", min_value=0.0, max_value=100.0, step=0.1)
        
        if st.form_submit_button("Guardar en Base de Datos"):
            pkg = round(pr / (gr / 1000), 0)
            nuevo = pd.DataFrame([{"Producto": p.upper(), "Fabricante": f, "Ocasión": o, 
                                   "Precio ($)": pr, "Gramaje (g)": gr, 
                                   "Precio por Kg ($)": pkg, "SOM (%)": sm}])
            st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
            st.session_state.data.to_csv(DB_FILE, index=False)
            st.success("Producto guardado.")
            st.rerun()

# Tabla editable para corregir datos rápido
st.subheader("📝 Editor de Datos")
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = edited_df
    edited_df.to_csv(DB_FILE, index=False)
    st.rerun()

# --- 4. GRÁFICO DOBLE OPTIMIZADO ---
if not st.session_state.data.empty:
    df_plot = st.session_state.data.copy()
    
    # Lógica de Ordenamiento
    mapa_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df_plot["Orden_Oca"] = df_plot["Ocasión"].str.upper().map(mapa_oca).fillna(99)
    df_plot = df_plot.sort_values(by=["Orden_Oca", "Precio ($)"])

    colores_map = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    
    # Crear Subplots: SOM arriba (chaparro) y Barras abajo (grande)
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.02, # Gráficos casi pegados
        row_heights=[0.25, 0.75]
    )

    # A. GRÁFICO SUPERIOR (SOM)
    fig.add_trace(
        go.Scatter(
            x=[df_plot["Ocasión"], df_plot["Producto"]],
            y=df_plot["SOM (%)"],
            mode="lines+markers", # Mantenemos markers para que la línea se conecte bien
            line=dict(color="#D3D3D3", width=1.5),
            marker=dict(size=1, color="#D3D3D3"), # Hacemos el punto casi invisible
            hoverinfo="skip"
        ),
        row=1, col=1
    )

    # Etiquetas SOM: CENTRADAS en el punto para taparlo
    for i in range(len(df_plot)):
        row = df_plot.iloc[i]
        fig.add_annotation(
            x=i, 
            y=row["SOM (%)"],
            text=f"<b>{row['SOM (%)']}%</b>",
            showarrow=False,
            # --- AJUSTES DE POSICIÓN ---
            yshift=0,          # Centrado exacto en la coordenada Y
            xshift=0,          # Centrado exacto en la coordenada X
            # ---------------------------
            font=dict(size=12, color="black"),
            bgcolor="#F0F0F0", # Fondo gris del cuadrito
            bordercolor="#BDBDBD",
            borderwidth=1,
            borderpad=4,       # Un poco más de aire dentro del cuadro
            row=1, col=1
        )

    # B. GRÁFICO INFERIOR (ESCALERA)
    fig.add_trace(
        go.Bar(
            x=[df_plot["Ocasión"], df_plot["Producto"]],
            y=df_plot["Precio ($)"],
            marker_color=[colores_map.get(str(fab).upper(), "#B0B0B0") for fab in df_plot["Fabricante"]],
            text=[f"<b>${p}</b>" for p in df_plot["Precio ($)"]],
            textposition='outside',
            textfont=dict(size=20, color="black"), # Precio Desembolso GRANDE
        ),
        row=2, col=1
    )

    # Etiquetas $/Kg dentro de las barras
    for i in range(len(df_plot)):
        row = df_plot.iloc[i]
        fig.add_annotation(
            x=i,
            y=row["Precio ($)"] * 0.15, # Posición baja dentro de la barra
            text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
            showarrow=False,
            font=dict(size=16, color="white" if str(row["Fabricante"]).upper() == "BARCEL" else "black"),
            bgcolor="rgba(0,0,0,0.3)" if str(row["Fabricante"]).upper() == "BARCEL" else "rgba(255,255,255,0.4)",
            row=2, col=1
        )

    # --- 5. AJUSTES FINALES DE LAYOUT ---
    fig.update_layout(
        template="plotly_white",
        height=850,
        margin=dict(t=50, b=150, l=60, r=40),
        showlegend=False
    )

    # Limpiar Eje SOM (Superior)
    fig.update_yaxes(
        showgrid=False, 
        showticklabels=False, 
        zeroline=False, 
        row=1, col=1,
        range=[0, df_plot["SOM (%)"].max() * 2.2] # Aire arriba para que no choque
    )

    # Eje Escalera (Inferior)
    fig.update_yaxes(
        title_text="<b>Precio ($)</b>", 
        row=2, col=1, 
        showgrid=True, 
        gridcolor="#f0f0f0",
        range=[0, df_plot["Precio ($)"].max() * 1.3]
    )

    # Eje X (Categorías y Ocasiones)
    fig.update_xaxes(
        tickfont=dict(size=12, family="Arial Black", color="black"),
        automargin=True,
        row=2, col=1
    )

    st.plotly_chart(fig, use_container_width=True)

    # Botón de Reset
    if st.sidebar.button("🗑️ Borrar Todo el Histórico"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()

else:
    st.info("No hay datos disponibles. Agrega productos en el formulario de arriba.")
