import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. IMPORTACIÓN DE PLANTILLAS EXTERNAS ---
from plantillas import PLANTILLAS
try:
    from price_pack import PLANTILLAS_PP
except ImportError:
    PLANTILLAS_PP = {}

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Barcel Price Architecture Expert", layout="wide")

# --- 3. NAVEGACIÓN Y ESTADO ---
st.sidebar.header("🚀 Navegación")
modo = st.sidebar.radio("Seleccionar Herramienta:", ["Price Ladder", "Price Pack"])

# Configuración dinámica según el modo seleccionado
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
    titulo_app = "📦 PRICE PACK ARCHITECTURE (INTERNAL)"

# --- 4. FUNCIONES DE CÁLCULO ---
def calcular_pkg(df):
    if df.empty: return df
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1).replace(0, 1)
    # Cálculo de Precio por Kilo con 1 decimal
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(1)
    if "SOM (%)" not in df.columns: df["SOM (%)"] = 0.0
    if "Fabricante" not in df.columns: df["Fabricante"] = "BARCEL"
    return df

def procesar_datos_piramide(df, agrupador):
    if df.empty: return df
    temp = df.copy()
    
    # Obtener el precio de referencia (el de mayor SOM o el promedio)
    def get_base(g):
        if g["SOM (%)"].max() > 0:
            return g.loc[g["SOM (%)"].idxmax(), "Precio por Kg ($)"]
        return g["Precio por Kg ($)"].mean() if not g.empty else 1
    
    bases = temp.groupby(agrupador).apply(lambda x: get_base(x)).reset_index()
    bases.columns = [agrupador, "P_Ref"]
    temp = temp.merge(bases, on=agrupador, how="left")
    temp["Idx_P"] = (temp["Precio por Kg ($)"] / temp["P_Ref"] * 100).round(0)
    
    # Clasificación de Tiers de Precio
    def asignar_tier(i):
        if i >= 170: return "PREMIUM"
        elif 120 <= i < 170: return "UPPER MAINSTREAM"
        elif 95 <= i < 120: return "MAINSTREAM"
        elif 80 <= i < 95: return "MAINSTREAM LOW"
        else: return "VALUE"
    
    temp["Tier"] = temp["Idx_P"].apply(asignar_tier)
    return temp

# --- 5. CARGA DE DATOS ---
if "data" not in st.session_state or st.session_state.get('last_modo') != modo:
    if os.path.exists(DB_FILE):
        st.session_state.data = calcular_pkg(pd.read_csv(DB_FILE))
    else:
        st.session_state.data = pd.DataFrame()
    st.session_state.last_modo = modo

# --- 6. SIDEBAR: ACCIONES ---
st.sidebar.divider()
st.sidebar.subheader(f"📁 Plantillas {modo}")
nombre_plantilla = st.sidebar.selectbox("Seleccionar Marca:", ["-- Seleccionar --"] + list(fuente_plantillas.keys()))

if st.sidebar.button("Cargar Datos de Plantilla"):
    if nombre_plantilla != "-- Seleccionar --":
        # Aseguramos que la columna del agrupador sea correcta (Ocasión o Canal)
        df_new = pd.DataFrame(fuente_plantillas[nombre_plantilla])
        if "Canal" in df_new.columns and modo == "Price Ladder":
            df_new = df_new.rename(columns={"Canal": "Ocasión"})
        elif "Ocasión" in df_new.columns and modo == "Price Pack":
            df_new = df_new.rename(columns={"Ocasión": "Canal"})
            
        st.session_state.data = calcular_pkg(df_new)
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Borrar Todo"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.data = pd.DataFrame()
    st.rerun()

# --- 7. INTERFAZ PRINCIPAL ---
st.title(titulo_app)

# Editor de datos
st.subheader("📝 Tabla de Datos")
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = calcular_pkg(edited_df)
    st.session_state.data.to_csv(DB_FILE, index=False)
    st.rerun()

