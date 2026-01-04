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
        {"Producto": "Mini Takis 35g", "Fabricante": "BARCEL", "Ocasión": "BITES", "Precio ($)": 10.0, "Gramaje (g)": 35, "SOM (%)": 0.7},
        {"Producto": "Doritos 41g", "Fabricante": "SABRITAS", "Ocasión": "BITES", "Precio ($)": 15.0, "Gramaje (g)": 41, "SOM (%)": 0.7},
        {"Producto": "Churrumais 70g", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 17.0, "Gramaje (g)": 70, "SOM (%)": 1.9},
        {"Producto": "Tostachos 75g", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 18.0, "Gramaje (g)": 75, "SOM (%)": 0.7},
        {"Producto": "Runners 72g", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 18.0, "Gramaje (g)": 72, "SOM (%)": 4.7},
        {"Producto": "Fritos 70g", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 18.0, "Gramaje (g)": 70, "SOM (%)": 8.1},
        {"Producto": "Chipotles 65g", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 18.0, "Gramaje (g)": 65, "SOM (%)": 1.4},
        {"Producto": "Rancheritos 58g", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 18.0, "Gramaje (g)": 58, "SOM (%)": 3.9},
        {"Producto": "Takis 70g", "Fabricante": "BARCEL", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 70, "SOM (%)": 13.8},
        {"Producto": "Doritos Dinamita 70g", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 70, "SOM (%)": 9.0},
        {"Producto": "Tostitos 62g", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 62, "SOM (%)": 6.7},
        {"Producto": "Doritos 58g", "Fabricante": "SABRITAS", "Ocasión": "INDIVIDUAL", "Precio ($)": 20.0, "Gramaje (g)": 58, "SOM (%)": 22.4},
        {"Producto": "Doritos Dinamita 120g", "Fabricante": "SABRITAS", "Ocasión": "HAMBRE", "Precio ($)": 25.0, "Gramaje (g)": 120, "SOM (%)": 0.6},
        {"Producto": "Tostitos 110g", "Fabricante": "SABRITAS", "Ocasión": "HAMBRE", "Precio ($)": 25.0, "Gramaje (g)": 110, "SOM (%)": 0.0},
        {"Producto": "Doritos 100g", "Fabricante": "SABRITAS", "Ocasión": "HAMBRE", "Precio ($)": 25.0, "Gramaje (g)": 100, "SOM (%)": 3.6},
        {"Producto": "Doritos Nacho 146g", "Fabricante": "SABRITAS", "Ocasión": "COMPARTIR", "Precio ($)": 40.0, "Gramaje (g)": 146, "SOM (%)": 0.9},
        {"Producto": "Rancheritos 145g", "Fabricante": "SABRITAS", "Ocasión": "COMPARTIR", "Precio ($)": 40.0, "Gramaje (g)": 145, "SOM (%)": 0.2},
        {"Producto": "Runners 200g", "Fabricante": "BARCEL", "Ocasión": "FAMILIAR", "Precio ($)": 40.0, "Gramaje (g)": 200, "SOM (%)": 0.0},
        {"Producto": "Churrumais 185g", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 40.0, "Gramaje (g)": 185, "SOM (%)": 0.1},
        {"Producto": "Tostitos 175g", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 40.0, "Gramaje (g)": 175, "SOM (%)": 0.7},
        {"Producto": "Fritos 170g", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 40.0, "Gramaje (g)": 170, "SOM (%)": 0.1},
        {"Producto": "Takis 200g", "Fabricante": "BARCEL", "Ocasión": "FAMILIAR", "Precio ($)": 45.0, "Gramaje (g)": 200, "SOM (%)": 0.2},
        {"Producto": "Doritos 245g", "Fabricante": "SABRITAS", "Ocasión": "FAMILIAR", "Precio ($)": 56.0, "Gramaje (g)": 245, "SOM (%)": 0.3}
   ]
}

def calcular_pkg(df):
    df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
    df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1).replace(0, 1)
    df["SOM (%)"] = pd.to_numeric(df["SOM (%)"], errors='coerce').fillna(0)
    df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(0)
    return df

