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

# --- 6. EDITOR DE TABLA CON FUNCIÓN DE ELIMINAR ---
st.markdown("### 📝 Gestión de Portafolio")

# Creamos una columna temporal para selección si queremos borrado masivo
df_with_selections = st.session_state.data.copy()
if "Select" not in df_with_selections.columns:
    df_with_selections.insert(0, "Select", False)

# El editor de datos
edited_df = st.data_editor(
    df_with_selections, 
    num_rows="dynamic",      # Permite agregar filas al final
    use_container_width=True,
    key="portfolio_editor",
    hide_index=True
)

# Lógica para guardar cambios o procesar eliminaciones
col_btn1, col_btn2 = st.columns([1, 4])

with col_btn1:
    # Botón para eliminar las filas que el usuario marcó en el checkbox
    if st.button("🗑️ Eliminar seleccionados", type="secondary"):
        # Filtramos para quedarnos solo con lo que NO está seleccionado
        df_final = edited_df[edited_df["Select"] == False].drop(columns=["Select"])
        st.session_state.data = calcular_pkg(df_final, modo)
        st.session_state.data.to_csv(DB_FILE, index=False)
        st.success("Filas eliminadas correctamente")
        st.rerun()

# Lógica para detectar si hubo cambios manuales en las celdas (precios, nombres, etc.)
# Ignoramos la columna 'Select' para comparar si hubo cambios reales en los datos
current_data_no_select = edited_df.drop(columns=["Select"])
if not current_data_no_select.equals(st.session_state.data):
    st.session_state.data = calcular_pkg(current_data_no_select, modo)
    st.session_state.data.to_csv(DB_FILE, index=False)
    st.rerun()


# --- 6.5 FILTROS DINÁMICOS (SOLO PARA PRICE LADDER) ---
sel_fab, sel_oca, sel_prod = [], [], [] # Inicializamos vacíos

if modo == "Price Ladder":
    st.write("") 
    with st.container(border=True):
        st.markdown("### 🔍 Filtros de Visualización (Price Ladder)")
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            lista_fab = sorted(st.session_state.data["Fabricante"].unique().tolist())
            sel_fab = st.multiselect("Filtrar por Fabricante", lista_fab)

        with col_f2:
            lista_oca = sorted(st.session_state.data["Ocasión"].unique().tolist())
            sel_oca = st.multiselect("Filtrar por Ocasión", lista_oca)

        with col_f3:
            lista_prod = sorted(st.session_state.data["Producto"].unique().tolist())
            sel_prod = st.multiselect("Filtrar por Producto", lista_prod)

# --- 7. GRÁFICO FINAL (CON FILTROS DINÁMICOS INTEGRADOS) ---

if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    
    # --- INSERCIÓN DE FILTROS ---
    if modo == "Price Ladder":
        if sel_fab:
            df_p = df_p[df_p["Fabricante"].isin(sel_fab)]
        if sel_oca:
            df_p = df_p[df_p["Ocasión"].isin(sel_oca)]
        if sel_prod:
            df_p = df_p[df_p["Producto"].isin(sel_prod)]
    # --- FIN DE INSERCIÓN ---

    # 2. Verificar si hay datos tras el filtrado
    if df_p.empty:
        st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados.")
    else:
        if modo == "Price Ladder":
            # --- LÓGICA PRICE LADDER ---
            ord_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5,"REUNIÓN":6, "FIESTA":7,"TRANSFORMADOR":8}
            df_p["O_Oca"] = df_p["Ocasión"].str.upper().map(ord_oca).fillna(99)
            # Ordenamiento con desempate por $/Kg
            df_p = df_p.sort_values(by=["O_Oca", "Precio ($)", "Precio por Kg ($)"]).reset_index(drop=True)
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
                text=[f"<b>${p:.1f}</b>" for p in df_p["Precio ($)"]], 
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
            # --- LÓGICA PRICE PACK (SIN FILTROS) ---
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

# --- 8. EXPORTAR DATOS ---
st.markdown("---")
st.write("### 📥 Descargar Reporte")

import io
from fpdf import FPDF

