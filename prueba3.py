import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. CONFIGURACIÓN Y CARGA DE PLANTILLAS ---
try:
    from plantillas import PLANTILLAS 
except ImportError:
    PLANTILLAS = {}

try:
    from price_pack import PLANTILLAS_PP
except ImportError:
    PLANTILLAS_PP = {}

st.set_page_config(page_title="Price Architecture Expert Pro", layout="wide")

# NAVEGACIÓN
st.sidebar.header("🚀 Modo de Visualización")
modo = st.sidebar.radio("Seleccionar Herramienta:", ["Price Ladder", "Price Pack"])

# Configuración de variables según el modo
if modo == "Price Ladder":
    DB_FILE = "historico_productos.csv"
    label_agru = "Ocasión"
    opciones_agru = ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR", "REUNIÓN", "FIESTA", "TRANSFORMADOR"]
    fuente_plantillas = PLANTILLAS
    columnas_tabla = ["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "SOM (%)"]
else:
    DB_FILE = "historico_price_pack.csv"
    label_agru = "Canal"
    opciones_agru = ["INSTITUCIONALES", "MAYOREO", "CLUBES", "DETALLE", "AUTOSERVICIO", "CONVENIENCIA"]
    fuente_plantillas = PLANTILLAS_PP
    columnas_tabla = ["Producto", "Familia", "Canal", "Precio ($)", "Gramaje (g)"]

# --- 2. FUNCIONES CORE ---
def calcular_pkg(df, modo_actual):
    if df.empty: return df
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1).replace(0, 1)
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(1)
    
    if modo_actual == "Price Ladder":
        if "SOM (%)" not in df.columns: df["SOM (%)"] = 0.0
        if "Fabricante" not in df.columns: df["Fabricante"] = "OTROS"
    return df

def procesar_datos_piramide(df):
    if df.empty: return df
    df_py = df.copy()
    avg_pkg = df_py.groupby("Ocasión")["Precio por Kg ($)"].transform("mean")
    df_py["Idx_P"] = (df_py["Precio por Kg ($)"] / avg_pkg) * 100
    
    def definir_tier(idx):
        if idx >= 120: return "PREMIUM"
        if idx >= 105: return "UPPER MAINSTREAM"
        if idx >= 95:  return "MAINSTREAM"
        if idx >= 85:  return "MAINSTREAM LOW"
        return "VALUE"
    
    df_py["Tier"] = df_py["Idx_P"].apply(definir_tier)
    return df_py

# --- 3. GESTIÓN DE ESTADO ---
if "data" not in st.session_state or st.session_state.get("last_modo") != modo:
    if os.path.exists(DB_FILE):
        st.session_state.data = calcular_pkg(pd.read_csv(DB_FILE), modo)
    else:
        st.session_state.data = pd.DataFrame(columns=columnas_tabla)
    st.session_state.last_modo = modo

# --- 4. BARRA LATERAL ---
st.sidebar.header("📁 Gestión de Datos")
nombre_plantilla = st.sidebar.selectbox("Cargar Plantilla:", ["-- Seleccionar --"] + list(fuente_plantillas.keys()))

if st.sidebar.button("Cargar Datos"):
    if nombre_plantilla != "-- Seleccionar --":
        st.session_state.data = calcular_pkg(pd.DataFrame(fuente_plantillas[nombre_plantilla]), modo)
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Reset"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.data = pd.DataFrame(columns=columnas_tabla)
    st.rerun()

st.title(f"📊 {modo.upper()}")

