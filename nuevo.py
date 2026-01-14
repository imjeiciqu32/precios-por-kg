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

try:
    from data_price_vol import PLANTILLA_PV
except ImportError:
    PLANTILLA_PV = {}
    
    
# --- CARGA DE ARQUITECTURA DESDE TU ARCHIVO EN GITHUB/LOCAL ---
try:
    # Suponiendo que tu archivo se llama arquitectura_empaque.py
    from arquitectura_empaque import render_arquitectura_empaque
    # Creamos un DataFrame independiente para NO tocar el df_p de las escaleras
    df_arq = pd.DataFrame(render_arquitectura_empaque)
except ImportError:
    st.error("No se pudo encontrar el archivo 'arquitectura_empaque.py' en el repositorio.")
    df_arq = pd.DataFrame() # DataFrame vacío para evitar que el código truene

    
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

# --- 1. NAVEGACIÓN Y CONFIGURACIÓN ---
with st.sidebar:
    st.header("🚀 Modo de Visualización")
    # Agregamos el nuevo modo a la lista
    modo = st.radio(
        "Seleccionar Herramienta:", 
        ["Price Ladder", "Price Pack", "Price and Volumen"], 
        label_visibility="collapsed"
    )
    
    # Botón limpio para el Glosario
    if st.button("❓ Ver Glosario Técnico", use_container_width=True):
        if 'mostrar_glosario' in globals(): # Verificación de seguridad
            mostrar_glosario()
        else:
            st.info("Función de glosario no definida aún.")
            
# LÓGICA DE MODOS (Actualizada con Price and Volumen)
if modo == "Price Ladder":
    DB_FILE = "historico_productos.csv"
    label_agru = "Ocasión"
    opciones_agru = ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR", "REUNIÓN", "FIESTA", "TRANSFORMADOR"]
    fuente_plantillas = PLANTILLAS if 'PLANTILLAS' in globals() else {}
    columnas_tabla = ["Producto", "Fabricante", "Ocasión", "Precio ($)", "Gramaje (g)", "SOM (%)"]

elif modo == "Price Pack":
    DB_FILE = "historico_price_pack.csv"
    label_agru = "Canal"
    opciones_agru = ["INSTITUCIONALES", "MAYOREO", "CLUBES", "DETALLE", "AUTOSERVICIOS", "CONVENIENCIA"]
    fuente_plantillas = PLANTILLAS_PP if 'PLANTILLAS_PP' in globals() else {}
    columnas_tabla = ["Producto", "Familia", "Canal", "Precio ($)", "Gramaje (g)"]

else: # MODO: Price and Volumen
    DB_FILE = "historico_ventas_semanales.csv"
    label_agru = "Semana" # Aquí agruparemos por número de semana
    
    # IMPORTANTE: Aseguramos que las opciones sean números para que coincidan con tu PLANTILLA_PV
    opciones_agru = list(range(1, 53)) 
    
    fuente_plantillas = PLANTILLA_PV if 'PLANTILLA_PV' in globals() else {}
    
    # Definimos las columnas exactas que vienen en tu nueva plantilla
    columnas_tabla = ["Semana", "Producto", "Fabricante", "Precio ($)", "Venta Volumen (Pzas)","Venta Valor ($)"]

# --- 2. FUNCIONES CORE (Mantenidas intactas) ---
def calcular_pkg(df, modo_actual):
    if df.empty: 
        return df
    
    # 1. LÓGICA PARA PRICE LADDER Y PRICE PACK
    # Solo calculamos $/kg si existen las columnas necesarias
    if "Precio ($)" in df.columns and "Gramaje (g)" in df.columns:
        df["Precio ($)"] = pd.to_numeric(df["Precio ($)"], errors='coerce').fillna(0)
        df["Gramaje (g)"] = pd.to_numeric(df["Gramaje (g)"], errors='coerce').fillna(1).replace(0, 1)
        # Mantenemos tu fórmula original: (Precio / (Gramos / 1000))
        df["Precio por Kg ($)"] = (df["Precio ($)"] / (df["Gramaje (g)"] / 1000)).round(1)
    
    # 2. LÓGICA ESPECÍFICA POR MODO
    if modo_actual == "Price Ladder":
        if "SOM (%)" not in df.columns: 
            df["SOM (%)"] = 0.0
        if "Fabricante" not in df.columns: 
            df["Fabricante"] = "OTROS"
            
    elif modo_actual == "Price and Volumen":
        # Para este modo, solo aseguramos que las columnas de valor y volumen sean numéricas
        cols_pv = ["Precio ($)", "Venta Volumen (Pzas)","Venta Valor ($)"]
        for col in cols_pv:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
    return df

def procesar_datos_piramide(df):
    if df.empty: return df
    df_py = df.copy()
    idx_referencia = df_py.groupby("Ocasión")["SOM (%)"].idxmax()
    df_ref = df_py.loc[idx_referencia, ["Ocasión", "Precio por Kg ($)"]]
    df_ref = df_ref.rename(columns={"Precio por Kg ($)": "Precio_Ref"})
    df_py = df_py.merge(df_ref, on="Ocasión", how="left")
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

# --- 4. BARRA LATERAL (GESTIÓN MEJORADA) ---
with st.sidebar:
    st.markdown("---")
    st.header("📁 Gestión de Datos")
    
    with st.container(border=True):
        nombre_plantilla = st.selectbox("Cargar Plantilla:", ["-- Seleccionar --"] + list(fuente_plantillas.keys()))
        
        if st.button("📥 Cargar Datos", use_container_width=True, type="primary"):
            if nombre_plantilla != "-- Seleccionar --":
                # Convertimos a DataFrame
                df_nuevo = pd.DataFrame(fuente_plantillas[nombre_plantilla])
                
                # CARGA INDEPENDIENTE: Evitamos pasar por calcular_pkg si es Price and Volumen
                if modo == "Price and Volumen":
                    st.session_state.data = df_nuevo
                else:
                    # Ladder y Pack sí necesitan calcular $/kg
                    st.session_state.data = calcular_pkg(df_nuevo, modo)
                
                st.session_state.data.to_csv(DB_FILE, index=False)
                st.success("¡Datos cargados!")
                st.rerun()

    # EXPORTACIÓN
    def to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Analisis_Portafolio')
        return output.getvalue()

    if not st.session_state.data.empty:
        st.divider()
        st.subheader("📥 Exportar Catálogo")
        excel_data = to_excel(st.session_state.data)
        st.download_button(
            label="📄 Descargar Excel Completo",
            data=excel_data,
            file_name=f'barcel_{modo.lower()}_data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            use_container_width=True
        )

    if st.button("🗑️ Reset Sistema", use_container_width=True):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state.data = pd.DataFrame(columns=columnas_tabla)
        st.rerun()

# --- 5. PANEL PRINCIPAL ---
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
sel_fab, sel_oca, sel_prod = [], [], [] 

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

    # --- CORRECCIÓN: DEFINICIÓN DE DF_P INMEDIATAMENTE DESPUÉS DE LOS FILTROS ---
    df_p = st.session_state.data.copy()
    if sel_fab:
        df_p = df_p[df_p["Fabricante"].isin(sel_fab)]
    if sel_oca:
        df_p = df_p[df_p["Ocasión"].isin(sel_oca)]
    if sel_prod:
        df_p = df_p[df_p["Producto"].isin(sel_prod)]
else:
    # Si no es Price Ladder, creamos df_p sin filtros para evitar errores en otras secciones
    df_p = st.session_state.data.copy()

# --- 6.8 PANEL EJECUTIVO (FORMATO TABLA EJECUTIVA) ---
if modo == "Price Ladder" and not df_p.empty:
    st.write("### 📈 Resumen de Mercado por Ocasión")
    
    # Agrupamos y preparamos los datos
    resumen_oca = df_p.groupby("Ocasión").agg({
        "Producto": "count",
        "Precio ($)": "mean",
        "Precio por Kg ($)": "mean"
    }).reset_index()

    # Orden lógico de las ocasiones
    ord_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5, "REUNIÓN": 6, "FIESTA": 7, "TRANSFORMADOR": 8}
    resumen_oca["Orden"] = resumen_oca["Ocasión"].str.upper().map(ord_oca).fillna(99)
    resumen_oca = resumen_oca.sort_values("Orden")

    # Mostramos la tabla con Formato Ejecutivo
    st.dataframe(
        resumen_oca[["Ocasión", "Producto", "Precio ($)", "Precio por Kg ($)"]],
        column_config={
            "Ocasión": st.column_config.TextColumn("Segmento / Ocasión"),
            "Producto": st.column_config.NumberColumn("SKUs", help="Cantidad de SKUs analizados"),
            "Precio ($)": st.column_config.NumberColumn(
                "Desembolso Prom.",
                format="$%.1f",  # Símbolo $ y 1 decimal
            ),
            "Precio por Kg ($)": st.column_config.NumberColumn(
                "$/KG Promedio",
                format="$%d",    # Símbolo $ y redondeado (sin decimales)
            ),
        },
        hide_index=True,
        use_container_width=True
    )
    st.write("")
    
# --- 7. GRÁFICO FINAL (CON FILTROS DINÁMICOS INTEGRADOS) ---

