import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. IMPORTACIÓN DE PLANTILLAS EXTERNAS ---
# Intentamos importar, si no existen los archivos, creamos diccionarios vacíos para evitar errores
try:
    from plantillas import PLANTILLAS
except ImportError:
    PLANTILLAS = {}

try:
    from price_pack import PLANTILLAS_PP
except ImportError:
    PLANTILLAS_PP = {}

# --- 2. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Price Architecture Expert Pro", layout="wide")

# --- 3. NAVEGACIÓN (SELECTOR DE MODO) ---
st.sidebar.header("🚀 Navegación")
modo = st.sidebar.radio("Seleccionar Herramienta:", ["Price Ladder", "Price Pack"])

# --- 4. CONFIGURACIÓN DINÁMICA SEGÚN EL MODO ---
if modo == "Price Ladder":
    DB_FILE = "historico_ladder.csv"
    fuente_plantillas = PLANTILLAS
    label_agrupador = "Ocasión"
    opciones_agrupador = ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR", "REUNIÓN", "FIESTA", "TRANSFORMADOR"]
    titulo_app = "📊 ESCALERAS DE PRECIO DINÁMICAS (MARKET)"
    columnas_base = ["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "SOM (%)"]
else:
    DB_FILE = "historico_price_pack.csv"
    fuente_plantillas = PLANTILLAS_PP
    label_agrupador = "Canal"
    # Orden jerárquico solicitado para Price Pack
    opciones_agrupador = ["INSTITUCIONALES", "MAYOREO", "CLUBES", "HARD DISCOUNT", "DETALLE", "AUTOSERVICIO", "CONVENIENCIA"]
    titulo_app = "📦 PRICE PACK ARCHITECTURE (INTERNAL BARCEL)"
    columnas_base = ["Producto", "Familia", "Canal", "Ocasión", "Precio ($)", "Gramaje (g)"]

# --- 5. FUNCIONES CORE DE CÁLCULO ---
def calcular_pkg(df):
    if df.empty: return df
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1).replace(0, 1)
    # Precio por Kg con un decimal (no redondeado a entero)
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(1)
    if "SOM (%)" not in df.columns: df["SOM (%)"] = 0.0
    if "Fabricante" not in df.columns: df["Fabricante"] = "BARCEL"
    return df

def procesar_datos_piramide(df, agrupador):
    if df.empty: return df
    temp = df.copy()
    
    # Obtener precio de referencia del líder (mayor SOM)
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

# --- 6. GESTIÓN DE ESTADO (SESSION STATE) ---
if "data" not in st.session_state or st.session_state.get('last_modo') != modo:
    if os.path.exists(DB_FILE):
        st.session_state.data = calcular_pkg(pd.read_csv(DB_FILE))
    else:
        st.session_state.data = pd.DataFrame(columns=columnas_base)
    st.session_state.last_modo = modo

# --- 7. BARRA LATERAL (GESTIÓN DE ARCHIVOS) ---
st.sidebar.divider()
st.sidebar.subheader(f"📁 Plantillas {modo}")
nombre_plantilla = st.sidebar.selectbox("Seleccionar Marca/Carga:", ["-- Seleccionar --"] + list(fuente_plantillas.keys()))

if st.sidebar.button("Cargar Datos"):
    if nombre_plantilla != "-- Seleccionar --":
        nuevos_datos = pd.DataFrame(fuente_plantillas[nombre_plantilla])
        st.session_state.data = calcular_pkg(nuevos_datos)
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Reset Histórico"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.data = pd.DataFrame(columns=columnas_base)
    st.rerun()

st.title(titulo_app)

# --- 8. EDITOR DE TABLA ---
st.subheader("📝 Editor de Datos")
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = calcular_pkg(edited_df)
    st.session_state.data.to_csv(DB_FILE, index=False)
    st.rerun()