# --- 5. FORMULARIOS DE AGREGAR ---
with st.expander(f"➕ Agregar nuevo SKU a {modo}", expanded=False):
    with st.form("form_nuevo_sku", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        f_nom = col1.text_input("Nombre del Producto").upper()
        if modo == "Price Ladder":
            f_fab = col2.selectbox("Fabricante", ["BARCEL", "SABRITAS", "OTROS", "PROPUESTA"])
            f_cat = col3.selectbox("Ocasión de Consumo", opciones_agru)
            col4, col5, col6 = st.columns(3)
            f_pre = col4.number_input("Precio ($)", min_value=0.0, step=0.5)
            f_gra = col5.number_input("Gramaje (g)", min_value=1.0, step=1.0)
            f_som = col6.number_input("SOM (%)", min_value=0.0, max_value=100.0, step=0.1)
            if st.form_submit_button("Añadir a Escalera"):
                nuevo = pd.DataFrame([{"Producto": f_nom, "Fabricante": f_fab, "Ocasión": f_cat, "Precio ($)": f_pre, "Gramaje (g)": f_gra, "SOM (%)": f_som}])
                st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
                st.session_state.data = calcular_pkg(st.session_state.data, modo)
                st.session_state.data.to_csv(DB_FILE, index=False)
                st.rerun()
        else:
            f_fam = col2.text_input("Familia").upper()
            f_can = col3.selectbox("Canal", opciones_agru)
            col4, col5 = st.columns(2)
            f_pre = col4.number_input("Precio ($)", min_value=0.0, step=0.5)
            f_gra = col5.number_input("Gramaje (g)", min_value=1.0, step=1.0)
            if st.form_submit_button("Añadir a Price Pack"):
                nuevo = pd.DataFrame([{"Producto": f_nom, "Familia": f_fam, "Canal": f_can, "Precio ($)": f_pre, "Gramaje (g)": f_gra}])
                st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
                st.session_state.data = calcular_pkg(st.session_state.data, modo)
                st.session_state.data.to_csv(DB_FILE, index=False)
                st.rerun()

# --- 6. EDITOR DE TABLA ---
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
if not edited_df.equals(st.session_state.data):
    st.session_state.data = calcular_pkg(edited_df, modo)
    st.session_state.data.to_csv(DB_FILE, index=False)
    st.rerun()

# --- 7. GRÁFICOS ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    
    if modo == "Price Ladder":
        # --- LÓGICA DE GRÁFICO LADDER (NUEVO FORMATO SOLICITADO) ---
        ord_oca = {cat: i+1 for i, cat in enumerate(opciones_agru)}
        df_p["O_Oca"] = df_p["Ocasión"].str.upper().map(ord_oca).fillna(99)
        df_p = df_p.sort_values(by=["O_Oca", "Precio ($)"]).reset_index(drop=True)
        som_por_ocasion = df_p.groupby("Ocasión")["SOM (%)"].sum().to_dict()

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.0, row_heights=[0.12, 0.88])

        # Trace SOM superior
        fig.add_trace(go.Scatter(
            x=df_p["Producto"], y=df_p["SOM (%)"], mode="lines+markers+text", 
            line=dict(color="#BBBBBB", width=1.5), 
            marker=dict(size=30, color="#E5E5E5", symbol="square", line=dict(color="#CCCCCC", width=1)), 
            text=[f"<b>{row['SOM (%)']}%</b>" for _, row in df_p.iterrows()],
            textposition="middle center", textfont=dict(size=13, color="black"),
        ), row=1, col=1)

        # Trace Barras Precio
        colors = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D", "PROPUESTA": "#4B207E"}
        fig.add_trace(go.Bar(
            x=df_p["Producto"], y=df_p["Precio ($)"],
            marker_color=[colors.get(str(f).upper(), "#999") for f in df_p["Fabricante"]],
            text=[f"<b>${int(p)}</b>" for p in df_p["Precio ($)"]], 
            textposition="outside", textfont=dict(size=18, color="black") 
        ), row=2, col=1)

        # Anotaciones $/Kg dentro de las barras
        for i, row in df_p.iterrows():
            fig.add_annotation(
                x=i, y=2.5, text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
                showarrow=False, font=dict(size=16, color="white" if row["Fabricante"] == "BARCEL" else "black"),
                bgcolor="rgba(70, 130, 180, 0.8)" if row["Fabricante"] == "BARCEL" else "rgba(255,255,255,0.8)",
                bordercolor="#444" if row["Fabricante"] != "BARCEL" else None, borderwidth=1, row=2, col=1
            )

        # Estética de líneas y divisiones por Ocasión
        for cat in df_p["Ocasión"].unique():
            idx_list = df_p.index[df_p["Ocasión"] == cat].tolist()
            center = (idx_list[0] + idx_list[-1]) / 2
            # Línea divisoria vertical
            fig.add_shape(type="line", x0=idx_list[-1] + 0.5, x1=idx_list[-1] + 0.5, y0=-0.01, y1=1, xref="x2", yref="paper", line=dict(color="#DDDDDD", width=1.5))
            # Texto de agrupación inferior
            fig.add_annotation(x=center, y=-0.50, xref="x2", yref="paper", text=f"<b>{cat}</b><br><span style='font-size:18px;'>{som_por_ocasion.get(cat, 0):.1f}%</span>", showarrow=False, font=dict(size=16, color="black"), align="center")

        # Recuadro exterior
        fig.add_shape(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1, line=dict(color="#DDDDDD", width=2))

        fig.update_layout(height=950, template="plotly_white", showlegend=False, margin=dict(t=50, b=350, l=40, r=40))
        fig.update_yaxes(showticklabels=False, row=1, col=1)
        fig.update_yaxes(showgrid=True, gridcolor="#DCDCDC", dtick=5, tickfont=dict(size=14), row=2, col=1)
        fig.update_xaxes(tickangle=-90, tickfont=dict(size=16, color="black"), row=2, col=1)
        
    else:
        # --- LÓGICA DE GRÁFICO PRICE PACK (Mantenido) ---
        ord_map = {cat.upper(): i for i, cat in enumerate(opciones_agru)}
        df_p["Orden_Agru"] = df_p[label_agru].str.upper().map(ord_map).fillna(99)
        df_p = df_p.sort_values(by=["Orden_Agru", "Precio ($)"], ascending=[True, True]).reset_index(drop=True)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_p.index, y=df_p["Precio por Kg ($)"], marker_color="#0B3C8C"))
        for i, r in df_p.iterrows():
            fig.add_annotation(x=i, y=r["Precio por Kg ($)"], text=f"<b>${r['Precio por Kg ($)']:,.0f}</b>", yshift=15, showarrow=False, font=dict(size=13), bgcolor="rgba(255,255,255,0.9)", bordercolor="black", borderwidth=1)
            fig.add_annotation(x=i, y=15, text=f"<b>${r['Precio ($)']:.1f}</b>", showarrow=False, font=dict(size=12), bgcolor="#E1F5FE", bordercolor="#BDBDBD", borderwidth=1, borderpad=4)
        
        for cat in df_p[label_agru].unique():
            indices = df_p.index[df_p[label_agru] == cat].tolist()
            if indices:
                center = (indices[0] + indices[-1]) / 2
                fig.add_shape(type="line", x0=indices[-1]+0.5, x1=indices[-1]+0.5, y0=0, y1=1, xref="x", yref="paper", line=dict(color="#DDD", width=2))
                fig.add_annotation(x=center, y=-0.4, xref="x", yref="paper", text=f"<b>{cat}</b>", showarrow=False, font=dict(size=14))
        
        fig.update_layout(height=750, margin=dict(b=250), template="plotly_white", xaxis=dict(tickmode='array', tickvals=list(df_p.index), ticktext=df_p["Producto"], tickangle=-90))

    st.plotly_chart(fig, use_container_width=True)

