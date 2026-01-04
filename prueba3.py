import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. IMPORTACIÓN DE PLANTILLAS SEPARADAS ---
from plantillas import PLANTILLAS
try:
    from price_pack import PLANTILLAS_PP
except ImportError:
    PLANTILLAS_PP = {}

# --- 2. CONFIGURACIÓN ---
st.set_page_config(page_title="Price Architecture Expert Pro", layout="wide")

# --- 3. SELECTOR DE MÓDULO (EL INTERRUPTOR) ---
st.sidebar.header("🚀 Navegación")
modo = st.sidebar.radio("Seleccionar Herramienta:", ["Price Ladder", "Price Pack"])

# Definición de variables dinámicas según el modo seleccionado
if modo == "Price Ladder":
    DB_FILE = "historico_ladder.csv"
    fuente_plantillas = PLANTILLAS
    label_agrupador = "Ocasión"
    # Opciones de tu código original
    opciones_agrupador = ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR", "REUNIÓN", "FIESTA", "TRANSFORMADOR"]
    titulo_app = "📊 ESCALERAS DE PRECIO DINÁMICAS"
    columnas_base = ["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"]
else:
    DB_FILE = "historico_price_pack.csv"
    fuente_plantillas = PLANTILLAS_PP
    label_agrupador = "Canal"
    # Opciones nuevas para Price Pack
    opciones_agrupador = ["DT", "AS", "CNV", "MAYOREO", "E-COMMERCE"]
    titulo_app = "📦 PRICE PACK ARCHITECTURE (BARCEL)"
    # Agregamos 'Familia' a las columnas de Price Pack
    columnas_base = ["Producto", "Fabricante", "Familia", "Canal", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"]

# --- 4. FUNCIONES CORE ---
def calcular_pkg(df):
    if df.empty: return df
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1).replace(0, 1)
    df["SOM (%)"] = pd.to_numeric(df["SOM (%)"], errors='coerce').fillna(0)
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(0)
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
    
    def asignar_t(i):
        if i >= 170: return "PREMIUM"
        elif 120 <= i < 170: return "UPPER MAINSTREAM"
        elif 95 <= i < 120: return "MAINSTREAM"
        elif 80 <= i < 95: return "MAINSTREAM LOW"
        else: return "VALUE"
    temp["Tier"] = temp["Idx_P"].apply(asignar_t)
    return temp

# --- 5. GESTIÓN DE ESTADO (SESSION STATE) ---
if "data" not in st.session_state or st.session_state.get('last_modo') != modo:
    if os.path.exists(DB_FILE):
        st.session_state.data = calcular_pkg(pd.read_csv(DB_FILE))
    else:
        st.session_state.data = pd.DataFrame(columns=columnas_base)
    st.session_state.last_modo = modo

# --- 6. BARRA LATERAL (GESTIÓN) ---
st.sidebar.divider()
st.sidebar.subheader(f"📁 Gestión {modo}")
nombre_plantilla = st.sidebar.selectbox("Cargar Plantilla:", ["-- Seleccionar --"] + list(fuente_plantillas.keys()))

if st.sidebar.button("Cargar Escalera" if modo == "Price Ladder" else "Cargar Price Pack"):
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