if not st.session_state.data.empty:
    df_p = st.session_state.data.copy()
    
    # --- CONFIGURACIÓN DE INTERFAZ EN SIDEBAR ---
    with st.sidebar:
        st.divider()
        st.subheader("🎨 Controles de Diseño")
        
        # Lógica de reseteo funcional (incluye todas las nuevas variables)
        def reset_diseno():
            st.session_state["slider_nombres"] = 14
            st.session_state["slider_precios"] = 18
            st.session_state["slider_pkg"] = 16
            st.session_state["slider_som"] = 13 # <--- NUEVO
            st.session_state["slider_ancho"] = 0.6
            st.session_state["slider_opacidad"] = 1.0
            st.session_state["slider_alto"] = 950
            st.session_state["slider_espacio"] = 0.03
            st.session_state["slider_margen_b"] = 400
            st.session_state["slider_angulo"] = -90

        if st.button("Resetear Todo el Diseño"):
            reset_diseno()
        
        # Inicialización de estados (Safe Check)
        defaults = {
            "slider_nombres": 14, "slider_precios": 18, "slider_pkg": 16,
            "slider_som": 13, "slider_ancho": 0.6, "slider_opacidad": 1.0, 
            "slider_alto": 950, "slider_espacio": 0.03, "slider_margen_b": 400, 
            "slider_angulo": -90
        }
        for key, val in defaults.items():
            if key not in st.session_state: st.session_state[key] = val

        # Agrupadores por Expander para limpieza visual
        with st.expander("📏 Dimensiones y Espaciado"):
            alto_grafico = st.slider("Alto del Gráfico", 400, 1500, key="slider_alto")
            espacio_v = st.slider("Espacio entre Gráficos", 0.0, 0.2, key="slider_espacio")
            margen_b = st.slider("Margen Inferior (Nombres)", 50, 600, key="slider_margen_b")
            ancho_barras = st.slider("Ancho de Barras", 0.1, 1.0, key="slider_ancho")
            opacidad_barras = st.slider("Opacidad Barras", 0.1, 1.0, key="slider_opacidad")

        with st.expander("🔡 Tipografía y Texto"):
            t_nombres = st.slider("Tamaño Nombres", 8, 30, key="slider_nombres")
            t_precios = st.slider("Tamaño Precios ($)", 10, 40, key="slider_precios")
            t_pkg = st.slider("Tamaño $/Kg", 10, 40, key="slider_pkg")
            t_som = st.slider("Tamaño SOM (%)", 8, 25, key="slider_som") # <--- NUEVO
            angulo_nombres = st.slider("Ángulo de Nombres", -90, 0, key="slider_angulo")
    
    # --- INSERCIÓN DE FILTROS (MODO LADDER) ---
    if modo == "Price Ladder":
        if sel_fab:
            df_p = df_p[df_p["Fabricante"].isin(sel_fab)]
        if sel_oca:
            df_p = df_p[df_p["Ocasión"].isin(sel_oca)]
        if sel_prod:
            df_p = df_p[df_p["Producto"].isin(sel_prod)]
    # --- FIN DE INSERCIÓN ---

    # 2. Verificar si hay datos tras el filtrado
    if df_p.empty and modo == "Price Ladder":
        st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados.")
    else:
        if modo == "Price Ladder":
            # --- LÓGICA PRICE LADDER ---
            ord_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5,"REUNIÓN":6, "FIESTA":7,"TRANSFORMADOR":8}
            df_p["O_Oca"] = df_p["Ocasión"].str.upper().map(ord_oca).fillna(99)
            
            # Ordenamiento con desempate por $/Kg
            df_p = df_p.sort_values(by=["O_Oca", "Precio ($)", "Precio por Kg ($)"]).reset_index(drop=True)
            som_por_ocasion = df_p.groupby("Ocasión")["SOM (%)"].sum().to_dict()

            # USO DE VARIABLE espacio_v
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=espacio_v, row_heights=[0.15, 0.85])

            # --- TRACE 1: SOM% ---
            fig.add_trace(go.Scatter(
                x=df_p["Producto"], y=df_p["SOM (%)"], mode="lines+markers+text", 
                line=dict(color="#BBBBBB", width=1.5), 
                marker=dict(size=30, color="#E5E5E5", symbol="square", line=dict(color="#CCCCCC", width=1)), 
                text=[f"<b>{row['SOM (%)']}%</b>" for _, row in df_p.iterrows()],
                textposition="middle center", textfont=dict(size=t_som, color="black"), # <--- t_som APLICADO
            ), row=1, col=1)

            # --- TRACE 2: BARRAS DE PRECIO ---
            colors = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D","PROPUESTA":"#4B207E"}
            
            # Lógica inteligente para etiquetas de Precio Desembolso
            labels_precios = []
            for p in df_p["Precio ($)"]:
                if p < 10:
                    labels_precios.append(f"<b>${p:.1f}</b>")
                else:
                    labels_precios.append(f"<b>${int(p)}</b>")

            fig.add_trace(go.Bar(
                x=df_p["Producto"], y=df_p["Precio ($)"],
                marker_color=[colors.get(str(f).upper(), "#999") for f in df_p["Fabricante"]],
                marker_opacity=opacidad_barras, 
                width=ancho_barras,
                text=labels_precios, 
                textposition="outside", 
                textfont=dict(size=t_precios, color="black")
            ), row=2, col=1)

            # Anotaciones de Precio por Kg dentro de las barras
            for i, row in df_p.iterrows():
                fig.add_annotation(
                    x=i, y=2.5, text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
                    showarrow=False, 
                    font=dict(size=t_pkg, color="white" if row["Fabricante"] == "BARCEL" else "black"),
                    bgcolor="rgba(70, 130, 180, 0.8)" if row["Fabricante"] == "BARCEL" else "rgba(255,255,255,0.8)",
                    bordercolor="#444" if row["Fabricante"] != "BARCEL" else None, borderwidth=1, row=2, col=1
                )

            # --- LÍNEAS DIVISORIAS ---
            for i in range(len(df_p) + 1):
                fig.add_shape(type="line", x0=i-0.5, x1=i-0.5, y0=-0.01, y1=-0.50, xref="x2", yref="paper", line=dict(color="#DDDDDD", width=1))

            for cat in df_p["Ocasión"].unique():
                idx_list = df_p.index[df_p["Ocasión"] == cat].tolist()
                fig.add_shape(
                    type="line", x0=idx_list[-1] + 0.5, x1=idx_list[-1] + 0.5, 
                    y0=-0.60, y1=1, xref="x2", yref="paper", 
                    line=dict(color="#CCCCCC", width=2)
                )
                center = (idx_list[0] + idx_list[-1]) / 2
                fig.add_annotation(
                    x=center, y=-0.60, xref="x2", yref="paper", 
                    text=f"<b>{cat}</b><br><span style='font-size:18px;'>{som_por_ocasion[cat]:.1f}%</span>", 
                    showarrow=False, font=dict(size=16, color="black"), align="center"
                )

            # CONFIGURACIÓN DE LAYOUT (ALTO Y MARGEN)
            fig.update_layout(
                height=alto_grafico, width=1950, template="plotly_white", showlegend=False, 
                margin=dict(t=50, b=margen_b, l=40, r=40)
            )
            
            fig.update_xaxes(
                tickangle=angulo_nombres, 
                tickfont=dict(size=t_nombres, color="black"),
                showline=False, 
                row=2, col=1
            )
            
            fig.update_yaxes(showticklabels=False, row=1, col=1)
            fig.update_yaxes(showgrid=True, gridcolor="#DCDCDC", tickprefix="$", tickfont=dict(size=14), row=2, col=1)
            
            # --- RENDERIZADO CON BOTÓN DE DESCARGA ---
            st.plotly_chart(fig, use_container_width=True, config={
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'Price_Ladder_Export',
                    'height': alto_grafico,
                    'width': 1950,
                    'scale': 2 # Alta resolución
                }
            })

        else:
            # --- 6.9 FILTROS DINÁMICOS PARA PRICE PACK ---
            # --- 6.9 FILTROS DINÁMICOS PARA PRICE PACK ---
            # Envolvemos TODO el bloque para que solo exista en el modo Price Pack
            if modo == "Price Pack":
                st.write("") 
                with st.container(border=True):
                    st.markdown("### 🔍 Filtros de Visualización (Price Pack)")
                    
                    # Verificación de seguridad: solo mostramos si la columna 'Canal' existe
                    if "Canal" in st.session_state.data.columns:
                        col_pp1, col_pp2 = st.columns(2)
                
                        with col_pp1:
                            lista_canales = sorted(st.session_state.data["Canal"].unique().tolist())
                            sel_canal_pp = st.multiselect("Filtrar por Canal", lista_canales, key="filter_pp_canal")
                
                        with col_pp2:
                            lista_prod_pp = sorted(st.session_state.data["Producto"].unique().tolist())
                            sel_prod_pp = st.multiselect("Filtrar por Producto", lista_prod_pp, key="filter_pp_prod")
                
                        # Lógica de filtrado sobre el DataFrame df_p
                        if sel_canal_pp:
                            df_p = df_p[df_p["Canal"].isin(sel_canal_pp)]
                        if sel_prod_pp:
                            df_p = df_p[df_p["Producto"].isin(sel_prod_pp)]
                
                        # Ordenamiento específico del modo Price Pack
                        ord_can = {"INSTITUCIONALES": 1, "MAYOREO": 2, "CLUBES": 3, "DETALLE": 4, "AUTOSERVICIOS": 5, "CONVENIENCIA": 6}
                        df_p["O_Can"] = df_p["Canal"].str.upper().map(ord_can).fillna(99)
                        df_p = df_p.sort_values(by=["O_Can", "Precio ($)"]).reset_index(drop=True)
                        
                        # Solo renderizamos el gráfico si hay datos tras filtrar
                        if not df_p.empty:
                            import plotly.graph_objects as go
                            fig = go.Figure()
                
                            # 1. Barras de fondo (Pkg)
                            fig.add_trace(go.Bar(
                                x=df_p.index, 
                                y=df_p["Precio por Kg ($)"], 
                                marker_color="#F8F9FA",
                                marker_line=dict(color="#D1D1D1", width=1),
                                marker_opacity=opacidad_barras,
                                width=ancho_barras,
                                showlegend=False
                            ))
                            
                            # Líneas de división de fondo
                            for i in range(len(df_p) + 1):
                                fig.add_shape(
                                    type="line", x0=i-0.5, x1=i-0.5, 
                                    y0=-0.45, y1=0, 
                                    xref="x", yref="paper",
                                    line=dict(color="#EEEEEE", width=1)
                                ) 
                
                            # Iteración para etiquetas y anotaciones
                            for i, r in df_p.iterrows():
                                # ETIQUETAS PARA $/KG
                                val_pkg_pp = r['Precio por Kg ($)']
                                txt_pkg_pp = f"${val_pkg_pp:,.0f}"
                
                                fig.add_annotation(
                                    x=i, y=r["Precio por Kg ($)"], 
                                    text=f"<b>{txt_pkg_pp}</b>", 
                                    yshift=15, 
                                    showarrow=False, 
                                    font=dict(size=t_pkg, color="#212121"),
                                    bgcolor="rgba(255,255,255,0.9)", 
                                    bordercolor="#616161", 
                                    borderwidth=1
                                )
                                
                                # ETIQUETAS PARA PRECIO DESEMBOLSO (Cajas Azules)
                                p_pp = r['Precio ($)']
                                txt_p_pp = f"${p_pp:.1f}" if p_pp < 10 else f"${int(p_pp)}"
                
                                fig.add_annotation(
                                    x=i, y=15, 
                                    text=f"<b>{txt_p_pp}</b>", 
                                    showarrow=False, 
                                    font=dict(size=t_precios, color="white"),
                                    bgcolor="#00B0F0", 
                                    bordercolor="black", 
                                    borderwidth=1.5,      
                                    borderpad=4
                                )
                            
                            # Agrupación visual por Canal en el eje X
                            for cat in df_p["Canal"].unique():
                                indices = df_p.index[df_p["Canal"] == cat].tolist()
                                center = (indices[0] + indices[-1]) / 2
                                fig.add_shape(
                                    type="line", x0=indices[-1]+0.5, x1=indices[-1]+0.5, 
                                    y0=-0.6, y1=1, xref="x", yref="paper", 
                                    line=dict(color="#CCCCCC", width=1.5) 
                                )
                                fig.add_annotation(
                                    x=center, y=-0.6, xref="x", yref="paper", 
                                    text=cat, 
                                    showarrow=False, 
                                    font=dict(size=14, color="#424242", family="Verdana")
                                )
                            
                            # Configuración de Layout (Ejes y Márgenes)
                            fig.update_layout(
                                height=alto_grafico,
                                margin=dict(b=margen_b, t=50, l=50, r=50),
                                template="plotly_white", 
                                xaxis=dict(
                                    tickmode='array', 
                                    tickvals=list(df_p.index), 
                                    ticktext=["<b>"+str(t)+"</b>" for t in df_p["Producto"]],
                                    tickangle=angulo_nombres,
                                    tickfont=dict(color="#000000", size=t_nombres, family="Verdana"),
                                    showgrid=False
                                ),
                                yaxis=dict(
                                    tickprefix="$", 
                                    showgrid=True, 
                                    gridcolor="#F5F5F5"
                                )
                            )
                    
                            # Renderizado con config de descarga
                            st.plotly_chart(fig, use_container_width=True, config={
                                'toImageButtonOptions': {
                                    'format': 'png',
                                    'filename': 'Price_Pack_Export',
                                    'height': alto_grafico,
                                    'width': 1950,
                                    'scale': 2
                                }
                            })
                        else:
                            st.info("Utiliza los filtros para visualizar los datos del Price Pack.")
                    else:
                        st.warning("La base de datos actual no corresponde al formato de Price Pack (Falta columna 'Canal').")
            
            # --- FIN DEL MODO PRICE PACK ---
                