# --- 8. COMPARATIVAS INDEX ---
if not st.session_state.data.empty:
    st.divider()
    st.subheader(f"📈 Comparativas Index $/Kg ({modo})")
    df_comp = df_p.copy()
    if modo == "Price Ladder":
        list_a = df_comp[df_comp["Fabricante"]=="BARCEL"]["Producto"].unique().tolist()
        list_b = df_comp[df_comp["Fabricante"]!="BARCEL"]["Producto"].unique().tolist()
        label_a, label_b = "Barcel", "Comp."
    else:
        list_a = df_comp["Producto"].unique().tolist()
        list_b = df_comp["Producto"].unique().tolist()
        label_a, label_b = "Producto A", "Producto B"

    if len(list_a) > 0 and len(list_b) > 0:
        idx_cols = st.columns(4)
        for i in range(4):
            with idx_cols[i]:
                with st.container(border=True):
                    p_a = st.selectbox(f"{label_a}", list_a, key=f"sa{i}")
                    p_b = st.selectbox(f"{label_b}", list_b, key=f"sb{i}", index=min(i+1, len(list_b)-1))
                    val_a = df_comp[df_comp["Producto"]==p_a]["Precio por Kg ($)"].values[0]
                    val_b = df_comp[df_comp["Producto"]==p_b]["Precio por Kg ($)"].values[0]
                    if val_b > 0:
                        index_val = int((val_a / val_b) * 100)
                        color_index = "#0B3C8C" if index_val <= 100 else "#D32F2F"
                        st.markdown(f'<div style="text-align:center; padding:10px; border-top:5px solid {color_index}; background:#f8f9fa; border-radius:5px;"><div style="font-size:1.8rem; font-weight:900; color:{color_index};">{index_val}</div><div style="font-size:0.7rem;">INDEX $/KG</div></div>', unsafe_allow_html=True)

