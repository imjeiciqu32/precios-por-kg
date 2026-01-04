import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from plantillas import PLANTILLAS 

# Intentamos cargar la nueva de Takis, si no existe no rompe el código
try:
    from price_pack import PLANTILLAS_PP
except ImportError:
    PLANTILLAS_PP = {}

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Price Architecture Expert Pro", layout="wide")

# NAVEGACIÓN ENTRE MODOS
st.sidebar.header("🚀 Modo de Visualización")
modo = st.sidebar.radio("Seleccionar:", ["Price Ladder", "Price Pack"])

if modo == "Price Ladder":
    DB_FILE = "historico_productos.csv"
    label_agru = "Ocasión"
    opciones_agru = ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR","REUNIÓN", "FIESTA","TRANSFORMADOR"]
    fuente_plantillas = PLANTILLAS
else:
    DB_FILE = "historico_price_pack.csv"
    label_agru = "Canal"
    opciones_agru = ["INSTITUCIONALES", "MAYOREO", "CLUBES", "HARD DISCOUNT", "DETALLE", "AUTOSERVICIO", "CONVENIENCIA"]
    fuente_plantillas = PLANTILLAS_PP

# --- 2. FUNCIONES CORE (ORIGINALES) ---
def calcular_pkg(df):
    if df.empty: return df
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1).replace(0, 1)
    df["SOM (%)"] = pd.to_numeric(df["SOM (%)"], errors='coerce').fillna(0)
    # Price Pack requiere decimales, Ladder suele ser entero. Dejamos 1 decimal para precisión.
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(1)
    return df

def procesar_datos_piramide(df, agrupador="Ocasión"):
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
    def asignar_t(i):
        if i >= 170: return "PREMIUM"
        elif 120 <= i < 170: return "UPPER MAINSTREAM"
        elif 95 <= i < 120: return "MAINSTREAM"
        elif 80 <= i < 95: return "MAINSTREAM LOW"
        else: return "VALUE"
    temp["Tier"] = temp["Idx_P"].apply(asignar_t)
    return temp

# --- 3. ESTADO DE SESIÓN ---
if "data" not in st.session_state or st.session_state.get("last_modo") != modo:
    if os.path.exists(DB_FILE):
        st.session_state.data = calcular_pkg(pd.read_csv(DB_FILE))
    else:
        st.session_state.data = pd.DataFrame(columns=["Producto", "Fabricante", label_agru, "Precio ($)", "Gramaje (g)", "SOM (%)"])
    st.session_state.last_modo = modo

# --- 4. BARRA LATERAL ---
st.sidebar.header("📁 Gestión")
nombre_plantilla = st.sidebar.selectbox("Cargar Plantilla:", ["-- Seleccionar --"] + list(fuente_plantillas.keys()))

if st.sidebar.button("Cargar Datos"):
    if nombre_plantilla != "-- Seleccionar --":
        nuevos_datos = pd.DataFrame(fuente_plantillas[nombre_plantilla])
        st.session_state.data = calcular_pkg(nuevos_datos)
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Reset"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.data = pd.DataFrame(columns=["Producto", "Fabricante", label_agru, "Precio ($)", "Gramaje (g)", "SOM (%)"])
    st.rerun()

st.title(f"📊 {modo.upper()}")