# --- 9. LÓGICA DE VISUALIZACIÓN ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    
    # Ordenamiento lógico según la jerarquía definida
    ord_map = {cat.upper(): i for i, cat in enumerate(opciones_agrupador)}
    df_p["Orden_Cat"] = df_p[label_agrupador].str.upper().map(ord_map).fillna(99)
    df_p = df_p.sort_values(by=["Orden_Cat", "Precio ($)"]).reset_index(drop=True)

    if modo == "Price Pack":
        # --- GRÁFICO ESPECÍFICO PRICE PACK ---
        fig = go.Figure()
        
        # Barras: Eje Y es Precio por Kg ($)
        fig.add_trace(go.Bar(
            x=df_p.index,
            y=df_p["Precio por Kg ($)"],
            marker_color="#0B3C8C",
            text=[f"<b>${p:,.1f}</b>" for p in df_p["Precio por Kg ($)"]],
            textposition="outside",
            textfont=dict(size=14, color="black")
        ))

        # Etiquetas de Precio Desembolso en la base (Formato $X.X)
        for i, row in df_p.iterrows():
            fig.add_annotation(
                x=i, y=max(df_p["Precio por Kg ($)"]) * 0.05,
                text=f"<b>${row['Precio ($)']:.1f}</b>",
                showarrow=False, font=dict(size=12, color="white"),
                bgcolor="rgba(0,0,0,0.7)", borderpad=4
            )

        # Configuración de Ejes (Nombres a 90 grados)
        fig.update_layout(
            xaxis=dict(
                tickmode='array', tickvals=list(df_p.index),
                ticktext=df_p["Producto"], tickangle=90, tickfont=dict(size=11)
            ),
            yaxis=dict(title="Precio por Kg ($)", range=[0, df_p["Precio por Kg ($)"].max() * 1.25]),
            height=750, margin=dict(b=250, t=50), template="plotly_white"
        )

        # Divisores y Etiquetas de Canal (Bajadas para no empalmar)
        for cat in df_p[label_agrupador].unique():
            indices = df_p.index[df_p[label_agrupador] == cat].tolist()
            if indices:
                center = (indices[0] + indices[-1]) / 2
                fig.add_shape(type="line", x0=indices[-1]+0.5, x1=indices[-1]+0.5, y0=0, y1=1, xref="x", yref="paper", line=dict(color="#DDD", width=2))
                fig.add_annotation(x=center, y=-0.38, xref="x", yref="paper", text=f"<b>{cat}</b>", showarrow=False, font=dict(size=13))

        st.plotly_chart(fig, use_container_width=True)

    else:
        # --- GRÁFICO ESPECÍFICO PRICE LADDER ---
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.2, 0.8])
        
        # Burbujas de SOM (Market Share)
        fig.add_trace(go.Scatter(
            x=df_p["Producto"], y=df_p["SOM (%)"], mode="lines+markers+text",
            line=dict(color="#CCC", width=1),
            marker=dict(size=35, color="#F0F0F0", symbol="square"),
            text=[f"<b>{s}%</b>" for s in df_p["SOM (%)"]], textposition="middle center"
        ), row=1, col=1)

        # Barras de Precio Desembolso
        colores_fab = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
        fig.add_trace(go.Bar(
            x=df_p["Producto"], y=df_p["Precio ($)"],
            marker_color=[colores_fab.get(str(f).upper(), "#999") for f in df_p["Fabricante"]],
            text=[f"<b>${p}</b>" for p in df_p["Precio ($)"]], textposition="outside"
        ), row=2, col=1)

        # Divisores de Ocasión
        for cat in df_p[label_agrupador].unique():
            indices = df_p.index[df_p[label_agrupador] == cat].tolist()
            if indices:
                center = (indices[0] + indices[-1]) / 2
                fig.add_shape(type="line", x0=indices[-1]+0.5, x1=indices[-1]+0.5, y0=0, y1=1, xref="x", yref="paper", line=dict(color="#DDD"), row=2, col=1)
                fig.add_annotation(x=center, y=-0.30, xref="x", yref="paper", text=f"<b>{cat}</b>", showarrow=False, row=2, col=1)

        fig.update_layout(height=850, margin=dict(b=200), template="plotly_white", showlegend=False)
        fig.update_xaxes(tickangle=90)
        st.plotly_chart(fig, use_container_width=True)

        # --- PIRÁMIDE DE PRECIOS ---
        st.divider()
        st.subheader(f"⛰️ Pirámide de Posicionamiento por {label_agrupador}")
        df_py = procesar_datos_piramide(df_p, label_agrupador)
        
        sel_cat = st.selectbox(f"Seleccionar {label_agrupador} para Pirámide:", df_py[label_agrupador].unique())
        df_cat = df_py[df_py[label_agrupador] == sel_cat].sort_values("Precio por Kg ($)", ascending=True)
        
        tier_colors = {"PREMIUM": "#1A237E", "UPPER MAINSTREAM": "#0D47A1", "MAINSTREAM": "#0B3C8C", "MAINSTREAM LOW": "#1976D2", "VALUE": "#42A5F5"}

        for tier in ["PREMIUM", "UPPER MAINSTREAM", "MAINSTREAM", "MAINSTREAM LOW", "VALUE"]:
            prod_tier = df_cat[df_cat["Tier"] == tier]
            if not prod_tier.empty:
                col1, col2 = st.columns([1, 4])
                col1.markdown(f'<div style="background-color:{tier_colors[tier]}; color:white; padding:10px; border-radius:5px; text-align:center;">{tier}</div>', unsafe_allow_html=True)
                cards = ""
                for _, r in prod_tier.iterrows():
                    b_color = "#4B207E" if r["Fabricante"] == "BARCEL" else "#AAA"
                    cards += f'<div style="display:inline-block; border:2px solid {b_color}; padding:8px; margin:4px; border-radius:5px; background:white; text-align:center;"><b>{r["Producto"]}</b><br>${r["Precio ($)"]}<br><small>Idx: {int(r["Idx_P"])}</small></div>'
                col2.markdown(cards, unsafe_allow_html=True)

st.sidebar.info("G g") # Siguiendo instrucción de formato