# --- 8. COMPARATIVAS INDEX (UNIFICADO: LADDER + ARQUITECTURA PPT) ---
# Agregamos la condición para que esta sección solo se ejecute en los modos que usan Index
if modo != "Price and Volumen" and not st.session_state.data.empty:
    st.divider()
    df_comp = st.session_state.data.copy()
    
    # Limpieza estándar segura (solo si las columnas existen)
    for col in ["Precio ($)", "Precio por Kg ($)"]:
        if col in df_comp.columns:
            df_comp[col] = pd.to_numeric(df_comp[col], errors='coerce').fillna(0)

    # --- MODO 1: PRICE LADDER (COMPARATIVAS 1 A 1) ---
    if modo == "Price Ladder":
        st.subheader(f"📈 Comparativas Index ({modo})")
        df_comp["Lookup_Key"] = df_comp["Producto"]
        list_a = df_comp[df_comp["Fabricante"]=="BARCEL"]["Lookup_Key"].unique().tolist()
        list_b = df_comp[df_comp["Fabricante"]!="BARCEL"]["Lookup_Key"].unique().tolist()
        label_a, label_b = "Barcel", "Comp."

        if list_a and list_b:
            sel_cols = st.columns(4)
            selections = []
            for i in range(4):
                with sel_cols[i]:
                    s_a = st.selectbox(f"{label_a}", list_a, key=f"sa{i}")
                    idx_default = min(i+1, len(list_b)-1) if len(list_b) > 1 else 0
                    s_b = st.selectbox(f"{label_b}", list_b, key=f"sb{i}", index=idx_default)
                    selections.append((s_a, s_b))

            # Fila Desembolso
            st.markdown("### 💰 Index Desembolso")
            des_cols = st.columns(4)
            for i, (sel_a, sel_b) in enumerate(selections):
                v_a = df_comp[df_comp["Lookup_Key"] == sel_a]["Precio ($)"].iloc[0]
                v_b = df_comp[df_comp["Lookup_Key"] == sel_b]["Precio ($)"].iloc[0]
                idx = int((v_a / v_b * 100)) if v_b > 0 else 0
                color = "#0B3C8C" if idx <= 100 else "#D32F2F"
                with des_cols[i]:
                    st.markdown(f"""<div style="background:white; border:1px solid #ddd; border-top:5px solid {color}; border-radius:10px; padding:10px; text-align:center;">
                        <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#666; margin-bottom:5px;"><span>{sel_a}</span><span>{sel_b}</span></div>
                        <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:1.1rem; margin-bottom:10px;"><span>${v_a:.1f}</span><span style="color:#ccc; font-size:0.7rem;">vs</span><span>${v_b:.1f}</span></div>
                        <div style="font-size:1.8rem; font-weight:900; color:{color};">{idx}</div><div style="font-size:0.6rem; font-weight:bold; color:#999;">Index Desembolso</div></div>""", unsafe_allow_html=True)

            # Fila $/Kg
            st.markdown("### ⚖️ Index Precio por Kg")
            pkg_cols = st.columns(4)
            for i, (sel_a, sel_b) in enumerate(selections):
                v_a = df_comp[df_comp["Lookup_Key"] == sel_a]["Precio por Kg ($)"].iloc[0]
                v_b = df_comp[df_comp["Lookup_Key"] == sel_b]["Precio por Kg ($)"].iloc[0]
                idx = int((v_a / v_b * 100)) if v_b > 0 else 0
                color = "#0B3C8C" if idx <= 100 else "#D32F2F"
                with pkg_cols[i]:
                    st.markdown(f"""<div style="background:white; border:1px solid #ddd; border-top:5px solid {color}; border-radius:10px; padding:10px; text-align:center;">
                        <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#666; margin-bottom:5px;"><span>{sel_a}</span><span>{sel_b}</span></div>
                        <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:1.1rem; margin-bottom:10px;"><span>${int(v_a)}</span><span style="color:#ccc; font-size:0.7rem;">vs</span><span>${int(v_b)}</span></div>
                        <div style="font-size:1.8rem; font-weight:900; color:{color};">{idx}</div><div style="font-size:0.6rem; font-weight:bold; color:#999;">Index $/Kg</div></div>""", unsafe_allow_html=True)

    # --- MODO 2: MATRIZ DE ARQUITECTURA (VISTA PPT) / PRICE PACK ---
    else:
        # Encabezado con leyenda a la derecha
        col_tit, col_ley = st.columns([2, 1])
        with col_tit:
            st.markdown("<h2 style='color: #0B3C8C; margin:0;'>🏛️ Matriz de Arquitectura Multibase</h2>", unsafe_allow_html=True)
        with col_ley:
            st.markdown("""<div style='text-align:right; padding-top:10px;'><span style='background:#f0f2f6; padding:5px 10px; border-radius:5px; font-size:14px; color:#555; border:1px solid #ddd;'><b>Nota:</b> Index Objetivo vs Detalle (Base 100)</span></div>""", unsafe_allow_html=True)
        
        # 1. Identificar Bases de Detalle y Colores
        # Verificamos que la columna 'Canal' exista para evitar errores
        if "Canal" in df_comp.columns:
            skus_det_base = sorted(df_comp[df_comp["Canal"].str.upper() == "DETALLE"]["Producto"].unique().tolist())
            colores_disponibles = ["#27AE60", "#8E44AD", "#2980B9", "#E67E22", "#D32F2F", "#7F8C8D"]
            dict_colores_base = {sku: colores_disponibles[i % len(colores_disponibles)] for i, sku in enumerate(skus_det_base)}
            dict_valores_base = {sku: df_comp[(df_comp["Canal"].str.upper() == "DETALLE") & (df_comp["Producto"] == sku)]["Precio por Kg ($)"].mean() for sku in skus_det_base}

            if skus_det_base:
                with st.expander("⚙️ Configurar productos y bases de comparación"):
                    canales_ordenados = ["INSTITUCIONALES", "MAYOREO", "CLUBES", "AUTOSERVICIOS", "CONVENIENCIA"]
                    objetivos_canales = {"INSTITUCIONALES": "Index 60", "MAYOREO": "Index 70", "CLUBES": "Index 80", "AUTOSERVICIOS": "Index 110-120", "CONVENIENCIA": "Index 120-130"}
                    config_cols = st.columns(5)
                    selecciones_usuario = {}

                    for i, canal_n in enumerate(canales_ordenados):
                        with config_cols[i]:
                            st.markdown(f"**{canal_n}**")
                            prods_canal = sorted(df_comp[df_comp["Canal"].str.upper() == canal_n]["Producto"].unique().tolist())
                            seleccionados = st.multiselect(f"Seleccionar {canal_n}", prods_canal, key=f"ms_{canal_n}", label_visibility="collapsed")
                            lista_configs = []
                            for p in seleccionados:
                                base_sel = st.selectbox(f"Vs: {p}", skus_det_base, key=f"base_{canal_n}_{p}")
                                lista_configs.append((p, base_sel))
                            selecciones_usuario[canal_n] = lista_configs

                st.write("")
                viz_cols = st.columns(5)
                bases_usadas_en_reporte = set()

                for i, canal_n in enumerate(canales_ordenados):
                    with viz_cols[i]:
                        st.markdown(f"""
                            <div style="text-align:center; border-bottom:3px solid #0B3C8C; margin-bottom:15px; padding-bottom:8px;">
                                <div style="font-size:16px; font-weight:900; color:#333; text-transform:uppercase; letter-spacing:1px;">{canal_n}</div>
                                <div style="font-size:13px; color:#D32F2F; font-weight:bold; margin-top:4px;">{objetivos_canales.get(canal_n, '')}</div>
                            </div>
                        """, unsafe_allow_html=True)

                        for p_name, b_name in selecciones_usuario.get(canal_n, []):
                            val_item = df_comp[(df_comp["Canal"].str.upper() == canal_n) & (df_comp["Producto"] == p_name)]["Precio por Kg ($)"].mean()
                            val_base = dict_valores_base[b_name]
                            index_calc = int((val_item / val_base * 100)) if val_base > 0 else 0
                            color_pill = dict_colores_base[b_name]
                            bases_usadas_en_reporte.add(b_name)

                            st.markdown(f"""
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; min-height:40px;">
                                    <span style="font-size:13px; color:#222; font-weight:500; line-height:1.2; width:70%; font-family:Verdana;">{p_name}</span>
                                    <span style="background:{color_pill}; color:white; padding:4px 8px; border-radius:6px; font-weight:900; font-size:15px; min-width:45px; text-align:center; box-shadow: 1px 1px 3px rgba(0,0,0,0.15);">{index_calc}</span>
                                </div>
                            """, unsafe_allow_html=True)

                if bases_usadas_en_reporte:
                    leyenda_items = "".join([f'<div style="display:inline-block; margin-right:25px; margin-bottom:10px;"><span style="color:{dict_colores_base[b]}; font-size:20px; vertical-align:middle;">●</span> <span style="font-weight:bold; font-size:14px; color:#444;">Vs {b}</span></div>' for b in sorted(list(bases_usadas_en_reporte))])
                    st.markdown(f"""<div style="background:#F8F9FA; padding:15px; border-radius:8px; border:1px solid #CCC; margin-top:20px;"><div style="font-size:12px; font-weight:bold; color:#888; margin-bottom:10px; text-transform:uppercase;">Leyenda de Comparación (Bases Detalle):</div>{leyenda_items}</div>""", unsafe_allow_html=True)
            else:
                st.warning("No hay datos en el canal DETALLE para realizar comparaciones.")
        else:
            st.error("⚠️ El formato de datos actual no es compatible con la Matriz (Falta columna 'Canal').")