# --- 8. LÓGICA DE GRÁFICOS ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    
    # Ordenamiento por la jerarquía definida en 'opciones_agrupador'
    ord_map = {cat.upper(): i for i, cat in enumerate(opciones_agrupador)}
    df_p["Orden_Cat"] = df_p[label_agrupador].str.upper().map(ord_map).fillna(99)
    df_p = df_p.sort_values(by=["Orden_Cat", "Precio ($)"]).reset_index(drop=True)

    if modo == "Price Pack":
        # --- MODO PRICE PACK ---
        fig = go.Figure()
        
        # Barras de Precio por Kilo
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
                bgcolor="rgba(0,0,0,0.6)", borderpad=4
            )

        # Configuración de Ejes
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=list(df_p.index),
                ticktext=df_p["Producto"],
                tickangle=90, # Nombres a 90 grados
                tickfont=dict(size=11)
            ),
            yaxis=dict(title="Precio por Kg ($)", range=[0, df_p["Precio por Kg ($)"].max() * 1.25]),
            height=750, margin=dict(b=200, t=50), template="plotly_white"
        )

        # Divisores y Etiquetas de Canal
        for cat in df_p[label_agrupador].unique():
            indices = df_p.index[df_p[label_agrupador] == cat].tolist()
            if indices:
                center = (indices[0] + indices[-1]) / 2
                fig.add_shape(type="line", x0=indices[-1]+0.5, x1=indices[-1]+0.5, y0=0, y1=1, xref="x", yref="paper", line=dict(color="#DDD", width=2))
                fig.add_annotation(x=center, y=-0.32, xref="x", yref="paper", text=f"<b>{cat}</b>", showarrow=False, font=dict(size=14, color="#333"))

        st.plotly_chart(fig, use_container_width=True)

    else:
        # --- MODO PRICE LADDER ---
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.2, 0.8])
        
        # 1. Burbujas de SOM
        fig.add_trace(go.Scatter(
            x=df_p["Producto"], y=df_p["SOM (%)"],
            mode="lines+markers+text",
            line=dict(color="#CCC", width=1),
            marker=dict(size=35, color="#F0F0F0", symbol="square"),
            text=[f"<b>{s}%</b>" for s in df_p["SOM (%)"]],
            textposition="middle center",
            textfont=dict(size=11)
        ), row=1, col=1)

        # 2. Barras de Precio Desembolso por Fabricante
        colores = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
        fig.add_trace(go.Bar(
            x=df_p["Producto"], y=df_p["Precio ($)"],
            marker_color=[colores.get(str(f).upper(), "#999") for f in df_p["Fabricante"]],
            text=[f"<b>${p}</b>" for p in df_p["Precio ($)"]],
            textposition="outside"
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

        # --- 9. PIRÁMIDES DE PRECIO ---
        st.divider()
        st.subheader("⛰️ Pirámide de Precios por Ocasión")
        df_py = procesar_datos_piramide(df_p, label_agrupador)
        
        sel_cat = st.selectbox("Seleccionar Ocasión para analizar:", df_py[label_agrupador].unique())
        df_cat = df_py[df_py[label_agrupador] == sel_cat].sort_values("Precio por Kg ($)", ascending=True)
        
        fig_py = go.Figure()
        colores_tier = {"PREMIUM": "#4A148C", "UPPER MAINSTREAM": "#1976D2", "MAINSTREAM": "#388E3C", "MAINSTREAM LOW": "#FBC02D", "VALUE": "#D32F2F"}
        
        fig_py.add_trace(go.Funnel(
            y=df_cat["Producto"] + " (" + df_cat["Tier"] + ")",
            x=df_cat["Precio por Kg ($)"],
            textinfo="value",
            marker=dict(color=[colores_tier.get(t, "#999") for t in df_cat["Tier"]])
        ))
        
        fig_py.update_layout(title=f"Índice de Precio en {sel_cat} (Base 100 = Líder SOM)", showlegend=False)
        st.plotly_chart(fig_py, use_container_width=True)

st.info("💡 Consejo: Puedes editar los gramos y precios directamente en la tabla y los gráficos se actualizarán automáticamente.")
