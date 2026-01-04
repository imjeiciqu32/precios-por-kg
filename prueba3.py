import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. IMPORTACIÓN DE PLANTILLAS ---
# Asegúrate de tener plantillas.py y price_pack.py en la misma carpeta
from plantillas import PLANTILLAS
try:
    from price_pack import PLANTILLAS_PP
except ImportError:
    PLANTILLAS_PP = {}

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Price Architecture Expert", layout="wide")

# --- 3. NAVEGACIÓN (SELECTOR DE MODO) ---
st.sidebar.header("🚀 Navegación")
modo = st.sidebar.radio("Seleccionar Herramienta:", ["Price Ladder", "Price Pack"])

# --- 4. CONFIGURACIÓN DINÁMICA ---
if modo == "Price Ladder":
    DB_FILE = "historico_ladder.csv"
    fuente_plantillas = PLANTILLAS
    label_agrupador = "Ocasión"
    opciones_agrupador = ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR", "REUNIÓN", "FIESTA", "TRANSFORMADOR"]
    titulo_app = "📊 ESCALERAS DE PRECIO (MARKET)"
else:
    DB_FILE = "historico_price_pack.csv"
    fuente_plantillas = PLANTILLAS_PP
    label_agrupador = "Canal"
    # Orden específico solicitado para Price Pack
    opciones_agrupador = ["INSTITUCIONALES", "MAYOREO", "CLUBES", "HARD DISCOUNT", "DETALLE", "AUTOSERVICIO", "CONVENIENCIA"]
    titulo_app = "📦 PRICE PACK ARCHITECTURE (INTERNAL BARCEL)"

# --- 5. FUNCIONES CORE ---
def calcular_pkg(df):
    if df.empty: return df
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1).replace(0, 1)
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(1)
    if "SOM (%)" not in df.columns: df["SOM (%)"] = 0.0
    return df

def procesar_datos_piramide(df, agrupador):
    if df.empty: return df
    temp = df.copy()
    def get_base(g):
        if g["SOM (%)"].max() > 0:
            return g.loc[g["SOM (%)"].idxmax(), "Precio por Kg ($)"]
        return g["Precio por Kg ($)"].mean() if not g.empty else 1
    
    bases = temp.groupby(agrupador).apply(lambda x: get_base(x)).reset_index()
    bases.columns = [agrupador, "P_Ref"]
    temp = temp.merge(bases, on=agrupador, how="left")
    temp["Idx_P"] = (temp["Precio por Kg ($)"] / temp["P_Ref"] * 100).round(0)
    
    def asignar_tier(i):
        if i >= 170: return "PREMIUM"
        elif 120 <= i < 170: return "UPPER MAINSTREAM"
        elif 95 <= i < 120: return "MAINSTREAM"
        elif 80 <= i < 95: return "MAINSTREAM LOW"
        else: return "VALUE"
    temp["Tier"] = temp["Idx_P"].apply(asignar_tier)
    return temp

# --- 6. GESTIÓN DE DATOS ---
if "data" not in st.session_state or st.session_state.get('last_modo') != modo:
    if os.path.exists(DB_FILE):
        st.session_state.data = calcular_pkg(pd.read_csv(DB_FILE))
    else:
        st.session_state.data = pd.DataFrame(columns=["Producto", "Familia", label_agrupador, "Precio ($)", "Gramaje (g)", "Fabricante", "SOM (%)"])
    st.session_state.last_modo = modo

# --- 7. SIDEBAR GESTIÓN ---
st.sidebar.divider()
st.sidebar.subheader(f"📁 Plantillas {modo}")
nombre_plantilla = st.sidebar.selectbox("Cargar:", ["-- Seleccionar --"] + list(fuente_plantillas.keys()))

if st.sidebar.button("Cargar datos"):
    if nombre_plantilla != "-- Seleccionar --":
        st.session_state.data = calcular_pkg(pd.DataFrame(fuente_plantillas[nombre_plantilla]))
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Reset Todo"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.data = pd.DataFrame()
    st.rerun()

st.title(titulo_app)

# --- 8. FORMULARIO DE ENTRADA ---
with st.expander(f"➕ Añadir nuevo SKU", expanded=False):
    with st.form("form_nuevo"):
        c1, c2, c3 = st.columns(3)
        f_nom = c1.text_input("Producto").upper()
        f_fam = c2.text_input("Familia (Marca)").upper()
        f_agru = c3.selectbox(label_agrupador, opciones_agrupador)
        
        c4, c5 = st.columns(2)
        f_pre = c4.number_input("Precio ($)", min_value=0.0, step=0.5)
        f_gra = c5.number_input("Gramos (g)", min_value=1.0, step=1.0)
        
        f_fab = "BARCEL"
        f_som = 0.0
        if modo == "Price Ladder":
            f_fab = st.selectbox("Fabricante", ["BARCEL", "SABRITAS", "OTROS"])
            f_som = st.number_input("SOM (%)", min_value=0.0, max_value=100.0)
            
        if st.form_submit_button("Guardar"):
            nueva_fila = pd.DataFrame([{"Producto": f_nom, "Familia": f_fam, label_agrupador: f_agru, "Precio ($)": f_pre, "Gramaje (g)": f_gra, "Fabricante": f_fab, "SOM (%)": f_som}])
            st.session_state.data = pd.concat([st.session_state.data, nueva_fila], ignore_index=True)
            st.session_state.data = calcular_pkg(st.session_state.data)
            st.session_state.data.to_csv(DB_FILE, index=False)
            st.rerun()