# --- FIN DE SECCIÓN 8 ---
        

# --- 10. PIRÁMIDE DE POSICIONAMIENTO (SOLO LADDER) ---
# Movimos el título y la lógica dentro del condicional para que no aparezca en Price Pack
if modo == "Price Ladder" and not st.session_state.data.empty:
    st.divider()
    
    # === CONTROL DE DESPLEGADO Y OPTIMIZACIÓN ===
    col_header_pyr, col_toggle_pyr = st.columns([3, 1])
    with col_header_pyr:
        st.subheader("🏔️ Pirámide de Posicionamiento por Tier de $ x KG")
    with col_toggle_pyr:
        activar_piramide = st.toggle("Activar Pirámide", value=False, help="Despliega el análisis de posicionamiento por Tiers.")

    if not activar_piramide:
        st.info("💡 La sección está contraída para mejorar el rendimiento. Activa el interruptor para ver los datos.")
    else:
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

        # Renderizado de la Pirámide
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
                    # Borde morado para destacar Barcel/Propuesta (Respetando G en nombres si aplica)
                    b_color = "#4B207E" if r["Fabricante"] in ["BARCEL", "PROPUESTA"] else "#CCCCCC"
                    
                    cards_html += f"""
                    <div style="display:inline-block; border: 2px solid {b_color}; border-radius: 10px; 
                    padding: 10px; background: white; min-width: 160px; margin: 5px; 
                    vertical-align: top; box-shadow: 1px 1px 3px rgba(0,0,0,0.1);">
                        <div style="font-weight:bold; font-size:0.9rem; color:#333; margin-bottom:4px;">{r['Producto']}</div>
                        <div style="color:#666; font-size:0.8rem;">Index: {int(r['Idx_P'])}</div>
                        <div style="font-weight:bold; font-size:1rem; color:#111; margin-top:4px;">${r['Precio ($)']:,.1f} ({int(r['Gramaje (g)'])}g)</div>
                    </div>"""
                
                with c2:
                    st.markdown(f'<div style="display: block; width: 100%;">{cards_html}</div>', unsafe_allow_html=True)
                st.write("")

# --- 11. MAPA DE VALOR ESTRATÉGICO (DISEÑO CLEAN) ---
if modo == "Price Ladder" and not st.session_state.data.empty:
    st.divider()
    
    # === CONTROL DE DESPLEGADO Y OPTIMIZACIÓN ===
    col_header_map, col_toggle_map = st.columns([3, 1])
    with col_header_map:
        st.markdown("<h3 style='margin:0; color: #0B3C8C;'>🏔️ Mapa de Posicionamiento: Desembolso vs. Eficiencia</h3>", unsafe_allow_html=True)
    with col_toggle_map:
        activar_mapa = st.toggle("Activar Mapa", value=False, help="Despliega el gráfico interactivo de dispersión.")

    if not activar_mapa:
        st.info("💡 La sección está contraída para mejorar el rendimiento. Activa el interruptor para ver los datos.")
    else:
        import plotly.express as px

        df_plot = st.session_state.data.copy()
        
        # 1. Asegurar formato numérico
        for c in ["Precio ($)", "Precio por Kg ($)", "SOM (%)"]:
            df_plot[c] = pd.to_numeric(df_plot[c], errors='coerce').fillna(0)

        # 2. Mapa de Colores
        color_map = {
            "BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", 
            "OTROS": "#7F8C8D", "PROPUESTA": "#4B207E"
        }

        def asignar_color(row):
            fab = str(row["Fabricante"]).upper()
            prod = str(row["Producto"]).upper()
            # Respetamos la G en la lógica de búsqueda si fuera necesario, aquí buscamos coincidencia de texto
            if "PROPUESTA" in prod or "SUGERIDO" in prod: return "PROPUESTA"
            if "BARCEL" in fab: return "BARCEL"
            if "SABRITAS" in fab or "PEPSICO" in fab: return "SABRITAS"
            return "OTROS"

        df_plot["Categoria_Color"] = df_plot.apply(asignar_color, axis=1)

        # 3. Filtro por Ocasión
        ocasiones = ["TODAS"] + sorted(df_plot["Ocasión"].unique().tolist())
        oca_selected = st.selectbox("🎯 Filtrar Ocasión:", ocasiones, key="filtro_oca_final_clean")
        
        if oca_selected != "TODAS":
            df_plot = df_plot[df_plot["Ocasión"] == oca_selected]

        if not df_plot.empty:
            # Ajuste de rangos para que no haya espacios vacíos
            y_min, y_max = df_plot["Precio ($)"].min() * 0.9, df_plot["Precio ($)"].max() * 1.1
            x_min, x_max = df_plot["Precio por Kg ($)"].min() * 0.9, df_plot["Precio por Kg ($)"].max() * 1.1

            fig = px.scatter(
                df_plot, x="Precio por Kg ($)", y="Precio ($)",
                size="SOM (%)", color="Categoria_Color",
                text="Producto", hover_name="Producto",
                color_discrete_map=color_map, size_max=40,
                custom_data=["SOM (%)", "Ocasión"]
            )

            # Estilo de etiquetas y burbujas
            fig.update_traces(
                textposition='top center',
                textfont=dict(family="Arial", size=10, color="#333"),
                marker=dict(line=dict(width=1.5, color='white'), opacity=0.9),
                hovertemplate="<b>%{hovertext}</b><br>Desembolso: $%{y:.1f}<br>Precio/Kg: $%{x:,.0f}<br>SOM: %{customdata[0]:.1f}%<extra></extra>"
            )

            # Configuración de Ejes
            fig.update_layout(
                template="plotly_white",
                height=700,
                xaxis=dict(
                    title="<b>EFICIENCIA ($/KG)</b>", tickprefix="$", 
                    range=[x_min, x_max], gridcolor="#F2F2F2"
                ),
                yaxis=dict(
                    title="<b>DESEMBOLSO (PRECIO $)</b>", tickprefix="$", 
                    range=[y_min, y_max], gridcolor="#F2F2F2"
                ),
                legend=dict(
                    title="", orientation="h", yanchor="bottom", 
                    y=1.02, xanchor="center", x=0.5
                )
            )

            # Líneas de referencia sutiles (Promedios)
            fig.add_vline(x=df_plot["Precio por Kg ($)"].mean(), line_dash="dot", line_color="#D1D1D1")
            fig.add_hline(y=df_plot["Precio ($)"].mean(), line_dash="dot", line_color="#D1D1D1")

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para la selección actual.")