# --- 9. PIRÁMIDE DE POSICIONAMIENTO (SOLO LADDER) ---
if modo == "Price Ladder" and not st.session_state.data.empty:
    st.divider()
    st.subheader("🏔️ Pirámide de Posicionamiento por Tier")
    df_pyramid = procesar_datos_piramide(df_p)
    sel_ocasion = st.selectbox("Seleccionar Segmento para Pirámide:", df_pyramid["Ocasión"].unique())
    df_f = df_pyramid[df_pyramid["Ocasión"] == sel_ocasion].sort_values("Idx_P", ascending=False)
    
    tier_colors = {"PREMIUM": "#1A237E", "UPPER MAINSTREAM": "#0D47A1", "MAINSTREAM": "#0B3C8C", "MAINSTREAM LOW": "#1976D2", "VALUE": "#42A5F5"}

    for tier in ["PREMIUM", "UPPER MAINSTREAM", "MAINSTREAM", "MAINSTREAM LOW", "VALUE"]:
        productos_tier = df_f[df_f["Tier"] == tier]
        if not productos_tier.empty:
            c1, c2 = st.columns([1, 4])
            c1.markdown(f'<div style="background-color:{tier_colors[tier]}; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; height:100%; display:flex; align-items:center; justify-content:center;">{tier}</div>', unsafe_allow_html=True)
            cards_html = '<div style="display: flex; flex-wrap: wrap;">'
            for _, r in productos_tier.iterrows():
                b_color = "#4B207E" if r["Fabricante"] == "BARCEL" else "#CCCCCC"
                cards_html += f"""
                <div style="border: 2px solid {b_color}; border-radius: 10px; padding: 10px; background: white; width: 160px; margin: 5px; box-shadow: 1px 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-weight:bold; font-size:0.85rem; color:#333; height:35px; overflow:hidden;">{r['Producto']}</div>
                    <div style="color:#666; font-size:0.75rem;">Index: {int(r['Idx_P'])}</div>
                    <div style="font-weight:bold; font-size:0.95rem; color:#111; margin-top:4px;">${int(r['Precio ($)'])} ({int(r['Gramaje (g)'])}g)</div>
                </div>"""
            cards_html += '</div>'
            c2.markdown(cards_html, unsafe_allow_html=True)
