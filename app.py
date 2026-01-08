import streamlit as st
import pandas as pd
import base64  # <--- ESTA ES LA LÍNEA QUE FALTA
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import io

# --- 1. CONFIGURACIÓN Y CARGA DE PLANTILLAS ---
try:
    from plantillas import PLANTILLAS 
except ImportError:
    PLANTILLAS = {}

try:
    from price_pack import PLANTILLAS_PP
except ImportError:
    PLANTILLAS_PP = {}

st.set_page_config(page_title="Price Ladder & Architecture Expert Pro", layout="wide")

# 2. AQUÍ PEGAS LA FUNCIÓN Y EL BLOQUE DEL LOGO
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    # Asegúrate de que 'logo_barcel.png' esté en tu carpeta del repositorio
    bin_str = get_base64_of_bin_file('logo_barcel.png')
    st.markdown(
        f"""
        <style>
            [data-testid="stHeader"] {{
                background-color: rgba(0,0,0,0);
            }}
            .logo-container {{
                position: fixed;
                top: 10px;
                right: 20px;
                z-index: 999999;
            }}
        </style>
        <div class="logo-container">
            <img src="data:image/png;base64,{bin_str}" width="100">
        </div>
        """,
        unsafe_allow_html=True
    )
except FileNotFoundError:
    pass # Si no encuentra el logo, la app sigue corriendo normal

# --- SWITCH DE MODO OSCURO ---
with st.sidebar:
    st.divider()
    modo_oscuro = st.toggle("🌙 Activar Modo Oscuro", value=False)