# --- 12. ANALISTA MAESTRO INTEGRAL: LADDER ULTRA 2.6 + ARQUITECTURA PRO ---
# Ajuste: No mostrar en el modo de Volumen para evitar KeyErrors
if modo != "Price and Volumen" and not st.session_state.data.empty:
    st.divider()
    
    # 1. PREPARACIÓN DE DATOS (Común para ambos modos)
    df_p = st.session_state.data.copy()
    
    # Limpieza segura de columnas numéricas
    for c in ["Precio ($)", "SOM (%)", "Precio por Kg ($)", "Gramaje (g)"]:
        if c in df_p.columns:
            df_p[c] = pd.to_numeric(df_p[c], errors='coerce').fillna(0)

    # --- MODO A: PRICE LADDER (Tu Código Ultra 2.6 Completo) ---
    if modo == "Price Ladder":
        st.subheader("🚀 Sugerencias / Observaciones en base al Mercado")
        
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
            if "Ocasión" in df_p.columns:
                pesos_oca = df_p.groupby("Ocasión")["SOM (%)"].sum().to_dict()

                # --- BLOQUE A: ESTRATEGIA DE PORTAFOLIO (GAPS) ---
                if "Fabricante" in df_p.columns:
                    df_b_global = df_p[df_p["Fabricante"] == "BARCEL"].sort_values("Precio ($)")
                    if len(df_b_global) >= 2:
                        for i in range(len(df_b_global) - 1):
                            p1, p2 = df_b_global.iloc[i]["Precio ($)"], df_b_global.iloc[i+1]["Precio ($)"]
                            if (p2 - p1) > 10:
                                id_gap = f"GAP_{int(p1)}_{int(p2)}"
                                if id_gap not in vistos:
                                    p_sug = ajustar_precio_psicologico((p1 + p2) / 2)
                                    p1_txt, p2_txt, p_sug_txt = f"\${int(p1)}", f"\${int(p2)}", f"\${int(p_sug)}"
                                    hallazgos.append({
                                        "Prioridad": "BAJA", "Tipo": "ESCALÓN DE PRECIO", "Ocasión": "PORTAFOLIO GLOBAL",
                                        "Msg": f"Hueco detectado entre {p1_txt} y {p2_txt}",
                                        "Detalle": f"Salto de \${int(p2-p1)} en la escalera. Riesgo de fuga de transacciones.",
                                        "Accion": f"🪜 **Extensión:** Evaluar SKU de **{calcular_rango_g(p_sug, df_b_global.iloc[i]['Precio por Kg ($)'])}** a **{p_sug_txt}**."
                                    })
                                    vistos.add(id_gap)

                # --- BLOQUE B: ANÁLISIS TÁCTICO POR OCASIÓN ---
                for oca in df_p["Ocasión"].unique():
                    df_oca = df_p[df_p["Ocasión"] == oca].copy()
                    if "Fabricante" in df_oca.columns:
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
            else:
                st.warning("⚠️ El análisis de mercado requiere la columna 'Ocasión'.")
        except Exception as e: st.error(f"Error en Ultra 2.6: {e}")
    
    # --- MODO B: ARQUITECTURA DINÁMICA (Price Pack / Arquitectura) ---
    else:
        st.subheader("🏛️ Auditoría de Arquitectura y Cascada de Precios")
        hallazgos = [] 
        
        objetivos = {
            "INSTITUCIONALES": (55, 60), "MAYOREO": (61, 70), "CLUBES": (75, 82), 
            "AUTOSERVICIOS": (110, 120), "CONVENIENCIA": (121, 130)
        }

        # 1. Semáforo de Objetivos
        if 'selecciones_usuario' in locals() and "Canal" in df_p.columns:
            for canal, lista_prods in selecciones_usuario.items():
                min_obj, max_obj = objetivos.get(canal, (0, 200))
                for p_name, b_name in lista_prods:
                    f_target = df_p[(df_p["Canal"].str.upper() == canal) & (df_p["Producto"] == p_name)]
                    f_base = df_p[(df_p["Canal"].str.upper() == "DETALLE") & (df_p["Producto"] == b_name)]
                    
                    if not f_target.empty and not f_base.empty:
                        v_t = f_target["Precio por Kg ($)"].mean()
                        v_b = f_base["Precio por Kg ($)"].mean()
                        idx = int((v_t / v_b * 100)) if v_b > 0 else 0
                        
                        if idx < min_obj:
                            hallazgos.append({
                                "Prioridad": "ALTA", "Tipo": "BAJO INDEX", "Ocasión": canal,
                                "Msg": f"{p_name} está sub-valuado",
                                "Detalle": f"Index {idx} vs Base {b_name}. Objetivo min: {min_obj}.",
                                "Accion": f"💰 **Revenue:** Incrementar precio o reducir gramaje para alcanzar el corredor estratégico."
                            })
                        elif idx > max_obj:
                            hallazgos.append({
                                "Prioridad": "MEDIA", "Tipo": "SOBREPRECIO", "Ocasión": canal,
                                "Msg": f"{p_name} con riesgo de volumen",
                                "Detalle": f"Index {idx} vs Base {b_name}. Objetivo máx: {max_obj}.",
                                "Accion": f"⚠️ **Competitividad:** Evaluar si el valor agregado justifica el sobreprecio."
                            })

        # 2. Cascada de Gramaje
        if "Canal" in df_p.columns and "Gramaje (g)" in df_p.columns:
            for canal in df_p["Canal"].unique():
                if "Fabricante" in df_p.columns:
                    df_c = df_p[(df_p["Canal"] == canal) & (df_p["Fabricante"] == "BARCEL")].sort_values("Gramaje (g)")
                else:
                    df_c = df_p[df_p["Canal"] == canal].sort_values("Gramaje (g)")
                
                if len(df_c) >= 2:
                    for i in range(len(df_c) - 1):
                        p_chico, p_grande = df_c.iloc[i], df_c.iloc[i+1]
                        if p_grande["Precio por Kg ($)"] > p_chico["Precio por Kg ($)"] and p_chico["Gramaje (g)"] > 0:
                            hallazgos.append({
                                "Prioridad": "MEDIA",
                                "Tipo": "CURVA DE PRECIO",
                                "Ocasión": canal,
                                "Msg": f"Desviación en curva: {p_grande['Producto']}",
                                "Detalle": f"El SKU de {int(p_grande['Gramaje (g)'])}g presenta un $/Kg superior al formato de {int(p_chico['Gramaje (g)'])}g.",
                                "Accion": f"📉 **Arquitectura:** Optimizar la eficiencia de valor. El incremento en gramaje debe mejorar el costo por kilo."
                            })
        else:
            st.info("ℹ️ Para activar la auditoría de cascada, asegúrate de que el archivo contenga: Canal y Gramaje.")

    # --- RENDERIZADO VISUAL ÚNICO (Para ambos modos) ---
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
                    st.markdown(f"**{h['Msg']}**")
                    st.caption(h['Detalle'])
                with col_a:
                    st.success(f"🧪 **Sugerencia:**\n\n{h['Accion']}")
    else:
        st.balloons()
        st.success("✅ **Estrategia en Paridad Optimizada (Sin hallazgos críticos).**")


