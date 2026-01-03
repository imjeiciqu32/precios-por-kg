import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- Configuración de Página ---
st.set_page_config(page_title="Price Ladder Pro", layout="wide")
DB_FILE = "historico_productos.csv"

# --- Funciones de Datos ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # Asegurar que las columnas numéricas sean correctas
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

# --- Sección de Carga (Excel) ---
with st.expander("📂 Cargar desde Excel o CSV", expanded=False):
    file = st.file_uploader("Sube tu archivo .xlsx o .csv", type=["xlsx", "csv"])
    if file:
        try:
            if file.name.endswith('.xlsx'):
                df_new = pd.read_excel(file, engine='openpyxl')
            else:
                df_new = pd.read_csv(file)
            
            # 1. Limpiar nombres de columnas (quitar espacios invisibles)
            df_new.columns = [c.strip() for c in df_new.columns]
            
            # 2. Procesar datos nuevos
            if "Precio ($)" in df_new.columns and "Gramaje (g)" in df_new.columns:
                df_new["Precio ($)"] = pd.to_numeric(df_new["Precio ($)"], errors='coerce').fillna(0)
                df_new["Gramaje (g)"] = pd.to_numeric(df_new["Gramaje (g)"], errors='coerce').fillna(1)
                df_new["Precio por Kg ($)"] = (df_new["Precio ($)"] / (df_new["Gramaje (g)"] / 1000)).round(0)
            
            # 3. Actualizar sesión y archivo
            st.session_state.data = pd.concat([st.session_state.data, df_new], ignore_index=True).drop_duplicates()
            st.session_state.data.to_csv(DB_FILE, index=False)
            
            st.success("✅ Datos integrados. El gráfico se actualizará ahora.")
            st.rerun() # Esto obliga a la app a ver los nuevos datos inmediatamente
            
        except Exception as e:
            st.error(f"Error al procesar el Excel: {e}")

# --- Gráfico de Escalera ---
if not st.session_state.data.empty:
    df_plot = st.session_state.data.copy()
    
    # Orden lógico de Ocasiones
    mapa_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df_plot["Orden_Oca"] = df_plot["Ocasión"].str.upper().str.strip().map(mapa_oca).fillna(99)
    
    # Ordenar: Ocasión -> Precio -> $/Kg
    df_plot = df_plot.sort_values(by=["Orden_Oca", "Precio ($)", "Precio por Kg ($)"])

    colores_map = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    
    fig = go.Figure()

    # Barra principal
    fig.add_trace(go.Bar(
        x=[df_plot["Ocasión"], df_plot["Producto"]],
        y=df_plot["Precio ($)"],
        marker_color=[colores_map.get(str(f).upper().strip(), "#B0B0B0") for f in df_plot["Fabricante"]],
        text=[f"<b>${p}</b>" for p in df_plot["Precio ($)"]],
        textposition='outside',
        textfont=dict(size=14, color="black"),
    ))

    # Anotaciones de $/Kg (GRANDES Y NEGRITAS)
    for i, row in df_plot.iterrows():
        fig.add_annotation(
            x=[row["Ocasión"], row["Producto"]],
            y=row["Precio ($)"] * 0.2, # Ubicado en la parte baja de la barra
            text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
            showarrow=False,
            font=dict(
                size=16, # Tamaño grande solicitado
                color="white" if str(row["Fabricante"]).upper().strip() == "BARCEL" else "black"
            ),
            bgcolor="rgba(0,0,0,0.3)" if str(row["Fabricante"]).upper().strip() == "BARCEL" else "rgba(255,255,255,0.4)"
        )

    # Ajustes de Layout para visibilidad total
    fig.update_layout(
        template="plotly_white",
        height=800, # Aumentamos altura para que no se amontone
        margin=dict(t=80, b=180, l=50, r=50),
        xaxis=dict(
            title=None,
            tickfont=dict(size=12, color="black", family="Arial Black"),
            showgrid=True,
            gridcolor="#E5E5E5",
            automargin=True # Clave para que aparezcan las ocasiones abajo
        ),
        yaxis=dict(
            title="Precio Desembolso ($)", 
            showgrid=True, 
            gridcolor="#F0F0F0",
            range=[0, df_plot["Precio ($)"].max() * 1.3] # Espacio para las etiquetas de arriba
        ),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # Botón para borrar histórico si es necesario
    if st.button("🚨 Borrar todo el histórico"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state.data = pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)"])
        st.rerun()

else:
    st.info("La base de datos está vacía. Sube un Excel para ver la escalera.")