# --- 5. FORMULARIO ---
with st.expander("➕ Agregar nuevo producto manualmente", expanded=False):
    with st.form("nuevo_sku_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        f_nom = c1.text_input("Nombre del Producto").upper()
        f_fab = c2.selectbox("Fabricante", ["BARCEL", "SABRITAS", "OTROS","PROPUESTA"])
        f_agru = c3.selectbox(label_agru, opciones_agru)
        c4, c5, c6 = st.columns(3)
        f_pre = c4.number_input("Precio ($)", min_value=0.0, step=0.5)
        f_gra = c5.number_input("Gramaje (g)", min_value=1.0, step=1.0)
        f_som = c6.number_input("SOM (%)", min_value=0.0, max_value=100.0, step=0.1)
        if st.form_submit_button("Añadir a la lista"):
            nuevo_sku = pd.DataFrame([{"Producto": f_nom, "Fabricante": f_fab, label_agru: f_agru, "Precio ($)": f_pre, "Gramaje (g)": f_gra, "SOM (%)": f_som}])
            st.session_state.data = pd.concat([st.session_state.data, nuevo_sku], ignore_index=True)
            st.session_state.data = calcular_pkg(st.session_state.data)
            st.session_state.data.to_csv(DB_FILE, index=False)
            st.rerun()

# --- 6. EDITOR ---
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = calcular_pkg(edited_df)
    st.session_state.data.to_csv(DB_FILE, index=False)
    st.rerun()

# --- 7. GRÁFICO (LÓGICA UNIFICADA) ---
if not st.session_state.data.empty:
    # Mapa de orden dinámico
    ord_map = {cat.upper(): i+1 for i, cat in enumerate(opciones_agru)}
    df_p = st.session_state.data.copy()
    df_p["Orden"] = df_p[label_agru].str.upper().map(ord_map).fillna(99)
    df_p = df_p.sort_values(by=["Orden", "Precio ($)"]).reset_index(drop=True)
    
    agru_list = df_p[label_agru].unique()
    som_por_agru = df_p.groupby(label_agru)["SOM (%)"].sum().to_dict()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.0, row_heights=[0.12, 0.88])

    # Burbujas Superiores (SOM %)
    fig.add_trace(go.Scatter(
        x=df_p.index, y=df_p["SOM (%)"], mode="lines+markers+text", 
        line=dict(color="#BBBBBB", width=1.5), 
        marker=dict(size=30, color="#E5E5E5", symbol="square", line=dict(color="#CCCCCC", width=1)), 
        text=[f"<b>{row['SOM (%)']}%</b>" for _, row in df_p.iterrows()],
        textposition="middle center", textfont=dict(size=12, color="black"),
    ), row=1, col=1)

    # Barras Inferiores (Precio Desembolso)
    colors_map = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D","PROPUESTA":"#4B207E"}
    
    # En Price Pack, si es BARCEL usamos el azul fuerte, si no, gris
    fig.add_trace(go.Bar(
        x=df_p.index, y=df_p["Precio ($)"],
        marker_color=[colors_map.get(str(f).upper(), "#999") for f in df_p["Fabricante"]],
        text=[f"<b>${p:,.1f}</b>" if modo == "Price Pack" else f"<b>${int(p)}</b>" for p in df_p["Precio ($)"]], 
        textposition="outside", textfont=dict(size=16, color="black") 
    ), row=2, col=1)

    # ETIQUETAS DE $/KG (Tu lógica de cuadros azules/blancos)
    for i, row in df_p.iterrows():
        # En modo Price Pack la ponemos en la parte superior de la barra o fija
        y_pos = row["Precio ($)"] * 0.5 if modo == "Price Ladder" else 2.5
        fig.add_annotation(
            x=i, y=y_pos, text=f"<b>${row['Precio por Kg ($)']:,.0f}</b>",
            showarrow=False, font=dict(size=14, color="white" if row["Fabricante"] == "BARCEL" else "black"),
            bgcolor="rgba(11, 60, 140, 0.85)" if row["Fabricante"] == "BARCEL" else "rgba(255,255,255,0.8)",
            bordercolor="#444", borderwidth=1, row=2, col=1
        )

    # Líneas Divisorias y Etiquetas de Agrupador (Ocasión o Canal)
    for cat in agru_list:
        idx_list = df_p.index[df_p[label_agru] == cat].tolist()
        center = (idx_list[0] + idx_list[-1]) / 2
        # Línea vertical divisoria
        fig.add_shape(type="line", x0=idx_list[-1] + 0.5, x1=idx_list[-1] + 0.5, y0=-0.01, y1=1, xref="x2", yref="paper", line=dict(color="#DDDDDD", width=1.5))
        # Etiqueta inferior
        txt_label = f"{cat}<br><span style='font-size:16px;'>{som_por_agru[cat]:.1f}%</span>"
        fig.add_annotation(x=center, y=-0.55, xref="x2", yref="paper", text=txt_label, showarrow=False, font=dict(size=14, color="black"), align="center")

    # Estética General
    fig.update_layout(
        height=900, width=1800, template="plotly_white", showlegend=False, 
        margin=dict(t=50, b=350, l=40, r=40)
    )
    fig.update_xaxes(
        tickmode='array', tickvals=list(df_p.index), ticktext=df_p["Producto"],
        tickangle=-90, tickfont=dict(size=14, color="black"), row=2, col=1
    )
    fig.update_yaxes(showticklabels=False, row=1, col=1)
    fig.update_yaxes(gridcolor="#EEE", row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)