# --- 12. GENERADOR DE RESUMEN EJECUTIVO ESTRATÉGICO ---
# Ajuste: No mostrar en el modo de Volumen para evitar errores de compilación de hallazgos
if modo != "Price and Volumen" and not st.session_state.data.empty:
    st.divider()
    
    # Título dinámico según el modo
    btn_label = "📄 Generar Resumen de Mercado" if modo == "Price Ladder" else "🏛️ Generar Resumen de Arquitectura"
    
    if st.button(btn_label, key="btn_exec_v4"):
        with st.spinner("Compilando diagnóstico..."):
            
            # Verificamos si existen hallazgos (esta variable viene de la sección anterior)
            if 'hallazgos' not in locals() or not hallazgos:
                st.success("✅ **Estado Óptimo:** No se detectan desviaciones en la estrategia actual.")
            else:
                st.markdown("""
                    <style>
                    .exec-box {
                        background-color: #ffffff; padding: 30px; border-radius: 12px;
                        border: 1px solid #d1d1d1; box-shadow: 4px 4px 15px rgba(0,0,0,0.05);
                        color: #1a1a1a;
                    }
                    .rival-name { font-weight: bold; color: #d32f2f; }
                    .barcel-blue { font-weight: bold; color: #003399; }
                    </style>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="exec-box">', unsafe_allow_html=True)
                
                # --- CASO A: RESUMEN PRICE LADDER ---
                if modo == "Price Ladder":
                    st.subheader("📝 Resumen Ejecutivo: Estrategia de Portafolio")
                    num_alta = len([h for h in hallazgos if h["Prioridad"] == "ALTA"])
                    st.write(f"Se han identificado **{len(hallazgos)} hallazgos estratégicos**, con **{num_alta} alertas críticas**.")

                    # Oportunidades (White Spaces)
                    ws_items = [h for h in hallazgos if h["Tipo"] == "WHITE SPACE"]
                    if ws_items:
                        st.markdown("#### 🚀 Expansión de Portafolio")
                        for ws in ws_items:
                            # Extracción segura de datos del string de detalle
                            rival = ws['Detalle'].split('dominado por ')[-1].replace('.', '')
                            sug_data = ws['Accion'].replace("⚡ **Entrada:** Lanzar ", "")
                            st.write(f"* **{ws['Ocasión']}:** Barcel no participa. Dominio de <span class='rival-name'>{rival}</span>. Acción: Introducir SKU de **{sug_data}**.", unsafe_allow_html=True)

                    # Competitividad (Duelos)
                    duelos = [h for h in hallazgos if "DUELO" in h["Tipo"]]
                    if duelos:
                        st.markdown("#### 🛡️ Ajustes de Paridad (Defensa)")
                        for d in duelos:
                            rival = d['Tipo'].replace("DUELO vs ", "")
                            sug_data = d['Accion'].replace("⚖️ **R&D:** Ajustar a ", "")
                            st.write(f"* **{d['Ocasión']}:** {d['Msg']} vs <span class='rival-name'>{rival}</span>. Rec: {sug_data}.", unsafe_allow_html=True)

                    st.markdown("---")
                    st.write("**💡 Veredicto:** Priorizar blindaje en segmentos donde el rival tiene ventaja competitiva en gramaje.")

                # --- CASO B: RESUMEN ARQUITECTURA PRO ---
                else:
                    st.subheader("📝 Diagnóstico de Arquitectura y Curva de Precios")
                    st.write(f"Se detectaron **{len(hallazgos)} puntos de atención** en la estructura interna de precios.")

                    # 1. Curva de Precio (Cascada)
                    curvas = [h for h in hallazgos if h["Tipo"] == "CURVA DE PRECIO"]
                    if curvas:
                        st.markdown("#### 📉 Eficiencia en Curva de Precios")
                        for c in curvas:
                            st.write(f"* **{c['Ocasión']}:** {c['Msg']}. {c['Detalle']}")
                            st.caption(f"↳ Sugerencia: {c['Accion']}")

                    # 2. Corredores Estratégicos (Index)
                    indices = [h for h in hallazgos if h["Tipo"] in ["BAJO INDEX", "SOBREPRECIO"]]
                    if indices:
                        st.markdown("#### 💰 Corredores por Canal (vs Detalle)")
                        for i in indices:
                            color_tag = "🔴" if i["Prioridad"] == "ALTA" else "🟡"
                            # Intento de extracción de Index para el resumen
                            try:
                                valor_idx = i['Detalle'].split('Index ')[1].split(' vs')[0]
                            except:
                                valor_idx = "N/A"
                            st.write(f"{color_tag} **{i['Ocasión']}:** {i['Msg']}. (Index {valor_idx})")

                    st.markdown("---")
                    st.write("**💡 Veredicto Interno:** Asegurar la consistencia de la curva para incentivar el 'upsize' y proteger la rentabilidad de los canales estratégicos.")

                st.markdown('</div>', unsafe_allow_html=True)




# --- 14. SIMULADOR ESTRATÉGICO DIRECTIVO (V6.1: VARIACIONES % + AJUSTE GRAMAJE + SNAPSHOTS) ---
if modo == "Price Ladder" and not st.session_state.data.empty:
    st.divider()
    
    # === CONTROL DE DESPLEGADO Y OPTIMIZACIÓN ===
    col_header_sim, col_toggle_sim = st.columns([3, 1])
    with col_header_sim:
        st.subheader("🧪 Simulador de Escenarios: Paridad y Eficiencia")
    with col_toggle_sim:
        activar_simulador = st.toggle("Activar Simulador", value=False, help="Habilita las herramientas de simulación de precios y gramajes.")

    if not activar_simulador:
        st.info("💡 La sección está contraída para mejorar el rendimiento. Activa el interruptor para ver los datos.")
    else:
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
                # Respeto a G en Barcel
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

# SIZE IMPRESSION
if modo == "Price Ladder":
    # === 0. INICIALIZACIÓN DE ESTADO ===
    if 'df_arq_sim' not in st.session_state:
        if 'df_arq' in locals() and not df_arq.empty:
            st.session_state.df_arq_sim = df_arq.copy()
        else:
            st.session_state.df_arq_sim = pd.DataFrame(columns=[
                "Producto", "Fabricante", "Marca", "Canal", "Ocasión de Consumo", "Ancho (cm)", "Alto (cm)"
            ])

    st.divider()
    
    # === CONTROL DE DESPLEGADO Y OPTIMIZACIÓN ===
    col_header, col_toggle = st.columns([3, 1])
    with col_header:
        st.subheader("📐 SIZE IMPRESSION")
    with col_toggle:
        # Interruptor maestro para plegar/desplegar y evitar carga innecesaria
        activar_seccion = st.toggle("Activar Módulo", value=False, help="Despliega la simulación y carga los datos.")

    if not activar_seccion:
        st.info("💡 La sección está contraída para mejorar el rendimiento. Activa el interruptor para ver los datos.")
    else:
        # === 1. FORMULARIO DE ALTA (NUEVO SKU) ===
        with st.expander("➕ Añadir un Nuevo SKU en la Simulación", expanded=False):
            with st.form("nuevo_sku_form"):
                c1, c2, c3 = st.columns(3)
                nuevo_p = c1.text_input("Nombre Completo (Producto)", placeholder="Ej. Takis Fuego 240g")
                nuevo_m = c2.text_input("Marca", placeholder="Ej. TAKIS")
                nuevo_f = c3.selectbox("Fabricante", ["BARCEL", "SABRITAS", "OTROS"])
                
                c4, c5, c6 = st.columns(3)
                nuevo_c = c4.text_input("Canal", value="AUTOSERVICIO")
                nuevo_o = c5.selectbox("Ocasión de Consumo", ["Bites", "Individual", "Hambre", "Compartir", "Familiar", "Reunión", "Fiesta", "Transformador"])
                nuevo_ancho = c6.number_input("Ancho (cm)", min_value=1.0, step=0.1)
                
                nuevo_alto = st.number_input("Alto (cm)", min_value=1.0, step=0.1)
                
                if st.form_submit_button("🚀 Registrar SKU"):
                    # Aplicamos la G mayúscula al producto
                    nuevo_p_fmt = nuevo_p.capitalize()
                    nueva_fila = {
                        "Producto": nuevo_p_fmt, "Fabricante": nuevo_f, "Marca": nuevo_m,
                        "Canal": nuevo_c, "Ocasión de Consumo": nuevo_o,
                        "Ancho (cm)": nuevo_ancho, "Alto (cm)": nuevo_alto
                    }
                    st.session_state.df_arq_sim = pd.concat([st.session_state.df_arq_sim, pd.DataFrame([nueva_fila])], ignore_index=True)
                    st.success(f"Producto {nuevo_p_fmt} añadido correctamente.")
                    st.rerun()

        # === 2. FILTROS AVANZADOS DINÁMICOS (VACÍOS POR DEFECTO PARA VELOCIDAD) ===
        with st.container(border=True):
            col_t1, col_t2 = st.columns([4, 1])
            col_t1.markdown("**Filtros Globales de Visualización**")
            
            if col_t2.button("🔄 Reset Filtros", use_container_width=True):
                st.rerun()
            
            df_base = st.session_state.df_arq_sim
            
            r1_c1, r1_c2, r1_c3 = st.columns(3)
            # Iniciamos en [] para que el usuario elija y no se sature la app
            sel_fab = r1_c1.multiselect("Fabricante", df_base["Fabricante"].unique(), default=[])
            
            df_can = df_base[df_base["Fabricante"].isin(sel_fab)]
            sel_can = r1_c2.multiselect("Canal", df_can["Canal"].unique(), default=[])
            
            df_mar = df_can[df_can["Canal"].isin(sel_can)]
            sel_marcas = r1_c3.multiselect("Marcas", df_mar["Marca"].unique(), default=[])
            
            r2_c1, r2_c2 = st.columns(2)
            df_oca = df_mar[df_mar["Marca"].isin(sel_marcas)]
            sel_ocasiones = r2_c1.multiselect("Ocasiones", df_oca["Ocasión de Consumo"].unique(), default=[])
            
            df_prod = df_oca[df_oca["Ocasión de Consumo"].isin(sel_ocasiones)]
            sel_productos = r2_c2.multiselect("Productos específicos", df_prod["Producto"].unique(), default=[])

        # --- LÓGICA DE FILTRADO ---
        df_filtered = df_base[
            (df_base["Fabricante"].isin(sel_fab)) & 
            (df_base["Canal"].isin(sel_can)) & 
            (df_base["Marca"].isin(sel_marcas)) & 
            (df_base["Ocasión de Consumo"].isin(sel_ocasiones)) &
            (df_base["Producto"].isin(sel_productos))
        ].copy()
        
        if df_filtered.empty:
            st.warning("⚠️ Selecciona filtros para visualizar la tabla y el gráfico.")
        else:
            # Agregamos columna de selección
            df_filtered.insert(0, "Seleccionar", False)
            
            # Editor Dinámico
            df_editado = st.data_editor(
                df_filtered,
                column_order=("Seleccionar", "Producto", "Marca", "Fabricante", "Canal", "Ocasión de Consumo", "Ancho (cm)", "Alto (cm)"),
                hide_index=True, 
                use_container_width=True, 
                key="editor_v5_1"
            )
            
            # Acciones
            c_save, c_del = st.columns(2)
            if c_save.button("💾 Guardar Cambios en Dimensiones", use_container_width=True, type="primary"):
                for _, row in df_editado.iterrows():
                    st.session_state.df_arq_sim.loc[st.session_state.df_arq_sim["Producto"] == row["Producto"], ["Ancho (cm)", "Alto (cm)"]] = [row["Ancho (cm)"], row["Alto (cm)"]]
                st.success("¡Dimensiones actualizadas!")
                st.rerun()
            
            if c_del.button("🗑️ Eliminar Productos Seleccionados", use_container_width=True):
                productos_a_eliminar = df_editado[df_editado["Seleccionar"] == True]["Producto"].tolist()
                if productos_a_eliminar:
                    st.session_state.df_arq_sim = st.session_state.df_arq_sim[~st.session_state.df_arq_sim["Producto"].isin(productos_a_eliminar)].copy()
                    st.rerun()

            # === 3. COMPARADOR 1 VS 1 ===
            st.markdown("#### ⚖️ Comparativa de Size Impression Index")
            with st.container(border=True):
                col_sel1, col_sel2 = st.columns(2)
                with col_sel1:
                    prod_base = st.selectbox("Producto 1 (Base 100)", st.session_state.df_arq_sim["Producto"].unique(), key="sb_1")
                with col_sel2:
                    prod_comp = st.selectbox("Producto 2 (Comparativo)", st.session_state.df_arq_sim["Producto"].unique(), key="sb_2")
                
                # Obtención de datos
                d1 = st.session_state.df_arq_sim[st.session_state.df_arq_sim["Producto"] == prod_base].iloc[0]
                d2 = st.session_state.df_arq_sim[st.session_state.df_arq_sim["Producto"] == prod_comp].iloc[0]
                
                # Cálculo de áreas e Index
                a1 = d1["Ancho (cm)"] * d1["Alto (cm)"]
                a2 = d2["Ancho (cm)"] * d2["Alto (cm)"]
                index_val = (a2 / a1) * 100
                delta = index_val - 100
            
                # === LÓGICA DE COLOR: POSITIVO SI SOBRE-INDEXA ===
                # Verde si el comparativo es más grande (>100), Rojo si es más pequeño (<100)
                color_exito = "#28a745" if index_val >= 100 else "#d32f2f"
                bg_exito = "#f0fff4" if index_val >= 100 else "#fff5f5"
            
                _, col_card, _ = st.columns([1, 2, 1])
                
                with col_card:
                    st.markdown(f"""
                        <div style="
                            background-color: white;
                            padding: 15px 25px;
                            border-radius: 12px;
                            border-top: 5px solid {color_exito};
                            box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
                            text-align: center;
                            margin: 10px auto;
                            max-width: 400px;
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 5px;">
                                <div style="text-align: left; width: 42%;">
                                    <p style="margin: 0; color: #777; font-size: 0.75rem; line-height: 1.1;">{prod_base}</p>
                                    <h4 style="margin: 2px 0; color: #333; font-weight: bold; font-size: 1.1rem;">{a1:,.0f} <span style="font-size: 0.7rem;">cm²</span></h4>
                                </div>
                                <div style="color: #bbb; font-size: 0.8rem; margin-top: 15px; font-weight: bold;">vs</div>
                                <div style="text-align: right; width: 42%;">
                                    <p style="margin: 0; color: #777; font-size: 0.75rem; line-height: 1.1;">{prod_comp}</p>
                                    <h4 style="margin: 2px 0; color: #333; font-weight: bold; font-size: 1.1rem;">{a2:,.0f} <span style="font-size: 0.7rem;">cm²</span></h4>
                                </div>
                            </div>
                            <div style="margin-top: 10px;">
                                <h1 style="margin: 0; color: {color_exito}; font-size: 3rem; font-weight: 800; line-height: 1;">{index_val:.0f}</h1>
                                <p style="margin: 2px 0; color: #666; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">Index Size Impression</p>
                                <div style="
                                    display: inline-block;
                                    margin-top: 8px;
                                    padding: 4px 12px;
                                    border-radius: 15px;
                                    background-color: {bg_exito};
                                    color: {color_exito};
                                    font-size: 0.9rem;
                                    font-weight: bold;
                                ">
                                    {'▲' if delta >= 0 else '▼'} {abs(delta):.1f}% <span style="font-weight: normal; font-size: 0.8rem;">vs base</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            # === GRÁFICO TÉCNICO ADAPTATIVO CON NAVEGACIÓN MEJORADA ===
            if not df_editado.empty:
                df_editado['Area'] = df_editado['Ancho (cm)'] * df_editado['Alto (cm)']
                # Aseguramos la G mayúscula en el nombre de los productos
                df_editado['Producto'] = df_editado['Producto'].str.upper()
                
                orden_o = ["Bites", "Individual", "Hambre", "Compartir", "Familiar", "Reunión", "Fiesta", "Transformador"]
                df_editado['Ocasión de Consumo'] = pd.Categorical(df_editado['Ocasión de Consumo'], categories=orden_o, ordered=True)
                df_viz = df_editado.sort_values(['Ocasión de Consumo', 'Area'])
            
                # === CONTROLES DE VISUALIZACIÓN MEJORADOS ===
                st.markdown("#### ⚙️ Controles de Visualización")
                
                col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns(4)
                
                with col_ctrl1:
                    escala_base = st.slider("📏 Escala Base", 20, 80, 45, step=5, 
                                           help="Aumenta para hacer los empaques más grandes")
                with col_ctrl2:
                    gap_productos = st.slider("↔️ Separación", 5, 30, 12, 
                                             help="Espacio entre productos")
                with col_ctrl3:
                    modo_vista = st.selectbox("👁️ Modo Vista", 
                                              ["Automático", "Compacto", "Expandido", "Ultra Grande"])
                with col_ctrl4:
                    zoom_nivel = st.selectbox("🔍 Zoom Inicial",
                                              ["100%", "125%", "150%", "175%", "200%"],
                                              index=0)
            
                # === CÁLCULO DE ESCALA INTELIGENTE ===
                num_productos = len(df_viz)
                
                if modo_vista == "Automático":
                    if num_productos <= 3:
                        PX_UNIT = escala_base * 1.5
                    elif num_productos <= 6:
                        PX_UNIT = escala_base * 1.2
                    elif num_productos <= 10:
                        PX_UNIT = escala_base
                    else:
                        PX_UNIT = escala_base * 0.8
                elif modo_vista == "Compacto":
                    PX_UNIT = escala_base * 0.6
                elif modo_vista == "Expandido":
                    PX_UNIT = escala_base * 1.3
                else:
                    PX_UNIT = escala_base * 2
                
                # Aplicar zoom inicial
                zoom_multiplier = float(zoom_nivel.replace("%", "")) / 100
                PX_UNIT = PX_UNIT * zoom_multiplier
            
                # === CONSTRUCCIÓN DEL GRÁFICO ===
                fig = go.Figure()
                colors = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D", "PROPUESTA": "#4B207E"}
                
                x_ptr = 0
                max_h = df_viz['Alto (cm)'].max()
                
                font_size_producto = max(12, int(PX_UNIT * 0.3))
                font_size_medidas = max(10, int(PX_UNIT * 0.25))
                font_size_area = max(16, int(PX_UNIT * 0.4))
                
                last_ocasion = None
                ocasion_positions = {}
            
                for i, (_, r) in enumerate(df_viz.iterrows()):
                    w, h = r['Ancho (cm)'], r['Alto (cm)']
                    area = r['Area']
                    c = colors.get(str(r['Fabricante']).upper(), "#7F8C8D")
                    
                    if r['Ocasión de Consumo'] not in ocasion_positions:
                        ocasion_positions[r['Ocasión de Consumo']] = {'start': x_ptr, 'end': x_ptr + w}
                    else:
                        ocasion_positions[r['Ocasión de Consumo']]['end'] = x_ptr + w
                    
                    # === EMPAQUE CON EFECTO 3D ===
                    fig.add_shape(
                        type="rect", 
                        x0=x_ptr, y0=0, x1=x_ptr+w, y1=h, 
                        line=dict(color=c, width=3), 
                        fillcolor=c, 
                        opacity=0.15
                    )
                    
                    # === SOMBRA MEJORADA ===
                    for offset in [0.15, 0.25, 0.35]:
                        fig.add_shape(
                            type="rect", 
                            x0=x_ptr+offset, y0=-offset, x1=x_ptr+w+offset, y1=h-offset,
                            line=dict(width=0), 
                            fillcolor="black", 
                            opacity=0.03, 
                            layer="below"
                        )
                    
                    # === NOMBRE DEL PRODUCTO CON FONDO ===
                    fig.add_annotation(
                        x=x_ptr+w/2, 
                        y=h+1.5, 
                        text=f"<b>{r['Producto']}</b>", 
                        showarrow=False, 
                        font=dict(size=font_size_producto, color="#222", family="Arial Black"), 
                        bgcolor="rgba(255,255,255,0.9)",
                        bordercolor="#DDD",
                        borderwidth=1,
                        borderpad=4,
                        yanchor="bottom"
                    )
                    
                    # === LÍNEAS MEDIDORAS ANCHO ===
                    fig.add_shape(type="line", x0=x_ptr, y0=-0.8, x1=x_ptr+w, y1=-0.8, line=dict(color="#333", width=2))
                    fig.add_shape(type="line", x0=x_ptr, y0=-1.2, x1=x_ptr, y1=-0.4, line=dict(color="#333", width=2))
                    fig.add_shape(type="line", x0=x_ptr+w, y0=-1.2, x1=x_ptr+w, y1=-0.4, line=dict(color="#333", width=2))
                    fig.add_annotation(
                        x=x_ptr+w/2, y=-2.2, text=f"<b>{w}cm</b>", 
                        showarrow=False, font=dict(size=font_size_medidas, color="#333"), yanchor="top"
                    )
                    
                    # === LÍNEAS MEDIDORAS ALTO ===
                    fig.add_shape(type="line", x0=x_ptr-0.8, y0=0, x1=x_ptr-0.8, y1=h, line=dict(color="#333", width=2))
                    fig.add_shape(type="line", x0=x_ptr-1.2, y0=0, x1=x_ptr-0.4, y1=0, line=dict(color="#333", width=2))
                    fig.add_shape(type="line", x0=x_ptr-1.2, y0=h, x1=x_ptr-0.4, y1=h, line=dict(color="#333", width=2))
                    fig.add_annotation(
                        x=x_ptr-2, y=h/2, text=f"<b>{h}cm</b>", textangle=-90, 
                        showarrow=False, font=dict(size=font_size_medidas, color="#333"), xanchor="right"
                    )
                    
                    # === ÁREA EN EL CENTRO (SOLO TEXTO REFORZADO) ===
                    fig.add_annotation(
                        x=x_ptr+w/2, y=h/2, 
                        text=f"<b>{area:.0f}</b><br><span style='font-size:{int(font_size_area*0.6)}px;'>cm²</span>", 
                        showarrow=False, 
                        font=dict(size=font_size_area, color=c, family="Arial Black"), 
                        align="center"
                    )
                    
                    # === SEPARADOR DE OCASIÓN ===
                    if r['Ocasión de Consumo'] != last_ocasion and i > 0:
                        fig.add_shape(
                            type="line", x0=x_ptr-(gap_productos/2), y0=-3, x1=x_ptr-(gap_productos/2), y1=max_h+4,
                            line=dict(color="#0B3C8C", width=2, dash="dot")
                        )
                    
                    last_ocasion = r['Ocasión de Consumo']
                    x_ptr += w + gap_productos
            
                # === ETIQUETAS DE OCASIÓN CON BADGE STYLE ===
                for ocasion, pos in ocasion_positions.items():
                    center_x = (pos['start'] + pos['end']) / 2
                    fig.add_annotation(
                        x=center_x, y=-4.5, text=f"<b>{ocasion}</b>", showarrow=False,
                        font=dict(size=max(14, int(PX_UNIT * 0.32)), color="white", family="Arial Black"),
                        bgcolor="#0B3C8C",
                        bordercolor="#1976D2",
                        borderwidth=2,
                        borderpad=6,
                        yanchor="top"
                    )
            
                # === CANVAS DIMENSIONES ===
                ancho_contenido = x_ptr
                margen_lateral = 5
                alto_canvas = max_h + 10
                
                canvas_width_px = int((ancho_contenido + margen_lateral * 2) * PX_UNIT)
                canvas_height_px = int(alto_canvas * PX_UNIT)
                canvas_width_px = max(600, min(canvas_width_px, 4000))
                canvas_height_px = max(350, min(canvas_height_px, 1200))
            
                # === LAYOUT ===
                fig.update_layout(
                    width=canvas_width_px,
                    height=canvas_height_px,
                    template="plotly_white",
                    showlegend=False,
                    margin=dict(l=20, r=20, t=20, b=20),
                    xaxis=dict(
                        range=[-margen_lateral-3, ancho_contenido + 2],
                        showgrid=False,
                        zeroline=False,
                        showticklabels=False,
                        fixedrange=False
                    ),
                    yaxis=dict(
                        range=[-12, max_h + 10],
                        showgrid=False,
                        zeroline=False,
                        showticklabels=False,
                        scaleanchor="x", 
                        scaleratio=1,
                        fixedrange=False
                    ),
                    dragmode='pan',
                    hovermode='closest'
                )
                
                # === CONTENEDOR DEL GRÁFICO (CON BORDE Y SOMBRA) ===
                st.markdown(
                    """
                    <div style="
                        background: #ffffff;
                        padding: 15px;
                        border-radius: 12px;
                        border: 2px solid #e0e4e9;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                        margin: 10px 0;
                        overflow-x: auto;
                    ">
                    """,
                    unsafe_allow_html=True
                )
                
                st.plotly_chart(
                    fig, 
                    use_container_width=False,
                    config={
                        'displayModeBar': True,
                        'modeBarButtonsToAdd': ['pan2d', 'zoomIn2d', 'zoomOut2d', 'resetScale2d', 'toImage'],
                        'scrollZoom': True,
                        'displaylogo': False,
                        'toImageButtonOptions': {
                            'format': 'png',
                            'filename': 'arquitectura_empaque_barcel',
                            'height': canvas_height_px,
                            'width': canvas_width_px,
                            'scale': 3
                        }
                    }
                )
                
                # Cerrar el div del contenedor
                st.markdown('</div>', unsafe_allow_html=True)
            
                # === LÍNEA VERDE DIVISORIA ===
                st.markdown('<hr style="border: 2px solid #28a745; border-radius: 5px; margin: 30px 0;">', unsafe_allow_html=True)


            # === GUÍA COMPLETA ===
            with st.expander("🎮 Guía Completa de Controles y Elementos"):
                col_g1, col_g2, col_g3 = st.columns(3)
                
                with col_g1:
                    st.markdown("""
                    **🖱️ Controles del Mouse:**
                    - Arrastrar: Mover vista
                    - Rueda: Zoom in/out
                    - Doble Click: Reset
                    
                    **⚙️ Barra Superior:**
                    - 🏠 Vista inicial
                    - 🔍 Zoom +/-
                    - 📸 Exportar PNG
                    """)
                
                with col_g2:
                    st.markdown("""
                    **🎨 Elementos Visuales:**
                    - Líneas Negras: Medidores
                    - Texto Central: Área cm²
                    - Badges Azules: Ocasiones
                    - Sombras: Profundidad 3D
                    """)
                
                with col_g3:
                    st.markdown("""
                    **💡 Tips Pro:**
                    - Aumenta "Escala Base" para agrandar
                    - "Zoom Inicial" 150% para presentar
                    - "Ultra Grande" para proyector
                    """)

if modo == "Price and Volumen":
    if st.session_state.data.empty:
        st.info("ℹ️ Por favor, selecciona una plantilla en la barra lateral y presiona 'Cargar Datos'.")
    else:
        st.success(f"✅ Datos cargados: {len(st.session_state.data)} registros encontrados.")
        # Opcional: mostrar una vista previa pequeña
        with st.expander("Ver vista previa de datos"):
            st.dataframe(st.session_state.data.head())
            
# --- 15. ANÁLISIS DE ELASTICIDAD: PRICE & VOLUME ---
if modo == "Price and Volumen" and not st.session_state.data.empty:
    st.divider()
    st.subheader("📈 Análisis de Tendencias y Elasticidad")

    df_pv = st.session_state.data.copy()
    columnas_necesarias = ["Producto", "Semana", "Venta Valor ($)", "Venta Volumen (Pzas)", "Precio ($)"]
    
    if all(col in df_pv.columns for col in columnas_necesarias):
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            lista_prods = sorted(df_pv["Producto"].unique())
            prod_sel = st.selectbox("Seleccionar Producto:", lista_prods)
        with c_f2:
            min_sem, max_sem = int(df_pv["Semana"].min()), int(df_pv["Semana"].max())
            rango_sem = st.slider("Rango de Semanas para Gráfico:", min_sem, max_sem, (min_sem, max_sem))

        mask = (df_pv["Producto"] == prod_sel) & (df_pv["Semana"].between(rango_sem[0], rango_sem[1]))
        df_filtrado = df_pv[mask].sort_values("Semana")

        if not df_filtrado.empty:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots

            # --- CORRECCIÓN DE ALINEACIÓN ---
            # Definimos márgenes laterales fijos para AMBOS gráficos
            m_lat = 80 
            margen_alineado = dict(l=m_lat, r=m_lat, t=20, b=20)

            # 1. Gráfico Base (Volumen y Valor)
            fig_perf = make_subplots(specs=[[{"secondary_y": True}]])
            fig_perf.add_trace(go.Scatter(
                x=df_filtrado["Semana"], y=df_filtrado["Venta Valor ($)"],
                name="Venta Valor ($)", fill='tozeroy', mode='lines',
                line=dict(color='#76D7C4', width=2), fillcolor='rgba(118, 215, 196, 0.3)'
            ), secondary_y=True)
            fig_perf.add_trace(go.Bar(
                x=df_filtrado["Semana"], y=df_filtrado["Venta Volumen (Pzas)"],
                name="Volumen (Pzas)", marker_color='#002366'
            ), secondary_y=False)

            fig_perf.update_layout(
                height=450, template="plotly_white", margin=margen_alineado,
                legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5),
                barmode='overlay'
            )
            fig_perf.update_yaxes(title_text="Volumen", secondary_y=False)
            fig_perf.update_yaxes(title_text="Venta Valor", secondary_y=True)

            # 2. Gráfico Superior (Precio) - Forzamos estructura idéntica
            fig_price = make_subplots(specs=[[{"secondary_y": True}]]) # Aunque no lo usemos, iguala el espacio del eje R
            fig_price.add_trace(go.Scatter(
                x=df_filtrado["Semana"], y=df_filtrado["Precio ($)"],
                name="Precio Unitario ($)", line=dict(color='#F72585', width=4),
                mode='lines+markers+text',
                text=df_filtrado["Precio ($)"].apply(lambda x: f"${x:.1f}"),
                textposition="top center",
                marker=dict(size=12, symbol='circle', color='#F72585', line=dict(width=2, color='white'))
            ), secondary_y=False)

            fig_price.update_layout(
                height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=margen_alineado, xaxis=dict(visible=False),
                showlegend=False
            )
            # Sincronizamos los ejes Y para que el área de dibujo sea igual
            fig_price.update_yaxes(title_text="Precio ($)", color="#F72585", secondary_y=False,
                                 range=[df_filtrado["Precio ($)"].min()*0.8, df_filtrado["Precio ($)"].max()*1.6])
            fig_price.update_yaxes(title_text="", secondary_y=True, showticklabels=False)

            # --- RENDERIZADO CON CSS ---
            st.markdown("""
                <style>
                .price-overlay { margin-top: -340px; position: relative; z-index: 99; pointer-events: none; }
                .price-overlay .js-plotly-plot .plotly .main-svg { background: transparent !important; }
                </style>
                """, unsafe_allow_html=True)

            st.plotly_chart(fig_perf, use_container_width=True)
            st.markdown('<div class="price-overlay">', unsafe_allow_html=True)
            st.plotly_chart(fig_price, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # --- CALCULADORA DE ELASTICIDAD ---
            st.markdown("### 🧮 Calculadora de Variación Periodo a Periodo")
            with st.expander("Configurar análisis de variación", expanded=True):
                col_calc1, col_calc2, col_calc3 = st.columns(3)
                with col_calc1:
                    sem_base = st.selectbox("Semana Base (Origen):", df_filtrado["Semana"].unique())
                with col_calc2:
                    sem_target = st.selectbox("Semana Objetivo (Comparar):", 
                                            [s for s in df_filtrado["Semana"].unique() if s != sem_base])
                
                # Obtención de datos
                d_base = df_filtrado[df_filtrado["Semana"] == sem_base].iloc[0]
                d_target = df_filtrado[df_filtrado["Semana"] == sem_target].iloc[0]

                # Cálculos
                var_p = (d_target["Precio ($)"] / d_base["Precio ($)"] - 1)
                var_v = (d_target["Venta Volumen (Pzas)"] / d_base["Venta Volumen (Pzas)"] - 1)
                var_val = (d_target["Venta Valor ($)"] / d_base["Venta Valor ($)"] - 1)
                
                # Elasticidad Arco Simple
                elasticidad = var_v / var_p if var_p != 0 else 0

                # Mostrar Resultados
                res1, res2, res3, res4 = st.columns(4)
                res1.metric(f"Δ% Precio", f"{var_p:.1%}")
                res2.metric(f"Δ% Volumen", f"{var_v:.1%}")
                res3.metric(f"Δ% Valor $", f"{var_val:.1%}")
                
                color_e = "normal" if abs(elasticidad) < 1 else "inverse"
                res4.metric("Elasticidad Calc.", f"{elasticidad:.2f}", 
                           help="Mayor a 1 (absoluto) indica alta sensibilidad", delta_color=color_e)

            # --- MÉTRICAS GENERALES ---
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Volumen Total", f"{df_filtrado['Venta Volumen (Pzas)'].sum():,}")
            m2.metric("Venta Total", f"${df_filtrado['Venta Valor ($)'].sum():,.0f}")
            m3.metric("Precio Promedio", f"${df_filtrado['Precio ($)'].mean():.2f}")
            if len(df_filtrado) > 1:
                corr = df_filtrado["Precio ($)"].corr(df_filtrado["Venta Volumen (Pzas)"])
                m4.metric("Corr. Precio/Vol", f"{corr:.2f}")
        else:
            st.warning("No hay datos para los filtros.")
    else:
        st.error("Faltan columnas necesarias en el archivo.")