# --- FUNCIÓN PIRÁMIDE (CORREGIDA PARA NO OMITIR SKUS) ---
def calcular_piramide_dinamica(df):
    if df.empty: return df
    df_temp = df.copy()
    
    # 1. Identificar el precio base por ocasión (el de mayor SOM)
    def get_base_price(group):
        if group["SOM (%)"].max() > 0:
            return group.loc[group["SOM (%)"].idxmax(), "Precio por Kg ($)"]
        return group["Precio por Kg ($)"].mean() # Fallback si no hay SOM

    precios_base = df_temp.groupby("Ocasión").apply(get_base_price).reset_index()
    precios_base.columns = ["Ocasión", "Precio_Base_100"]
    
    df_temp = df_temp.merge(precios_base, on="Ocasión", how="left")
    df_temp["Brand_Index"] = (df_temp["Precio por Kg ($)"] / df_temp["Precio_Base_100"] * 100).round(0)

    def asignar_tier(idx):
        if idx >= 170: return "PREMIUM"
        elif 120 <= idx < 170: return "UPPER MAINSTREAM"
        elif 95 <= idx < 120: return "MAINSTREAM"
        elif 80 <= idx < 95: return "MAINSTREAM LOW"
        else: return "VALUE"
    
    df_temp["Tier"] = df_temp["Brand_Index"].apply(asignar_tier)
    orden_tiers = {"PREMIUM": 1, "UPPER MAINSTREAM": 2, "MAINSTREAM": 3, "MAINSTREAM LOW": 4, "VALUE": 5}
    df_temp["Tier_Order"] = df_temp["Tier"].map(orden_tiers)
    return df_temp

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

# --- 4. FORMULARIO ---
with st.expander("➕ Agregar nuevo producto manualmente", expanded=False):
    with st.form("nuevo_sku_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        f_nom = c1.text_input("Nombre del Producto").upper()
        f_fab = c2.selectbox("Fabricante", ["BARCEL", "SABRITAS", "OTROS","PROPUESTA"])
        f_oca = c3.selectbox("Ocasión", ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR","REUNIÓN", "FIESTA","TRANSFORMADOR"])
        c4, c5, c6 = st.columns(3)
        f_pre = c4.number_input("Precio ($)", min_value=0.0, step=0.5)
        f_gra = c5.number_input("Gramaje (g)", min_value=1.0, step=1.0)
        f_som = c6.number_input("SOM (%)", min_value=0.0, max_value=100.0, step=0.1)
        if st.form_submit_button("Añadir a la lista"):
            nuevo_sku = pd.DataFrame([{"Producto": f_nom, "Fabricante": f_fab, "Ocasión": f_oca, "Precio ($)": f_pre, "Gramaje (g)": f_gra, "SOM (%)": f_som}])
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

# --- 6. GRÁFICO FINAL (TU CÓDIGO ORIGINAL ÍNTEGRO) ---
if not st.session_state.data.empty:
    ord_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5,"REUNIÓN":6, "FIESTA":7,"TRANSFORMADOR":8}
    df_p = st.session_state.data.copy()
    df_p["O_Oca"] = df_p["Ocasión"].str.upper().map(ord_oca).fillna(99)
    df_p = df_p.sort_values(by=["O_Oca", "Precio ($)"]).reset_index(drop=True)
    som_por_ocasion = df_p.groupby("Ocasión")["SOM (%)"].sum().to_dict()

    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.0, 
        row_heights=[0.12, 0.88]
    )

    # SOM (Cuadro gris)
    fig.add_trace(go.Scatter(
        x=df_p["Producto"], y=df_p["SOM (%)"], mode="lines+markers+text", 
        line=dict(color="#BBBBBB", width=1.5), 
        marker=dict(size=30, color="#E5E5E5", symbol="square", line=dict(color="#CCCCCC", width=1)), 
        text=[f"<b>{row['SOM (%)']}%</b>" for _, row in df_p.iterrows()],
        textposition="middle center", textfont=dict(size=13, color="black"),
    ), row=1, col=1)

    # BARRAS
    colors = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D","PROPUESTA":"#4B207E"}
    fig.add_trace(go.Bar(
        x=df_p["Producto"], y=df_p["Precio ($)"],
        marker_color=[colors.get(str(f).upper(), "#999") for f in df_p["Fabricante"]],
        text=[f"<b>${int(p)}</b>" for p in df_p["Precio ($)"]], 
        textposition="outside", textfont=dict(size=18, color="black") 
    ), row=2, col=1)

    # $/KG Anotaciones
    for i, row in df_p.iterrows():
        fig.add_annotation(
            x=i, y=2.5, text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
            showarrow=False, font=dict(size=16, color="white" if row["Fabricante"] == "BARCEL" else "black"),
            bgcolor="rgba(70, 130, 180, 0.8)" if row["Fabricante"] == "BARCEL" else "rgba(255,255,255,0.8)",
            bordercolor="#444" if row["Fabricante"] != "BARCEL" else None, borderwidth=1,
            row=2, col=1
        )

    # Divisiones verticales cortas
    for i in range(len(df_p) + 1):
        fig.add_shape(type="line", x0=i-0.5, x1=i-0.5, y0=-0.01, y1=-0.50, xref="x2", yref="paper", line=dict(color="#DDDDDD", width=1))

    # Divisiones largas por ocasión
    fig.add_shape(type="line", x0=-0.5, x1=-0.5, y0=-0.01, y1=1, xref="x2", yref="paper", line=dict(color="#DDDDDD", width=1.5))
    for cat in df_p["Ocasión"].unique():
        idx_list = df_p.index[df_p["Ocasión"] == cat].tolist()
        center = (idx_list[0] + idx_list[-1]) / 2
        fig.add_shape(type="line", x0=idx_list[-1] + 0.5, x1=idx_list[-1] + 0.5, y0=-0.01, y1=1, xref="x2", yref="paper", line=dict(color="#DDDDDD", width=1.5))
        fig.add_annotation(x=center, y=-0.60, xref="x2", yref="paper", text=f"{cat}<br><span style='font-size:18px;'>{som_por_ocasion[cat]:.1f}%</span>", showarrow=False, font=dict(size=16, color="black"), align="center")

    # Marco Gris
    fig.add_shape(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1, line=dict(color="#DDDDDD", width=2))

    fig.update_layout(height=950, width=1950, template="plotly_white", showlegend=False, margin=dict(t=50, b=400, l=40, r=40))
    fig.update_yaxes(showticklabels=False, showline=False, zeroline=False, row=1, col=1)
    fig.update_yaxes(showgrid=True, gridcolor="#DCDCDC", dtick=5, tickprefix="$", tickfont=dict(size=14, color="black"), automargin=False, row=2, col=1)
    fig.update_xaxes(tickangle=-90, tickfont=dict(size=16, color="black"), row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)

