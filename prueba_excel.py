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

if "data" not in st.session_state:
    if os.path.exists(DB_FILE):
        st.session_state.data = calcular_pkg(pd.read_csv(DB_FILE))
    else:
        st.session_state.data = pd.DataFrame(columns=["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "Precio por Kg ($)", "SOM (%)"])

df_p = st.session_state.data.copy()

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
        f_fab = c2.selectbox("Fabricante", ["BARCEL", "SABRITAS", "OTROS"])
        f_oca = c3.selectbox("Ocasión", ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"])
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
   
# --- 6. GRÁFICO ACTUALIZADO CON LÍNEAS CADA $5 ---
if not st.session_state.data.empty:
    ord_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5}
    df_p = st.session_state.data.copy()
    df_p["O_Oca"] = df_p["Ocasión"].str.upper().map(ord_oca).fillna(99)
    df_p = df_p.sort_values(by=["O_Oca", "Precio ($)"]).reset_index(drop=True)
    som_por_ocasion = df_p.groupby("Ocasión")["SOM (%)"].sum().to_dict()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.12, 0.88])

    # SOM (Líneas tenues)
    fig.add_trace(go.Scatter(
        x=df_p["Producto"], y=df_p["SOM (%)"], 
        mode="lines+markers", line=dict(color="#CCCCCC", width=1.5), 
        marker=dict(size=5, color="#AAAAAA")
    ), row=1, col=1)

    # Etiquetas SOM (Negras con fondo gris)
    for i, row in df_p.iterrows():
        fig.add_annotation(
            x=i, y=row["SOM (%)"], text=f"<b>{row['SOM (%)']}%</b>", 
            showarrow=False, yshift=15, 
            font=dict(size=13, color="black"), 
            bgcolor="#E5E5E5", bordercolor="#CCCCCC", borderwidth=1, borderpad=4,
            row=1, col=1
        )

    # Barras de Precio (Desembolso)
    colors = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D"}
    fig.add_trace(go.Bar(
        x=df_p["Producto"], 
        y=df_p["Precio ($)"],
        marker_color=[colors.get(str(f).upper(), "#999") for f in df_p["Fabricante"]],
        text=[f"<b>${int(p)}</b>" for p in df_p["Precio ($)"]], 
        textposition="outside",
        textfont=dict(size=18, color="black") 
    ), row=2, col=1)

    # $/Kg (Azul acero para Barcel)
    for i, row in df_p.iterrows():
        fig.add_annotation(
            x=i, y=2.5, 
            text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
            showarrow=False, font=dict(size=16, color="white" if row["Fabricante"] == "BARCEL" else "black"),
            bgcolor="rgba(70, 130, 180, 0.8)" if row["Fabricante"] == "BARCEL" else "rgba(255,255,255,0.8)",
            bordercolor="#444" if row["Fabricante"] != "BARCEL" else None, borderwidth=1,
            row=2, col=1
        )

    # Divisiones verticales entre productos (Tenues)
    for i in range(len(df_p) + 1):
        fig.add_shape(
            type="line", x0=i-0.5, x1=i-0.5, y0=-0.01, y1=-0.50,
            xref="x2", yref="paper",
            line=dict(color="#DDDDDD", width=1) 
        )

    # Ocasiones (Ajustadas un poco más abajo)
    for cat in df_p["Ocasión"].unique():
        idx_list = df_p.index[df_p["Ocasión"] == cat].tolist()
        center = (idx_list[0] + idx_list[-1]) / 2
        
        fig.add_vline(x=idx_list[-1] + 0.5, line_color="#DDDDDD", line_width=1.5, row=2, col=1)
        
        fig.add_annotation(
            x=center, y=-0.60, 
            xref="x2", yref="paper",
            text=f"{cat}<br><span style='font-size:18px;'>{som_por_ocasion[cat]:.1f}%</span>",
            showarrow=False, font=dict(size=16, color="black"), align="center"
        )

    # Layout y Ejes (Líneas cada $5)
    fig.update_layout(
        height=1100, width=1950,
        template="plotly_white", showlegend=False, 
        margin=dict(t=50, b=550, l=100, r=80) 
    )

    fig.update_yaxes(
        showgrid=True, 
        gridcolor="#F0F0F0", 
        dtick=5,             
        tickprefix="$",      
        tickfont=dict(size=16, color="black"),
        row=2, col=1
    )

    fig.update_xaxes(tickangle=-90, tickfont=dict(size=16, color="black"), row=2, col=1)
    fig.update_yaxes(showgrid=False, showticklabels=False, row=1, col=1)

    st.plotly_chart(fig, use_container_width=True)


# --- 7. COMPARATIVAS ---
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
                    <div style="
                        background-color: #f8f9fa; 
                        padding: 15px 10px; 
                        border-radius: 10px; 
                        border-top: 5px solid {color_index}; 
                        text-align: center;
                        max-width: 200px; 
                        margin: 10px auto;
                        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
                    ">
                        <div style="
                            font-size: 0.9rem; 
                            font-weight: bold; 
                            color: #333; 
                            margin-bottom: 8px;
                            line-height: 1.2;
                        ">
                            {p_b} <br> <span style="color: #888; font-size: 0.7rem;">vs</span> <br> {p_c}
                        </div>
                        <div style="
                            font-size: 2.2rem; 
                            font-weight: 900; 
                            color: {color_index};
                        ">
                            {index_val}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