if modo_oscuro:
    # Inyectamos CSS para forzar colores oscuros en toda la interfaz
    st.markdown(
        """
        <style>
            /* Fondo principal y sidebar */
            .stApp, [data-testid="stSidebar"] {
                background-color: #0E1117 !important;
                color: #FAFAFA !important;
            }
            /* Títulos y textos */
            h1, h2, h3, p, span {
                color: #FAFAFA !important;
            }
            /* Ajuste para que las tarjetas de Index no se pierdan */
            div[style*="background:#f8f9fa"] {
                background-color: #1E1E1E !important;
                border: 1px solid #333 !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

@st.dialog("📖 Glosario de Metodologías Estratégicas")
def mostrar_glosario():
    st.markdown("### 🔍 Conceptos Clave de Pricing")
    st.write("Esta sección detalla la metodología técnica utilizada para el análisis de Pricing en Barcel.")
    
    st.divider()

    # --- SECCIÓN: PRICE LADDER ---
    st.info("#### **1. Price Ladder (Escalera de Precios)**")
    st.markdown("""
    Es una herramienta estratégica de **mapeo competitivo** que genera una "fotografía" de los productos de la categoría en un canal y segmento específico. 
    Permite analizar la jerarquía de valor basada en el **Precio Desembolsado, Gramaje y Precio por Kilo ($/Kg).**
    
    **El rol del SOM (Share of Market):** El SOM es el indicador de relevancia crítica dentro de la escalera. Al visualizar el peso de cada producto, identificamos qué 'escalones' de precio dominan la preferencia del consumidor. Esto permite **jerarquizar las ocasiones de consumo** y priorizar aquellos 'gaps' de mercado donde existe una mayor concentración de volumen en el mercado, asegurando que participemos en las ocasiones de consumo y bandas de desembolso con mayor fuerza competitiva y oportunidad real de captura de share.
    """)
    
    st.divider()

    # --- SECCIÓN: PRICE ARCHITECTURE ---
    st.success("#### **2. Price Architecture (Arquitectura de Precios)**")
    st.markdown("""
    Es el análisis integral que nos permite gestionar estratégicamente nuestro portafolio a través de todos los canales de venta. Su objetivo es optimizar la relación entre el gramaje y el precio para maximizar la rentabilidad y la cobertura de mercado.
    
    **Impacto Interno y Estratégico:**
    * **Gestión de Portafolio:** Permite visualizar cómo se despliega una marca a lo largo de los distintos canales, asegurando que existan opciones lógicas para el consumidor en cada punto de contacto.
    * **Curvas de Precio:** Facilita el análisis de las curvas de valor para identificar desviaciones y asegurar una transición suave entre diferentes tamaños (gramajes) y desembolsos.
    * **Benchmarking Inter-Canal:** Mediante la comparación de los **Index por Kilo ($/Kg)**, podemos evaluar cómo "jugamos" en cada canal, garantizando que nuestra competitividad sea consistente y evitando la canibalización interna entre canales de venta.
    """)

    st.divider()

    # --- SECCIÓN: PRECIO POR KILO E INDEX ---
    st.warning("#### **3. Precio por Kilo ($/Kg) e Index**")
    st.markdown("""    
    **¿Qué es el Index $/Kg?**
    Es una métrica de paridad que mide la distancia porcentual (en precio x kg) entre dos productos:
    * **Index 100:** Indica paridad absoluta de precio por kilo entre los productos comparados.
    * **Index > 100:** Indica que nuestro producto es más caro por kilo (ej. un Index de 115 significa que somos 15% más caros).
    * **Index < 100:** Indica que nuestro producto ofrece un precio por kilo más competitivo que la referencia.
    
    Esta métrica es vital para definir si nuestra estrategia de precio está alineada con el posicionamiento de marca (Premium vs. Value) frente a la competencia.
    """)

    if st.button("Entendido", use_container_width=True):
        st.rerun()

# NAVEGACIÓN
st.sidebar.header("🚀 Modo de Visualización")
modo = st.sidebar.radio("Seleccionar Herramienta:", ["Price Ladder", "Price Pack"])

# Botón limpio para el Glosario
if st.sidebar.button("❓ Ver Glosario Técnico", use_container_width=True):
    mostrar_glosario()
    
# LÓGICA DE MODOS

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
    """Calcula los Tiers basados en un Producto Referencia (Index 100 = Mayor SOM de la Ocasión)"""
    if df.empty: return df
    
    df_py = df.copy()
    # Identificamos el producto con mayor SOM por cada Ocasión para que sea el Index 100
    idx_referencia = df_py.groupby("Ocasión")["SOM (%)"].idxmax()
    df_ref = df_py.loc[idx_referencia, ["Ocasión", "Precio por Kg ($)"]]
    df_ref = df_ref.rename(columns={"Precio por Kg ($)": "Precio_Ref"})
    
    # Unimos para tener el precio de referencia en cada fila
    df_py = df_py.merge(df_ref, on="Ocasión", how="left")
    
    # Calculamos el Index real comparado contra el líder (Mainstream)
    df_py["Idx_P"] = (df_py["Precio por Kg ($)"] / df_py["Precio_Ref"]) * 100
    
    def definir_tier(idx):
        if idx >= 115: return "PREMIUM"
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

# --- 4. BARRA LATERAL (CONTINUACIÓN: EXPORTACIÓN) ---
def to_excel(df):
    output = io.BytesIO()
    # Usamos openpyxl como engine para evitar errores de dependencias
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Analisis_Portafolio')
    return output.getvalue()

if not st.session_state.data.empty:
    st.sidebar.divider()
    st.sidebar.subheader("📥 Exportar Catálogo")
    excel_data = to_excel(st.session_state.data)
    st.sidebar.download_button(
        label="📄 Descargar Excel Completo",
        data=excel_data,
        file_name=f'barcel_{modo.lower()}_data.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        use_container_width=True
    )

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

# --- 7. GRÁFICO FINAL ---
if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    
    if modo == "Price Ladder":
        ord_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5,"REUNIÓN":6, "FIESTA":7,"TRANSFORMADOR":8}
        df_p["O_Oca"] = df_p["Ocasión"].str.upper().map(ord_oca).fillna(99)
        df_p = df_p.sort_values(by=["O_Oca", "Precio ($)"]).reset_index(drop=True)
        som_por_ocasion = df_p.groupby("Ocasión")["SOM (%)"].sum().to_dict()

        # Mantenemos el alto para que no se vea "chaparro"
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.15, 0.85])

        # --- TRACE 1: SOM% ---
        fig.add_trace(go.Scatter(
            x=df_p["Producto"], y=df_p["SOM (%)"], mode="lines+markers+text", 
            line=dict(color="#BBBBBB", width=1.5), 
            marker=dict(size=30, color="#E5E5E5", symbol="square", line=dict(color="#CCCCCC", width=1)), 
            text=[f"<b>{row['SOM (%)']}%</b>" for _, row in df_p.iterrows()],
            textposition="middle center", textfont=dict(size=13, color="black"),
        ), row=1, col=1)

        # --- TRACE 2: BARRAS DE PRECIO ---
        colors = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D","PROPUESTA":"#4B207E"}
        fig.add_trace(go.Bar(
            x=df_p["Producto"], y=df_p["Precio ($)"],
            marker_color=[colors.get(str(f).upper(), "#999") for f in df_p["Fabricante"]],
            text=[f"<b>${int(p)}</b>" for p in df_p["Precio ($)"]], 
            textposition="outside", textfont=dict(size=18, color="black") 
        ), row=2, col=1)

        # Anotaciones de Precio por Kg dentro de las barras
        for i, row in df_p.iterrows():
            fig.add_annotation(
                x=i, y=2.5, text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
                showarrow=False, font=dict(size=16, color="white" if row["Fabricante"] == "BARCEL" else "black"),
                bgcolor="rgba(70, 130, 180, 0.8)" if row["Fabricante"] == "BARCEL" else "rgba(255,255,255,0.8)",
                bordercolor="#444" if row["Fabricante"] != "BARCEL" else None, borderwidth=1, row=2, col=1
            )

        # --- LÍNEAS DIVISORIAS ---
        # 1. Líneas cortas para separar NOMBRES de productos (Solo abajo)
        for i in range(len(df_p) + 1):
            fig.add_shape(type="line", x0=i-0.5, x1=i-0.5, y0=-0.01, y1=-0.50, xref="x2", yref="paper", line=dict(color="#DDDDDD", width=1))

        # 2. Líneas largas para separar OCASIONES (Cruzan todo el gráfico)
        for cat in df_p["Ocasión"].unique():
            idx_list = df_p.index[df_p["Ocasión"] == cat].tolist()
            
            # Línea divisoria al final de cada categoría (y0=-0.6 para que baje hasta el texto del canal)
            fig.add_shape(
                type="line", x0=idx_list[-1] + 0.5, x1=idx_list[-1] + 0.5, 
                y0=-0.60, y1=1, xref="x2", yref="paper", 
                line=dict(color="#CCCCCC", width=2)
            )
            
            # Texto de la Ocasión y SOM%
            center = (idx_list[0] + idx_list[-1]) / 2
            fig.add_annotation(
                x=center, y=-0.60, xref="x2", yref="paper", 
                text=f"<b>{cat}</b><br><span style='font-size:18px;'>{som_por_ocasion[cat]:.1f}%</span>", 
                showarrow=False, font=dict(size=16, color="black"), align="center"
            )

        # Ajustes finales de Layout
        fig.update_layout(
            height=950, width=1950, template="plotly_white", showlegend=False, 
            margin=dict(t=50, b=400, l=40, r=40)
        )
        
        # Restaurar visibilidad del eje X inferior (Nombres de productos en negro y 90°)
        fig.update_xaxes(
            tickangle=-90, 
            tickfont=dict(size=16, color="black"), 
            showline=False, 
            row=2, col=1
        )
        
        # Ocultar ejes innecesarios
        fig.update_yaxes(showticklabels=False, row=1, col=1)
        fig.update_yaxes(showgrid=True, gridcolor="#DCDCDC", tickprefix="$", tickfont=dict(size=14), row=2, col=1)
    else:
        # 1. Ordenamiento por Canal y Desembolso
        ord_can = {"INSTITUCIONALES": 1, "MAYOREO": 2, "CLUBES": 3, "DETALLE": 4, "AUTOSERVICIO": 5, "CONVENIENCIA": 6}
        df_p["O_Can"] = df_p["Canal"].str.upper().map(ord_can).fillna(99)
        df_p = df_p.sort_values(by=["O_Can", "Precio ($)"]).reset_index(drop=True)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_p.index, y=df_p["Precio por Kg ($)"], marker_color="#0B3C8C"))
        
        # 2. LÍNEAS DIVISORIAS ENTRE NOMBRES (ABAJO)
        # Dibujamos líneas tenues para separar visualmente los nombres de los productos
        for i in range(len(df_p) + 1):

            fig.add_shape(

                type="line", x0=i-0.5, x1=i-0.5, 

                y0=-0.45, y1=0, # Ajustado para que bajen a la zona de los nombres

                xref="x", yref="paper",

                line=dict(color="#DDDDDD", width=1)

            ) 

        # 3. Etiquetas de datos sobre las barras y desembolso en la base
        for i, r in df_p.iterrows():
            fig.add_annotation(x=i, y=r["Precio por Kg ($)"], text=f"<b>${r['Precio por Kg ($)']:,.0f}</b>", yshift=15, showarrow=False, font=dict(size=13), bgcolor="rgba(255,255,255,0.9)", bordercolor="black", borderwidth=1)
            fig.add_annotation(x=i, y=15, text=f"<b>${r['Precio ($)']:.1f}</b>", showarrow=False, font=dict(size=12), bgcolor="#E1F5FE", bordercolor="#BDBDBD", borderwidth=1, borderpad=4)
        
        # 4. Divisiones de Canales y Etiquetas de Canal
        for cat in df_p["Canal"].unique():
            indices = df_p.index[df_p["Canal"] == cat].tolist()
            center = (indices[0] + indices[-1]) / 2
            
            # LÍNEA QUE SEPARA LOS CANALES
            fig.add_shape(
                type="line", x0=indices[-1]+0.5, x1=indices[-1]+0.5, 
                y0=-0.6, y1=1, xref="x", yref="paper", 
                # CAMBIOS: 
                # Color #CCCCCC es un gris claro pero visible.
                # Width 1.5 para que no sea tan tosca.
                line=dict(color="#CCCCCC", width=1.5) 
            )
            
            # Etiqueta de Canal
            fig.add_annotation(
                x=center, y=-0.6, xref="x", yref="paper", 
                text=f"<b>{cat}</b>", showarrow=False, 
                font=dict(size=14, color="black")
            )
        
        # 5. Configuración del Layout
        fig.update_layout(
            height=850, 
            margin=dict(b=300, t=50, l=50, r=50), 
            template="plotly_white", 
            xaxis=dict(
                tickmode='array', 
                tickvals=list(df_p.index), 
                ticktext=df_p["Producto"], 
                tickangle=-90,
                tickfont=dict(color="black", size=12, family="Arial Black"),
                showgrid=False
            )
        )

    st.plotly_chart(fig, use_container_width=True)
# --- 8. COMPARATIVAS INDEX ---
if not st.session_state.data.empty:
    st.divider()
    st.subheader(f"📈 Comparativas Index $/Kg ({modo})")
    df_comp = df_p.copy()
    
    if modo == "Price Ladder":
        df_comp["Lookup_Key"] = df_comp["Producto"]
        list_a = df_comp[df_comp["Fabricante"]=="BARCEL"]["Lookup_Key"].unique().tolist()
        list_b = df_comp[df_comp["Fabricante"]!="BARCEL"]["Lookup_Key"].unique().tolist()
        label_a, label_b = "Barcel", "Comp."
    else:
        df_comp["Lookup_Key"] = df_comp["Producto"] + " (" + df_comp["Canal"] + ")"
        list_a = df_comp["Lookup_Key"].unique().tolist()
        list_b = list_a.copy()
        label_a, label_b = "Producto A", "Producto B"

    if len(list_a) > 0 and len(list_b) > 0:
        idx_cols = st.columns(4)
        for i in range(4):
            with idx_cols[i]:
                with st.container(border=True):
                    sel_a = st.selectbox(f"{label_a}", list_a, key=f"sa{i}")
                    sel_b = st.selectbox(f"{label_b}", list_b, key=f"sb{i}", index=min(i+1, len(list_b)-1))
                    
                    val_a = df_comp[df_comp["Lookup_Key"] == sel_a]["Precio por Kg ($)"].values[0]
                    val_b = df_comp[df_comp["Lookup_Key"] == sel_b]["Precio por Kg ($)"].values[0]
                    
                    if val_b > 0:
                        index_val = int((val_a / val_b) * 100)
                        color_index = "#0B3C8C" if index_val <= 100 else "#D32F2F"
                        
                        st.markdown(f"""
                            <div style="background:#ffffff; border: 1px solid #e6e9ef; border-radius:10px; padding:15px; border-top:5px solid {color_index};">
                                <div style="display:flex; justify-content:space-between; align-items: flex-start; min-height:60px;">
                                    <div style="width:45%; text-align:left;">
                                        <div style="font-size:0.85rem; color:#666; font-weight:500; line-height:1.1; margin-bottom:4px;">{sel_a}</div>
                                        <div style="font-size:1.05rem; font-weight:800; color:#111;">${val_a:.1f}</div>
                                    </div>
                                    <div style="width:10%; text-align:center; padding-top:15px; font-weight:bold; color:#ccc; font-size:0.8rem;">vs</div>
                                    <div style="width:45%; text-align:right;">
                                        <div style="font-size:0.85rem; color:#666; font-weight:500; line-height:1.1; margin-bottom:4px;">{sel_b}</div>
                                        <div style="font-size:1.05rem; font-weight:800; color:#111;">${val_b:.1f}</div>
                                    </div>
                                </div>
                                <div style="text-align:center; margin-top:10px; padding-top:10px; border-top:1px solid #f0f2f6;">
                                    <div style="font-size:2.2rem; font-weight:900; color:{color_index}; line-height:1; margin-bottom:2px;">{index_val}</div>
                                    <div style="font-size:0.7rem; font-weight:bold; letter-spacing:1px; color:#999; text-transform:uppercase;">Index $/Kg</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
# --- 9. PIRÁMIDE DE POSICIONAMIENTO (SOLO LADDER) ---
# Movimos el título y la lógica dentro del condicional para que no aparezca en Price Pack
if modo == "Price Ladder" and not st.session_state.data.empty:
    st.divider()
    st.subheader("🏔️ Pirámide de Posicionamiento por Tier de $ x KG")
    
    # Usamos la función procesar_datos_piramide que fija el Index 100 en el mayor SOM
    df_pyramid = procesar_datos_piramide(st.session_state.data)
    
    # Selector de ocasión
    sel_ocasion = st.selectbox("Seleccionar Segmento para Pirámide:", df_pyramid["Ocasión"].unique())
    
    # Filtrar por ocasión y ordenar por Index de mayor a menor
    df_f = df_pyramid[df_pyramid["Ocasión"] == sel_ocasion].sort_values("Idx_P", ascending=False)
    
    tier_colors = {
        "PREMIUM": "#1A237E", 
        "UPPER MAINSTREAM": "#0D47A1", 
        "MAINSTREAM": "#0B3C8C", 
        "MAINSTREAM LOW": "#1976D2", 
        "VALUE": "#42A5F5"
    }

    for tier in ["PREMIUM", "UPPER MAINSTREAM", "MAINSTREAM", "MAINSTREAM LOW", "VALUE"]:
        productos_tier = df_f[df_f["Tier"] == tier]
        if not productos_tier.empty:
            c1, c2 = st.columns([1, 4])
            
            # Etiqueta visual del Tier
            c1.markdown(f"""
                <div style="background-color:{tier_colors[tier]}; color:white; padding:15px; 
                border-radius:10px; text-align:center; font-weight:bold; height:100%; 
                display:flex; align-items:center; justify-content:center; min-height:80px;">
                    {tier}
                </div>
            """, unsafe_allow_html=True)
            
            # Construcción de tarjetas horizontales
            cards_html = ""
            for _, r in productos_tier.iterrows():
                # Borde morado para destacar Barcel/Propuesta
                b_color = "#4B207E" if r["Fabricante"] in ["BARCEL", "PROPUESTA"] else "#CCCCCC"
                
                cards_html += f"""
                <div style="display:inline-block; border: 2px solid {b_color}; border-radius: 10px; 
                padding: 10px; background: white; min-width: 160px; margin: 5px; 
                vertical-align: top; box-shadow: 1px 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-weight:bold; font-size:0.9rem; color:#333; margin-bottom:4px;">{r['Producto']}</div>
                    <div style="color:#666; font-size:0.8rem;">Index: {int(r['Idx_P'])}</div>
                    <div style="font-weight:bold; font-size:1rem; color:#111; margin-top:4px;">${int(r['Precio ($)'])} ({int(r['Gramaje (g)'])}g)</div>
                </div>"""
            
            with c2:
                st.markdown(f'<div style="display: block; width: 100%;">{cards_html}</div>', unsafe_allow_html=True)
            st.write("")

# --- 10. ANALISTA MAESTRO ULTRA 2.6: ESTRATEGIA INTEGRAL OPTIMIZADA ---
if modo == "Price Ladder" and not st.session_state.data.empty:
    st.divider()
    st.subheader("🚀 Sugerencias / Observaciones en base al Mercado")
    
    df_p = st.session_state.data.copy()
    # Conversión robusta a números
    for c in ["Precio ($)", "SOM (%)", "Precio por Kg ($)"]:
        df_p[c] = pd.to_numeric(df_p[c], errors='coerce').fillna(0)

    mapa_rivales = {
        "TAKIS": ["DORITO", "DINAMITA"],
        "CHIPS": ["SABRITA", "RECETA CRUJIENTE"],
        "PAPAS BARCEL": ["SABRITA", "RECETA CRUJIENTE"],
        "CHIPOTLES": ["RANCHERITO", "FRITO"],
        "RUNNERS": ["FRITO", "RANCHERITO"],
        "BIG MIX": ["PAKETAXO"],
        "POP KARAMELADAS": ["ACT II"],
        "HOT NUTS": ["KACANG"],
        "GOLDEN NUTS": ["MAFER"],
        "KIYAKIS": ["KARATE"],
        "VALENTONES": ["SABRITONE"],
        "PIX":["TORCIDITOS"]
    }

    def ajustar_precio_psicologico(p):
        puntos_magicos = [10, 12, 15, 18, 20, 22, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80]
        return min(puntos_magicos, key=lambda x: abs(x - p))

    def identificar_marca(n):
        n = str(n).upper()
        for m in mapa_rivales.keys():
            if m in n: return m
        return "OTRO"

    def es_rival_de(n_comp, m_barcel):
        n_comp = str(n_comp).upper()
        if m_barcel in mapa_rivales:
            for r in mapa_rivales[m_barcel]:
                if r in n_comp: return True
        return False

    def calcular_rango_g(p_target, pkg_ref):
        if pkg_ref <= 0: return "N/A"
        return f"{int((p_target/(pkg_ref*0.95))*1000)}g - {int((p_target/(pkg_ref*0.85))*1000)}g"

    hallazgos = []
    vistos = set() # Evita duplicados "al cuadrado"

    try:
        pesos_oca = df_p.groupby("Ocasión")["SOM (%)"].sum().to_dict()

        # --- BLOQUE A: ESTRATEGIA DE PORTAFOLIO (GAPS) ---
        df_b_global = df_p[df_p["Fabricante"] == "BARCEL"].sort_values("Precio ($)")
        if len(df_b_global) >= 2:
            for i in range(len(df_b_global) - 1):
                p1, p2 = df_b_global.iloc[i]["Precio ($)"], df_b_global.iloc[i+1]["Precio ($)"]
                if (p2 - p1) > 10:
                    id_gap = f"GAP_{int(p1)}_{int(p2)}"
                    if id_gap not in vistos:
                        p_sug = ajustar_precio_psicologico((p1 + p2) / 2)
                        hallazgos.append({
                            "Prioridad": "BAJA", "Tipo": "ESCALÓN DE PRECIO", "Ocasión": "PORTAFOLIO GLOBAL",
                            "Msg": f"Hueco detectado entre ${p1} y ${p2}",
                            "Detalle": f"Salto de ${p2-p1:.0f} en la escalera. Riesgo de fuga de transacciones.",
                            "Accion": f"🪜 **Extensión:** Evaluar SKU de **{calcular_rango_g(p_sug, df_b_global.iloc[i]['Precio por Kg ($)'])}** a **${int(p_sug)}**."
                        })
                        vistos.add(id_gap)

        # --- BLOQUE B: ANÁLISIS TÁCTICO POR OCASIÓN ---
        for oca in df_p["Ocasión"].unique():
            df_oca = df_p[df_p["Ocasión"] == oca].copy()
            df_barcel = df_oca[df_oca["Fabricante"] == "BARCEL"]
            df_comp = df_oca[df_oca["Fabricante"] != "BARCEL"]
            if df_oca.empty: continue
            
            peso_seg = pesos_oca.get(oca, 0)
            lider_abs = df_oca.loc[df_oca["SOM (%)"].idxmax()]
            lider_c = df_comp.sort_values("SOM (%)", ascending=False).iloc[0] if not df_comp.empty else None

            # 1. White Space
            if df_barcel.empty and lider_c is not None:
                p_sug = ajustar_precio_psicologico(lider_c["Precio ($)"])
                hallazgos.append({
                    "Prioridad": "ALTA" if peso_seg > 15 else "MEDIA", "Tipo": "WHITE SPACE", "Ocasión": oca,
                    "Msg": f"Barcel no participa ({peso_seg:.1f}% Occ)",
                    "Detalle": f"Segmento dominado por {lider_abs['Producto']}.",
                    "Accion": f"⚡ **Entrada:** Lanzar **{calcular_rango_g(p_sug, lider_c['Precio por Kg ($)'])}** a **${int(p_sug)}**."
                })

            # 2. Duelos y Liderazgo
            else:
                for _, row_b in df_barcel.iterrows():
                    # Si Barcel es Líder
                    if row_b["Producto"] == lider_abs["Producto"] and lider_c is not None:
                        idx = int((row_b["Precio por Kg ($)"] / lider_c["Precio por Kg ($)"]) * 100)
                        if idx < 95:
                            hallazgos.append({
                                "Prioridad": "MEDIA", "Tipo": "DOMINANCIA", "Ocasión": oca,
                                "Msg": f"Barcel lidera (Aporte Occ: {peso_seg:.1f}%)",
                                "Detalle": f"Index {idx} vs competidor. Oportunidad de rentabilidad.",
                                "Accion": f"📈 **Modo Líder:** Evaluar ajuste a **{calcular_rango_g(row_b['Precio ($)'], lider_c['Precio por Kg ($)'])}**."
                            })
                    # Si Barcel es Seguidor (Duelo)
                    elif lider_c is not None:
                        marca_b = identificar_marca(row_b["Producto"])
                        rivales = df_comp[df_comp.apply(lambda x: es_rival_de(x["Producto"], marca_b), axis=1)]
                        bench = rivales.sort_values("SOM (%)", ascending=False).iloc[0] if not rivales.empty else lider_c
                        idx = int((row_b["Precio por Kg ($)"] / bench["Precio por Kg ($)"]) * 100)
                        if idx > 95:
                            hallazgos.append({
                                "Prioridad": "ALTA", "Tipo": f"DUELO vs {bench['Producto']}", "Ocasión": oca,
                                "Msg": f"{row_b['Producto']} fuera de rango ({peso_seg:.1f}% Occ)",
                                "Detalle": f"Index {idx} vs rival. Riesgo de pérdida de preferencia.",
                                "Accion": f"⚖️ **R&D:** Ajustar a **{calcular_rango_g(row_b['Precio ($)'], bench['Precio por Kg ($)'])}**."
                            })

    except Exception as e: st.error(f"Error en Ultra 2.6: {e}")

    # --- RENDERIZADO VISUAL ---
    if hallazgos:
        # Ordenamos por prioridad: ALTA -> MEDIA -> BAJA
        hallazgos.sort(key=lambda x: {"ALTA": 0, "MEDIA": 1, "BAJA": 2}.get(x["Prioridad"], 2))
        for h in hallazgos:
            with st.container(border=True):
                col_i, col_t, col_a = st.columns([1.5, 3.5, 3])
                with col_i:
                    if h["Prioridad"] == "ALTA": st.error(f"🔴 **{h['Tipo']}**")
                    elif h["Prioridad"] == "MEDIA": st.warning(f"🟡 **{h['Tipo']}**")
                    else: st.info(f"🔵 **{h['Tipo']}**")
                with col_t:
                    st.markdown(f"#### {h['Ocasión']}")
                    st.write(f"**{h['Msg']}**")
                    st.caption(h['Detalle'])
                with col_a:
                    st.success(f"🧪 **Sugerencia:**\n\n{h['Accion']}")
    else:
        st.balloons()
        st.success("✅ **Portafolio en Paridad Optimizada.**")


        
# --- GENERADOR DE REPORTE ESTRATÉGICO (PDF) ---
    if hallazgos:
        st.divider()
        st.subheader("📋 Reporte de Sugerencias")
        
        # Función para crear un reporte simple en formato texto/Markdown descargable
        # Nota: Usamos un .txt profesional o .md para evitar errores de fuentes PDF en Streamlit Cloud
        reporte_texto = f"REPORTE ESTRATÉGICO DE PORTAFOLIO - {modo.upper()}\n"
        reporte_texto += "="*50 + "\n\n"
        
        for h in hallazgos:
            reporte_texto += f"[{h['Prioridad']}] {h['Ocasión']}: {h['Tipo']}\n"
            reporte_texto += f"Detalle: {h['Msg']}\n"
            reporte_texto += f"Acción Sugerida: {h['Accion']}\n"
            reporte_texto += "-"*30 + "\n"

        st.download_button(
            label="🚩 Descargar Resumen de Acciones (TXT)",
            data=reporte_texto,
            file_name=f"acciones_estrategicas_{modo.lower()}.txt",
            mime="text/plain",
            use_container_width=True
        )

# --- 13. VISUALIZACIÓN ESTRATÉGICA PRO: MAPA DE VALOR CON FILTRO DINÁMICO ---
if modo == "Price Ladder" and not st.session_state.data.empty:
    st.divider()
    st.subheader("📊 Mapa Estratégico de Valor: Barcel vs Competencia")
    
    import plotly.express as px
    import pandas as pd
    import numpy as np

    df_plot = st.session_state.data.copy()
    
    # Limpieza y preparación de datos
    for c in ["Precio ($)", "Precio por Kg ($)", "SOM (%)"]:
        df_plot[c] = pd.to_numeric(df_plot[c], errors='coerce').fillna(0)

    # --- PLUS: FILTRO POR OCASIÓN DENTRO DE LA SECCIÓN ---
    ocasiones = ["TODAS"] + sorted(df_plot["Ocasión"].unique().tolist())
    oca_selected = st.selectbox("🎯 Filtrar por Momento de Consumo (Ocasión):", ocasiones)
    
    if oca_selected != "TODAS":
        df_plot = df_plot[df_plot["Ocasión"] == oca_selected]

    if not df_plot.empty:
        # --- PLUS: JITTERING PRO (Evita solapamiento de burbujas) ---
        # El jittering es proporcional a la escala para mantener la legibilidad
        rango_y = df_plot["Precio ($)"].max() - df_plot["Precio ($)"].min()
        stdev = (rango_y * 0.03) if rango_y > 0 else 0.5
        df_plot["Precio_Jitter"] = df_plot["Precio ($)"] + np.random.uniform(-stdev, stdev, size=len(df_plot))

        # Colores corporativos con énfasis en BARCEL
        colores = {
            "BARCEL": "#E20613",      # Rojo Barcel
            "SABRITAS": "#FFD700",    # Amarillo Sabritas
            "PEPSICO": "#004B91",     # Azul Pepsico
            "FRITO LAY": "#004B91",
            "OTRO": "#A0A0A0"         # Gris para el resto
        }

        # Crear el gráfico
        fig = px.scatter(
            df_plot,
            x="Precio por Kg ($)",
            y="Precio_Jitter",
            size="SOM (%)",
            color="Fabricante",
            hover_name="Producto",
            text="Producto",
            color_discrete_map=colores,
            size_max=55,
            labels={
                "Precio por Kg ($)": "Eficiencia de Valor (Precio/Kg)",
                "Precio_Jitter": "Punto de Precio (Desembolso)",
                "Fabricante": "Marca"
            },
            custom_data=["Precio ($)", "SOM (%)", "Ocasión"]
        )

        # Configuración de Etiquetas y Hover
        fig.update_traces(
            textposition='top center',
            marker=dict(line=dict(width=1, color='DarkSlateGrey')),
            hovertemplate="<b>%{hovertext}</b><br>" +
                          "Ocasión: %{customdata[2]}<br>" +
                          "Desembolso Real: $%{customdata[0]:.2f}<br>" +
                          "Precio/Kg: $%{x:.2f}<br>" +
                          "SOM: %{customdata[1]:.1f}%<extra></extra>"
        )

        # Formato Pro de Ejes y Layout
        fig.update_layout(
            template="plotly_white",
            height=750,
            xaxis=dict(
                title="<b>Valor x Dinero: Mayor Eficiencia (Precio/Kg) ⮕</b>",
                tickprefix="$",
                showgrid=True,
                gridcolor='#F0F0F0'
            ),
            yaxis=dict(
                title="<b>Punto de Precio (Desembolso)</b>",
                tickprefix="$",
                tickformat=".0f",
                showgrid=True,
                gridcolor='#F0F0F0'
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                title=None
            )
        )

        # Líneas de referencia para precios psicológicos
        precios_clave = [10, 15, 20, 25, 30, 40, 50, 70, 100]
        max_p = df_plot["Precio ($)"].max()
        for p in [x for x in precios_clave if x <= max_p + 10]:
            fig.add_hline(y=p, line_dash="dot", line_color="#CCCCCC", line_width=1)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos disponibles para la ocasión seleccionada.")

    # Guía rápida para el usuario
    st.info("💡 **Tip de Análisis:** Busca a Barcel (Burbuja Roja). Si está sola en un nivel de precio, es dueña del escalón. Si hay burbujas amarillas o azules más a la izquierda en el mismo nivel, el competidor ofrece más producto por el mismo dinero.")

# --- 12. SIMULADOR DE RESPUESTA TÁCTICA (ESCENARIOS DE ALZA) ---
if modo == "Price Ladder" and not st.session_state.data.empty:
    st.divider()
    st.subheader("🧪 Hipótesis de Mercado")
    st.info("Simula un incremento de precio en la competencia para determinar el ajuste técnico necesario en Barcel.")

    df_sim = st.session_state.data.copy()
    lista_comp = df_sim[df_sim["Fabricante"] != "BARCEL"].sort_values("SOM (%)", ascending=False)
    
    if not lista_comp.empty:
        col_s1, col_s2 = st.columns([2, 3])
        
        with col_s1:
            st.markdown("### 1. Escenario de Alza")
            comp_a_mover = st.selectbox("Seleccionar Benchmark Competidor:", lista_comp["Producto"].unique())
            datos_comp = lista_comp[lista_comp["Producto"] == comp_a_mover].iloc[0]
            
            precio_actual_comp = datos_comp["Precio ($)"]
            nuevo_precio_comp = st.number_input(f"Nuevo Precio Simulado de {comp_a_mover} ($):", 
                                                min_value=float(precio_actual_comp), 
                                                value=float(precio_actual_comp + 2.0), 
                                                step=1.0)
            
            p_incremento = ((nuevo_precio_comp / precio_actual_comp) - 1) * 100
            st.metric("Variación en Benchmark", f"${nuevo_precio_comp}", f"+{p_incremento:.1f}%")

        with col_s2:
            st.markdown("### 2. Impacto en Paridad Barcel")
            oca_sim = datos_comp["Ocasión"]
            df_barcel_oca = df_sim[(df_sim["Fabricante"] == "BARCEL") & (df_sim["Ocasión"] == oca_sim)]
            
            if not df_barcel_oca.empty:
                prod_b = st.selectbox("Producto Barcel a Proteger:", df_barcel_oca["Producto"].unique())
                row_b = df_barcel_oca[df_barcel_oca["Producto"] == prod_b].iloc[0]
                
                # PKG Competidor Proyectado
                pkg_comp_nuevo = nuevo_precio_comp / (datos_comp["Gramaje (g)"] / 1000)
                nuevo_index = (row_b["Precio por Kg ($)"] / pkg_comp_nuevo) * 100
                
                c_m1, c_m2 = st.columns(2)
                c_m1.metric("Index $/Kg Actual", f"{int((row_b['Precio por Kg ($)'] / datos_comp['Precio por Kg ($)']) * 100)}")
                c_m2.metric("Index Proyectado", f"{int(nuevo_index)}", f"{int(nuevo_index - (row_b['Precio por Kg ($)'] / datos_comp['Precio por Kg ($)']) * 100)} pts")

                st.divider()
                st.markdown(f"#### 🛡️ Alternativas de Ajuste (Rango Meta Index: 85-95)")
                
                # CÁLCULOS TÉCNICOS
                # A. Subir Precio para mantener Index 90 (punto medio del rango)
                precio_sugerido = (pkg_comp_nuevo * 0.90) * (row_b["Gramaje (g)"] / 1000)
                
                # B. Bajar Gramaje para mantener Index 90 con precio actual
                gramaje_sugerido_b = (row_b["Precio ($)"] / (pkg_comp_nuevo * 0.90)) * 1000
                g_redondeado_b = int(5 * round(gramaje_sugerido_b / 5))
                
                # C. Igualar Desembolso (Me-Too Pricing)
                g_idx_95 = int(5 * round(((nuevo_precio_comp / (pkg_comp_nuevo * 0.95)) * 1000) / 5))
                g_idx_85 = int(5 * round(((nuevo_precio_comp / (pkg_comp_nuevo * 0.85)) * 1000) / 5))

                tab1, tab2, tab3 = st.tabs(["A. Ajuste de Precio", "B. Ajuste de Gramaje", "C. Paridad de Desembolso"])
                
                with tab1:
                    st.success(f"**Mantener formato de {int(row_b['Gramaje (g)'])}g**")
                    st.markdown(f"Para sostener competitividad, el nuevo precio debe situarse en: **${precio_sugerido:.1f}**")
                
                with tab2:
                    st.success(f"**Mantener precio actual de ${int(row_b['Precio ($)'])}**")
                    st.markdown(f"Para proteger el Index, reducir contenido técnico a: **{g_redondeado_b}g**")
                
                with tab3:
                    st.success(f"**Igualar desembolso de ${int(nuevo_precio_comp)}**")
                    st.markdown(f"Para mantener un posicionamiento competitivo en el PDV con el mismo precio del benchmark, el gramaje debe oscilar entre:")
                    st.subheader(f"🎯 {g_idx_95}g — {g_idx_85}g")
                    st.caption(f"Rango calculado para asegurar un Index $/Kg entre 85 (Agresivo) y 95 (Eficiente) frente a {comp_a_mover}.")

            else:
                st.warning(f"No hay SKUs de Barcel registrados en la ocasión **{oca_sim}**.")