# --- 9. TABLA ---
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = calcular_pkg(edited_df)
    st.session_state.data.to_csv(DB_FILE, index=False)
    st.rerun()

# --- 10. GRÁFICOS ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    ord_map = {cat: i for i, cat in enumerate(opciones_agrupador)}
    df_p["Orden"] = df_p[label_agrupador].str.upper().map(ord_map).fillna(99)
    df_p = df_p.sort_values(by=["Orden", "Precio ($)"]).reset_index(drop=True)

    if modo == "Price Pack":
        # GRÁFICO PRICE PACK (Basado en la imagen cargada)
        fig = go.Figure()
        
        # Barras principales (Precio por Kg)
        fig.add_trace(go.Bar(
            x=df_p["Producto"], y=df_p["Precio por Kg ($)"],
            marker_color="#0B3C8C",
            text=[f"<b>${p:,.1f}</b>" for p in df_p["Precio por Kg ($)"]],
            textposition="outside",
            textfont=dict(size=14, color="black")
        ))

        # Etiquetas de Precio Desembolso en la base
        for i, row in df_p.iterrows():
            fig.add_annotation(
                x=i, y=max(df_p["Precio por Kg ($)"]) * 0.03,
                text=f"<b>${row['Precio ($)']:.1f}</b>",
                showarrow=False, font=dict(size=12, color="white"),
                bgcolor="rgba(40,40,40,0.8)", borderpad=3
            )

        # Líneas y Nombres de Canales
        for cat in df_p[label_agrupador].unique():
            idx_list = df_p.index[df_p[label_agrupador] == cat].tolist()
            center = (idx_list[0] + idx_list[-1]) / 2
            fig.add_shape(type="line", x0=idx_list[-1]+0.5, x1=idx_list[-1]+0.5, y0=0, y1=1, xref="x", yref="paper", line=dict(color="#DDD", width=2))
            fig.add_annotation(x=center, y=-0.25, xref="x", yref="paper", text=f"<b>{cat}</b>", showarrow=False, font=dict(size=14))

        fig.update_layout(
            title="Arquitectura de Precio por Kg por Canal",
            height=700, margin=dict(b=200, t=80), template="plotly_white",
            xaxis=dict(tickangle=90, tickfont=dict(size=11)) # Nombres a 90 grados
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        # GRÁFICO PRICE LADDER (Market Share + Precio Desembolso)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.0, row_heights=[0.15, 0.85])
        
        # Burbujas SOM
        fig.add_trace(go.Scatter(
            x=df_p["Producto"], y=df_p["SOM (%)"], mode="lines+markers+text",
            line=dict(color="#BBBBBB"), marker=dict(size=30, color="#E5E5E5", symbol="square"),
            text=[f"<b>{s}%</b>" for s in df_p["SOM (%)"]], textposition="middle center"
        ), row=1, col=1)

        # Barras de Precio Desembolso
        colores = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
        fig.add_trace(go.Bar(
            x=df_p["Producto"], y=df_p["Precio ($)"],
            marker_color=[colores.get(str(f).upper(), "#999") for f in df_p["Fabricante"]],
            text=[f"<b>${p}</b>" for p in df_p["Precio ($)"]], textposition="outside"
        ), row=2, col=1)

        # Divisores de Ocasión
        for cat in df_p[label_agrupador].unique():
            idx_list = df_p.index[df_p[label_agrupador] == cat].tolist()
            center = (idx_list[0] + idx_list[-1]) / 2
            fig.add_shape(type="line", x0=idx_list[-1]+0.5, x1=idx_list[-1]+0.5, y0=0, y1=1, xref="x", yref="paper", line=dict(color="#DDD"), row=2, col=1)
            fig.add_annotation(x=center, y=-0.25, xref="x", yref="paper", text=f"<b>{cat}</b>", showarrow=False, row=2, col=1)

        fig.update_layout(height=800, margin=dict(b=200), template="plotly_white", showlegend=False)
        fig.update_xaxes(tickangle=90) # Nombres a 90 grados
        st.plotly_chart(fig, use_container_width=True)

        # Pirámide (Solo en Ladder)
        st.divider()
        df_py = procesar_datos_piramide(df_p, label_agrupador)
        sel_cat = st.selectbox(f"Pirámide por {label_agrupador}:", df_py[label_agrupador].unique())
        # ... (Aquí sigue la lógica de visualización de pirámides que ya teníamos)