# --- FUNCIÓN CORREGIDA PARA EL PDF (Sin errores de bytearray) ---
def generar_pdf(df, titulo_modo):
    pdf = FPDF()
    pdf.add_page()
    # Usamos Helvetica que es una fuente estándar muy estable
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Reporte de Precios: {titulo_modo}", ln=True, align='C')
    pdf.ln(10)
    
    # Encabezados de la tabla
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(75, 10, "Producto", 1)
    pdf.cell(40, 10, "Fabricante", 1)
    pdf.cell(35, 10, "Precio ($)", 1)
    pdf.cell(35, 10, "Precio/Kg", 1)
    pdf.ln()
    
    # Filas de la tabla
    pdf.set_font("Helvetica", size=10)
    for _, row in df.iterrows():
        # Limpieza de caracteres para evitar errores de codificación
        p_nom = str(row['Producto'])[:35].encode('latin-1', 'replace').decode('latin-1')
        f_nom = str(row['Fabricante']).encode('latin-1', 'replace').decode('latin-1')
        
        pdf.cell(75, 10, p_nom, 1)
        pdf.cell(40, 10, f_nom, 1)
        pdf.cell(35, 10, f"${row['Precio ($)']:,.1f}", 1)
        pdf.cell(35, 10, f"${row['Precio por Kg ($)']:,.0f}", 1)
        pdf.ln()
    
    # IMPORTANTE: En fpdf2, output() ya devuelve los bytes necesarios
    return pdf.output()

# --- BOTONES DE DESCARGA ---
if not df_p.empty:
    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        # EXCEL
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='xlsxwriter') as writer:
            df_p.to_excel(writer, index=False)
        
        st.download_button(
            label="📊 Descargar Excel",
            data=buffer_excel.getvalue(),
            file_name=f"Analisis_{modo}.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True
        )
            