# --- 7. COMPARATIVAS (TU CÓDIGO ORIGINAL ÍNTEGRO) ---
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
                st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 15px 10px; border-radius: 10px; border-top: 5px solid {color_index}; text-align: center; margin: 10px auto; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                        <div style="font-size: 1.1rem; font-weight: bold; color: #333; margin-bottom: 8px; line-height: 1.2;"> {p_b} <br> <span style="color: #888; font-size: 0.9rem;">vs</span> <br> {p_c} </div>
                        <div style="font-size: 2.2rem; font-weight: 900; color: {color_index};"> {index_val} </div>
                    </div>
                """, unsafe_allow_html=True)

# --- 8. PIRÁMIDE DE MARCA (RECONSTRUIDA PARA SER COMPLETA) ---
st.divider()
st.subheader("🏔️ Pirámide de Posicionamiento por Tier")

if not st.session_state.data.empty:
    df_pira = calcular_piramide_dinamica(st.session_state.data)
    filtro_oca = st.selectbox("Seleccionar Segmento para Pirámide:", df_pira["Ocasión"].unique())
    df_filtered = df_pira[df_pira["Ocasión"] == filtro_oca].sort_values("Brand_Index", ascending=False)

    tier_colors = {"PREMIUM": "#1A237E", "UPPER MAINSTREAM": "#0D47A1", "MAINSTREAM": "#0B3C8C", "MAINSTREAM LOW": "#1976D2", "VALUE": "#42A5F5"}

    for tier in ["PREMIUM", "UPPER MAINSTREAM", "MAINSTREAM", "MAINSTREAM LOW", "VALUE"]:
        prods = df_filtered[df_filtered["Tier"] == tier]
        if not prods.empty:
            c1, c2 = st.columns([1, 4])
            c1.markdown(f'<div style="background-color:{tier_colors[tier]}; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; min-height:80px; display:flex; align-items:center; justify-content:center;">{tier}</div>', unsafe_allow_html=True)
            
            cards_html = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
            for _, r in prods.iterrows():
                b_color = "#4B207E" if r["Fabricante"] == "BARCEL" else "#CCCCCC"
                cards_html += f"""
                    <div style="border: 2px solid {b_color}; border-radius: 10px; padding: 10px; background: white; min-width: 170px; flex: 1 1 170px; box-shadow: 1px 1px 3px rgba(0,0,0,0.1);">
                        <div style="font-size: 0.9rem; font-weight: bold; color: #333; height: 35px; overflow: hidden;">{r['Producto']}</div>
                        <div style="color: #666; font-size: 0.8rem; margin-top:5px;">Index: <b>{int(r['Brand_Index'])}</b></div>
                        <div style="font-size: 1.1rem; font-weight: 800; color: #111;">${int(r['Precio ($)'])} <span style="font-size:0.7rem; font-weight:400;">({int(r['Gramaje (g)'])}g)</span></div>
                    </div>
                """
            cards_html += '</div>'
            c2.markdown(cards_html, unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