# --- 7. FORMULARIO ---
with st.expander(f"➕ Agregar nuevo producto manualmente", expanded=False):
    with st.form("nuevo_sku_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        f_nom = c1.text_input("Nombre del Producto").upper()
        
        if modo == "Price Pack":
            f_fab = "BARCEL"
            f_fam = c2.text_input("Familia (Marca)").upper()
            f_agrupar = c3.selectbox(label_agrupador, opciones_agrupador)
        else:
            f_fab = c2.selectbox("Fabricante", ["BARCEL", "SABRITAS", "OTROS", "PROPUESTA"])
            f_fam = "N/A"
            f_agrupar = c3.selectbox(label_agrupador, opciones_agrupador)

        c4, c5, c6 = st.columns(3)
        f_pre = c4.number_input("Precio ($)", min_value=0.0, step=0.5)
        f_gra = c5.number_input("Gramaje (g)", min_value=1.0, step=1.0)
        f_som = c6.number_input("SOM (%)", min_value=0.0, max_value=100.0, step=0.1)
        
        # Ocasión de consumo extra para Price Pack
        f_oca_sec = "N/A"
        if modo == "Price Pack":
            f_oca_sec = st.selectbox("Ocasión de Consumo", ["INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"])

        if st.form_submit_button("Añadir a la lista"):
            nuevo_sku = pd.DataFrame([{
                "Producto": f_nom, "Fabricante": f_fab, "Familia": f_fam,
                label_agrupador: f_agrupar, "Ocasión": f_oca_sec if modo == "Price Pack" else f_agrupar,
                "Precio ($)": f_pre, "Gramaje (g)": f_gra, "SOM (%)": f_som
            }])
            st.session_state.data = pd.concat([st.session_state.data, nuevo_sku], ignore_index=True)
            st.session_state.data = calcular_pkg(st.session_state.data)
            st.session_state.data.to_csv(DB_FILE, index=False)
            st.rerun()

# --- 8. EDITOR ---
st.subheader("📝 Tabla de Datos")
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = calcular_pkg(edited_df)
    st.session_state.data.to_csv(DB_FILE, index=False)
    st.rerun()

# --- 9. GRÁFICO FINAL ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    
    # Ordenamiento Lógico
    if modo == "Price Ladder":
        ord_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5,"REUNIÓN":6, "FIESTA":7,"TRANSFORMADOR":8}
        df_p["O_Ord"] = df_p[label_agrupador].str.upper().map(ord_oca).fillna(99)
    else:
        ord_can = {"DT": 1, "AS": 2, "CNV": 3, "MAYOREO": 4}
        df_p["O_Ord"] = df_p[label_agrupador].str.upper().map(ord_can).fillna(99)

    df_p = df_p.sort_values(by=["O_Ord", "Precio ($)"]).reset_index(drop=True)
    som_por_ocasion = df_p.groupby(label_agrupador)["SOM (%)"].sum().to_dict()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.0, row_heights=[0.12, 0.88])

    # Burbujas de SOM
    fig.add_trace(go.Scatter(
        x=df_p["Producto"], y=df_p["SOM (%)"], mode="lines+markers+text", 
        line=dict(color="#BBBBBB", width=1.5), 
        marker=dict(size=30, color="#E5E5E5", symbol="square", line=dict(color="#CCCCCC", width=1)), 
        text=[f"<b>{row['SOM (%)']}%</b>" for _, row in df_p.iterrows()],
        textposition="middle center", textfont=dict(size=13, color="black"),
    ), row=1, col=1)

    # Barras de Precio
    colors = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D","PROPUESTA":"#4B207E"}
    fig.add_trace(go.Bar(
        x=df_p["Producto"], y=df_p["Precio ($)"],
        marker_color=[colors.get(str(f).upper(), "#999") for f in df_p["Fabricante"]],
        text=[f"<b>${int(p)}</b>" for p in df_p["Precio ($)"]], 
        textposition="outside", textfont=dict(size=18, color="black") 
    ), row=2, col=1)

    # Anotaciones de Precio por Kg
    for i, row in df_p.iterrows():
        fig.add_annotation(
            x=i, y=2.5, text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
            showarrow=False, font=dict(size=16, color="white" if row["Fabricante"] == "BARCEL" else "black"),
            bgcolor="rgba(70, 130, 180, 0.8)" if row["Fabricante"] == "BARCEL" else "rgba(255,255,255,0.8)",
            bordercolor="#444" if row["Fabricante"] != "BARCEL" else None, borderwidth=1, row=2, col=1
        )

    # Separadores y Etiquetas de Agrupador (Ocasión/Canal)
    for cat in df_p[label_agrupador].unique():
        idx_list = df_p.index[df_p[label_agrupador] == cat].tolist()
        center = (idx_list[0] + idx_list[-1]) / 2
        fig.add_shape(type="line", x0=idx_list[-1] + 0.5, x1=idx_list[-1] + 0.5, y0=-0.01, y1=1, xref="x2", yref="paper", line=dict(color="#DDDDDD", width=1.5))
        fig.add_annotation(x=center, y=-0.60, xref="x2", yref="paper", text=f"{cat}<br><span style='font-size:18px;'>{som_por_ocasion[cat]:.1f}%</span>", showarrow=False, font=dict(size=16, color="black"), align="center")

    fig.update_layout(height=900, width=1600, template="plotly_white", showlegend=False, margin=dict(t=50, b=300, l=40, r=40))
    fig.update_yaxes(showticklabels=False, row=1, col=1)
    fig.update_xaxes(tickangle=-90, tickfont=dict(size=14), row=2, col=1)
    st.plotly_chart(fig, use_container_width=True)

# --- 10. PIRÁMIDE ---
st.divider()
st.subheader(f"🏔️ Pirámide de Posicionamiento ({label_agrupador})")

if not st.session_state.data.empty:
    df_pyramid = procesar_datos_piramide(df_p, label_agrupador)
    sel_cat = st.selectbox(f"Seleccionar {label_agrupador}:", df_pyramid[label_agrupador].unique())
    df_f = df_pyramid[df_pyramid[label_agrupador] == sel_cat].sort_values("Idx_P", ascending=False)
    
    tier_colors = {"PREMIUM": "#1A237E", "UPPER MAINSTREAM": "#0D47A1", "MAINSTREAM": "#0B3C8C", "MAINSTREAM LOW": "#1976D2", "VALUE": "#42A5F5"}

    for tier in ["PREMIUM", "UPPER MAINSTREAM", "MAINSTREAM", "MAINSTREAM LOW", "VALUE"]:
        productos_tier = df_f[df_f["Tier"] == tier]
        if not productos_tier.empty:
            c1, c2 = st.columns([1, 4])
            c1.markdown(f'<div style="background-color:{tier_colors[tier]}; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">{tier}</div>', unsafe_allow_html=True)
            cards_html = ""
            for _, r in productos_tier.iterrows():
                b_color = "#4B207E" if r["Fabricante"] == "BARCEL" else "#CCCCCC"
                cards_html += f"""
                <div style="display:inline-block; border: 2px solid {b_color}; border-radius: 10px; padding: 10px; background: white; min-width: 150px; margin: 5px; text-align:center;">
                    <div style="font-weight:bold; font-size:0.85rem;">{r['Producto']}</div>
                    <div style="color:#666; font-size:0.8rem;">Idx: {int(r['Idx_P'])}</div>
                    <div style="font-weight:bold; color:#111;">${int(r['Precio ($)'])}</div>
                </div>"""
            st.markdown(f'<div style="display: block; width: 100%;">{cards_html}</div>', unsafe_allow_html=True)