# --- 9. COMPARATIVAS INDEX (DOBLE FILA: DESEMBOLSO Y $/KG) ---
if not st.session_state.data.empty:
    st.divider()
    st.subheader(f"📈 Comparativas Index ({modo})")
    df_comp = st.session_state.data.copy()
    
    # Limpieza y conversión
    for col in ["Precio ($)", "Precio por Kg ($)"]:
        df_comp[col] = pd.to_numeric(df_comp[col], errors='coerce').fillna(0)
    
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
        # 1. Selectores (se mantienen arriba para controlar ambas filas)
        sel_cols = st.columns(4)
        selections = []
        for i in range(4):
            with sel_cols[i]:
                s_a = st.selectbox(f"{label_a}", list_a, key=f"sa{i}")
                s_b = st.selectbox(f"{label_b}", list_b, key=f"sb{i}", index=min(i+1, len(list_b)-1))
                selections.append((s_a, s_b))

        # 2. PRIMERA FILA: INDEX DESEMBOLSO
        st.markdown("### 💰 Index Desembolso")
        des_cols = st.columns(4)
        for i, (sel_a, sel_b) in enumerate(selections):
            row_a = df_comp[df_comp["Lookup_Key"] == sel_a].iloc[0]
            row_b = df_comp[df_comp["Lookup_Key"] == sel_b].iloc[0]
            v_a, v_b = row_a["Precio ($)"], row_b["Precio ($)"]
            
            idx = int((v_a / v_b * 100)) if v_b > 0 else 0
            color = "#0B3C8C" if idx <= 100 else "#D32F2F"
            
            with des_cols[i]:
                st.markdown(f"""
                    <div style="background:white; border:1px solid #ddd; border-top:5px solid {color}; border-radius:10px; padding:10px; text-align:center;">
                        <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#666; margin-bottom:5px;">
                            <span style="width:45%; text-align:left; height:20px; overflow:hidden;">{sel_a}</span>
                            <span style="width:45%; text-align:right; height:20px; overflow:hidden;">{sel_b}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:1.1rem; margin-bottom:10px;">
                            <span>${v_a:.1f}</span>
                            <span style="color:#ccc; font-size:0.7rem; padding-top:5px;">vs</span>
                            <span>${v_b:.1f}</span>
                        </div>
                        <div style="font-size:1.8rem; font-weight:900; color:{color}; line-height:1;">{idx}</div>
                        <div style="font-size:0.6rem; font-weight:bold; color:#999; text-transform:uppercase;">Index Desembolso</div>
                    </div>
                """, unsafe_allow_html=True)

        st.write("") # Espaciador

        # 3. SEGUNDA FILA: INDEX PRECIO X KG
        st.markdown("### ⚖️ Index Precio por Kg")
        pkg_cols = st.columns(4)
        for i, (sel_a, sel_b) in enumerate(selections):
            row_a = df_comp[df_comp["Lookup_Key"] == sel_a].iloc[0]
            row_b = df_comp[df_comp["Lookup_Key"] == sel_b].iloc[0]
            v_a, v_b = row_a["Precio por Kg ($)"], row_b["Precio por Kg ($)"]
            
            idx = int((v_a / v_b * 100)) if v_b > 0 else 0
            color = "#0B3C8C" if idx <= 100 else "#D32F2F"
            
            with pkg_cols[i]:
                st.markdown(f"""
                    <div style="background:white; border:1px solid #ddd; border-top:5px solid {color}; border-radius:10px; padding:10px; text-align:center;">
                        <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#666; margin-bottom:5px;">
                            <span style="width:45%; text-align:left; height:20px; overflow:hidden;">{sel_a}</span>
                            <span style="width:45%; text-align:right; height:20px; overflow:hidden;">{sel_b}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:1.1rem; margin-bottom:10px;">
                            <span>${int(v_a)}</span>
                            <span style="color:#ccc; font-size:0.7rem; padding-top:5px;">vs</span>
                            <span>${int(v_b)}</span>
                        </div>
                        <div style="font-size:1.8rem; font-weight:900; color:{color}; line-height:1;">{idx}</div>
                        <div style="font-size:0.6rem; font-weight:bold; color:#999; text-transform:uppercase;">Index $/Kg</div>
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

# --- 10. ANALISTA MAESTRO ULTRA 2.6: ESTRATEGIA INTEGRAL OPTIMIZADA (VERSIÓN FINAL CORREGIDA) ---
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

    def ajustar_precio_psicologico(p):
        puntos_magicos = [10, 12, 15, 18, 20, 22, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80]
        return min(puntos_magicos, key=lambda x: abs(x - p))

    def calcular_rango_g(p_target, pkg_ref):
        if pkg_ref <= 0: return "N/A"
        return f"{int((p_target/(pkg_ref*0.95))*1000)}g - {int((p_target/(pkg_ref*0.85))*1000)}g"

    hallazgos = []
    vistos = set()

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
                        
                        # USAMOS \$ PARA ESCAPAR EL SÍMBOLO Y EVITAR EL FORMATO DE CÓDIGO
                        p1_txt = f"\${int(p1)}"
                        p2_txt = f"\${int(p2)}"
                        p_sug_txt = f"\${int(p_sug)}"
                        
                        hallazgos.append({
                            "Prioridad": "BAJA", 
                            "Tipo": "ESCALÓN DE PRECIO", 
                            "Ocasión": "PORTAFOLIO GLOBAL",
                            "Msg": f"Hueco detectado entre {p1_txt} y {p2_txt}",
                            "Detalle": f"Salto de \${int(p2-p1)} en la escalera. Riesgo de fuga de transacciones.",
                            "Accion": f"🪜 **Extensión:** Evaluar SKU de **{calcular_rango_g(p_sug, df_b_global.iloc[i]['Precio por Kg ($)'])}** a **{p_sug_txt}**."
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

            if df_barcel.empty and lider_c is not None:
                p_sug = ajustar_precio_psicologico(lider_c["Precio ($)"])
                hallazgos.append({
                    "Prioridad": "ALTA" if peso_seg > 15 else "MEDIA", "Tipo": "WHITE SPACE", "Ocasión": oca,
                    "Msg": f"Barcel no participa ({peso_seg:.1f}% Occ)",
                    "Detalle": f"Segmento dominado por {lider_abs['Producto']}.",
                    "Accion": f"⚡ **Entrada:** Lanzar **{calcular_rango_g(p_sug, lider_c['Precio por Kg ($)'])}** a **\${int(p_sug)}**."
                })
            else:
                for _, row_b in df_barcel.iterrows():
                    if row_b["Producto"] == lider_abs["Producto"] and lider_c is not None:
                        idx = int((row_b["Precio por Kg ($)"] / lider_c["Precio por Kg ($)"]) * 100)
                        if idx < 95:
                            hallazgos.append({
                                "Prioridad": "MEDIA", "Tipo": "DOMINANCIA", "Ocasión": oca,
                                "Msg": f"Barcel lidera ({peso_seg:.1f}% Occ)",
                                "Detalle": f"Index {idx} vs competidor. Oportunidad de rentabilidad.",
                                "Accion": f"📈 **Modo Líder:** Evaluar ajuste a **{calcular_rango_g(row_b['Precio ($)'], lider_c['Precio por Kg ($)'])}**."
                            })
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
                    # Renderizado limpio en negrita
                    st.markdown(f"**{h['Msg']}**")
                    st.caption(h['Detalle'])
                with col_a:
                    st.success(f"🧪 **Sugerencia:**\n\n{h['Accion']}")
    else:
        st.balloons()
        st.success("✅ **Portafolio en Paridad Optimizada.**")

# --- 11. GENERADOR DE RESUMEN EJECUTIVO ESTRATÉGICO (V4: FIX ARQUITECTURA) ---
if modo == "Price Ladder" and not st.session_state.data.empty:
    st.divider()
    
    if st.button("📄 Generar Resumen Ejecutivo Detallado", key="btn_exec_v4"):
        with st.spinner("Compilando datos de mercado..."):
            
            if not hallazgos:
                st.success("✅ **Estado de Mercado:** El portafolio actual no presenta desviaciones críticas.")
            else:
                st.markdown("""
                    <style>
                    .exec-box {
                        background-color: #ffffff; padding: 30px; border-radius: 12px;
                        border: 1px solid #d1d1d1; box-shadow: 4px 4px 15px rgba(0,0,0,0.05);
                        color: #1a1a1a;
                    }
                    .rival-name { font-weight: bold; color: #d32f2f; }
                    </style>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="exec-box">', unsafe_allow_html=True)
                st.subheader("📝 Resumen Ejecutivo: Estrategia de Portafolio")
                
                # --- A. DIAGNÓSTICO ---
                num_alta = len([h for h in hallazgos if h["Prioridad"] == "ALTA"])
                st.write(f"Se han identificado **{len(hallazgos)} hallazgos estratégicos**, con **{num_alta} alertas críticas**.")

                # --- B. OPORTUNIDADES (WHITE SPACES) ---
                ws_items = [h for h in hallazgos if h["Tipo"] == "WHITE SPACE"]
                if ws_items:
                    st.markdown("#### 🚀 Expansión de Portafolio")
                    for ws in ws_items:
                        rival = ws['Detalle'].split('dominado por ')[-1].replace('.', '')
                        sug_data = ws['Accion'].replace("⚡ **Entrada:** Lanzar ", "")
                        st.write(f"* **{ws['Ocasión']}:** Barcel no participa. Dominio de <span class='rival-name'>{rival}</span>. "
                                 f"**Acción:** Introducir SKU de **{sug_data}**.", unsafe_allow_html=True)

                # --- C. COMPETITIVIDAD (DUELOS) ---
                duelos = [h for h in hallazgos if "DUELO" in h["Tipo"]]
                if duelos:
                    st.markdown("#### 🛡️ Ajustes de Paridad (Defensa)")
                    for d in duelos:
                        rival = d['Tipo'].replace("DUELO vs ", "")
                        sug_data = d['Accion'].replace("⚖️ **R&D:** Ajustar a ", "")
                        st.write(f"* **{d['Ocasión']}:** {d['Msg']} vs <span class='rival-name'>{rival}</span>. "
                                 f"**Rec:** {sug_data}.", unsafe_allow_html=True)

                # --- D. HUECOS EN LA ESCALERA (GAPS) - CORREGIDO ---
                gaps = [h for h in hallazgos if h["Tipo"] == "ESCALÓN DE PRECIO"]
                if gaps:
                    st.markdown("#### 🪜 Arquitectura de Precios")
                    for g in gaps:
                        # Extraemos los precios limpiando el mensaje original de forma segura
                        rango_precios = g['Msg'].replace("Hueco detectado entre ", "").strip()
                        # Aseguramos que el formato sea "$X y $Y" con espacios
                        rango_formateado = rango_precios.replace("y", " y ")
                        sug_data = g['Accion'].replace("🪜 **Extensión:** Evaluar SKU de ", "")
                        
                        st.write(f"* **Brecha de Salto:** Rango entre **{rango_formateado}**. "
                                 f"**Sugerencia:** SKU puente de **{sug_data}**.")

                st.markdown("---")
                st.write("**💡 Veredicto:** Priorizar blindaje en segmentos donde el rival tiene ventaja competitiva en gramaje.")
                st.markdown('</div>', unsafe_allow_html=True)



# --- 13. VISUALIZACIÓN ESTRATÉGICA PRO: MAPA DE VALOR LIMPIO ---
if modo == "Price Ladder" and not st.session_state.data.empty:
    st.divider()
    st.subheader("📊 Mapa Estratégico de Valor: Barcel vs Competencia")
    
    import plotly.express as px
    import pandas as pd
    import numpy as np

    df_plot = st.session_state.data.copy()
    
    # 1. Limpieza y preparación de datos numéricos
    for c in ["Precio ($)", "Precio por Kg ($)", "SOM (%)"]:
        df_plot[c] = pd.to_numeric(df_plot[c], errors='coerce').fillna(0)

    # 2. Lógica de Colores Personalizada (Barcel Azul, Sabritas Amarillo, Otros Gris, Propuesta Morado)
    def asignar_color(row):
        fab = str(row["Fabricante"]).upper()
        prod = str(row["Producto"]).upper()
        # Si el nombre del producto contiene "PROPUESTA" (útil para simulaciones)
        if "PROPUESTA" in prod or "SUGERIDO" in prod: 
            return "PROPUESTA"
        if "BARCEL" in fab: 
            return "BARCEL"
        if "SABRITAS" in fab or "PEPSICO" in fab: 
            return "SABRITAS"
        return "OTROS"

    df_plot["Categoria_Color"] = df_plot.apply(asignar_color, axis=1)

    # 3. Filtro por Ocasión para limpiar la vista
    ocasiones = ["TODAS"] + sorted(df_plot["Ocasión"].unique().tolist())
    oca_selected = st.selectbox("🎯 Selecciona Momento de Consumo:", ocasiones, key="filtro_oca_viz_clean")
    
    if oca_selected != "TODAS":
        df_plot = df_plot[df_plot["Ocasión"] == oca_selected]

    if not df_plot.empty:
        # Jittering: Pequeño ruido en el eje Y para separar burbujas con el mismo precio exacto
        stdev = (df_plot["Precio ($)"].std() * 0.03) if len(df_plot) > 1 else 0.5
        df_plot["Precio_Jitter"] = df_plot["Precio ($)"] + np.random.uniform(-stdev, stdev, size=len(df_plot))

        # Mapa de colores solicitado por el usuario
        color_map = {
            "BARCEL": "#002366",    # Azul Fuerte
            "SABRITAS": "#FFD700",  # Amarillo
            "OTROS": "#A0A0A0",     # Gris
            "PROPUESTA": "#800080"  # Morado
        }

        # Creación del gráfico Pro
        fig = px.scatter(
            df_plot,
            x="Precio por Kg ($)",
            y="Precio_Jitter",
            size="SOM (%)",
            color="Categoria_Color",
            hover_name="Producto",
            text="Producto",
            color_discrete_map=color_map,
            size_max=55,
            labels={
                "Precio por Kg ($)": "Eficiencia (Precio/Kg)", 
                "Precio_Jitter": "Desembolso ($)",
                "Categoria_Color": "Leyenda"
            },
            custom_data=["Precio ($)", "SOM (%)", "Ocasión"]
        )

        # Ajuste de etiquetas y hover para que no estorben
        fig.update_traces(
            textposition='top center',
            marker=dict(line=dict(width=1, color='white')),
            hovertemplate="<b>%{hovertext}</b><br>" +
                          "Ocasión: %{customdata[2]}<br>" +
                          "Precio Real: $%{customdata[0]:.2f}<br>" +
                          "Precio/Kg: $%{x:.2f}<br>" +
                          "SOM: %{customdata[1]:.1f}%<extra></extra>"
        )

        # Configuración Pro del Layout (Ejes con $)
        fig.update_layout(
            template="plotly_white",
            height=750,
            xaxis=dict(
                title="<b>Eficiencia de Valor (Precio por Kg)</b>", 
                tickprefix="$", 
                showgrid=True,
                gridcolor='#F0F0F0'
            ),
            yaxis=dict(
                title="<b>Punto de Precio (Desembolso)</b>", 
                tickprefix="$", 
                showgrid=True,
                gridcolor='#F0F0F0'
            ),
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=1.02, 
                xanchor="center", 
                x=0.5
            )
        )

        # Líneas sutiles de referencia para los umbrales de precio (Magic Prices)
        max_p = df_plot["Precio ($)"].max()
        for p in [15, 25, 35, 50, 70, 100]:
            if p <= max_p + 15:
                fig.add_hline(y=p, line_dash="dot", line_color="#E0E0E0", line_width=1)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar en esta selección.")

    st.caption("💡 **Interpretación:** Las burbujas moradas representan las propuestas de ajuste. El objetivo es que Barcel (Azul) no esté más a la derecha que Sabritas (Amarillo) en el mismo nivel de precio")

# --- 14. SIMULADOR ESTRATÉGICO DIRECTIVO (V6.1: VARIACIONES % + AJUSTE GRAMAJE + SNAPSHOTS) ---
if modo == "Price Ladder" and not st.session_state.data.empty:
    st.divider()
    
    if 'snapshots' not in st.session_state:
        st.session_state.snapshots = []

    st.markdown("""
        <style>
        [data-testid="stMetricValue"] { font-size: 1.7rem; font-weight: bold; color: #002366; }
        .report-card { 
            background-color: #f8f9fa; border-radius: 10px; padding: 20px; 
            border-left: 5px solid #002366; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.subheader("🧪 Simulador de Escenarios: Paridad y Eficiencia")
    
    df_sim = st.session_state.data.copy()
    for c in ["Precio ($)", "SOM (%)", "Precio por Kg ($)", "Gramaje (g)"]:
        df_sim[c] = pd.to_numeric(df_sim[c], errors='coerce').fillna(0)

    lista_comp = df_sim[df_sim["Fabricante"] != "BARCEL"].sort_values("SOM (%)", ascending=False)
    
    if not lista_comp.empty:
        # --- PARTE 1: CONFIGURACIÓN HORIZONTAL ---
        st.markdown("##### ⚙️ Configuración del Escenario")
        c_in1, c_in2, c_in3, c_in4 = st.columns(4)
        
        with c_in1:
            comp_a_mover = st.selectbox("Benchmark Competidor:", lista_comp["Producto"].unique(), key="v6_c")
            datos_comp = lista_comp[lista_comp["Producto"] == comp_a_mover].iloc[0]
            n_p_c = st.number_input(f"Nuevo Precio {comp_a_mover}:", min_value=1.0, value=float(datos_comp["Precio ($)"]), step=1.0)
            n_g_c = st.number_input(f"Gramaje {comp_a_mover} (g):", min_value=1, value=int(datos_comp["Gramaje (g)"]), step=1)
            pkg_c_nuevo = n_p_c / (n_g_c / 1000)

        with c_in3:
            oca_sim = datos_comp["Ocasión"]
            df_barcel_oca = df_sim[(df_sim["Fabricante"] == "BARCEL") & (df_sim["Ocasión"] == oca_sim)]
            if not df_barcel_oca.empty:
                prod_b = st.selectbox("Producto Barcel:", df_barcel_oca["Producto"].unique(), key="v6_b")
                row_b = df_barcel_oca[df_barcel_oca["Producto"] == prod_b].iloc[0]
                n_p_b = st.number_input(f"Nuevo Precio {prod_b}:", min_value=1.0, value=float(row_b["Precio ($)"]), step=1.0)
                n_g_b = st.number_input(f"Gramaje {prod_b} (g):", min_value=1, value=int(row_b["Gramaje (g)"]), step=1)
                pkg_b_nuevo = n_p_b / (n_g_b / 1000)
            else:
                st.warning(f"Sin Barcel en {oca_sim}"); st.stop()

        # --- CÁLCULOS DE VARIACIÓN (DELTAS) ---
        var_p_c = ((n_p_c / datos_comp["Precio ($)"]) - 1) * 100 if datos_comp["Precio ($)"] > 0 else 0
        var_pkg_c = ((pkg_c_nuevo / datos_comp["Precio por Kg ($)"]) - 1) * 100 if datos_comp["Precio por Kg ($)"] > 0 else 0
        
        var_p_b = ((n_p_b / row_b["Precio ($)"]) - 1) * 100 if row_b["Precio ($)"] > 0 else 0
        var_pkg_b = ((pkg_b_nuevo / row_b["Precio por Kg ($)"]) - 1) * 100 if row_b["Precio por Kg ($)"] > 0 else 0

        # Cálculos de Index (Enteros)
        idx_des_ant = int(round((row_b["Precio ($)"] / datos_comp["Precio ($)"]) * 100))
        idx_des_nue = int(round((n_p_b / n_p_c) * 100))
        idx_pkg_ant = int(round((row_b["Precio por Kg ($)"] / datos_comp["Precio por Kg ($)"]) * 100))
        idx_pkg_nue = int(round((pkg_b_nuevo / pkg_c_nuevo) * 100))

        # --- PARTE 2: DIAGNÓSTICO ---
        st.markdown(f"### 📊 Diagnóstico de Paridad ({oca_sim})")
        
        with st.container():
            st.markdown('<div class="report-card">', unsafe_allow_html=True)
            st.write("💰 **ANÁLISIS DE DESEMBOLSO (OUT-OF-POCKET)**")
            c1, c2, c3 = st.columns(3)
            c1.metric(f"{comp_a_mover}", f"${n_p_c:.0f}", f"{var_p_c:+.1f}% vs act.")
            c2.metric(f"{prod_b}", f"${n_p_b:.0f}", f"{var_p_b:+.1f}% vs act.")
            c3.metric("INDEX PRECIO", f"{idx_des_nue}", f"{idx_des_nue - idx_des_ant} pts")
            st.markdown('</div>', unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="report-card">', unsafe_allow_html=True)
            st.write("⚖️ **ANÁLISIS DE EFICIENCIA (VALOR $/KG)**")
            c1, c2, c3 = st.columns(3)
            c1.metric(f"$/Kg {comp_a_mover}", f"${pkg_c_nuevo:.2f}", f"{var_pkg_c:+.1f}% efec.")
            c2.metric(f"$/Kg {prod_b}", f"${pkg_b_nuevo:.2f}", f"{var_pkg_b:+.1f}% efec.")
            c3.metric("INDEX $/KG", f"{idx_pkg_nue}", f"{idx_pkg_nue - idx_pkg_ant} pts")
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("📸 Guardar Snapshot del Escenario"):
            nuevo_snap = {
                "Escenario": f"Esc {len(st.session_state.snapshots)+1}",
                "Producto": prod_b,
                "vs Rival": comp_a_mover,
                "Precio B": n_p_b, "Gramos B": n_g_b,
                "Precio C": n_p_c, "Gramos C": n_g_c,
                "Index Desem.": idx_des_nue,
                "Index $/Kg": idx_pkg_nue
            }
            st.session_state.snapshots.append(nuevo_snap)
            st.toast("Escenario guardado correctamente")

        # --- PARTE 3: ALTERNATIVAS R&D ---
        st.markdown("---")
        st.markdown("#### 🛡️ Ingeniería de Producto: Alternativas para un Index (85-95) ")
        
        def a_psicologico_estricto(p_target, p_comp):
            puntos = [10, 12, 15, 18, 20, 22, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80]
            sug = min(puntos, key=lambda x: abs(x - p_target))
            lider_occ = df_sim[df_sim["Ocasión"] == oca_sim].sort_values("SOM (%)", ascending=False).iloc[0]
            if not (lider_occ["Fabricante"] == "BARCEL") and sug > p_comp:
                p_debajo = [p for p in puntos if p <= p_comp]
                return p_debajo[-1] if p_debajo else p_comp
            return sug

        p_tec = (pkg_c_nuevo * 0.92) * (n_g_b / 1000)
        p_final = a_psicologico_estricto(p_tec, n_p_c)
        g_final = int(5 * round(((n_p_b / (pkg_c_nuevo * 0.92)) * 1000) / 5))

        col_a, col_b = st.columns(2)
        with col_a:
            st.info(f"**Escenario A: Mantener {n_g_b}g**\n\nPrecio Sugerido: **${p_final}**")
            st.caption(f"Index $/Kg Proyectado: {int(round(((p_final/(n_g_b/1000))/pkg_c_nuevo)*100))}")
        with col_b:
            st.info(f"**Escenario B: Mantener Precio de ${n_p_b}**\n\nContenido Sugerido: **{g_final}g**")
            st.caption(f"Index $/Kg Proyectado: {int(round(((n_p_b/(g_final/1000))/pkg_c_nuevo)*100))}")

    if st.session_state.snapshots:
        st.write("---")
        st.markdown("### 📋 Historial de Escenarios Guardados")
        df_snaps = pd.DataFrame(st.session_state.snapshots)
        st.table(df_snaps)
        if st.button("🗑️ Limpiar Historial"):
            st.session_state.snapshots = []
            st.rerun()