# --- 8. COMPARATIVAS INDEX ---
st.divider()
st.subheader("📈 Comparativas Index $/Kg")
barcel_list = df_p[df_p["Fabricante"]=="BARCEL"]["Producto"].unique() if not df_p.empty else []
comp_list = df_p[df_p["Fabricante"]!="BARCEL"]["Producto"].unique() if not df_p.empty else []

if len(barcel_list) > 0 and len(comp_list) > 0:
    idx_cols = st.columns(4)
    for i in range(4):
        with idx_cols[i]:
            with st.container(border=True):
                p_b = st.selectbox(f"Barcel", barcel_list, key=f"sb{i}", label_visibility="collapsed")
                p_c = st.selectbox(f"Comp.", comp_list, key=f"sc{i}", label_visibility="collapsed")
                val_b = df_p[df_p["Producto"]==p_b]["Precio por Kg ($)"].values[0]
                val_c = df_p[df_p["Producto"]==p_c]["Precio por Kg ($)"].values[0]
                index_val = int((val_b / val_c) * 100)
                color_index = "#0B3C8C" if index_val <= 100 else "#D32F2F"
                st.markdown(f"""<div style="background-color: #f8f9fa; padding: 10px; border-radius: 10px; border-top: 5px solid {color_index}; text-align: center;"><div style="font-weight: bold;">{p_b} vs {p_c}</div><div style="font-size: 2rem; font-weight: 900; color: {color_index};">{index_val}</div></div>""", unsafe_allow_html=True)

# --- 9. PIRÁMIDE ---
st.divider()
st.subheader(f"🏔️ Pirámide de Posicionamiento por {label_agru}")
if not df_p.empty:
    df_pyramid = procesar_datos_piramide(df_p, label_agru)
    sel_seg = st.selectbox(f"Segmento:", df_pyramid[label_agru].unique())
    df_f = df_pyramid[df_pyramid[label_agru] == sel_seg].sort_values("Idx_P", ascending=False)
    
    tier_colors = {"PREMIUM": "#1A237E", "UPPER MAINSTREAM": "#0D47A1", "MAINSTREAM": "#0B3C8C", "MAINSTREAM LOW": "#1976D2", "VALUE": "#42A5F5"}

    for tier in ["PREMIUM", "UPPER MAINSTREAM", "MAINSTREAM", "MAINSTREAM LOW", "VALUE"]:
        productos_tier = df_f[df_f["Tier"] == tier]
        if not productos_tier.empty:
            c1, c2 = st.columns([1, 4])
            c1.markdown(f'<div style="background-color:{tier_colors[tier]}; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">{tier}</div>', unsafe_allow_html=True)
            cards_html = ""
            for _, r in productos_tier.iterrows():
                b_color = "#4B207E" if r["Fabricante"] == "BARCEL" else "#CCCCCC"
                cards_html += f"""<div style="display:inline-block; border: 2px solid {b_color}; border-radius: 10px; padding: 10px; background: white; min-width: 150px; margin: 5px;"><b>{r['Producto']}</b><br>Idx: {int(r['Idx_P'])}<br>${r['Precio ($)']} ({int(r['Gramaje (g)'])}g)</div>"""
            st.markdown(f'<div style="display: block; width: 100%;">{cards_html}</div>', unsafe_allow_html=True)

st.sidebar.caption("G g")
