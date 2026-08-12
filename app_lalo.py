# ============================================================================
# PRICE LADDER & ARCHITECTURE EXPERT PRO
# ----------------------------------------------------------------------------
# ÍNDICE DEL ARCHIVO (usa Ctrl+F con estos títulos para saltar de sección):
#
#   0. IMPORTS
#   1. CONFIGURACIÓN DE PÁGINA (st.set_page_config)
#   2. FUNCIONES AUXILIARES
#        2.1 Persistencia de escenarios (guardar/cargar/backup)
#        2.2 Modo presentación (CSS)
#        2.3 Logo (carga de imagen en base64)
#        2.4 Glosario técnico
#        2.5 Funciones core (cálculo de PKG, pirámide, datos macro, historial)
#        2.6 Configuraciones guardadas (guardar/cargar/exportar/importar/eliminar/duplicar)
#   3. CONSTANTES Y CONFIGURACIÓN GLOBAL (Banxico, series macro)
#   4. CARGA DE PLANTILLAS Y ARQUITECTURA (archivos externos del repo)
#   5. INICIALIZACIÓN DE SESSION STATE (sliders, colores, comentarios, etc.)
#   6. EJECUCIÓN: modo presentación + logo
#   7. BARRA LATERAL (SIDEBAR)
#        7.1 Navegación y selección de modo
#        7.2 Botón de modo presentación
#        7.3 Lógica de modos (Price Ladder / Price Pack / Macro)
#        7.4 Gestión de escenarios
#        7.5 Comparación de escenarios
#        7.6 Gestión de estado (carga inicial de datos según el modo)
#        7.7 Barra lateral principal (carga/edición de datos)
#        7.8 Panel de control en sidebar (configuraciones guardadas)
#   8. PANEL PRINCIPAL (todo el contenido central de la app: formularios,
#      editor de tabla, gráficos, comparativas Index, pirámide, mapa de valor,
#      analista maestro Ultra 2.6, resumen ejecutivo, simulador estratégico,
#      elasticidad Price & Volume, indicadores macro)
#
#   Nota: el chatbot de IA que existía al final del archivo fue eliminado.
# ============================================================================

# ============================================================================
# 0. IMPORTS
# ============================================================================
import streamlit as st
import pandas as pd
import base64
import plotly.graph_objects as go
import requests
from plotly.subplots import make_subplots
import os
import io
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ============================================================================
# 1. CONFIGURACIÓN DE PÁGINA (debe ser el PRIMER comando de Streamlit)
# ============================================================================
    
st.set_page_config(page_title="Price Ladder & Architecture Expert Pro", layout="wide")

# ============================================================================
# 2. FUNCIONES AUXILIARES
# ============================================================================

# --- 2.1 Persistencia de escenarios ---
# --- FUNCIONES DE PERSISTENCIA DE ESCENARIOS ---
def guardar_escenarios_a_disco():
    """Guarda escenarios en archivo JSON"""
    try:
        escenarios_serializables = {}
        for key, escenario in st.session_state.get("escenarios_guardados", {}).items():
            escenarios_serializables[key] = {
                "nombre": escenario["nombre"],
                "modo": escenario["modo"],
                "data": escenario["data"].to_dict('records'),  # Convertir DataFrame a dict
                "fecha": escenario["fecha"],
                "num_productos": escenario["num_productos"],
                "custom_colors": escenario.get("custom_colors", {})
            }
        
        with open("escenarios_guardados.json", "w", encoding="utf-8") as f:
            json.dump(escenarios_serializables, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Error guardando escenarios: {e}")
        return False

def cargar_escenarios_desde_disco():
    """Carga escenarios desde archivo JSON"""
    try:
        if os.path.exists("escenarios_guardados.json"):
            with open("escenarios_guardados.json", "r", encoding="utf-8") as f:
                escenarios_dict = json.load(f)
            
            # Reconstruir con DataFrames
            escenarios_reconstruidos = {}
            for key, escenario in escenarios_dict.items():
                escenarios_reconstruidos[key] = {
                    "nombre": escenario["nombre"],
                    "modo": escenario["modo"],
                    "data": pd.DataFrame(escenario["data"]),
                    "fecha": escenario["fecha"],
                    "num_productos": escenario["num_productos"],
                    "custom_colors": escenario.get("custom_colors", {})
                }
            
            return escenarios_reconstruidos
        return {}
    except Exception as e:
        print(f"Error cargando escenarios: {e}")
        return {}

def crear_backup_escenarios():
    """Crea backup con timestamp"""
    try:
        if os.path.exists("escenarios_guardados.json"):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Crear carpeta de backups si no existe
            if not os.path.exists("backups_escenarios"):
                os.makedirs("backups_escenarios")
            
            import shutil
            shutil.copy("escenarios_guardados.json", f"backups_escenarios/escenarios_{timestamp}.json")
            return True
        return False
    except Exception as e:
        print(f"Error creando backup: {e}")
        return False

# --- CSS PARA MODO PRESENTACIÓN ---
def aplicar_modo_presentacion():
    if "modo_presentacion" in st.session_state and st.session_state["modo_presentacion"]:
        st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                display: none;
            }
            .main .block-container {
                max-width: 100%;
                padding-left: 2rem;
                padding-right: 2rem;
            }
            </style>
        """, unsafe_allow_html=True)

# 2. AQUÍ PEGAS LA FUNCIÓN Y EL BLOQUE DEL LOGO
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


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
    
    st.divider()
    
    # --- SECCIÓN: PRICE AND VOLUME ANALYTICS ---
    st.info("#### **4. Price & Volume Analytics (Análisis de Precio y Volumen)**")
    st.markdown("""
    Es el módulo de **análisis temporal** que evalúa el desempeño comercial mediante el seguimiento semanal de las métricas clave del negocio. Permite comprender la dinámica entre las decisiones de pricing y la respuesta del mercado.
    
    **Indicadores de Performance:**
    * **Evolución de Ventas en Valor:** Monitoreo del ingreso total generado semana a semana, identificando tendencias y períodos de crecimiento o contracción.
    * **Evolución de Ventas en Volumen:** Seguimiento de las unidades vendidas para entender la rotación real de los productos de manera Sell In.
    * **Tendencias de Precio:** Análisis de la variación promedio del precio para poder observar cuando fue el cambio de precios de determinado producto.
    
    **Análisis de Sensibilidad al Precio:**
    * **Variación Valor vs. Volumen:** Cuantificación del cambio porcentual en ventas valor y unidades vendidas entre períodos.
    * **Elasticidad Precio-Demanda:** Medición del impacto que tienen los ajustes de precio sobre el volumen de ventas, permitiendo calcular la **sensibilidad del consumidor** ante cambios en la estrategia de pricing.
    * **Identificación de Períodos Críticos:** Reconocimiento de semanas donde las variaciones de precio generaron impactos significativos (positivos o negativos) en el desempeño comercial.

    """)
    
    st.divider()
    
    if st.button("✅ Entendido", use_container_width=True):
        st.rerun()

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

# --- FUNCIÓN DE CONSULTA POR BLOQUES ---
@st.cache_data(ttl=86400)
def importar_datos_macro(token, series_lista):
    headers = {"Accept": "application/json", "Bmx-Token": token}
    mapeo_nombres = {id_serie: nombre for id_serie, nombre in series_lista}
    ids_totales = list(mapeo_nombres.keys())
    
    # Tamaño máximo de series por petición para evitar el error 413
    TAMANO_BLOQUE = 10
    lista_dfs = []

    # Dividir la lista total en sublistas de máximo 10 elementos
    for i in range(0, len(ids_totales), TAMANO_BLOQUE):
        bloque_ids = ids_totales[i : i + TAMANO_BLOQUE]
        ids_concatenados = ",".join(bloque_ids)
        
        url = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{ids_concatenados}/datos"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            series_data = response.json()['bmx']['series']
            
            for s in series_data:
                id_serie = s['idSerie']
                nombre_columna = mapeo_nombres.get(id_serie, id_serie)
                
                if 'datos' in s:
                    df_temp = pd.DataFrame(s['datos'])
                    df_temp['fecha'] = pd.to_datetime(df_temp['fecha'], dayfirst=True)
                    df_temp['dato'] = pd.to_numeric(df_temp['dato'].str.replace(',', ''), errors='coerce')
                    
                    df_temp = df_temp.rename(columns={'fecha': 'Fecha', 'dato': nombre_columna})
                    df_temp = df_temp.set_index('Fecha').resample('ME').last()
                    lista_dfs.append(df_temp)
                    
        except Exception as e:
            # Si un bloque falla, lo reportamos pero permitimos revisar qué pasó
            st.error(f"Error en el bloque que inicia con {bloque_ids[0]}: {e}")
            continue

    # Unir todos los dataframes recolectados de los distintos bloques
    if lista_dfs:
        df_final = pd.concat(lista_dfs, axis=1).sort_index()
        
        # Filtrar por rango de fechas
        df_final = df_final.loc[FECHA_INICIO_FILTRO:FECHA_FIN_FILTRO]
        
        # Rellenar las expectativas (Exp_) hacia adelante si existen
        cols_exp = [c for c in df_final.columns if c.startswith("Exp_")]
        if cols_exp:
            df_final[cols_exp] = df_final[cols_exp].ffill()
            
        return df_final

    return None


# --- FUNCIÓN PARA REGISTRAR CAMBIOS EN HISTORIAL ---
def registrar_cambio(producto, campo, valor_anterior, valor_nuevo, modo_app):
    if valor_anterior != valor_nuevo:
        cambio = {
            "timestamp": pd.Timestamp.now(),
            "fecha": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            "producto": producto,
            "campo": campo,
            "anterior": valor_anterior,
            "nuevo": valor_nuevo,
            "modo": modo_app
        }
        st.session_state["historial_cambios"].append(cambio)
    

# --- FUNCIÓN PARA GUARDAR CONFIGURACIÓN ---
def guardar_configuracion(nombre):
    """Guarda la configuración actual completa"""
    config = {
        "nombre": nombre,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "diseno": {
            "slider_nombres": st.session_state.get("slider_nombres", 14),
            "slider_precios": st.session_state.get("slider_precios", 18),
            "slider_pkg": st.session_state.get("slider_pkg", 16),
            "slider_som": st.session_state.get("slider_som", 13),
            "slider_ancho": st.session_state.get("slider_ancho", 0.6),
            "slider_alto_barras": st.session_state.get("slider_alto_barras", 1.0),
            "slider_opacidad": st.session_state.get("slider_opacidad", 1.0),
            "slider_alto": st.session_state.get("slider_alto", 950),
            "slider_espacio": st.session_state.get("slider_espacio", 0.03),
            "slider_margen_b": st.session_state.get("slider_margen_b", 440),
            "slider_angulo": st.session_state.get("slider_angulo", -90)
        },
        "grid": {
            "grid_color": st.session_state.get("grid_color", "#707070"),
            "grid_grosor": st.session_state.get("grid_grosor", 1.30),
            "grid_opacidad": st.session_state.get("grid_opacidad", 0.5),
            "grid_estilo": st.session_state.get("grid_estilo", "solid"),
            "grid_y_visible": st.session_state.get("grid_y_visible", True),
            "grid_x_visible": st.session_state.get("grid_x_visible", False),
            "nticks_y": st.session_state.get("nticks_y", 16),
            "grid_layer": st.session_state.get("grid_layer", "below traces")
        },
        "colores_personalizados": st.session_state.get("custom_colors", {})
    }
    st.session_state["configs_guardadas"][nombre] = config
    return config

# --- FUNCIÓN PARA CARGAR CONFIGURACIÓN ---
def cargar_configuracion(nombre):
    """Carga una configuración guardada"""
    if nombre not in st.session_state["configs_guardadas"]:
        return False
    
    config = st.session_state["configs_guardadas"][nombre]
    
    # Aplicar diseño
    if "diseno" in config:
        for key, value in config["diseno"].items():
            st.session_state[key] = value
    
    # Aplicar grid
    if "grid" in config:
        for key, value in config["grid"].items():
            st.session_state[key] = value
    
    # Aplicar colores personalizados
    if "colores_personalizados" in config:
        st.session_state["custom_colors"] = config["colores_personalizados"]
    
    return True

# --- FUNCIÓN PARA EXPORTAR CONFIGURACIÓN ---
def exportar_configuracion(nombre):
    """Exporta configuración como archivo JSON"""
    if nombre not in st.session_state["configs_guardadas"]:
        return None
    config = st.session_state["configs_guardadas"][nombre]
    json_str = json.dumps(config, indent=2, ensure_ascii=False)
    return json_str

# --- FUNCIÓN PARA IMPORTAR CONFIGURACIÓN ---
def importar_configuracion(json_str):
    """Importa configuración desde JSON"""
    try:
        config = json.loads(json_str)
        nombre = config.get("nombre", f"Importada_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        st.session_state["configs_guardadas"][nombre] = config
        return nombre
    except:
        return None

# --- FUNCIÓN PARA ELIMINAR CONFIGURACIÓN ---
def eliminar_configuracion(nombre):
    """Elimina una configuración guardada"""
    if nombre in st.session_state["configs_guardadas"]:
        del st.session_state["configs_guardadas"][nombre]
        return True
    return False

# --- FUNCIÓN PARA DUPLICAR CONFIGURACIÓN ---
def duplicar_configuracion(nombre_original, nombre_nuevo):
    """Crea una copia de una configuración"""
    if nombre_original not in st.session_state["configs_guardadas"]:
        return False
    config_original = st.session_state["configs_guardadas"][nombre_original].copy()
    config_original["nombre"] = nombre_nuevo
    config_original["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["configs_guardadas"][nombre_nuevo] = config_original
    return True


# ============================================================================
# 3. CONSTANTES Y CONFIGURACIÓN GLOBAL
# ============================================================================
    
TOKEN_BANXICO = "08d1b98b48cd9bb05d95b88e3fd37886ec747aa5e563b562b7bef9de21cde974"
FECHA_INICIO_FILTRO = "2020-01-01"
FECHA_FIN_FILTRO = "2027-12-31"

SERIES_A_CONSULTAR = [
    # =====================================================================
    # 1. INPC / INPP Y MACRO (Originales)
    # =====================================================================
    ("SP30577", "INPC_Inflacion_Mensual"), ("SP30579", "INPC_Inflacion_Acumulada"),
    ("SP30578", "INPC_Inflacion_Anual"), ("SP1", "INPC_Nivel_Historico"),
    ("SP6", "INPP_Mercancias_Servicios_ExPetroleo"), ("SP5", "INPP_Mercancias_Servicios_ConPetroleo"),
    
    # Mercado Cambiario y Monetario
    ("SF17890", "TipoCambio_Cotizacion_Minima"), ("SF17891", "TipoCambio_Cotizacion_Maxima"),
    ("SF331450", "TIIE_Fondeo_1Dia"),
    
    # Mercado Laboral
    ("SL11298", "Salario_Minimo_General"), ("SL1", "Tasa_Desocupacion_Nacional"),

    # Expectativas de la Encuesta de Especialistas (Medias y Extremos)
    ("SR14222", "Exp_Inflacion_Media"), ("SR14226", "Exp_Inflacion_Minima"),
    ("SR14227", "Exp_Inflacion_Maxima"), ("SR14790", "Exp_TipoCambio_Media"),
    ("SR14794", "Exp_TipoCambio_Minima"), ("SR14795", "Exp_TipoCambio_Maxima"),

    ("SR14658", "Exp_TasaFondeo_Media"), ("SR14662", "Exp_TasaFondeo_Minima"),
    ("SR14663", "Exp_TasaFondeo_Maxima"), ("SR14902", "Exp_TasaDesocupacion_Media"),
    ("SR14906", "Exp_TasaDesocupacion_Minima"), ("SR14907", "Exp_TasaDesocupacion_Maxima"),

    # =====================================================================
    # 2. NUEVAS SERIES AGREGADAS (Clima de Negocios, Billetes y Monedas)
    # =====================================================================

    # Encuesta de Expectativas de Clima de Negocios
    ("SR15028", "Exp_ClimaNegocios_Mejorara"),     # Clima de negocios próximos 6 meses: Mejorará
    ("SR15029", "Exp_ClimaNegocios_Igual"),        # Clima de negocios próximos 6 meses: Permanecerá igual
    ("SR15030", "Exp_ClimaNegocios_Empeorara"),    # Clima de negocios próximos 6 meses: Empeorará
    ("SR16207", "Exp_ClimaNegocios_NumRespuestas"), # Número de respuestas
    
    # Encuesta de Expectativas de Situación Económica Actual
    ("SR15031", "Exp_EconActual_Mejor"),           # Economía mejor que hace un año: Sí
    ("SR15032", "Exp_EconActual_Peor"),            # Economía mejor que hace un año: No
    ("SR16208", "Exp_EconActual_NumRespuestas"),  # Número de respuestas

    # Billetes en Circulación (Totales, Millones de Pesos)
    ("SM1472", "Billete_20_Circulacion"),
    ("SM1478", "Billete_50_Circulacion"),
    ("SM1479", "Billete_100_Circulacion"),
    ("SM1480", "Billete_200_Circulacion"),
    ("SM1481", "Billete_500_Circulacion"),
    ("SM1482", "Billete_1000_Circulacion"),

    # Monedas en Circulación (Totales, Millones de Pesos)
    ("SM9", "Moneda_05C_Circulacion"),
    ("SM10", "Moneda_10C_Circulacion"),
    ("SM11", "Moneda_20C_Circulacion"),
    ("SM12", "Moneda_50C_Circulacion"),
    ("SM13", "Moneda_1_Circulacion"),
    ("SM14", "Moneda_2_Circulacion"),
    ("SM15", "Moneda_5_Circulacion"),
    ("SM16", "Moneda_10_Circulacion"),
    ("SM17", "Moneda_20_Circulacion")
]

# ============================================================================
# 4. CARGA DE PLANTILLAS Y ARQUITECTURA
# ============================================================================

# --- 1. CONFIGURACIÓN Y CARGA DE PLANTILLAS ---
try:
    from plantillas import PLANTILLAS 
except ImportError:
    PLANTILLAS = {}

try:
    from price_pack import PLANTILLAS_PP
except ImportError:
    PLANTILLAS_PP = {}
    
# --- CARGA DE ARQUITECTURA DESDE TU ARCHIVO EN GITHUB/LOCAL ---
try:
    # Suponiendo que tu archivo se llama arquitectura_empaque.py
    from arquitectura_empaque import render_arquitectura_empaque
    # Creamos un DataFrame independiente para NO tocar el df_p de las escaleras
    df_arq = pd.DataFrame(render_arquitectura_empaque)
except ImportError:
    st.error("No se pudo encontrar el archivo 'arquitectura_empaque.py' en el repositorio.")
    df_arq = pd.DataFrame() # DataFrame vacío para evitar que el código truene

# ============================================================================
# 5. INICIALIZACIÓN DE SESSION STATE
# ============================================================================
# ============================================
# INICIALIZACIÓN DE SLIDERS Y ESTADOS (DEBE ESTAR AQUÍ AL INICIO)
# ============================================
if 'form_success' not in st.session_state:
    st.session_state.form_success = False
if "slider_nombres" not in st.session_state:
    st.session_state["slider_nombres"] = 16
if "slider_precios" not in st.session_state:
    st.session_state["slider_precios"] = 18
if "slider_pkg" not in st.session_state:
    st.session_state["slider_pkg"] = 15
if "slider_som" not in st.session_state:
    st.session_state["slider_som"] = 15
if "slider_ancho" not in st.session_state:
    st.session_state["slider_ancho"] = 0.8
if "slider_opacidad" not in st.session_state:
    st.session_state["slider_opacidad"] = 1.0
if "slider_alto" not in st.session_state:
    st.session_state["slider_alto"] = 950
if "slider_espacio" not in st.session_state:
    st.session_state["slider_espacio"] = 0.03
if "slider_margen_b" not in st.session_state:
    st.session_state["slider_margen_b"] = 440
if "slider_angulo" not in st.session_state:
    st.session_state["slider_angulo"] = -90

# Inicializar custom_colors si no existe
if "custom_colors" not in st.session_state:
    st.session_state["custom_colors"] = {}

# Inicializar comentarios y historial
if "comentarios_productos" not in st.session_state:
    st.session_state["comentarios_productos"] = {}
if "historial_cambios" not in st.session_state:
    st.session_state["historial_cambios"] = []
if "modo_presentacion" not in st.session_state:
    st.session_state["modo_presentacion"] = True

# ============================================================================
# SISTEMA DE GUARDAR/CARGAR CONFIGURACIONES
# Copiar y pegar este código completo al inicio de tu app (después de imports)
# ============================================================================

# --- INICIALIZACIÓN DE SESSION STATE ---
if "configs_guardadas" not in st.session_state:
    st.session_state["configs_guardadas"] = {}


# ============================================================================
# 6. EJECUCIÓN: MODO PRESENTACIÓN Y LOGO
# ============================================================================
# Aplicar CSS si está en modo presentación
aplicar_modo_presentacion()

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





# ============================================================================
# 7. BARRA LATERAL (SIDEBAR)
# ============================================================================
        
# --- 1. NAVEGACIÓN Y CONFIGURACIÓN ---
with st.sidebar:
    st.header("🚀 Modo de Visualización")
    # Agregamos el nuevo modo a la lista de radio
    modo = st.radio(
        "Seleccionar Herramienta:", 
        ["Price Ladder", "Price Pack", "Indicadores Macro"], 
        label_visibility="collapsed"
    )
    
    # Botón limpio para el Glosario
    if st.button("❓ Ver Glosario Técnico", use_container_width=True):
        if 'mostrar_glosario' in globals():
            mostrar_glosario()
        else:
            st.info("Función de glosario no definida aún.")

# --- BOTÓN MODO PRESENTACIÓN (FUERA DEL SIDEBAR) ---
if "modo_presentacion" in st.session_state and st.session_state["modo_presentacion"]:
    # Modo presentación - botón flotante para salir
    col_exit = st.columns([10, 1])[1]
    with col_exit:
        if st.button("🚪 Salir", key="exit_presentation"):
            st.session_state["modo_presentacion"] = False
            st.rerun()



# --- LÓGICA DE MODOS (Configuración de variables) ---
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

else: # MODO: Indicadores Macro
    DB_FILE = None
    label_agru = None
    opciones_agru = []
    fuente_plantillas = {}
    columnas_tabla = []
        


# --- SECCIÓN 2.5: GESTIÓN DE ESCENARIOS ---
if "data" in st.session_state and not st.session_state.data.empty and modo in ["Price Ladder", "Price Pack"]:
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style='background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); 
                    padding: 1rem; 
                    border-radius: 10px; 
                    margin-bottom: 1rem;
                    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);'>
            <h3 style='color: white; margin: 0; font-weight: 600; text-align: center; font-size: 1.1rem;'>
                📸 Gestión de Escenarios
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Inicializar escenarios (con carga desde disco)
    if "escenarios_guardados" not in st.session_state:
        st.session_state["escenarios_guardados"] = cargar_escenarios_desde_disco()
    
    with st.container(border=True):
        st.markdown("### 💾 Guardar Escenario Actual")
        
        col_nombre, col_btn = st.columns([3, 1])
        
        with col_nombre:
            nombre_escenario = st.text_input(
                "Nombre del escenario:",
                placeholder="Ej: Escenario Base, Propuesta Q1, etc.",
                label_visibility="collapsed",
                key="input_nombre_escenario"
            )
        
        with col_btn:
            if st.button("💾", use_container_width=True, help="Guardar escenario", key="btn_guardar_escenario"):
                if nombre_escenario and nombre_escenario.strip():
                    # Guardar snapshot del estado actual
                    escenario_key = f"{modo}_{nombre_escenario.strip()}"
                    st.session_state["escenarios_guardados"][escenario_key] = {
                        "nombre": nombre_escenario.strip(),
                        "modo": modo,
                        "data": st.session_state.data.copy(),
                        "fecha": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
                        "num_productos": len(st.session_state.data),
                        "custom_colors": st.session_state["custom_colors"].copy() if "custom_colors" in st.session_state else {}
                    }
                    guardar_escenarios_a_disco()
                    st.success(f"✅ Escenario '{nombre_escenario}' guardado!")
                    st.rerun()
                else:
                    st.warning("⚠️ Por favor ingresa un nombre para el escenario")
        
        # Mostrar escenarios guardados del modo actual
        escenarios_modo_actual = {k: v for k, v in st.session_state["escenarios_guardados"].items() if v["modo"] == modo}
        
        if escenarios_modo_actual:
            st.markdown("---")
            st.markdown("### 📋 Escenarios Guardados")
            
            for key, escenario in escenarios_modo_actual.items():
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"""
                            <div style='padding: 0.5rem; background: #F3F4F6; border-radius: 6px; margin-bottom: 0.5rem;'>
                                <strong style='color: #1F2937;'>📌 {escenario['nombre']}</strong><br>
                                <span style='font-size: 0.75rem; color: #6B7280;'>
                                    {escenario['fecha']} • {escenario['num_productos']} productos
                                </span>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("📂", key=f"load_{key}", use_container_width=True, help="Cargar este escenario"):
                            # Cargar el escenario
                            st.session_state.data = escenario["data"].copy()
                            st.session_state.data.to_csv(DB_FILE, index=False)
                            
                            # Restaurar colores personalizados si existen
                            if escenario.get("custom_colors"):
                                st.session_state["custom_colors"] = escenario["custom_colors"].copy()
                            
                            guardar_escenarios_a_disco()  # Guardar estado actual
                            st.success(f"✅ Escenario '{escenario['nombre']}' cargado!")
                            st.rerun()
                    
                    with col3:
                        if st.button("🗑️", key=f"delete_{key}", use_container_width=True, help="Eliminar este escenario"):
                            del st.session_state["escenarios_guardados"][key]
                            guardar_escenarios_a_disco()
                            st.success(f"✅ Escenario '{escenario['nombre']}' eliminado")
                            st.rerun()

            # Controles de backup
            st.markdown("---")
            st.markdown("### 💾 Respaldo y Recuperación")
            
            col_backup1, col_backup2 = st.columns(2)
            
            with col_backup1:
                if st.button("📦 Crear Backup", use_container_width=True, help="Guarda una copia de seguridad con fecha"):
                    if crear_backup_escenarios():
                        st.success("✅ Backup creado!")
                    else:
                        st.error("❌ Error al crear backup")
            
            with col_backup2:
                # Exportar escenarios como JSON descargable
                escenarios_export = {}
                for key, esc in st.session_state["escenarios_guardados"].items():
                    escenarios_export[key] = {
                        "nombre": esc["nombre"],
                        "modo": esc["modo"],
                        "data": esc["data"].to_dict('records'),
                        "fecha": esc["fecha"],
                        "num_productos": esc["num_productos"],
                        "custom_colors": esc.get("custom_colors", {})
                    }
                
                json_str = json.dumps(escenarios_export, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📥 Descargar JSON",
                    data=json_str,
                    file_name=f"escenarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # 🆕 VER Y RESTAURAR BACKUPS
            with st.expander("🗂️ Ver Backups Guardados"):
                if os.path.exists("backups_escenarios"):
                    archivos_backup = sorted(
                        [f for f in os.listdir("backups_escenarios") if f.endswith('.json')],
                        reverse=True  # Más recientes primero
                    )
                    
                    if archivos_backup:
                        st.markdown(f"**{len(archivos_backup)} backup(s) disponible(s):**")
                        
                        for archivo in archivos_backup:
                            # Extraer fecha del nombre del archivo
                            try:
                                fecha_str = archivo.replace("escenarios_", "").replace(".json", "")
                                fecha_obj = datetime.strptime(fecha_str, '%Y%m%d_%H%M%S')
                                fecha_legible = fecha_obj.strftime('%d/%m/%Y %H:%M:%S')
                            except:
                                fecha_legible = archivo
                            
                            col_info, col_restaurar, col_descargar = st.columns([3, 1, 1])
                            
                            with col_info:
                                st.caption(f"📅 {fecha_legible}")
                            
                            with col_restaurar:
                                if st.button("♻️", key=f"restore_{archivo}", help="Restaurar este backup"):
                                    try:
                                        # Leer el backup
                                        with open(f"backups_escenarios/{archivo}", "r", encoding="utf-8") as f:
                                            escenarios_backup = json.load(f)
                                        
                                        # Reconstruir escenarios
                                        escenarios_restaurados = {}
                                        for key, escenario in escenarios_backup.items():
                                            escenarios_restaurados[key] = {
                                                "nombre": escenario["nombre"],
                                                "modo": escenario["modo"],
                                                "data": pd.DataFrame(escenario["data"]),
                                                "fecha": escenario["fecha"],
                                                "num_productos": escenario["num_productos"],
                                                "custom_colors": escenario.get("custom_colors", {})
                                            }
                                        
                                        # Reemplazar escenarios actuales
                                        st.session_state["escenarios_guardados"] = escenarios_restaurados
                                        guardar_escenarios_a_disco()
                                        
                                        st.success(f"✅ Backup restaurado: {len(escenarios_restaurados)} escenarios")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error restaurando: {e}")
                            
                            with col_descargar:
                                # Descargar backup específico
                                with open(f"backups_escenarios/{archivo}", "r", encoding="utf-8") as f:
                                    backup_content = f.read()
                                
                                st.download_button(
                                    label="⬇️",
                                    data=backup_content,
                                    file_name=archivo,
                                    mime="application/json",
                                    key=f"download_{archivo}",
                                    help="Descargar este backup"
                                )
                        
                        # Opción de eliminar backups antiguos
                        st.markdown("---")
                        if st.button("🗑️ Eliminar TODOS los backups", type="secondary", use_container_width=True):
                            try:
                                import shutil
                                shutil.rmtree("backups_escenarios")
                                st.success("✅ Todos los backups eliminados")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                    else:
                        st.info("No hay backups guardados aún")
                else:
                    st.info("No hay backups guardados aún. Presiona 'Crear Backup' para guardar uno.")
            
            # Importar escenarios desde archivo
            st.markdown("---")
            st.markdown("**📂 Importar Escenarios:**")
            uploaded_json = st.file_uploader(
                "Subir archivo JSON de escenarios",
                type=['json'],
                key="upload_escenarios",
                help="Importar escenarios desde un archivo JSON descargado previamente"
            )
            
            if uploaded_json:
                try:
                    escenarios_importados = json.load(uploaded_json)
                    
                    # Reconstruir con DataFrames
                    for key, escenario in escenarios_importados.items():
                        st.session_state["escenarios_guardados"][key] = {
                            "nombre": escenario["nombre"],
                            "modo": escenario["modo"],
                            "data": pd.DataFrame(escenario["data"]),
                            "fecha": escenario["fecha"],
                            "num_productos": escenario["num_productos"],
                            "custom_colors": escenario.get("custom_colors", {})
                        }
                    
                    guardar_escenarios_a_disco()
                    st.success(f"✅ {len(escenarios_importados)} escenarios importados!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error importando: {e}")
            
            # Opción de exportar todos los escenarios como Excel
            st.markdown("---")
            
            if st.button("📥 Exportar Todos los Escenarios (Excel)", use_container_width=True, type="secondary"):
                # Crear un archivo con todos los escenarios
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for key, escenario in escenarios_modo_actual.items():
                        sheet_name = escenario['nombre'][:31]  # Excel limita a 31 caracteres
                        escenario["data"].to_excel(writer, index=False, sheet_name=sheet_name)
                
                st.download_button(
                    label="⬇️ Descargar Excel con Todos los Escenarios",
                    data=output.getvalue(),
                    file_name=f'escenarios_{modo.lower().replace(" ", "_")}_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True
                )
        else:
            st.info("💡 No hay escenarios guardados aún. Crea tu primer escenario arriba.")


# --- SECCIÓN 2.6: COMPARACIÓN DE ESCENARIOS ---
if "data" in st.session_state and not st.session_state.data.empty and modo in ["Price Ladder", "Price Pack"]:
    if len(escenarios_modo_actual) >= 1:  # Necesitamos al menos 1 escenario guardado para comparar con el actual
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style='background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); 
                        padding: 1rem; 
                        border-radius: 10px; 
                        margin-bottom: 1rem;
                        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);'>
                <h3 style='color: white; margin: 0; font-weight: 600; text-align: center; font-size: 1.1rem;'>
                    🔄 Comparar Escenarios
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("### 📊 Comparación Lado a Lado")
            
            # Selector de escenario para comparar
            escenario_comparar = st.selectbox(
                "Comparar escenario actual con:",
                ["-- Seleccionar --"] + [v["nombre"] for v in escenarios_modo_actual.values()],
                key="select_comparar_escenario"
            )
            
            if escenario_comparar != "-- Seleccionar --":
                # Encontrar el escenario seleccionado
                escenario_obj = None
                for key, esc in escenarios_modo_actual.items():
                    if esc["nombre"] == escenario_comparar:
                        escenario_obj = esc
                        break
                
                if escenario_obj:
                    st.markdown("---")
                    
                    # Tabs para diferentes vistas de comparación
                    tab1, tab2, tab3 = st.tabs(["📈 Resumen", "🔍 Diferencias", "📊 Tabla Completa"])
                    
                    with tab1:
                        # RESUMEN EJECUTIVO
                        col_actual, col_vs, col_guardado = st.columns([1, 0.2, 1])
                        
                        with col_actual:
                            st.markdown("""
                                <div style='background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                                            padding: 1rem; border-radius: 8px; text-align: center;'>
                                    <h4 style='color: white; margin: 0;'>📌 ESCENARIO ACTUAL</h4>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            st.metric("Total Productos", len(st.session_state.data))
                            if modo == "Price Ladder":
                                st.metric("Precio Promedio", f"${st.session_state.data['Precio ($)'].mean():.2f}")
                                st.metric("$/Kg Promedio", f"${st.session_state.data['Precio por Kg ($)'].mean():.2f}")
                                st.metric("SOM Total", f"{st.session_state.data['SOM (%)'].sum():.1f}%")
                            else:
                                st.metric("Precio Promedio", f"${st.session_state.data['Precio ($)'].mean():.2f}")
                                st.metric("$/Kg Promedio", f"${st.session_state.data['Precio por Kg ($)'].mean():.2f}")
                        
                        with col_vs:
                            st.markdown("<div style='padding-top: 80px; text-align: center; font-size: 2rem;'>⚡</div>", unsafe_allow_html=True)
                        
                        with col_guardado:
                            st.markdown(f"""
                                <div style='background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); 
                                            padding: 1rem; border-radius: 8px; text-align: center;'>
                                    <h4 style='color: white; margin: 0;'>💾 {escenario_obj['nombre'].upper()}</h4>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            st.metric("Total Productos", len(escenario_obj["data"]))
                            if modo == "Price Ladder":
                                st.metric("Precio Promedio", f"${escenario_obj['data']['Precio ($)'].mean():.2f}")
                                st.metric("$/Kg Promedio", f"${escenario_obj['data']['Precio por Kg ($)'].mean():.2f}")
                                st.metric("SOM Total", f"{escenario_obj['data']['SOM (%)'].sum():.1f}%")
                            else:
                                st.metric("Precio Promedio", f"${escenario_obj['data']['Precio ($)'].mean():.2f}")
                                st.metric("$/Kg Promedio", f"${escenario_obj['data']['Precio por Kg ($)'].mean():.2f}")
                    
                    with tab2:
                        # ANÁLISIS DE DIFERENCIAS
                        st.markdown("### 🔍 Productos con Cambios")
                        
                        # Merge de ambos datasets
                        df_actual = st.session_state.data.copy()
                        df_guardado = escenario_obj["data"].copy()
                        
                        # Identificar productos en común
                        productos_comunes = set(df_actual["Producto"]) & set(df_guardado["Producto"])
                        productos_nuevos = set(df_actual["Producto"]) - set(df_guardado["Producto"])
                        productos_eliminados = set(df_guardado["Producto"]) - set(df_actual["Producto"])
                        
                        # Mostrar cambios
                        if productos_nuevos:
                            st.success(f"✅ **{len(productos_nuevos)} Producto(s) Nuevo(s)**: {', '.join(list(productos_nuevos)[:5])}")
                        
                        if productos_eliminados:
                            st.error(f"❌ **{len(productos_eliminados)} Producto(s) Eliminado(s)**: {', '.join(list(productos_eliminados)[:5])}")
                        
                        # Comparar productos comunes
                        cambios = []
                        for prod in productos_comunes:
                            actual_row = df_actual[df_actual["Producto"] == prod].iloc[0]
                            guardado_row = df_guardado[df_guardado["Producto"] == prod].iloc[0]
                            
                            precio_actual = actual_row["Precio ($)"]
                            precio_guardado = guardado_row["Precio ($)"]
                            
                            if abs(precio_actual - precio_guardado) > 0.01:  # Si hay diferencia
                                cambio = {
                                    "Producto": prod,
                                    "Precio Anterior": precio_guardado,
                                    "Precio Actual": precio_actual,
                                    "Diferencia ($)": precio_actual - precio_guardado,
                                    "Diferencia (%)": ((precio_actual - precio_guardado) / precio_guardado * 100) if precio_guardado > 0 else 0
                                }
                                cambios.append(cambio)
                        
                        if cambios:
                            df_cambios = pd.DataFrame(cambios)
                            st.dataframe(
                                df_cambios,
                                column_config={
                                    "Producto": st.column_config.TextColumn("Producto", width="medium"),
                                    "Precio Anterior": st.column_config.NumberColumn("Precio Anterior", format="$%.2f"),
                                    "Precio Actual": st.column_config.NumberColumn("Precio Actual", format="$%.2f"),
                                    "Diferencia ($)": st.column_config.NumberColumn("Diferencia ($)", format="$%.2f"),
                                    "Diferencia (%)": st.column_config.NumberColumn("Diferencia (%)", format="%.1f%%"),
                                },
                                hide_index=True,
                                use_container_width=True
                            )
                        else:
                            st.info("✅ No hay cambios de precio en productos comunes")
                    
                    with tab3:
                        # TABLA COMPARATIVA COMPLETA
                        st.markdown("### 📋 Vista Completa Lado a Lado")
                        
                        # Merge completo
                        df_comp = df_actual.merge(
                            df_guardado, 
                            on="Producto", 
                            how="outer", 
                            suffixes=(" (Actual)", " (Guardado)")
                        )
                        
                        st.dataframe(df_comp, use_container_width=True, hide_index=True)
                        
                        # Opción de descarga
                        csv_comparacion = df_comp.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Descargar Comparación CSV",
                            data=csv_comparacion,
                            file_name=f'comparacion_{escenario_comparar}_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv',
                            mime='text/csv',
                            use_container_width=True
                        )



# ============================================================================
# CÓDIGO DEL SIDEBAR - SIN SISTEMA DE CONFIGURACIONES GUARDADAS
# ============================================================================
# Este código va después de tus imports
# Incluye: gestión de estado y sidebar completo (SIN sistema de presets)
# ============================================================================



# --- 3. GESTIÓN DE ESTADO ---
if "data" not in st.session_state or st.session_state.get("last_modo") != modo:
    if DB_FILE is not None and os.path.exists(DB_FILE):
        st.session_state.data = calcular_pkg(pd.read_csv(DB_FILE), modo)
    elif modo == "Indicadores Macro":
        st.session_state.data = pd.DataFrame() 
    else:
        st.session_state.data = pd.DataFrame(columns=columnas_tabla)
    
    st.session_state.last_modo = modo


# --- 4. BARRA LATERAL (GESTIÓN MEJORADA CON DISEÑO PREMIUM) ---
with st.sidebar:
    # Header principal con gradiente
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem 1rem; 
                    border-radius: 12px; 
                    margin-bottom: 1.5rem;
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);'>
            <h2 style='color: white; margin: 0; font-weight: 700; text-align: center; font-size: 1.5rem;'>
                📁 Gestión de Datos
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # --- SECCIÓN 1: CARGAR DATOS ---
    with st.container(border=True):
        st.markdown("""
            <div style='text-align: center; padding-bottom: 0.5rem;'>
                <span style='font-size: 1.1rem; font-weight: 600; color: #334155;'>
                    📥 Cargar Plantilla
                </span>
            </div>
        """, unsafe_allow_html=True)
        
        nombre_plantilla = st.selectbox(
            "Selecciona una plantilla:", 
            ["-- Seleccionar --"] + list(fuente_plantillas.keys()),
            label_visibility="collapsed"
        )
        
        if nombre_plantilla != "-- Seleccionar --":
            df_preview = pd.DataFrame(fuente_plantillas[nombre_plantilla])
            num_productos = len(df_preview['Producto'].unique()) if 'Producto' in df_preview.columns else 0
            num_registros = len(df_preview)
            
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); 
                            padding: 0.8rem; 
                            border-radius: 8px; 
                            margin: 0.5rem 0;
                            border-left: 3px solid #3B82F6;'>
                    <p style='margin: 0; font-size: 0.85rem; color: #1E40AF;'>
                        <strong>📊 Vista Previa:</strong><br>
                        • {num_productos} productos únicos<br>
                        • {num_registros} registros totales<br>
                        • Modo: <strong>{modo}</strong>
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        if st.button("🚀 Cargar Datos", use_container_width=True, type="primary"):
            if nombre_plantilla != "-- Seleccionar --":
                with st.spinner("⏳ Procesando datos..."):
                    df_nuevo = pd.DataFrame(fuente_plantillas[nombre_plantilla])
                    
                    st.session_state.data = calcular_pkg(df_nuevo, modo)
                    
                    st.session_state.data.to_csv(DB_FILE, index=False)
                    st.success("✅ ¡Datos cargados exitosamente!")
                    st.balloons()
                    st.rerun()
            else:
                st.warning("⚠️ Por favor selecciona una plantilla válida")
    
    # --- SECCIÓN 2: EXPORTACIÓN ---
    if not st.session_state.data.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style='background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                        padding: 1rem; 
                        border-radius: 10px; 
                        margin-bottom: 1rem;
                        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);'>
                <h3 style='color: white; margin: 0; font-weight: 600; text-align: center; font-size: 1.1rem;'>
                    📥 Exportar Datos
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            def to_excel(df):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Datos_Completos')
                    
                    if 'Producto' in df.columns and 'Venta Valor ($)' in df.columns:
                        resumen = df.groupby('Producto').agg({
                            'Venta Valor ($)': 'sum',
                            'Venta Volumen (Pzas)': 'sum' if 'Venta Volumen (Pzas)' in df.columns else 'count'
                        }).reset_index()
                        resumen.columns = ['Producto', 'Total Ventas ($)', 'Total Volumen']
                        resumen = resumen.sort_values('Total Ventas ($)', ascending=False)
                        resumen.to_excel(writer, index=False, sheet_name='Resumen_por_Producto')
                    
                    metadata = pd.DataFrame({
                        'Información': ['Fecha de Exportación', 'Modo de Análisis', 'Total Registros', 'Productos Únicos'],
                        'Valor': [
                            pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                            modo,
                            len(df),
                            len(df['Producto'].unique()) if 'Producto' in df.columns else 'N/A'
                        ]
                    })
                    metadata.to_excel(writer, index=False, sheet_name='Metadata')
                
                return output.getvalue()
            
            excel_data = to_excel(st.session_state.data)
            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            
            st.download_button(
                label="📊 Descargar Excel Completo",
                data=excel_data,
                file_name=f'barcel_{modo.lower().replace(" ", "_")}_{timestamp}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                use_container_width=True,
                type="primary"
            )
            
            csv_data = st.session_state.data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Descargar CSV",
                data=csv_data,
                file_name=f'barcel_{modo.lower().replace(" ", "_")}_{timestamp}.csv',
                mime='text/csv',
                use_container_width=True
            )
            
            st.markdown("""
                <div style='background: #F0FDF4; 
                            padding: 0.6rem; 
                            border-radius: 6px; 
                            margin-top: 0.5rem;
                            border-left: 3px solid #10B981;'>
                    <p style='margin: 0; font-size: 0.8rem; color: #065F46;'>
                        💡 <strong>Tip:</strong> El Excel incluye múltiples hojas con datos completos y metadata
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    # --- SECCIÓN 3: CONTROLES DE DISEÑO (MOVIDOS ANTES DEL FOOTER) ---
    if not st.session_state.data.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()
        st.subheader("🎨 Controles de Diseño")
        
        def reset_diseno():
            st.session_state["slider_nombres"] = 14
            st.session_state["slider_precios"] = 18
            st.session_state["slider_pkg"] = 16
            st.session_state["slider_som"] = 13
            st.session_state["slider_ancho"] = 0.6
            st.session_state["slider_alto_barras"] = 1.0  # NUEVO: Alto de barras
            st.session_state["slider_opacidad"] = 1.0
            st.session_state["slider_alto"] = 950
            st.session_state["slider_espacio"] = 0.03
            st.session_state["slider_margen_b"] = 440
            st.session_state["slider_angulo"] = -90
            st.session_state["custom_colors"] = {}
            # Resets para grid (CORREGIDOS)
            st.session_state["grid_color"] = "#707070"
            st.session_state["grid_grosor"] = 1.30
            st.session_state["grid_opacidad"] = 0.5
            st.session_state["grid_estilo"] = "solid"
            st.session_state["grid_y_visible"] = True
            st.session_state["grid_x_visible"] = False
            st.session_state["nticks_y"] = 16
            st.session_state["grid_layer"] = "below traces"  # CORREGIDO
            
        if st.button("Resetear Todo el Diseño"):
            reset_diseno()
            st.rerun()
            
        with st.expander("📏 Dimensiones y Espaciado"):
            alto_grafico = st.slider("Alto del Gráfico", 400, 1500, value=st.session_state["slider_alto"], key="slider_alto")
            espacio_v = st.slider("Espacio entre Gráficos", 0.0, 0.2, value=st.session_state["slider_espacio"], key="slider_espacio")
            margen_b = st.slider("Margen Inferior (Nombres)", 50, 600, value=st.session_state["slider_margen_b"], key="slider_margen_b")
            
            col_barras1, col_barras2 = st.columns(2)
            with col_barras1:
                ancho_barras = st.slider("Ancho de Barras", 0.1, 1.0, value=st.session_state["slider_ancho"], key="slider_ancho")
            with col_barras2:
                alto_barras = st.slider("Alto de Barras (escala Y)", 0.1, 2.0, value=st.session_state.get("slider_alto_barras", 1.0), step=0.1, key="slider_alto_barras", help="Multiplica la altura de las barras. >1 = más altas, <1 = más bajas")
            
            opacidad_barras = st.slider("Opacidad Barras", 0.1, 1.0, value=st.session_state["slider_opacidad"], key="slider_opacidad")
        
        with st.expander("🔡 Tipografía y Texto"):
            t_nombres = st.slider("Tamaño Nombres", 8, 30, value=st.session_state["slider_nombres"], key="slider_nombres")
            t_precios = st.slider("Tamaño Precios ($)", 10, 40, value=st.session_state["slider_precios"], key="slider_precios")
            t_pkg = st.slider("Tamaño $/Kg", 10, 40, value=st.session_state["slider_pkg"], key="slider_pkg")
            t_som = st.slider("Tamaño SOM (%)", 8, 25, value=st.session_state["slider_som"], key="slider_som")
            angulo_nombres = st.slider("Ángulo de Nombres", -90, 0, value=st.session_state["slider_angulo"], key="slider_angulo")
        
        # === EXPANDER PARA LÍNEAS DIVISORIAS / GRID (CORREGIDO) ===
        with st.expander("📊 Líneas Divisorias (Grid)"):
            st.markdown("#### Visibilidad del Grid")
            col_vis1, col_vis2 = st.columns(2)
            with col_vis1:
                grid_y_visible = st.checkbox(
                    "Mostrar líneas horizontales (Y)", 
                    value=st.session_state.get("grid_y_visible", True),
                    key="grid_y_visible",
                    help="Líneas horizontales del eje Y"
                )
            with col_vis2:
                grid_x_visible = st.checkbox(
                    "Mostrar líneas verticales (X)", 
                    value=st.session_state.get("grid_x_visible", False),
                    key="grid_x_visible",
                    help="Líneas verticales del eje X"
                )
            
            st.markdown("#### Estilo de Líneas")
            col_style1, col_style2, col_style3 = st.columns(3)
            
            with col_style1:
                grid_color = st.color_picker(
                    "Color de Líneas",
                    value=st.session_state.get("grid_color", "#707070"),
                    key="grid_color",
                    help="Color de las líneas divisorias"
                )
            
            with col_style2:
                grid_grosor = st.slider(
                    "Grosor de Líneas",
                    0.1, 5.0, 
                    value=st.session_state.get("grid_grosor", 1.30),
                    step=0.1,
                    key="grid_grosor",
                    help="Grosor de las líneas en puntos"
                )
            
            with col_style3:
                grid_opacidad = st.slider(
                    "Opacidad de Líneas",
                    0.0, 1.0,
                    value=st.session_state.get("grid_opacidad", 0.5),
                    step=0.05,
                    key="grid_opacidad",
                    help="Transparencia de las líneas (visual, no afecta Plotly)"
                )
            
            col_style4, col_style5 = st.columns(2)
            
            with col_style4:
                grid_estilo = st.selectbox(
                    "Estilo de Línea",
                    options=["solid", "dash", "dot", "dashdot"],  # CORREGIDO: valores válidos
                    index=["solid", "dash", "dot", "dashdot"].index(
                        st.session_state.get("grid_estilo", "solid")
                    ),
                    key="grid_estilo",
                    help="Tipo de línea: solid (continua), dash (discontinua), dot (punteada), dashdot (mixta)"
                )
            
            with col_style5:
                # CORREGIDO: usar valores válidos de Plotly
                grid_layer_option = st.selectbox(
                    "Posición de Grid",
                    options=["Detrás de barras", "Delante de barras"],
                    index=0 if st.session_state.get("grid_layer", "below traces") == "below traces" else 1,
                    key="grid_layer_select",
                    help="Si las líneas aparecen detrás o delante de las barras"
                )
                grid_layer = "below traces" if grid_layer_option == "Detrás de barras" else "above traces"
                st.session_state["grid_layer"] = grid_layer
            
            st.markdown("#### Cantidad de Líneas")
            col_qty1, col_qty2 = st.columns(2)
            
            with col_qty1:
                nticks_y = st.slider(
                    "Número de líneas horizontales",
                    3, 30,
                    value=st.session_state.get("nticks_y", 16),
                    key="nticks_y",
                    help="Cantidad de divisiones en el eje Y"
                )
            
            with col_qty2:
                st.info("💡 **Tip**: Más líneas = grid más denso. Menos líneas = gráfico más limpio.")
            
            # Preview de configuración actual
            st.markdown("---")
            st.markdown("#### 👁️ Vista Previa de Configuración")
            preview_cols = st.columns(3)
            with preview_cols[0]:
                st.markdown(f"""
                    <div style='background: white; padding: 10px; border-radius: 5px; border: 1px solid #ddd;'>
                        <div style='font-size: 12px; color: #666; margin-bottom: 5px;'>Color</div>
                        <div style='background: {grid_color}; height: 30px; border-radius: 3px; border: 1px solid #ccc;'></div>
                    </div>
                """, unsafe_allow_html=True)
            with preview_cols[1]:
                st.markdown(f"""
                    <div style='background: white; padding: 10px; border-radius: 5px; border: 1px solid #ddd;'>
                        <div style='font-size: 12px; color: #666; margin-bottom: 5px;'>Grosor & Opacidad</div>
                        <div style='font-weight: bold; font-size: 18px; color: #333;'>{grid_grosor}px · {int(grid_opacidad*100)}%</div>
                    </div>
                """, unsafe_allow_html=True)
            with preview_cols[2]:
                st.markdown(f"""
                    <div style='background: white; padding: 10px; border-radius: 5px; border: 1px solid #ddd;'>
                        <div style='font-size: 12px; color: #666; margin-bottom: 5px;'>Estilo & Líneas</div>
                        <div style='font-weight: bold; font-size: 18px; color: #333;'>{grid_estilo.title()} · {nticks_y} líneas</div>
                    </div>
                """, unsafe_allow_html=True)
    
        # ✨ SELECTOR DE COLORES PERSONALIZADOS
        with st.expander("🎨 Colores Personalizados (Opcional)"):
            st.markdown("**Contorno de las barras (aplica a todas):**")
            col_contorno1, col_contorno2 = st.columns(2)
            with col_contorno1:
                color_contorno_barras = st.color_picker(
                    "Color del contorno",
                    value=st.session_state.get("color_contorno_barras", "#000000"),
                    key="color_contorno_barras",
                    help="Color del borde/contorno de todas las barras del gráfico"
                )
            with col_contorno2:
                grosor_contorno_barras = st.slider(
                    "Grosor del contorno",
                    0.0, 5.0,
                    value=st.session_state.get("grosor_contorno_barras", 1.0),
                    step=0.25,
                    key="grosor_contorno_barras",
                    help="Grosor del borde de las barras (0 = sin contorno)"
                )
            st.markdown("---")
            st.markdown("**Selecciona un producto para cambiar su color:**")
            
            if "Producto" in st.session_state.data.columns:
                productos_disponibles = sorted(st.session_state.data["Producto"].unique().tolist())
                
                producto_seleccionado = st.selectbox(
                    "Producto a personalizar:",
                    ["-- Ninguno --"] + productos_disponibles,
                    key="color_picker_producto"
                )
                
                if producto_seleccionado != "-- Ninguno --":
                    st.markdown("---")
                    st.markdown("#### 🎨 Personalización de Barra")
                    
                    # Obtener fabricante del producto seleccionado para defaults inteligentes
                    fabricante_prod = st.session_state.data[st.session_state.data["Producto"] == producto_seleccionado]["Fabricante"].iloc[0] if "Fabricante" in st.session_state.data.columns else "OTROS"
                    
                    # Defaults inteligentes según fabricante
                    default_barra = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D", "PROPUESTA": "#4B207E"}.get(fabricante_prod.upper(), "#999999")
                    default_texto_pkg = "#FFFFFF" if fabricante_prod.upper() == "BARCEL" else "#000000"
                    default_fondo_pkg = "#4682B4" if fabricante_prod.upper() == "BARCEL" else "#FFFFFF"
                    default_borde_pkg = "#444444" if fabricante_prod.upper() != "BARCEL" else "#333333"
                    
                    # Color de la barra
                    color_barra = st.color_picker(
                        "Color de barra",
                        value=st.session_state["custom_colors"].get(producto_seleccionado, {}).get("barra", default_barra),
                        key=f"color_barra_{producto_seleccionado}"
                    )
                    
                    st.markdown("#### 📝 Personalización de Precios")
                    
                    col_precio1, col_precio2 = st.columns(2)
                    
                    with col_precio1:
                        st.markdown("**Precio Desembolso (arriba)**")
                        # Color del texto del precio desembolso
                        color_texto_desembolso = st.color_picker(
                            "Color texto",
                            value=st.session_state["custom_colors"].get(producto_seleccionado, {}).get("texto_desembolso", "#000000"),
                            key=f"color_texto_desembolso_{producto_seleccionado}",
                            help="Color del texto del precio arriba de la barra"
                        )
                        
                        # Color de fondo del precio desembolso (solo Price Pack)
                        if modo == "Price Pack":
                            color_fondo_desembolso = st.color_picker(
                                "Color fondo (caja azul)",
                                value=st.session_state["custom_colors"].get(producto_seleccionado, {}).get("fondo_desembolso", "#00B0F0"),
                                key=f"color_fondo_desembolso_{producto_seleccionado}"
                            )
                        else:
                            color_fondo_desembolso = None
                    
                    with col_precio2:
                        st.markdown("**Precio por Kg (dentro)**")
                        # Color del texto del precio por kg
                        color_texto_pkg = st.color_picker(
                            "Color texto",
                            value=st.session_state["custom_colors"].get(producto_seleccionado, {}).get("texto_pkg", default_texto_pkg),
                            key=f"color_texto_pkg_{producto_seleccionado}",
                            help="Color del texto del precio por kg dentro de la barra"
                        )
                        
                        # Color de fondo del precio por kg
                        color_fondo_pkg = st.color_picker(
                            "Color fondo",
                            value=st.session_state["custom_colors"].get(producto_seleccionado, {}).get("fondo_pkg", default_fondo_pkg),
                            key=f"color_fondo_pkg_{producto_seleccionado}",
                            help="Color de fondo de la cajita del precio por kg"
                        )
                    
                    st.markdown("#### 🔲 Personalización de Bordes")
                    
                    col_borde1, col_borde2 = st.columns(2)
                    
                    with col_borde1:
                        if modo == "Price Pack":
                            # Color del borde del precio desembolso
                            color_borde_desembolso = st.color_picker(
                                "Borde Precio Desembolso",
                                value=st.session_state["custom_colors"].get(producto_seleccionado, {}).get("borde_desembolso", "#000000"),
                                key=f"color_borde_desembolso_{producto_seleccionado}"
                            )
                        else:
                            color_borde_desembolso = None
                    
                    with col_borde2:
                        # Color del borde del precio por kg
                        color_borde_pkg = st.color_picker(
                            "Borde Precio por Kg",
                            value=st.session_state["custom_colors"].get(producto_seleccionado, {}).get("borde_pkg", default_borde_pkg),
                            key=f"color_borde_pkg_{producto_seleccionado}"
                        )
                    
                    # Guardar todos los colores personalizados
                    st.session_state["custom_colors"][producto_seleccionado] = {
                        "barra": color_barra,
                        "texto_desembolso": color_texto_desembolso,
                        "fondo_desembolso": color_fondo_desembolso,
                        "texto_pkg": color_texto_pkg,
                        "fondo_pkg": color_fondo_pkg,
                        "borde_desembolso": color_borde_desembolso,
                        "borde_pkg": color_borde_pkg
                    }
                    
                    st.success(f"✅ Colores personalizados aplicados a: {producto_seleccionado}")
                    
                    # Botón para quitar personalización
                    if st.button(f"🗑️ Quitar personalización de {producto_seleccionado}", key=f"remove_custom_{producto_seleccionado}"):
                        if producto_seleccionado in st.session_state["custom_colors"]:
                            del st.session_state["custom_colors"][producto_seleccionado]
                            st.success(f"✅ Personalización eliminada de {producto_seleccionado}")
                            st.rerun()
                
                # Mostrar productos personalizados
                if st.session_state["custom_colors"]:
                    st.markdown("---")
                    st.markdown("**📋 Productos con colores personalizados:**")
                    for prod in list(st.session_state["custom_colors"].keys()):
                        col_prod, col_btn = st.columns([3, 1])
                        with col_prod:
                            st.caption(f"• {prod}")
                        with col_btn:
                            if st.button("🗑️", key=f"quick_remove_{prod}"):
                                del st.session_state["custom_colors"][prod]
                                st.rerun()
                            
        # --- SECCIÓN 4: HERRAMIENTAS AVANZADAS ---
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style='background: linear-gradient(135deg, #64748B 0%, #475569 100%); 
                        padding: 1rem; 
                        border-radius: 10px; 
                        margin-bottom: 1rem;
                        box-shadow: 0 2px 8px rgba(100, 116, 139, 0.3);'>
                <h3 style='color: white; margin: 0; font-weight: 600; text-align: center; font-size: 1.1rem;'>
                    🛠️ Herramientas
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            # MODO PRESENTACIÓN
            if st.button("🖥️ Modo Presentación", use_container_width=True, type="primary"):
                st.session_state["modo_presentacion"] = True
                st.rerun()
            
            if st.button("🔄 Refrescar Vista", use_container_width=True):
                st.rerun()
            
            # HISTORIAL DE CAMBIOS
            with st.expander("📜 Ver Historial de Cambios"):
                if st.session_state["historial_cambios"]:
                    df_historial = pd.DataFrame(st.session_state["historial_cambios"])
                    # Filtrar por modo actual
                    df_historial_modo = df_historial[df_historial["modo"] == modo]
                    
                    if not df_historial_modo.empty:
                        # Mostrar los últimos 10 cambios
                        st.dataframe(
                            df_historial_modo[["fecha", "producto", "campo", "anterior", "nuevo"]].tail(10),
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Botón para descargar historial completo
                        csv_historial = df_historial_modo.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Descargar Historial Completo",
                            data=csv_historial,
                            file_name=f'historial_{modo.lower().replace(" ", "_")}_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv',
                            mime='text/csv',
                            use_container_width=True
                        )
                        
                        # Botón para limpiar historial
                        if st.button("🗑️ Limpiar Historial", use_container_width=True):
                            st.session_state["historial_cambios"] = []
                            st.rerun()
                    else:
                        st.info(f"No hay cambios registrados para {modo}")
                else:
                    st.info("No hay cambios registrados aún")
            
            with st.expander("ℹ️ Información del Sistema"):
                st.markdown(f"""
                    **Modo Actual:** {modo}  
                    **Base de Datos:** `{DB_FILE}`  
                    **Estado:** {'✅ Datos cargados' if not st.session_state.data.empty else '⚠️ Sin datos'}  
                    **Última actualización:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
                """)
            
            # Reset con confirmación mejorada
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
                <div style='background: #FEF2F2; 
                            padding: 0.6rem; 
                            border-radius: 6px;
                            border-left: 3px solid #DC2626;'>
                    <p style='margin: 0; font-size: 0.8rem; color: #991B1B;'>
                        ⚠️ <strong>Zona de Peligro</strong>
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            confirmar_reset = st.checkbox("Confirmar eliminación de datos", value=False)
            
            if st.button(
                "🗑️ Resetear Sistema Completo", 
                use_container_width=True, 
                type="secondary",
                disabled=not confirmar_reset
            ):
                if confirmar_reset:
                    if DB_FILE and os.path.exists(DB_FILE): 
                        os.remove(DB_FILE)
                    st.session_state.data = pd.DataFrame(columns=columnas_tabla)
                    st.session_state["historial_cambios"] = []
                    st.session_state["comentarios_productos"] = {}
                    st.success("✅ Sistema reseteado correctamente")
                    st.rerun()
                else:
                    st.warning("⚠️ Debes confirmar la acción marcando la casilla")



# ============================================================================
# PANEL DE CONTROL EN SIDEBAR
# Este código va en tu sidebar, donde quieras que aparezca el panel
# ============================================================================

with st.sidebar:
    st.markdown("---")
    
    with st.expander("💾 Configuraciones", expanded=False):
        st.markdown("### Guardar/Cargar Presets")
        st.caption("Guarda tu configuración actual de diseño, grid y colores.")
        
        # ===== GUARDAR NUEVA =====
        st.markdown("#### 💾 Guardar Actual")
        nombre_nuevo = st.text_input(
            "Nombre del preset",
            placeholder="Ej: Presentación Ejecutiva",
            key="input_nombre_config"
        )
        
        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            if st.button("💾 Guardar", key="btn_guardar_config", use_container_width=True):
                if nombre_nuevo.strip():
                    guardar_configuracion(nombre_nuevo)
                    st.success(f"✅ '{nombre_nuevo}' guardado!")
                    st.rerun()
                else:
                    st.error("❌ Ingresa un nombre")
        
        with col_g2:
            num_configs = len(st.session_state["configs_guardadas"])
            st.metric("Total", num_configs)
        
        # ===== CARGAR EXISTENTE =====
        if st.session_state["configs_guardadas"]:
            st.markdown("---")
            st.markdown("#### 📂 Cargar Preset")
            
            config_seleccionada = st.selectbox(
                "Selecciona un preset",
                ["-- Ninguna --"] + list(st.session_state["configs_guardadas"].keys()),
                key="select_config"
            )
            
            if config_seleccionada != "-- Ninguna --":
                config_info = st.session_state["configs_guardadas"][config_seleccionada]
                
                st.info(f"""
📅 **Creada:** {config_info['fecha']}

**Incluye:**
- ✅ Tamaños de texto
- ✅ Dimensiones de gráfico
- ✅ Configuración de grid
- ✅ Colores personalizados ({len(config_info.get('colores_personalizados', {}))})
                """)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📂 Cargar", key="btn_cargar_config", use_container_width=True):
                        if cargar_configuracion(config_seleccionada):
                            st.success(f"✅ Cargado!")
                            st.rerun()
                
                with col2:
                    json_export = exportar_configuracion(config_seleccionada)
                    if json_export:
                        st.download_button(
                            "📥",
                            data=json_export,
                            file_name=f"{config_seleccionada.replace(' ', '_')}.json",
                            mime="application/json",
                            key="btn_export_config",
                            use_container_width=True
                        )
                
                with col3:
                    if st.button("🗑️", key="btn_delete_config", use_container_width=True):
                        if eliminar_configuracion(config_seleccionada):
                            st.success("✅ Eliminado!")
                            st.rerun()
                
                # Duplicar
                st.markdown("**Duplicar:**")
                col_d1, col_d2 = st.columns([2, 1])
                with col_d1:
                    nombre_dup = st.text_input(
                        "Nuevo nombre",
                        placeholder=f"{config_seleccionada} Copia",
                        key="input_duplicar",
                        label_visibility="collapsed"
                    )
                with col_d2:
                    if st.button("📋", key="btn_duplicar", use_container_width=True):
                        if nombre_dup.strip():
                            if duplicar_configuracion(config_seleccionada, nombre_dup):
                                st.success(f"✅ Duplicado!")
                                st.rerun()
        
        # ===== IMPORTAR =====
        st.markdown("---")
        st.markdown("#### 📤 Importar")
        archivo_config = st.file_uploader(
            "Sube JSON",
            type=["json"],
            key="upload_config",
            label_visibility="collapsed"
        )
        
        if archivo_config:
            try:
                json_str = archivo_config.read().decode("utf-8")
                nombre_importada = importar_configuracion(json_str)
                if nombre_importada:
                    st.success(f"✅ '{nombre_importada}' importado!")
                    st.rerun()
                else:
                    st.error("❌ Archivo inválido")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        
        # ===== LISTA RÁPIDA =====
        if st.session_state["configs_guardadas"]:
            st.markdown("---")
            st.markdown("#### 📋 Todos")
            
            for nombre in list(st.session_state["configs_guardadas"].keys()):
                col_n, col_b = st.columns([3, 1])
                with col_n:
                    st.caption(f"• {nombre}")
                with col_b:
                    if st.button("🗑️", key=f"qdel_{nombre}"):
                        if eliminar_configuracion(nombre):
                            st.rerun()
        else:
            st.info("💡 No hay presets. ¡Crea el primero!")
        
        # ===== AYUDA =====
        st.markdown("---")
        with st.expander("❓ Ayuda"):
            st.markdown("""
**Guardar:**
1. Ajusta sliders y colores
2. Dale un nombre
3. Click "Guardar"

**Cargar:**
1. Selecciona preset
2. Click "Cargar"
3. ¡Listo!

**Exportar/Importar:**
- Exportar: backup o compartir
- Importar: restaurar o usar de otros
            """)

        
        # --- FOOTER (AHORA AL FINAL) ---
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; padding: 1rem; border-top: 1px solid #E2E8F0;'>
                <p style='margin: 0; font-size: 0.75rem; color: #94A3B8;'>
                    🚀 Powered by <br>
                     Revenue Growth Management - Pricing
                </p>
            </div>
        """, unsafe_allow_html=True)


# ============================================================================
# 8. PANEL PRINCIPAL
# ============================================================================

# ============================================================================
# FIN DEL CÓDIGO DEL SIDEBAR
# ============================================================================
    
# --- 5. PANEL PRINCIPAL ---
iconos_modo = {
    "price ladder": "🪜",
    "price pack": "📦",
    "price and volume": "📊"
}
icono = iconos_modo.get(modo.lower(), "📊")
st.title(f"{icono} {modo.upper()}")
st.divider()

# --- 5. FORMULARIOS DE AGREGAR ---
if modo in ["Price Ladder", "Price Pack"]:
    
    if st.session_state.form_success:
        st.success("✅ ¡Producto agregado exitosamente!")
        st.session_state.form_success = False
    
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
                    nuevo = pd.DataFrame([{
                        "Producto": f_nom, 
                        "Fabricante": f_fab, 
                        "Ocasión": f_cat, 
                        "Precio ($)": f_pre, 
                        "Gramaje (g)": f_gra, 
                        "SOM (%)": f_som
                    }])
                    st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
                    st.session_state.data = calcular_pkg(st.session_state.data, modo)
                    st.session_state.data.to_csv(DB_FILE, index=False)
                    st.session_state.form_success = True
                    st.rerun()
            
            else:
                f_fam = col2.text_input("Familia").upper()
                f_can = col3.selectbox("Canal", opciones_agru)
                col4, col5 = st.columns(2)
                f_pre = col4.number_input("Precio ($)", min_value=0.0, step=0.5)
                f_gra = col5.number_input("Gramaje (g)", min_value=1.0, step=1.0)
                
                if st.form_submit_button("Añadir a Price Pack"):
                    nuevo = pd.DataFrame([{
                        "Producto": f_nom, 
                        "Familia": f_fam, 
                        "Canal": f_can, 
                        "Precio ($)": f_pre, 
                        "Gramaje (g)": f_gra
                    }])
                    st.session_state.data = pd.concat([st.session_state.data, nuevo], ignore_index=True)
                    st.session_state.data = calcular_pkg(st.session_state.data, modo)
                    st.session_state.data.to_csv(DB_FILE, index=False)
                    st.session_state.form_success = True
                    st.rerun()

# --- 5.5 CAMBIOS MASIVOS ---
if modo in ["Price Ladder", "Price Pack"]:
    st.write("")
    with st.expander("⚡ Aplicar Cambios Masivos", expanded=False):
        st.markdown("### 🎯 Herramienta de Modificación Masiva")
        
        # Paso 1: Seleccionar filtro
        st.markdown("**Paso 1: ¿A qué productos aplicar el cambio?**")
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            tipo_filtro = st.radio(
                "Filtrar por:",
                ["Todos los productos", "Fabricante", "Ocasión/Canal", "Producto específico"],
                key="tipo_filtro_masivo"
            )
        
        with col_filtro2:
            productos_afectados = []
            
            if tipo_filtro == "Fabricante" and "Fabricante" in st.session_state.data.columns:
                fab_seleccionado = st.selectbox("Selecciona fabricante:", st.session_state.data["Fabricante"].unique())
                productos_afectados = st.session_state.data[st.session_state.data["Fabricante"] == fab_seleccionado]["Producto"].tolist()
            
            elif tipo_filtro == "Ocasión/Canal":
                if modo == "Price Ladder":
                    oca_seleccionada = st.selectbox("Selecciona ocasión:", st.session_state.data["Ocasión"].unique())
                    productos_afectados = st.session_state.data[st.session_state.data["Ocasión"] == oca_seleccionada]["Producto"].tolist()
                else:
                    canal_seleccionado = st.selectbox("Selecciona canal:", st.session_state.data["Canal"].unique())
                    productos_afectados = st.session_state.data[st.session_state.data["Canal"] == canal_seleccionado]["Producto"].tolist()
            
            elif tipo_filtro == "Producto específico":
                prod_seleccionado = st.selectbox("Selecciona producto:", st.session_state.data["Producto"].unique())
                productos_afectados = [prod_seleccionado]
            
            else:  # Todos
                productos_afectados = st.session_state.data["Producto"].tolist()
        
        if productos_afectados:
            st.info(f"📦 Se aplicará a **{len(productos_afectados)}** producto(s)")
        
        # Paso 2: Tipo de cambio
        st.markdown("---")
        st.markdown("**Paso 2: ¿Qué cambio aplicar?**")
        
        tipo_cambio = st.selectbox(
            "Tipo de modificación:",
            ["Ajustar precio (%)", "Ajustar precio ($)", "Cambiar gramaje", "Ajustar $/Kg objetivo"],
            key="tipo_cambio_masivo"
        )
        
        col_valor1, col_valor2 = st.columns(2)
        
        with col_valor1:
            if tipo_cambio == "Ajustar precio (%)":
                porcentaje = st.number_input("% de cambio (ej: 5 para +5%, -10 para -10%):", value=0.0, step=0.5, key="input_porcentaje")
            elif tipo_cambio == "Ajustar precio ($)":
                cantidad = st.number_input("Cantidad a sumar/restar ($):", value=0.0, step=0.5, key="input_cantidad")
            elif tipo_cambio == "Cambiar gramaje":
                nuevo_gramaje = st.number_input("Nuevo gramaje (g):", min_value=1.0, value=50.0, step=1.0, key="input_gramaje")
            else:  # $/Kg objetivo
                pkg_objetivo = st.number_input("$/Kg objetivo:", min_value=0.0, value=100.0, step=1.0, key="input_pkg")
        
        # Vista previa
        st.markdown("---")
        st.markdown("**Vista Previa de Cambios:**")
        
        if st.button("🔍 Generar Vista Previa", use_container_width=True):
            df_preview = st.session_state.data[st.session_state.data["Producto"].isin(productos_afectados)].copy()
            
            if tipo_cambio == "Ajustar precio (%)":
                df_preview["Precio Nuevo ($)"] = df_preview["Precio ($)"] * (1 + porcentaje/100)
                df_preview["Diferencia ($)"] = df_preview["Precio Nuevo ($)"] - df_preview["Precio ($)"]
            elif tipo_cambio == "Ajustar precio ($)":
                df_preview["Precio Nuevo ($)"] = df_preview["Precio ($)"] + cantidad
                df_preview["Diferencia ($)"] = cantidad
            elif tipo_cambio == "Cambiar gramaje":
                df_preview["Gramaje Nuevo (g)"] = nuevo_gramaje
                df_preview["Diferencia (g)"] = nuevo_gramaje - df_preview["Gramaje (g)"]
            else:  # $/Kg objetivo
                df_preview["Gramaje Nuevo (g)"] = (df_preview["Precio ($)"] / pkg_objetivo) * 1000
                df_preview["Diferencia (g)"] = df_preview["Gramaje Nuevo (g)"] - df_preview["Gramaje (g)"]
            
            st.dataframe(df_preview, use_container_width=True, hide_index=True)
        
        # Aplicar cambios
        st.markdown("---")
        
        col_aplicar, col_cancelar = st.columns(2)
        
        with col_aplicar:
            if st.button("✅ APLICAR CAMBIOS", type="primary", use_container_width=True):
                for prod in productos_afectados:
                    mask = st.session_state.data["Producto"] == prod
                    
                    if tipo_cambio == "Ajustar precio (%)":
                        valor_anterior = st.session_state.data.loc[mask, "Precio ($)"].values[0]
                        valor_nuevo = valor_anterior * (1 + porcentaje/100)
                        st.session_state.data.loc[mask, "Precio ($)"] = valor_nuevo
                        registrar_cambio(prod, "Precio ($)", valor_anterior, valor_nuevo, modo)
                    
                    elif tipo_cambio == "Ajustar precio ($)":
                        valor_anterior = st.session_state.data.loc[mask, "Precio ($)"].values[0]
                        valor_nuevo = valor_anterior + cantidad
                        st.session_state.data.loc[mask, "Precio ($)"] = valor_nuevo
                        registrar_cambio(prod, "Precio ($)", valor_anterior, valor_nuevo, modo)
                    
                    elif tipo_cambio == "Cambiar gramaje":
                        valor_anterior = st.session_state.data.loc[mask, "Gramaje (g)"].values[0]
                        st.session_state.data.loc[mask, "Gramaje (g)"] = nuevo_gramaje
                        registrar_cambio(prod, "Gramaje (g)", valor_anterior, nuevo_gramaje, modo)
                    
                    else:  # $/Kg objetivo
                        precio_actual = st.session_state.data.loc[mask, "Precio ($)"].values[0]
                        gramaje_anterior = st.session_state.data.loc[mask, "Gramaje (g)"].values[0]
                        gramaje_nuevo = (precio_actual / pkg_objetivo) * 1000
                        st.session_state.data.loc[mask, "Gramaje (g)"] = gramaje_nuevo
                        registrar_cambio(prod, "Gramaje (g)", gramaje_anterior, gramaje_nuevo, modo)
                
                # Recalcular $/Kg
                st.session_state.data = calcular_pkg(st.session_state.data, modo)
                st.session_state.data.to_csv(DB_FILE, index=False)
                
                st.success(f"✅ Cambios aplicados a {len(productos_afectados)} producto(s)!")
                st.rerun()

# --- 6. EDITOR DE TABLA CON COMENTARIOS Y TRACKING ---
if modo in ["Price Ladder", "Price Pack"]:
    st.markdown("### 📝 Gestión de Portafolio")

    # 🔍 BUSCADOR DE PRODUCTOS
    search_term = st.text_input(
        "🔍 Buscar producto:",
        placeholder="Escribe el nombre del producto para filtrar...",
        key="search_productos"
    )

    # Crear copia con comentarios
    df_with_selections = st.session_state.data.copy()
    
    # APLICAR FILTRO DE BÚSQUEDA
    if search_term:
        df_with_selections = df_with_selections[
            df_with_selections["Producto"].str.contains(search_term, case=False, na=False)
        ]
        st.info(f"🔍 Mostrando **{len(df_with_selections)}** productos que coinciden con '{search_term}'")
    
    if "Select" not in df_with_selections.columns:
        df_with_selections.insert(0, "Select", False)
    
    # Agregar columna de comentarios
    df_with_selections["💬 Comentarios"] = df_with_selections["Producto"].apply(
        lambda x: st.session_state["comentarios_productos"].get(x, "")
    )

    # El editor de datos con comentarios
    edited_df = st.data_editor(
        df_with_selections, 
        num_rows="dynamic",
        use_container_width=True,
        key="portfolio_editor",
        hide_index=True,
        column_config={
            "💬 Comentarios": st.column_config.TextColumn(
                "💬 Comentarios",
                help="Agrega notas o comentarios sobre este producto",
                max_chars=200,
                width="medium"
            )
        }
    )

    # BOTONES DE ACCIÓN
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])

    with col_btn1:
        if st.button("🗑️ Eliminar seleccionados", type="secondary"):
            df_final = edited_df[edited_df["Select"] == False].drop(columns=["Select", "💬 Comentarios"])
            
            # Registrar eliminaciones en historial
            productos_eliminados = edited_df[edited_df["Select"] == True]["Producto"].tolist()
            for prod in productos_eliminados:
                registrar_cambio(prod, "ELIMINADO", "Existente", "Eliminado", modo)
                # Eliminar comentario asociado
                if prod in st.session_state["comentarios_productos"]:
                    del st.session_state["comentarios_productos"][prod]
            
            st.session_state.data = calcular_pkg(df_final, modo)
            st.session_state.data.to_csv(DB_FILE, index=False)
            st.success("Filas eliminadas correctamente")
            st.rerun()
    
    with col_btn2:
        # BOTÓN: GUARDAR CAMBIOS
        if st.button("💾 Guardar Cambios", type="primary"):
            current_data_no_select = edited_df.drop(columns=["Select", "💬 Comentarios"])
            
            # Guardar comentarios actualizados
            for idx, row in edited_df.iterrows():
                producto = row["Producto"]
                comentario_nuevo = row["💬 Comentarios"]
                comentario_anterior = st.session_state["comentarios_productos"].get(producto, "")
                
                if comentario_nuevo != comentario_anterior:
                    st.session_state["comentarios_productos"][producto] = comentario_nuevo
                    if comentario_nuevo:
                        registrar_cambio(producto, "Comentario", comentario_anterior, comentario_nuevo, modo)
            
            # Detectar cambios en datos numéricos
            if not current_data_no_select.equals(st.session_state.data):
                # Comparar fila por fila
                for idx, row in current_data_no_select.iterrows():
                    producto = row["Producto"]
                    if producto in st.session_state.data["Producto"].values:
                        old_row = st.session_state.data[st.session_state.data["Producto"] == producto].iloc[0]
                        
                        # Revisar cada campo
                        for col in ["Precio ($)", "Gramaje (g)", "SOM (%)"]:
                            if col in row.index and col in old_row.index:
                                if pd.notna(row[col]) and pd.notna(old_row[col]):
                                    if abs(float(row[col]) - float(old_row[col])) > 0.01:
                                        registrar_cambio(producto, col, old_row[col], row[col], modo)
                
                st.session_state.data = calcular_pkg(current_data_no_select, modo)
                st.session_state.data.to_csv(DB_FILE, index=False)
                st.success("✅ Cambios guardados correctamente!")
                st.rerun()
            else:
                st.info("No hay cambios que guardar")
    
    with col_btn3:
        # BOTÓN: DUPLICAR PRODUCTO
        with st.expander("📋 Duplicar Producto"):
            productos_lista = st.session_state.data["Producto"].unique().tolist()
            producto_duplicar = st.selectbox(
                "Selecciona producto a duplicar:",
                productos_lista,
                key="select_duplicar"
            )
            
            nuevo_nombre = st.text_input(
                "Nombre del duplicado:",
                value=f"{producto_duplicar} - COPIA",
                key="input_duplicar"
            )
            
            if st.button("📋 Duplicar", key="btn_duplicar", use_container_width=True, type="primary"):
                # Obtener datos del producto original
                producto_original = st.session_state.data[st.session_state.data["Producto"] == producto_duplicar].iloc[0]
                
                # Crear copia
                nuevo_producto = producto_original.copy()
                nuevo_producto["Producto"] = nuevo_nombre
                
                # Agregar a la tabla
                st.session_state.data = pd.concat([st.session_state.data, nuevo_producto.to_frame().T], ignore_index=True)
                st.session_state.data = calcular_pkg(st.session_state.data, modo)
                st.session_state.data.to_csv(DB_FILE, index=False)
                
                # Registrar en historial
                registrar_cambio(nuevo_nombre, "CREADO", "N/A", f"Duplicado de {producto_duplicar}", modo)
                
                # Copiar comentarios si existen
                if producto_duplicar in st.session_state["comentarios_productos"]:
                    st.session_state["comentarios_productos"][nuevo_nombre] = st.session_state["comentarios_productos"][producto_duplicar] + " [DUPLICADO]"
                
                st.success(f"✅ Producto '{nuevo_nombre}' creado exitosamente!")
                st.rerun()
    
    # Indicador visual de cambios pendientes
    current_data_no_select = edited_df.drop(columns=["Select", "💬 Comentarios"])
    if not current_data_no_select.equals(st.session_state.data):
        st.warning("⚠️ **Hay cambios sin guardar.** Presiona el botón '💾 Guardar Cambios' para aplicarlos.")
        
# --- 6.5 FILTROS DINÁMICOS UNIFICADOS ---
sel_fab, sel_oca, sel_prod = [], [], []
sel_canal_pp, sel_prod_pp = [], []

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

elif modo == "Price Pack":
    st.write("") 
    with st.container(border=True):
        st.markdown("### 🔍 Filtros de Visualización (Price Pack)")
        
        if "Canal" in st.session_state.data.columns:
            col_pp1, col_pp2 = st.columns(2)
    
            with col_pp1:
                lista_canales = sorted(st.session_state.data["Canal"].unique().tolist())
                sel_canal_pp = st.multiselect("Filtrar por Canal", lista_canales, key="filter_pp_canal")
    
            with col_pp2:
                lista_prod_pp = sorted(st.session_state.data["Producto"].unique().tolist())
                sel_prod_pp = st.multiselect("Filtrar por Producto", lista_prod_pp, key="filter_pp_prod")

# --- 6.8 PANEL EJECUTIVO ---
if modo == "Price Ladder" and not st.session_state.data.empty:
    df_filtered = st.session_state.data.copy()
    if sel_fab:
        df_filtered = df_filtered[df_filtered["Fabricante"].isin(sel_fab)]
    if sel_oca:
        df_filtered = df_filtered[df_filtered["Ocasión"].isin(sel_oca)]
    if sel_prod:
        df_filtered = df_filtered[df_filtered["Producto"].isin(sel_prod)]
    
    if not df_filtered.empty:
        st.write("### 📈 Resumen de Mercado por Ocasión")
        
        resumen_oca = df_filtered.groupby("Ocasión").agg({
            "Producto": "count",
            "Precio ($)": "mean",
            "Precio por Kg ($)": "mean"
        }).reset_index()

        ord_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5, "REUNIÓN": 6, "FIESTA": 7, "TRANSFORMADOR": 8}
        resumen_oca["Orden"] = resumen_oca["Ocasión"].str.upper().map(ord_oca).fillna(99)
        resumen_oca = resumen_oca.sort_values("Orden")

        st.dataframe(
            resumen_oca[["Ocasión", "Producto", "Precio ($)", "Precio por Kg ($)"]],
            column_config={
                "Ocasión": st.column_config.TextColumn("Segmento / Ocasión"),
                "Producto": st.column_config.NumberColumn("SKUs", help="Cantidad de SKUs analizados"),
                "Precio ($)": st.column_config.NumberColumn("Desembolso Prom.", format="$%.1f"),
                "Precio por Kg ($)": st.column_config.NumberColumn("$/KG Promedio", format="$%d"),
            },
            hide_index=True,
            use_container_width=True
        )
        st.write("")

# --- 7. GRÁFICO FINAL CON CONFIGURACIÓN DE GRID ---
if not st.session_state.data.empty:
    
    df_p = st.session_state.data.copy()
    
    if modo == "Price Ladder":
        if sel_fab:
            df_p = df_p[df_p["Fabricante"].isin(sel_fab)]
        if sel_oca:
            df_p = df_p[df_p["Ocasión"].isin(sel_oca)]
        if sel_prod:
            df_p = df_p[df_p["Producto"].isin(sel_prod)]
    elif modo == "Price Pack":
        if sel_canal_pp:
            df_p = df_p[df_p["Canal"].isin(sel_canal_pp)]
        if sel_prod_pp:
            df_p = df_p[df_p["Producto"].isin(sel_prod_pp)]

    if df_p.empty:
        st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados.")
    else:
        if modo == "Price Ladder":
            ord_oca = {"BITES": 1, "INDIVIDUAL": 2, "HAMBRE": 3, "COMPARTIR": 4, "FAMILIAR": 5,"REUNIÓN":6, "FIESTA":7,"TRANSFORMADOR":8}
            df_p["O_Oca"] = df_p["Ocasión"].str.upper().map(ord_oca).fillna(99)
            
            df_p = df_p.sort_values(by=["O_Oca", "Precio ($)", "Precio por Kg ($)"]).reset_index(drop=True)
            som_por_ocasion = df_p.groupby("Ocasión")["SOM (%)"].sum().to_dict()

            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=espacio_v, row_heights=[0.13, 0.09, 0.78])

            fig.add_trace(go.Scatter(
                x=df_p["Producto"], y=df_p["SOM (%)"], mode="lines+markers+text", 
                line=dict(color="#BBBBBB", width=1.5), 
                marker=dict(size=30, color="#E5E5E5", symbol="square", line=dict(color="#CCCCCC", width=1)), 
                text=[f"<b>{row['SOM (%)']}%</b>" for _, row in df_p.iterrows()],
                textposition="middle center", textfont=dict(size=t_som, color="black"),
                showlegend=False,
            ), row=1, col=1)

            # --- FILA 2 (NUEVA): trace invisible solo para habilitar el eje de la franja de "Escalón de Precio" ---
            fig.add_trace(go.Scatter(
                x=df_p["Producto"], y=[0] * len(df_p), mode="markers",
                marker=dict(size=0.001, color="rgba(0,0,0,0)"),
                showlegend=False, hoverinfo="skip"
            ), row=2, col=1)

            # --- TRACE 2: BARRAS DE PRECIO CON PERSONALIZACIÓN Y ALTO AJUSTABLE ---
            colors = {"BARCEL": "#0B3C8C", "SABRITAS": "#F5C400", "OTROS": "#7F8C8D","PROPUESTA":"#4B207E"}

            bar_colors = []
            label_colors_desembolso = []

            for _, row in df_p.iterrows():
                # Color de la barra
                if row["Producto"] in st.session_state["custom_colors"]:
                    bar_colors.append(st.session_state["custom_colors"][row["Producto"]]["barra"])
                    label_colors_desembolso.append(st.session_state["custom_colors"][row["Producto"]].get("texto_desembolso", "black"))
                else:
                    bar_colors.append(colors.get(str(row["Fabricante"]).upper(), "#999"))
                    label_colors_desembolso.append("black")

            labels_precios = []
            for _, row in df_p.iterrows():
                p = row["Precio ($)"]
                if p < 10:
                    labels_precios.append(f"${p:.1f}")
                else:
                    labels_precios.append(f"${int(p)}")

            # Crear un trace por cada producto con alto ajustable
            for idx, (i, row) in enumerate(df_p.iterrows()):
                fig.add_trace(go.Bar(
                    x=[row["Producto"]], 
                    y=[row["Precio ($)"] * alto_barras],  # ⭐ APLICAR MULTIPLICADOR DE ALTO
                    marker_color=bar_colors[idx],
                    marker_opacity=opacidad_barras, 
                    marker_line=dict(
                        color=st.session_state.get("color_contorno_barras", "#000000"),
                        width=st.session_state.get("grosor_contorno_barras", 1.0)
                    ),
                    width=ancho_barras,
                    text=[f"<b>{labels_precios[idx]}</b>"],
                    textposition="outside", 
                    textfont=dict(size=t_precios, color=label_colors_desembolso[idx]),
                    showlegend=False,
                    hovertemplate=f"{row['Producto']}<br>Precio: ${row['Precio ($)']}<extra></extra>"
                ), row=3, col=1)

            # Anotaciones de Precio por Kg dentro de las barras - CON PERSONALIZACIÓN
            for i, row in df_p.iterrows():
                # Obtener colores personalizados o usar defaults
                if row["Producto"] in st.session_state["custom_colors"]:
                    custom = st.session_state["custom_colors"][row["Producto"]]
                    color_texto_pkg = custom.get("texto_pkg", "white" if row["Fabricante"] == "BARCEL" else "black")
                    
                    # Convertir el color del fondo si viene en formato hex
                    fondo_pkg_custom = custom.get("fondo_pkg", None)
                    if fondo_pkg_custom and fondo_pkg_custom.startswith("#"):
                        # Convertir hex a rgba con opacidad
                        import matplotlib.colors as mcolors
                        try:
                            rgb = mcolors.hex2color(fondo_pkg_custom)
                            color_fondo_pkg = f"rgba({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)}, 0.8)"
                        except:
                            color_fondo_pkg = fondo_pkg_custom
                    else:
                        color_fondo_pkg = fondo_pkg_custom if fondo_pkg_custom else ("rgba(70, 130, 180, 0.8)" if row["Fabricante"] == "BARCEL" else "rgba(255,255,255,0.8)")
                    
                    color_borde_pkg = custom.get("borde_pkg", "#444" if row["Fabricante"] != "BARCEL" else None)
                else:
                    color_texto_pkg = "white" if row["Fabricante"] == "BARCEL" else "black"
                    color_fondo_pkg = "rgba(70, 130, 180, 0.8)" if row["Fabricante"] == "BARCEL" else "rgba(255,255,255,0.8)"
                    color_borde_pkg = "#444" if row["Fabricante"] != "BARCEL" else None
                
                fig.add_annotation(
                    x=i, y=2.5 * alto_barras,  # ⭐ AJUSTAR POSICIÓN SEGÚN ALTO DE BARRAS
                    text=f"<b>${int(row['Precio por Kg ($)'])}</b>",
                    showarrow=False, 
                    font=dict(size=t_pkg, color=color_texto_pkg),
                    bgcolor=color_fondo_pkg,
                    bordercolor=color_borde_pkg,
                    borderwidth=1, 
                    row=3, col=1
                )

            for i in range(len(df_p) + 1):
                fig.add_shape(type="line", x0=i-0.5, x1=i-0.5, y0=-0.01, y1=-0.50, xref="x3", yref="paper", line=dict(color="#DDDDDD", width=1))

            for cat in df_p["Ocasión"].unique():
                idx_list = df_p.index[df_p["Ocasión"] == cat].tolist()
                fig.add_shape(
                    type="line", x0=idx_list[-1] + 0.5, x1=idx_list[-1] + 0.5, 
                    y0=-0.60, y1=1, xref="x3", yref="paper", 
                    line=dict(color="#CCCCCC", width=2)
                )
                center = (idx_list[0] + idx_list[-1]) / 2
                fig.add_annotation(
                    x=center, y=-0.60, xref="x3", yref="paper", 
                    text=f"<b>{cat}</b><br><span style='font-size:18px;'>{som_por_ocasion[cat]:.1f}%</span>", 
                    showarrow=False, font=dict(size=16, color="black"), align="center"
                )

            # --- PESO POR ESCALÓN DE PRECIO (TIER): suma de SOM de los productos que comparten el mismo precio ---
            # Ahora vive en su propia fila (fila 2), entre el gráfico de SOM y la escalera de precios,
            # con bandas intercaladas teal/lavanda: neutras, no compiten con Barcel (azul) ni Sabritas (dorado).
            df_p["_grupo_precio"] = (df_p["Precio ($)"] != df_p["Precio ($)"].shift()).cumsum()
            resumen_tiers = df_p.groupby("_grupo_precio").agg(
                precio=("Precio ($)", "first"),
                som_total=("SOM (%)", "sum"),
            )
            resumen_tiers["idx_ini"] = df_p.groupby("_grupo_precio").apply(lambda g: g.index[0])
            resumen_tiers["idx_fin"] = df_p.groupby("_grupo_precio").apply(lambda g: g.index[-1])

            # Marco superior e inferior que enmarca toda la franja del tier, para que se lea como una banda propia
            fig.add_shape(
                type="line", x0=0, x1=1, y0=1, y1=1, xref="paper", yref="y2 domain",
                line=dict(color="#AFAFAF", width=1.5)
            )
            fig.add_shape(
                type="line", x0=0, x1=1, y0=0, y1=0, xref="paper", yref="y2 domain",
                line=dict(color="#AFAFAF", width=1.5)
            )

            # Bandas alternadas: teal suave / lavanda suave, con su texto a juego (más saturado para contraste)
            bandas_tier = [
                {"fondo": "#DFF3F1", "texto": "#0E6E63"},   # teal suave
                {"fondo": "#F1EAF9", "texto": "#6A3E9B"},   # lavanda suave
            ]

            for n_tier, (_, fila_tier) in enumerate(resumen_tiers.iterrows()):
                idx_ini, idx_fin = fila_tier["idx_ini"], fila_tier["idx_fin"]
                center_tier = (idx_ini + idx_fin) / 2
                p_val = fila_tier["precio"]
                precio_txt_tier = f"${p_val:.1f}" if p_val < 10 else f"${int(p_val)}"

                banda = bandas_tier[n_tier % 2]
                color_fondo_tier = banda["fondo"]
                color_texto_tier = "#333333"
                color_pct_tier = banda["texto"]

                # Fondo intercalado para cada escalón de precio
                fig.add_shape(
                    type="rect",
                    x0=idx_ini - 0.5, x1=idx_fin + 0.5, y0=0, y1=1,
                    xref="x2", yref="y2 domain",
                    fillcolor=color_fondo_tier,
                    line=dict(color="rgba(0,0,0,0)", width=0),
                    layer="below"
                )

                # Línea divisoria entre escalones de precio (dentro de la franja de la fila 2)
                if idx_fin < len(df_p) - 1:
                    fig.add_shape(
                        type="line", x0=idx_fin + 0.5, x1=idx_fin + 0.5,
                        y0=0, y1=1, xref="x2", yref="y2 domain",
                        line=dict(color="rgba(0,0,0,0.12)", width=1)
                    )

                fig.add_annotation(
                    x=center_tier, y=0.5, xref="x2", yref="y2 domain",
                    text=f"<span style='color:{color_texto_tier};'><b>{precio_txt_tier}</b></span><br><span style='font-size:13px; color:{color_pct_tier};'><b>{fila_tier['som_total']:.1f}%</b></span>",
                    showarrow=False, font=dict(size=12), align="center"
                )

            # --- LEYENDA DE COLORES POR FABRICANTE ---
            # Trazas "fantasma" (sin datos reales) solo para que aparezcan en la leyenda.
            # Las barras reales siguen con showlegend=False, así que esto no las duplica.
            fabricantes_presentes = df_p["Fabricante"].astype(str).str.upper().unique().tolist()
            for fab in ["BARCEL", "SABRITAS", "OTROS", "PROPUESTA"]:
                if fab in fabricantes_presentes:
                    fig.add_trace(go.Bar(
                        x=[None], y=[None],
                        marker_color=colors.get(fab, "#999"),
                        marker_line=dict(
                            color=st.session_state.get("color_contorno_barras", "#000000"),
                            width=st.session_state.get("grosor_contorno_barras", 1.0)
                        ),
                        name=fab.title(),
                        showlegend=True,
                    ), row=3, col=1)

            fig.update_layout(
                height=alto_grafico, width=1950, template="plotly_white", showlegend=True, 
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.06, xanchor="center", x=0.5,
                    font=dict(size=13)
                ),
                margin=dict(t=85, b=margen_b, l=40, r=40),
                # Configuración de layer para el grid
                xaxis_layer=st.session_state.get("grid_layer", "below traces"),
                yaxis_layer=st.session_state.get("grid_layer", "below traces"),
            )
            
            fig.update_xaxes(
                tickangle=angulo_nombres, 
                tickfont=dict(size=t_nombres, color="black"),
                showline=False,
                showgrid=grid_x_visible,
                gridcolor=grid_color,
                gridwidth=grid_grosor,
                griddash=grid_estilo,
                row=3, col=1
            )
            
            fig.update_yaxes(showticklabels=False, showgrid=False, row=1, col=1)
            fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, row=2, col=1)
            fig.update_yaxes(
                showgrid=grid_y_visible,
                gridcolor=grid_color,
                gridwidth=grid_grosor,
                griddash=grid_estilo,
                nticks=nticks_y,
                tickprefix="$", 
                tickfont=dict(size=14), 
                row=3, col=1
            )
            
            st.markdown("""
                <style>
                .st-key-card_price_ladder {
                    background-color: #FFFFFF;
                    border-radius: 14px;
                    padding: 20px 16px 8px 16px;
                    box-shadow: 0 4px 18px rgba(0,0,0,0.10);
                    border: 1px solid #EEEEEE;
                }
                </style>
            """, unsafe_allow_html=True)

            with st.container(border=False, key="card_price_ladder"):
                st.plotly_chart(fig, use_container_width=True, config={
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'Price_Ladder_Export',
                        'height': alto_grafico,
                        'width': 1950,
                        'scale': 2
                    }
                })

        elif modo == "Price Pack" and "Canal" in st.session_state.data.columns:
            ord_can = {"INSTITUCIONALES": 1, "MAYOREO": 2, "CLUBES": 3, "DETALLE": 4, "AUTOSERVICIOS": 5, "CONVENIENCIA": 6}
            df_p["O_Can"] = df_p["Canal"].str.upper().map(ord_can).fillna(99)
            df_p = df_p.sort_values(by=["O_Can", "Precio ($)"]).reset_index(drop=True)
            
            import plotly.graph_objects as go
            fig = go.Figure()

            # ✨ APLICAR COLORES PERSONALIZADOS Y ALTO AJUSTABLE EN PRICE PACK
            bar_colors_pp = []
            for _, row in df_p.iterrows():
                if row["Producto"] in st.session_state["custom_colors"]:
                    bar_colors_pp.append(st.session_state["custom_colors"][row["Producto"]]["barra"])
                else:
                    bar_colors_pp.append("#F8F9FA")

            fig.add_trace(go.Bar(
                x=df_p.index, 
                y=df_p["Precio por Kg ($)"] * alto_barras,  # ⭐ APLICAR MULTIPLICADOR DE ALTO
                marker_color=bar_colors_pp,
                marker_line=dict(
                    color=st.session_state.get("color_contorno_barras", "#000000"),
                    width=st.session_state.get("grosor_contorno_barras", 1.0)
                ),
                marker_opacity=opacidad_barras,
                width=ancho_barras,
                showlegend=False
            ))
            
            for i in range(len(df_p) + 1):
                fig.add_shape(
                    type="line", x0=i-0.5, x1=i-0.5, 
                    y0=-0.45, y1=0, 
                    xref="x", yref="paper",
                    line=dict(color="#EEEEEE", width=1)
                ) 

            # Iteración para etiquetas y anotaciones - CON PERSONALIZACIÓN COMPLETA
            for i, r in df_p.iterrows():
                # Obtener colores personalizados
                if r["Producto"] in st.session_state["custom_colors"]:
                    custom = st.session_state["custom_colors"][r["Producto"]]
                    color_texto_pkg = custom.get("texto_pkg", "#212121")
                    
                    # Convertir fondo_pkg de hex a rgba si es necesario
                    fondo_pkg_custom = custom.get("fondo_pkg", "rgba(255,255,255,0.9)")
                    if fondo_pkg_custom and fondo_pkg_custom.startswith("#"):
                        import matplotlib.colors as mcolors
                        try:
                            rgb = mcolors.hex2color(fondo_pkg_custom)
                            color_fondo_pkg = f"rgba({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)}, 0.9)"
                        except:
                            color_fondo_pkg = fondo_pkg_custom
                    else:
                        color_fondo_pkg = fondo_pkg_custom
                    
                    color_borde_pkg = custom.get("borde_pkg", "#616161")
                    color_texto_desembolso = custom.get("texto_desembolso", "white")
                    color_fondo_desembolso = custom.get("fondo_desembolso", "#00B0F0")
                    color_borde_desembolso = custom.get("borde_desembolso", "black")
                else:
                    color_texto_pkg = "#212121"
                    color_fondo_pkg = "rgba(255,255,255,0.9)"
                    color_borde_pkg = "#616161"
                    color_texto_desembolso = "white"
                    color_fondo_desembolso = "#00B0F0"
                    color_borde_desembolso = "black"
                
                # ETIQUETAS PARA $/KG
                val_pkg_pp = r['Precio por Kg ($)']
                txt_pkg_pp = f"${val_pkg_pp:,.0f}"

                fig.add_annotation(
                    x=i, y=r["Precio por Kg ($)"] * alto_barras,  # ⭐ AJUSTAR SEGÚN ALTO
                    text=f"<b>{txt_pkg_pp}</b>", 
                    yshift=15, 
                    showarrow=False, 
                    font=dict(size=t_pkg, color=color_texto_pkg),
                    bgcolor=color_fondo_pkg, 
                    bordercolor=color_borde_pkg, 
                    borderwidth=1
                )
                
                # ETIQUETAS PARA PRECIO DESEMBOLSO
                p_pp = r['Precio ($)']
                txt_p_pp = f"${p_pp:.1f}" if p_pp < 10 else f"${int(p_pp)}"

                fig.add_annotation(
                    x=i, y=15 * alto_barras,  # ⭐ AJUSTAR SEGÚN ALTO
                    text=f"<b>{txt_p_pp}</b>", 
                    showarrow=False, 
                    font=dict(size=t_precios, color=color_texto_desembolso),
                    bgcolor=color_fondo_desembolso, 
                    bordercolor=color_borde_desembolso, 
                    borderwidth=1.5,      
                    borderpad=4
                )
            
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
            
            fig.update_layout(
                height=alto_grafico,
                margin=dict(b=margen_b, t=50, l=50, r=50),
                template="plotly_white",
                # Configuración de layer para el grid
                xaxis_layer=st.session_state.get("grid_layer", "below traces"),
                yaxis_layer=st.session_state.get("grid_layer", "below traces"),
                xaxis=dict(
                    tickmode='array', 
                    tickvals=list(df_p.index), 
                    ticktext=["<b>"+str(t)+"</b>" for t in df_p["Producto"]],
                    tickangle=angulo_nombres,
                    tickfont=dict(color="#000000", size=t_nombres, family="Verdana"),
                    showgrid=grid_x_visible,
                    gridcolor=grid_color,
                    gridwidth=grid_grosor,
                    griddash=grid_estilo,
                ),
                yaxis=dict(
                    tickprefix="$", 
                    showgrid=grid_y_visible,
                    gridcolor=grid_color,
                    gridwidth=grid_grosor,
                    griddash=grid_estilo,
                    nticks=nticks_y,
                )
            )
    
            st.plotly_chart(fig, use_container_width=True, config={
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'Price_Pack_Export',
                    'height': alto_grafico,
                    'width': 1950,
                    'scale': 2
                }
            })
                
# --- 8. COMPARATIVAS INDEX (UNIFICADO: LADDER + ARQUITECTURA PPT) ---

# Agregamos la condición para que esta sección solo se ejecute en los modos que usan Index
if not st.session_state.data.empty:
    st.divider()
    df_comp = st.session_state.data.copy()
    
    # Limpieza estándar segura (solo si las columnas existen)
    for col in ["Precio ($)", "Precio por Kg ($)"]:
        if col in df_comp.columns:
            df_comp[col] = pd.to_numeric(df_comp[col], errors='coerce').fillna(0)

    # --- MODO 1: PRICE LADDER (COMPARATIVAS 1 A 1) ---
    if modo == "Price Ladder":
        # === HEADER EJECUTIVO ===
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #0B3C8C 0%, #1565C0 100%);
                padding: 25px 30px;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 8px 20px rgba(11, 60, 140, 0.2);
            ">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <h1 style="color: white; margin: 0; font-size: 2rem; font-weight: 900; letter-spacing: -0.5px;">
                            📊 Comparativas Index
                        </h1>
                        <p style="color: rgba(255,255,255,0.85); margin: 8px 0 0 0; font-size: 1rem; font-weight: 400;">
                            Análisis competitivo Price Ladder · Desembolso & Precio por Kg
                        </p>
                    </div>
                    <div style="
                        background: rgba(255,255,255,0.15);
                        backdrop-filter: blur(10px);
                        padding: 12px 20px;
                        border-radius: 10px;
                        border: 1px solid rgba(255,255,255,0.2);
                    ">
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.7); text-transform: uppercase; letter-spacing: 1px;">Modo Activo</div>
                        <div style="font-size: 1.1rem; color: white; font-weight: bold; margin-top: 2px;">Price Ladder</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # === CONTROLES DE PERSONALIZACIÓN ===
        with st.expander("⚙️ Personalizar tamaño de tarjetas", expanded=False):
            st.markdown("#### 📐 Dimensiones de Tarjeta")
            col_dim1, col_dim2, col_dim3, col_dim4 = st.columns(4)
            with col_dim1:
                ancho_tarjeta = st.slider("Ancho (px)", 200, 600, 300, 20, key="ancho_card")
            with col_dim2:
                alto_tarjeta = st.slider("Alto (px)", 150, 400, 220, 20, key="alto_card")
            with col_dim3:
                padding_tarjeta = st.slider("Padding (px)", 10, 40, 18, 2, key="pad_card")
            with col_dim4:
                separacion_tarjetas = st.slider("Separación entre tarjetas (px)", 0, 50, 5, 5, key="sep_card")
            
            st.markdown("#### 🔤 Tamaños de Texto")
            col_txt1, col_txt2, col_txt3, col_txt4, col_txt5 = st.columns(5)
            with col_txt1:
                size_producto = st.slider("Nombre Producto", 8, 24, 13, 1, key="txt_prod")
            with col_txt2:
                size_precio = st.slider("Precio", 14, 36, 22, 2, key="txt_precio")
            with col_txt3:
                size_vs = st.slider("VS", 8, 24, 11, 1, key="txt_vs")
            with col_txt4:
                size_index = st.slider("Index", 24, 72, 42, 4, key="txt_index")
            with col_txt5:
                size_label = st.slider("Etiquetas", 7, 18, 11, 1, key="txt_label")
            
            st.markdown("#### 🎨 Estilo Visual")
            col_style1, col_style2 = st.columns(2)
            with col_style1:
                border_width = st.slider("Grosor Borde (px)", 1, 6, 2, 1, key="border_w")
                border_top_width = st.slider("Grosor Borde Superior (px)", 3, 12, 6, 1, key="border_top_w")
            with col_style2:
                shadow_intensity = st.slider("Intensidad Sombra", 0, 20, 8, 2, key="shadow_i")
                border_radius = st.slider("Redondeo Esquinas (px)", 4, 20, 12, 2, key="radius")
        
        # === FUNCIÓN PARA GENERAR IMAGEN PNG ===
        def generar_imagen_tarjeta(sel_a, sel_b, v_a, v_b, tipo_metrica, ancho, alto, pad, s_prod, s_precio, s_vs, s_idx, s_label, b_top_width, radius):
            """Genera una imagen PNG de la tarjeta usando Pillow"""
            idx = int((v_a / v_b * 100)) if v_b > 0 else 0
            color_rgb = (11, 60, 140) if idx <= 100 else (211, 47, 47)  # Azul o Rojo
            label_metrica = "INDEX DESEMBOLSO" if tipo_metrica == "desembolso" else "INDEX $/KG"
            precio_fmt_a = f"${v_a:.1f}" if tipo_metrica == "desembolso" else f"${int(v_a)}"
            precio_fmt_b = f"${v_b:.1f}" if tipo_metrica == "desembolso" else f"${int(v_b)}"
            
            # Crear imagen con fondo blanco
            img = Image.new('RGB', (ancho, alto), color='white')
            draw = ImageDraw.Draw(img)
            
            # Dibujar borde superior de color
            draw.rectangle([0, 0, ancho, b_top_width], fill=color_rgb)
            
            # Dibujar bordes grises
            border_color = (221, 221, 221)
            draw.rectangle([0, b_top_width, 2, alto], fill=border_color)  # Izquierda
            draw.rectangle([ancho-2, b_top_width, ancho, alto], fill=border_color)  # Derecha
            draw.rectangle([0, alto-2, ancho, alto], fill=border_color)  # Abajo
            
            # Intentar cargar fuentes (con fallback)
            try:
                font_producto = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s_prod)
                font_precio = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s_precio)
                font_vs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", s_vs)
                font_index = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s_idx)
                font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s_label)
            except:
                font_producto = ImageFont.load_default()
                font_precio = ImageFont.load_default()
                font_vs = ImageFont.load_default()
                font_index = ImageFont.load_default()
                font_label = ImageFont.load_default()
            
            # Posiciones Y
            y_productos = b_top_width + pad + 5
            y_precios = y_productos + s_prod + 15
            y_index = y_precios + s_precio + 20
            y_label = y_index + s_idx + 5
            
            # Dibujar nombres de productos
            draw.text((pad, y_productos), sel_a, fill=(51, 51, 51), font=font_producto)
            bbox_b = draw.textbbox((0, 0), sel_b, font=font_producto)
            width_b = bbox_b[2] - bbox_b[0]
            draw.text((ancho - pad - width_b, y_productos), sel_b, fill=(51, 51, 51), font=font_producto)
            
            # Dibujar precios
            draw.text((pad, y_precios), precio_fmt_a, fill=(34, 34, 34), font=font_precio)
            
            # Dibujar "vs" centrado
            vs_text = "vs"
            bbox_vs = draw.textbbox((0, 0), vs_text, font=font_vs)
            width_vs = bbox_vs[2] - bbox_vs[0]
            draw.text((ancho//2 - width_vs//2, y_precios), vs_text, fill=(187, 187, 187), font=font_vs)
            
            # Dibujar precio B
            bbox_precio_b = draw.textbbox((0, 0), precio_fmt_b, font=font_precio)
            width_precio_b = bbox_precio_b[2] - bbox_precio_b[0]
            draw.text((ancho - pad - width_precio_b, y_precios), precio_fmt_b, fill=(34, 34, 34), font=font_precio)
            
            # Dibujar INDEX centrado
            idx_text = str(idx)
            bbox_idx = draw.textbbox((0, 0), idx_text, font=font_index)
            width_idx = bbox_idx[2] - bbox_idx[0]
            draw.text((ancho//2 - width_idx//2, y_index), idx_text, fill=color_rgb, font=font_index)
            
            # Dibujar label centrado
            bbox_label = draw.textbbox((0, 0), label_metrica, font=font_label)
            width_label = bbox_label[2] - bbox_label[0]
            draw.text((ancho//2 - width_label//2, y_label), label_metrica, fill=(119, 119, 119), font=font_label)
            
            return img
        
        # Función para crear HTML de tarjeta (para vista previa)
        def crear_tarjeta_html(sel_a, sel_b, v_a, v_b, tipo_metrica, ancho, alto, pad, s_prod, s_precio, s_vs, s_idx, s_label, b_width, b_top_width, shadow, radius, separacion):
            idx = int((v_a / v_b * 100)) if v_b > 0 else 0
            color = "#0B3C8C" if idx <= 100 else "#D32F2F"
            label_metrica = "Index Desembolso" if tipo_metrica == "desembolso" else "Index $/Kg"
            precio_fmt_a = f"${v_a:.1f}" if tipo_metrica == "desembolso" else f"${int(v_a)}"
            precio_fmt_b = f"${v_b:.1f}" if tipo_metrica == "desembolso" else f"${int(v_b)}"
            
            return f"""
            <div style="background:white; 
                        border:{b_width}px solid #ddd; 
                        border-top:{b_top_width}px solid {color}; 
                        border-radius:{radius}px; 
                        padding:{pad}px; 
                        text-align:center; 
                        width:{ancho}px; 
                        height:{alto}px; 
                        display:inline-flex; 
                        flex-direction:column; 
                        justify-content:space-between;
                        box-shadow: 0 4px {shadow}px rgba(0,0,0,0.12);
                        margin: {separacion}px;">
                <div style="display:flex; 
                            justify-content:space-between; 
                            font-size:{s_prod}px; 
                            color:#333; 
                            font-weight:700; 
                            margin-bottom:10px; 
                            line-height:1.3;">
                    <span style="text-align:left; max-width:48%; overflow:hidden;">{sel_a}</span>
                    <span style="text-align:right; max-width:48%; overflow:hidden;">{sel_b}</span>
                </div>
                <div style="display:flex; 
                            justify-content:space-between; 
                            align-items:center; 
                            font-weight:bold; 
                            font-size:{s_precio}px; 
                            margin-bottom:14px;">
                    <span style="color:#222;">{precio_fmt_a}</span>
                    <span style="color:#bbb; font-size:{s_vs}px; font-weight:600;">vs</span>
                    <span style="color:#222;">{precio_fmt_b}</span>
                </div>
                <div style="font-size:{s_idx}px; font-weight:900; color:{color}; margin-bottom:6px; line-height:1;">{idx}</div>
                <div style="font-size:{s_label}px; font-weight:bold; color:#777; text-transform:uppercase; letter-spacing:0.5px;">{label_metrica}</div>
            </div>
            """
        
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
                
                with des_cols[i]:
                    # Mostrar vista previa HTML
                    card_html = crear_tarjeta_html(sel_a, sel_b, v_a, v_b, "desembolso", 
                                                   ancho_tarjeta, alto_tarjeta, padding_tarjeta,
                                                   size_producto, size_precio, size_vs, size_index, size_label,
                                                   border_width, border_top_width, shadow_intensity, border_radius,
                                                   separacion_tarjetas)
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    # Generar imagen y botón de descarga
                    img = generar_imagen_tarjeta(sel_a, sel_b, v_a, v_b, "desembolso",
                                                ancho_tarjeta, alto_tarjeta, padding_tarjeta,
                                                size_producto, size_precio, size_vs, size_index, size_label,
                                                border_top_width, border_radius)
                    
                    # Convertir imagen a bytes
                    buf = io.BytesIO()
                    img.save(buf, format='PNG')
                    buf.seek(0)
                    
                    # Botón de descarga
                    nombre_archivo = f"desembolso_{sel_a.replace(' ', '_')}_vs_{sel_b.replace(' ', '_')}.png"
                    st.download_button(
                        label="⬇️ Descargar PNG",
                        data=buf,
                        file_name=nombre_archivo,
                        mime="image/png",
                        key=f"download_des_{i}",
                        use_container_width=True
                    )

            # Fila $/Kg
            st.markdown("### ⚖️ Index Precio por Kg")
            
            pkg_cols = st.columns(4)
            for i, (sel_a, sel_b) in enumerate(selections):
                v_a = df_comp[df_comp["Lookup_Key"] == sel_a]["Precio por Kg ($)"].iloc[0]
                v_b = df_comp[df_comp["Lookup_Key"] == sel_b]["Precio por Kg ($)"].iloc[0]
                
                with pkg_cols[i]:
                    # Mostrar vista previa HTML
                    card_html = crear_tarjeta_html(sel_a, sel_b, v_a, v_b, "precio_kg",
                                                   ancho_tarjeta, alto_tarjeta, padding_tarjeta,
                                                   size_producto, size_precio, size_vs, size_index, size_label,
                                                   border_width, border_top_width, shadow_intensity, border_radius,
                                                   separacion_tarjetas)
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    # Generar imagen y botón de descarga
                    img = generar_imagen_tarjeta(sel_a, sel_b, v_a, v_b, "precio_kg",
                                                ancho_tarjeta, alto_tarjeta, padding_tarjeta,
                                                size_producto, size_precio, size_vs, size_index, size_label,
                                                border_top_width, border_radius)
                    
                    # Convertir imagen a bytes
                    buf = io.BytesIO()
                    img.save(buf, format='PNG')
                    buf.seek(0)
                    
                    # Botón de descarga
                    nombre_archivo = f"precio_kg_{sel_a.replace(' ', '_')}_vs_{sel_b.replace(' ', '_')}.png"
                    st.download_button(
                        label="⬇️ Descargar PNG",
                        data=buf,
                        file_name=nombre_archivo,
                        mime="image/png",
                        key=f"download_pkg_{i}",
                        use_container_width=True
                    )

    # --- MODO 2: MATRIZ DE ARQUITECTURA (VISTA PPT) / PRICE PACK ---
    else:
        # Encabezado con leyenda a la derecha
        # === HEADER EJECUTIVO PARA PRICE PACK ===
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%);
                padding: 25px 30px;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 8px 20px rgba(142, 68, 173, 0.25);
            ">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center;">
                            <span style="font-size: 2.5rem; margin-right: 15px;">🏛️</span>
                            <div>
                                <h1 style="color: white; margin: 0; font-size: 2rem; font-weight: 900; letter-spacing: -0.5px;">
                                    Index del Price Pack Multibase
                                </h1>
                                <p style="color: rgba(255,255,255,0.85); margin: 8px 0 0 0; font-size: 1rem; font-weight: 400;">
                                    Análisis de arquitectura competitiva por canal · Base Detalle 100
                                </p>
                            </div>
                        </div>
                    </div>
                    <div style="
                        background: rgba(255,255,255,0.15);
                        backdrop-filter: blur(10px);
                        padding: 15px 25px;
                        border-radius: 12px;
                        border: 1px solid rgba(255,255,255,0.2);
                        text-align: center;
                        min-width: 220px;
                    ">
                        <div style="font-size: 0.7rem; color: rgba(255,255,255,0.7); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 5px;">📌 Metodología</div>
                        <div style="font-size: 0.95rem; color: white; font-weight: 700; line-height: 1.3;">Index Objetivo vs Detalle<br/><span style="font-size: 0.85rem; font-weight: 500;">(Base 100)</span></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
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
# Ajuste: No mostrar en el modo de Volume para evitar KeyErrors
if not st.session_state.data.empty:
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
            "TAKIS": ["DORITO","doritos", "DINAMITA"],
            "CHIPS": ["SABRITA", "RECETA CRUJIENTE"],
            "TOSTACHOS": ["TOSTITOS","TOSTITO"],
            "PAPAS BARCEL": ["SABRITA", "RECETA CRUJIENTE"],
            "CHIPOTLES": ["RANCHERITO"],
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
                                    
                                    # Cálculo del Index de Precio por Kg
                                    idx = int((row_b["Precio por Kg ($)"] / bench["Precio por Kg ($)"]) * 100)
                                    
                                    # CASO 1: ESTÁS MUY CARO (INDEX > 95)
                                    if idx > 95:
                                        hallazgos.append({
                                            "Prioridad": "ALTA", "Tipo": f"DUELO vs {bench['Producto']}", "Ocasión": oca,
                                            "Msg": f"{row_b['Producto']} está sobre-preciado (Index {idx})",
                                            "Detalle": f"Estás {idx-100}% más caro por Kg que tu rival directo en {oca}.",
                                            "Accion": f"⚖️ **Defensa:** Aumentar gramaje a **{calcular_rango_g(row_b['Precio ($)'], bench['Precio por Kg ($)'])}** para ser competitivo."
                                        })
                                    
                                    # CASO 2: ESTÁS REGALANDO PRODUCTO (INDEX < 90) - ¡EL QUE TE FALTABA!
                                    elif idx < 86:
                                        hallazgos.append({
                                            "Prioridad": "MEDIA", "Tipo": f"RENTABILIDAD vs {bench['Producto']}", "Ocasión": oca,
                                            "Msg": f"{row_b['Producto']} con exceso de gramaje (Index {idx})",
                                            "Detalle": f"Estás {100-idx}% por debajo del precio/kg del rival. Estás sacrificando margen innecesariamente.",
                                            "Accion": f"💰 **Optimización:** Reducir gramaje a **{calcular_rango_g(row_b['Precio ($)'], bench['Precio por Kg ($)'])}** para alinear rentabilidad."
                                        })
            else:
                st.warning("⚠️ El análisis de mercado requiere la columna 'Ocasión'.")
        except Exception as e: st.error(f"Error en Ultra 2.6: {e}")
    
    # --- MODO B: ARQUITECTURA DINÁMICA (Price Pack / Arquitectura) ---
    else:
        st.subheader("🏛️ Sugerencias / Observaciones del price pack y de la curva de precio")
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
        st.success("✅ **Estrategia en Paridad Optimizada (Sin hallazgos críticos).**")


# --- 12. GENERADOR DE RESUMEN EJECUTIVO ESTRATÉGICO ---
# Ajuste: No mostrar en el modo de Volumen para evitar errores de compilación de hallazgos
if not st.session_state.data.empty:
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
        st.subheader("🧪 Simulador de Cambios en el Mercado")
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
            st.markdown(f"### 📊 Diagnóstico de Index ({oca_sim})")
            
            with st.container():
                st.markdown('<div class="report-card">', unsafe_allow_html=True)
                st.write("💰 **Index de $ Desembolso **")
                c1, c2, c3 = st.columns(3)
                c1.metric(f"{comp_a_mover}", f"${n_p_c:.0f}", f"{var_p_c:+.1f}% vs act.")
                c2.metric(f"{prod_b}", f"${n_p_b:.0f}", f"{var_p_b:+.1f}% vs act.")
                c3.metric("INDEX PRECIO", f"{idx_des_nue}", f"{idx_des_nue - idx_des_ant} pts")
                st.markdown('</div>', unsafe_allow_html=True)

            with st.container():
                st.markdown('<div class="report-card">', unsafe_allow_html=True)
                st.write("⚖️ **Index de $/KG**")
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

    # === NUEVO: Estados para persistir filtros y configuración ===
    if 'size_imp_filtros' not in st.session_state:
        st.session_state.size_imp_filtros = {
            'fabricantes': [],
            'canales': [],
            'marcas': [],
            'ocasiones': [],
            'productos': []
        }
    
    if 'size_imp_config' not in st.session_state:
        st.session_state.size_imp_config = {
            'escala_base': 45,
            'gap_productos': 12,
            'modo_vista': "Automático",
            'zoom_nivel': "100%"
        }

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
        # === 1. FORMULARIO DE ALTA (NUEVO SKU) - SIN RERUN ===
        with st.expander("➕ Añadir un Nuevo SKU", expanded=False):
            with st.form("nuevo_sku_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                nuevo_p = c1.text_input("Nombre Completo (Producto)", placeholder="Ej. Takis Fuego 240g")
                nuevo_m = c2.text_input("Marca", placeholder="Ej. TAKIS")
                nuevo_f = c3.selectbox("Fabricante", ["BARCEL", "SABRITAS", "OTROS"])
                
                c4, c5, c6 = st.columns(3)
                nuevo_c = c4.text_input("Canal", value="AUTOSERVICIO")
                nuevo_o = c5.selectbox("Ocasión de Consumo", ["Bites", "Individual", "Hambre", "Compartir", "Familiar", "Reunión", "Fiesta", "Transformador"])
                nuevo_ancho = c6.number_input("Ancho (cm)", min_value=1.0, step=0.1, value=10.0)
                
                nuevo_alto = st.number_input("Alto (cm)", min_value=1.0, step=0.1, value=15.0)
                
                if st.form_submit_button("🚀 Registrar SKU"):
                    if nuevo_p.strip():  # Validar que no esté vacío
                        # Aplicamos la capitalización al producto
                        nuevo_p_fmt = nuevo_p.strip().upper()
                        nueva_fila = {
                            "Producto": nuevo_p_fmt, 
                            "Fabricante": nuevo_f, 
                            "Marca": nuevo_m.strip().upper(),
                            "Canal": nuevo_c.strip().upper(), 
                            "Ocasión de Consumo": nuevo_o,
                            "Ancho (cm)": nuevo_ancho, 
                            "Alto (cm)": nuevo_alto
                        }
                        st.session_state.df_arq_sim = pd.concat(
                            [st.session_state.df_arq_sim, pd.DataFrame([nueva_fila])], 
                            ignore_index=True
                        )
                        st.success(f"✅ Producto **{nuevo_p_fmt}** añadido correctamente.")
                        # NO HACEMOS RERUN - Los datos se actualizarán automáticamente
                    else:
                        st.error("⚠️ El nombre del producto no puede estar vacío.")

        # === 2. FILTROS AVANZADOS DINÁMICOS CON PERSISTENCIA ===
        with st.container(border=True):
            col_t1, col_t2 = st.columns([4, 1])
            col_t1.markdown("**Filtros Globales de Visualización**")
            
            if col_t2.button("🔄 Reset Filtros", use_container_width=True):
                st.session_state.size_imp_filtros = {
                    'fabricantes': [],
                    'canales': [],
                    'marcas': [],
                    'ocasiones': [],
                    'productos': []
                }
                st.rerun()
            
            df_base = st.session_state.df_arq_sim
            
            r1_c1, r1_c2, r1_c3 = st.columns(3)
            
            # Filtro Fabricante
            sel_fab = r1_c1.multiselect(
                "Fabricante", 
                df_base["Fabricante"].unique(), 
                default=st.session_state.size_imp_filtros['fabricantes'],
                key="filt_fab"
            )
            st.session_state.size_imp_filtros['fabricantes'] = sel_fab
            
            # Filtro Canal (dependiente de Fabricante)
            df_can = df_base[df_base["Fabricante"].isin(sel_fab)] if sel_fab else df_base
            canales_disponibles = df_can["Canal"].unique()
            sel_can_filtrados = [c for c in st.session_state.size_imp_filtros['canales'] if c in canales_disponibles]
            
            sel_can = r1_c2.multiselect(
                "Canal", 
                canales_disponibles, 
                default=sel_can_filtrados,
                key="filt_can"
            )
            st.session_state.size_imp_filtros['canales'] = sel_can
            
            # Filtro Marca (dependiente de Canal)
            df_mar = df_can[df_can["Canal"].isin(sel_can)] if sel_can else df_can
            marcas_disponibles = df_mar["Marca"].unique()
            sel_mar_filtrados = [m for m in st.session_state.size_imp_filtros['marcas'] if m in marcas_disponibles]
            
            sel_marcas = r1_c3.multiselect(
                "Marcas", 
                marcas_disponibles, 
                default=sel_mar_filtrados,
                key="filt_mar"
            )
            st.session_state.size_imp_filtros['marcas'] = sel_marcas
            
            r2_c1, r2_c2 = st.columns(2)
            
            # Filtro Ocasión (dependiente de Marca)
            df_oca = df_mar[df_mar["Marca"].isin(sel_marcas)] if sel_marcas else df_mar
            ocasiones_disponibles = df_oca["Ocasión de Consumo"].unique()
            sel_oca_filtrados = [o for o in st.session_state.size_imp_filtros['ocasiones'] if o in ocasiones_disponibles]
            
            sel_ocasiones = r2_c1.multiselect(
                "Ocasiones", 
                ocasiones_disponibles, 
                default=sel_oca_filtrados,
                key="filt_oca"
            )
            st.session_state.size_imp_filtros['ocasiones'] = sel_ocasiones
            
            # Filtro Producto (dependiente de Ocasión)
            df_prod = df_oca[df_oca["Ocasión de Consumo"].isin(sel_ocasiones)] if sel_ocasiones else df_oca
            productos_disponibles = df_prod["Producto"].unique()
            sel_prod_filtrados = [p for p in st.session_state.size_imp_filtros['productos'] if p in productos_disponibles]
            
            sel_productos = r2_c2.multiselect(
                "Productos específicos", 
                productos_disponibles, 
                default=sel_prod_filtrados,
                key="filt_prod"
            )
            st.session_state.size_imp_filtros['productos'] = sel_productos

        # --- LÓGICA DE FILTRADO ---
        df_filtered = df_base.copy()
        
        if sel_fab:
            df_filtered = df_filtered[df_filtered["Fabricante"].isin(sel_fab)]
        if sel_can:
            df_filtered = df_filtered[df_filtered["Canal"].isin(sel_can)]
        if sel_marcas:
            df_filtered = df_filtered[df_filtered["Marca"].isin(sel_marcas)]
        if sel_ocasiones:
            df_filtered = df_filtered[df_filtered["Ocasión de Consumo"].isin(sel_ocasiones)]
        if sel_productos:
            df_filtered = df_filtered[df_filtered["Producto"].isin(sel_productos)]
        
        if df_filtered.empty:
            st.warning("⚠️ Selecciona filtros para visualizar la tabla y el gráfico.")
        else:
            # Agregamos columna de selección
            df_filtered = df_filtered.copy()
            df_filtered.insert(0, "Seleccionar", False)
            
            # Editor Dinámico
            df_editado = st.data_editor(
                df_filtered,
                column_order=("Seleccionar", "Producto", "Marca", "Fabricante", "Canal", "Ocasión de Consumo", "Ancho (cm)", "Alto (cm)"),
                hide_index=True, 
                use_container_width=True, 
                key="editor_v6_persistente"
            )
            
            # Acciones
            c_save, c_del = st.columns(2)
            if c_save.button("💾 Guardar Cambios en Dimensiones", use_container_width=True, type="primary"):
                for _, row in df_editado.iterrows():
                    mask = st.session_state.df_arq_sim["Producto"] == row["Producto"]
                    st.session_state.df_arq_sim.loc[mask, ["Ancho (cm)", "Alto (cm)"]] = [row["Ancho (cm)"], row["Alto (cm)"]]
                st.success("✅ ¡Dimensiones actualizadas correctamente!")
                # NO hacemos rerun - las actualizaciones se reflejarán automáticamente
            
            if c_del.button("🗑️ Eliminar Productos Seleccionados", use_container_width=True):
                productos_a_eliminar = df_editado[df_editado["Seleccionar"] == True]["Producto"].tolist()
                if productos_a_eliminar:
                    st.session_state.df_arq_sim = st.session_state.df_arq_sim[
                        ~st.session_state.df_arq_sim["Producto"].isin(productos_a_eliminar)
                    ].copy()
                    st.success(f"✅ {len(productos_a_eliminar)} producto(s) eliminado(s)")
                    st.rerun()
                else:
                    st.warning("⚠️ No hay productos seleccionados para eliminar")

            # === 3. COMPARADOR 1 VS 1 - ADAPTATIVO A FILTROS ===
            st.markdown("#### ⚖️ Comparativa de Size Impression Index")
            
            # USAR SOLO LOS PRODUCTOS FILTRADOS
            productos_disponibles_comparar = df_editado["Producto"].unique().tolist()
            
            if len(productos_disponibles_comparar) < 2:
                st.info("ℹ️ Necesitas al menos 2 productos en la vista filtrada para realizar comparaciones.")
            else:
                with st.container(border=True):
                    col_sel1, col_sel2 = st.columns(2)
                    with col_sel1:
                        prod_base = st.selectbox(
                            "Producto 1 (Base 100)", 
                            productos_disponibles_comparar, 
                            key="sb_1_filtrado"
                        )
                    with col_sel2:
                        # Asegurar que el producto 2 sea diferente al 1
                        productos_comp = [p for p in productos_disponibles_comparar if p != prod_base]
                        prod_comp = st.selectbox(
                            "Producto 2 (Comparativo)", 
                            productos_comp, 
                            key="sb_2_filtrado"
                        )
                    
                    # Obtención de datos desde el dataframe filtrado
                    d1 = df_editado[df_editado["Producto"] == prod_base].iloc[0]
                    d2 = df_editado[df_editado["Producto"] == prod_comp].iloc[0]
                    
                    # Cálculo de áreas e Index
                    a1 = d1["Ancho (cm)"] * d1["Alto (cm)"]
                    a2 = d2["Ancho (cm)"] * d2["Alto (cm)"]
                    index_val = (a2 / a1) * 100
                    delta = index_val - 100
                
                    # === LÓGICA DE COLOR: POSITIVO SI SOBRE-INDEXA ===
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

            # === GRÁFICO TÉCNICO ADAPTATIVO CON CONFIGURACIÓN PERSISTENTE ===
            if not df_editado.empty:
                df_editado_graf = df_editado.copy()
                df_editado_graf['Area'] = df_editado_graf['Ancho (cm)'] * df_editado_graf['Alto (cm)']
                df_editado_graf['Producto'] = df_editado_graf['Producto'].str.upper()
                
                orden_o = ["Bites", "Individual", "Hambre", "Compartir", "Familiar", "Reunión", "Fiesta", "Transformador"]
                df_editado_graf['Ocasión de Consumo'] = pd.Categorical(
                    df_editado_graf['Ocasión de Consumo'], 
                    categories=orden_o, 
                    ordered=True
                )
                df_viz = df_editado_graf.sort_values(['Ocasión de Consumo', 'Area'])
            
                # === CONTROLES DE VISUALIZACIÓN CON PERSISTENCIA ===
                st.markdown("#### ⚙️ Controles de Visualización")
                
                col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns(4)
                
                with col_ctrl1:
                    escala_base = st.slider(
                        "📏 Escala Base", 20, 80, 
                        st.session_state.size_imp_config['escala_base'], 
                        step=5, 
                        help="Aumenta para hacer los empaques más grandes",
                        key="slider_escala"
                    )
                    st.session_state.size_imp_config['escala_base'] = escala_base
                    
                with col_ctrl2:
                    gap_productos = st.slider(
                        "↔️ Separación", 5, 30, 
                        st.session_state.size_imp_config['gap_productos'], 
                        help="Espacio entre productos",
                        key="slider_gap"
                    )
                    st.session_state.size_imp_config['gap_productos'] = gap_productos
                    
                with col_ctrl3:
                    modo_vista = st.selectbox(
                        "👁️ Modo Vista", 
                        ["Automático", "Compacto", "Expandido", "Ultra Grande"],
                        index=["Automático", "Compacto", "Expandido", "Ultra Grande"].index(
                            st.session_state.size_imp_config['modo_vista']
                        ),
                        key="select_modo"
                    )
                    st.session_state.size_imp_config['modo_vista'] = modo_vista
                    
                with col_ctrl4:
                    zoom_nivel = st.selectbox(
                        "🔍 Zoom Inicial",
                        ["100%", "125%", "150%", "175%", "200%"],
                        index=["100%", "125%", "150%", "175%", "200%"].index(
                            st.session_state.size_imp_config['zoom_nivel']
                        ),
                        key="select_zoom"
                    )
                    st.session_state.size_imp_config['zoom_nivel'] = zoom_nivel
            
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
                    
                    # === ÁREA EN EL CENTRO ===
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
            
                # === ETIQUETAS DE OCASIÓN ===
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
                
                # === CONTENEDOR DEL GRÁFICO ===
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
                    - Los ajustes se mantienen al agregar SKUs
                    """)


# --- APARTADO DE VISUALIZACIÓN: INDICADORES MACRO ---
if modo == "Indicadores Macro":
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import datetime
    
    st.caption("Datos oficiales del Banco de México actualizados en tiempo real")
    
    with st.spinner("Consultando API de Banxico..."):
        df_macro = importar_datos_macro(TOKEN_BANXICO, SERIES_A_CONSULTAR)
        
    if df_macro is not None:
        df_macro = df_macro[(df_macro.index >= FECHA_INICIO_FILTRO) & (df_macro.index <= FECHA_FIN_FILTRO)]
        df_macro = df_macro.dropna(axis=1, how='all')
        
        if df_macro.empty:
            st.warning("No hay datos disponibles para el rango seleccionado.")
        else:
            # ==================== FILTRO DE FECHAS PRO ====================
            # ==================== FILTRO DE FECHAS ====================
            st.markdown("### 📅 Filtro de Fechas")
            
            # 1. Definir los límites reales según tu DataFrame
            min_date_df = df_macro.index.min().date()
            max_date_df = df_macro.index.max().date()
            
            # 2. Definir tus fechas deseadas
            FECHA_INICIO_OBJETIVO = pd.to_datetime("2020-01-01").date()
            FECHA_FIN_OBJETIVO = pd.to_datetime("2025-12-31").date()
            
            # 3. Ajuste automático para evitar errores de rango
            # Esto asegura que: min_date <= value <= max_date
            default_inicio = max(FECHA_INICIO_OBJETIVO, min_date_df)
            default_fin = min(FECHA_FIN_OBJETIVO, max_date_df)
            
            col_f1, col_f2 = st.columns(2)
            
            with col_f1:
                fecha_inicio = st.date_input(
                    "Fecha Inicio", 
                    value=default_inicio,
                    min_value=min_date_df, 
                    max_value=max_date_df
                )
            
            with col_f2:
                fecha_fin = st.date_input(
                    "Fecha Fin", 
                    value=default_fin,
                    min_value=min_date_df, 
                    max_value=max_date_df
                )
            
            # 4. Aplicar el filtro al DataFrame
            df_macro = df_macro[(df_macro.index.date >= fecha_inicio) & (df_macro.index.date <= fecha_fin)]
            
            st.divider()
            
            # ==================== KPIs CORPORATIVOS ====================
            st.markdown("### 📊 Indicadores Clave")
            
            kpi_data = []
            
            if "INPC_Inflacion_Anual" in df_macro.columns:
                serie = df_macro["INPC_Inflacion_Anual"].dropna()
                if len(serie) >= 2:
                    val, prev = serie.iloc[-1], serie.iloc[-2]
                    delta = val - prev
                    kpi_data.append({'titulo': 'Inflación Anual', 'valor': f'{val:.2f}%', 
                                   'delta': f'{"↑" if delta > 0 else "↓"} {abs(delta):.2f} pp', 'icon': '📈'})
            
            if "TipoCambio_Cotizacion_Maxima" in df_macro.columns:
                serie = df_macro["TipoCambio_Cotizacion_Maxima"].dropna()
                if len(serie) >= 2:
                    val, prev = serie.iloc[-1], serie.iloc[-2]
                    delta = val - prev
                    kpi_data.append({'titulo': 'Tipo de Cambio', 'valor': f'${val:.2f}', 
                                   'delta': f'{"↑" if delta > 0 else "↓"} {abs(delta):.2f} MXN', 'icon': '💱'})
            
            if "TIIE_Fondeo_1Dia" in df_macro.columns:
                serie = df_macro["TIIE_Fondeo_1Dia"].dropna()
                if len(serie) >= 2:
                    val, prev = serie.iloc[-1], serie.iloc[-2]
                    delta = val - prev
                    kpi_data.append({'titulo': 'Tasa de Interés (1 día)', 'valor': f'{val:.2f}%', 
                                   'delta': f'{"↑" if delta > 0 else "↓"} {abs(delta):.2f} pp', 'icon': '💰'})
            
            if "Exp_TasaDesocupacion_Media" in df_macro.columns:
                serie = df_macro["Exp_TasaDesocupacion_Media"].dropna()
                if len(serie) >= 2:
                    val, prev = serie.iloc[-1], serie.iloc[-2]
                    delta = val - prev
                    kpi_data.append({'titulo': 'Desocupación', 'valor': f'{val:.2f}%', 
                                   'delta': f'{"↑" if delta > 0 else "↓"} {abs(delta):.2f} pp', 'icon': '👥'})
            
            if "Salario_Minimo_General" in df_macro.columns:
                serie = df_macro["Salario_Minimo_General"].dropna()
                if len(serie) >= 2:
                    val, prev = serie.iloc[-1], serie.iloc[-2]
                    delta = val - prev
                    kpi_data.append({'titulo': 'Salario Mínimo', 'valor': f'${val:.2f}', 
                                   'delta': f'{"↑" if delta > 0 else "↓"} ${abs(delta):.2f}', 'icon': '💵'})
            
            kpi_html = """<style>
.kpi-container {display: flex; gap: 16px; margin-bottom: 30px; flex-wrap: wrap;}
.kpi-card {flex: 1; min-width: 180px; background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: all 0.3s ease;}
.kpi-card:hover {box-shadow: 0 4px 12px rgba(0,0,0,0.15); border-color: #667eea;}
.kpi-icon {font-size: 28px; margin-bottom: 8px;}
.kpi-titulo {color: #666; font-size: 12px; font-weight: 600; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;}
.kpi-valor {color: #1a1a1a; font-size: 32px; font-weight: 700; margin-bottom: 8px; line-height: 1;}
.kpi-delta {font-size: 13px; font-weight: 600; padding: 4px 10px; border-radius: 4px; display: inline-block; background: #f5f5f5; color: #666;}
</style><div class="kpi-container">"""
            
            for kpi in kpi_data:
                kpi_html += f'<div class="kpi-card"><div class="kpi-icon">{kpi["icon"]}</div><div class="kpi-titulo">{kpi["titulo"]}</div><div class="kpi-valor">{kpi["valor"]}</div><div class="kpi-delta">{kpi["delta"]}</div></div>'
            
            kpi_html += "</div>"
            st.markdown(kpi_html, unsafe_allow_html=True)
            st.divider()
            
            # ==================== INFLACIÓN ====================
            st.markdown("### 📈 Análisis de Inflación")
            tab_inf1, tab_inf2 = st.tabs(["📊 Evolución Histórica", "🔮 Expectativas"])
            
            with tab_inf1:
                st.markdown("**INPC - Inflación Anual y Nivel Histórico**")
                if "INPC_Inflacion_Anual" in df_macro.columns and "INPC_Nivel_Historico" in df_macro.columns:
                    df_plot = df_macro[["INPC_Inflacion_Anual", "INPC_Nivel_Historico"]].dropna()
                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    fig.add_trace(go.Bar(
                        x=df_plot.index, 
                        y=df_plot["INPC_Inflacion_Anual"], 
                        name="Inflación Anual (%)",
                        marker_color='rgba(102, 126, 234, 0.7)', 
                        text=[f"{v:.1f}%" for v in df_plot["INPC_Inflacion_Anual"]],
                        textposition='outside', 
                        textfont=dict(size=10),
                        hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'
                    ), secondary_y=False)
                    fig.add_trace(go.Scatter(
                        x=df_plot.index, 
                        y=df_plot["INPC_Nivel_Historico"], 
                        name="Nivel Histórico",
                        line=dict(color='rgb(255, 75, 75)', width=3), 
                        hovertemplate='%{x}<br>%{y:.2f}<extra></extra>'
                    ), secondary_y=True)
                    fig.update_xaxes(title_text="Fecha")
                    fig.update_yaxes(title_text="Inflación (%)", secondary_y=False)
                    fig.update_yaxes(title_text="Nivel (Base 2018)", secondary_y=True)
                    fig.update_layout(
                        hovermode='x unified', 
                        height=450, 
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Tarjetas mejoradas
                st.markdown("#### 📌 Métricas Complementarias")
                col1, col2, col3 = st.columns(3)
                if "INPC_Inflacion_Mensual" in df_macro.columns:
                    val = df_macro['INPC_Inflacion_Mensual'].dropna().iloc[-1]
                    col1.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 5px;'>💠 Mensual</div>
                        <div style='font-size: 28px; font-weight: bold;'>{val:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                if "INPC_Inflacion_Acumulada" in df_macro.columns:
                    val = df_macro['INPC_Inflacion_Acumulada'].dropna().iloc[-1]
                    col2.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 5px;'>💠 Acumulada</div>
                        <div style='font-size: 28px; font-weight: bold;'>{val:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                if "INPC_Nivel_Historico" in df_macro.columns:
                    val = df_macro['INPC_Nivel_Historico'].dropna().iloc[-1]
                    col3.markdown(f"""
                    <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 5px;'>💠 Nivel</div>
                        <div style='font-size: 28px; font-weight: bold;'>{val:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.caption("Fuente: Banco de México")
            
            with tab_inf2:
                st.markdown("**Expectativas de Inflación - Media**")
                if "Exp_Inflacion_Media" in df_macro.columns:
                    df_plot = df_macro[["Exp_Inflacion_Media"]].dropna()
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_plot.index, 
                        y=df_plot["Exp_Inflacion_Media"], 
                        name='Media',
                        line=dict(color='rgb(102, 126, 234)', width=3), 
                        fill='tozeroy',
                        fillcolor='rgba(102, 126, 234, 0.3)',
                        hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'
                    ))
                    fig.update_layout(
                        hovermode='x', 
                        height=450, 
                        yaxis_title="(%)", 
                        xaxis_title="Fecha",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("#### 📌 Rango de Expectativas")
                col1, col2, col3 = st.columns(3)
                if "Exp_Inflacion_Media" in df_macro.columns:
                    val = df_macro['Exp_Inflacion_Media'].dropna().iloc[-1]
                    col1.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 5px;'>📊 Media</div>
                        <div style='font-size: 28px; font-weight: bold;'>{val:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                if "Exp_Inflacion_Minima" in df_macro.columns:
                    val = df_macro['Exp_Inflacion_Minima'].dropna().iloc[-1]
                    col2.markdown(f"""
                    <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 5px;'>📉 Mínima</div>
                        <div style='font-size: 28px; font-weight: bold;'>{val:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                if "Exp_Inflacion_Maxima" in df_macro.columns:
                    val = df_macro['Exp_Inflacion_Maxima'].dropna().iloc[-1]
                    col3.markdown(f"""
                    <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 5px;'>📈 Máxima</div>
                        <div style='font-size: 28px; font-weight: bold;'>{val:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.caption("Fuente: Encuesta de Expectativas - Banxico")
            
            st.divider()
            
            # ==================== MERCADO CAMBIARIO ====================
            st.markdown("### 💱 Mercado Cambiario y Tasas")
            tab1, tab2 = st.tabs(["💵 Tipo de Cambio", "📊 Tasas"])
            
            with tab1:
                st.markdown("**Tipo de Cambio USD/MXN**")
                if "TipoCambio_Cotizacion_Minima" in df_macro.columns:
                    df_plot = df_macro[["TipoCambio_Cotizacion_Minima", "TipoCambio_Cotizacion_Maxima"]].dropna()
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_plot.index, 
                        y=df_plot["TipoCambio_Cotizacion_Minima"], 
                        name="Mínima",
                        line=dict(color='rgb(67, 233, 123)', width=2), 
                        mode='lines+markers',
                        marker=dict(size=4),
                        hovertemplate='%{x}<br>$%{y:.2f}<extra></extra>'
                    ))
                    fig.add_trace(go.Scatter(
                        x=df_plot.index, 
                        y=df_plot["TipoCambio_Cotizacion_Maxima"], 
                        name="Máxima",
                        line=dict(color='rgb(255, 75, 75)', width=2), 
                        mode='lines+markers',
                        marker=dict(size=4),
                        hovertemplate='%{x}<br>$%{y:.2f}<extra></extra>'
                    ))
                    fig.update_layout(
                        hovermode='x unified', 
                        height=450, 
                        yaxis_title="MXN/USD", 
                        xaxis_title="Fecha", 
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("#### 📌 Expectativas de Tipo de Cambio")
                col1, col2, col3 = st.columns(3)
                if "Exp_TipoCambio_Media" in df_macro.columns:
                    val = df_macro['Exp_TipoCambio_Media'].dropna().iloc[-1]
                    col1.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 5px;'>📊 Media Esperada</div>
                        <div style='font-size: 28px; font-weight: bold;'>${val:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                if "Exp_TipoCambio_Minima" in df_macro.columns:
                    val = df_macro['Exp_TipoCambio_Minima'].dropna().iloc[-1]
                    col2.markdown(f"""
                    <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 5px;'>📉 Mínima Esperada</div>
                        <div style='font-size: 28px; font-weight: bold;'>${val:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                if "Exp_TipoCambio_Maxima" in df_macro.columns:
                    val = df_macro['Exp_TipoCambio_Maxima'].dropna().iloc[-1]
                    col3.markdown(f"""
                    <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 5px;'>📈 Máxima Esperada</div>
                        <div style='font-size: 28px; font-weight: bold;'>${val:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.caption("Fuente: Banco de México")
            
            with tab2:
                st.markdown("**TIIE 1 Día**")
                if "TIIE_Fondeo_1Dia" in df_macro.columns:
                    df_plot = df_macro[["TIIE_Fondeo_1Dia"]].dropna()
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_plot.index, 
                        y=df_plot["TIIE_Fondeo_1Dia"], 
                        name="TIIE",
                        line=dict(color='rgb(102, 126, 234)', width=3), 
                        fill='tozeroy',
                        fillcolor='rgba(102, 126, 234, 0.3)',
                        hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'
                    ))
                    fig.update_layout(
                        hovermode='x', 
                        height=450, 
                        yaxis_title="(%)", 
                        xaxis_title="Fecha",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("#### 📌 Expectativas de Tasa de Fondeo")
                col1, col2, col3 = st.columns(3)
                if "Exp_TasaFondeo_Media" in df_macro.columns:
                    val = df_macro['Exp_TasaFondeo_Media'].dropna().iloc[-1]
                    col1.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 5px;'>📊 Media Esperada</div>
                        <div style='font-size: 28px; font-weight: bold;'>{val:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                if "Exp_TasaFondeo_Minima" in df_macro.columns:
                    val = df_macro['Exp_TasaFondeo_Minima'].dropna().iloc[-1]
                    col2.markdown(f"""
                    <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 5px;'>📉 Mínima Esperada</div>
                        <div style='font-size: 28px; font-weight: bold;'>{val:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                if "Exp_TasaFondeo_Maxima" in df_macro.columns:
                    val = df_macro['Exp_TasaFondeo_Maxima'].dropna().iloc[-1]
                    col3.markdown(f"""
                    <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 5px;'>📈 Máxima Esperada</div>
                        <div style='font-size: 28px; font-weight: bold;'>{val:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.caption("Fuente: Banco de México")
            
            st.divider()

            
            # ==================== CLIMA NEGOCIOS ====================
            st.markdown("### 🏢 Expectativas y Clima de Negocios")
            
            st.markdown("**Clima de Negocios - Próximos 6 Meses**")
            series = ["Exp_ClimaNegocios_Mejorara", "Exp_ClimaNegocios_Igual", "Exp_ClimaNegocios_Empeorara"]
            if all(s in df_macro.columns for s in series):
                df_plot = df_macro[series].dropna()
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df_plot.index, 
                    y=df_plot[series[0]], 
                    name='Mejorará', 
                    marker_color='rgba(76, 201, 240, 0.8)',
                    text=[f"{v:.0f}%" if v > 5 else "" for v in df_plot[series[0]]], 
                    textposition='inside',
                    textfont=dict(size=10, color='white'),
                    hovertemplate='Mejorará<br>%{x}<br>%{y:.1f}%<extra></extra>'
                ))
                fig.add_trace(go.Bar(
                    x=df_plot.index, 
                    y=df_plot[series[1]], 
                    name='Igual', 
                    marker_color='rgba(155, 135, 245, 0.8)',
                    text=[f"{v:.0f}%" if v > 5 else "" for v in df_plot[series[1]]], 
                    textposition='inside',
                    textfont=dict(size=10, color='white'),
                    hovertemplate='Igual<br>%{x}<br>%{y:.1f}%<extra></extra>'
                ))
                fig.add_trace(go.Bar(
                    x=df_plot.index, 
                    y=df_plot[series[2]], 
                    name='Empeorará', 
                    marker_color='rgba(255, 154, 162, 0.8)',
                    text=[f"{v:.0f}%" if v > 5 else "" for v in df_plot[series[2]]], 
                    textposition='inside',
                    textfont=dict(size=10, color='white'),
                    hovertemplate='Empeorará<br>%{x}<br>%{y:.1f}%<extra></extra>'
                ))
                fig.update_layout(
                    barmode='stack', 
                    height=450, 
                    hovermode='x unified', 
                    yaxis_title="(%)", 
                    xaxis_title="Fecha", 
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Fuente: Encuesta de Expectativas - Banxico")
            
            st.markdown("")
            
            st.markdown("**Situación Económica vs Hace un Año**")
            series = ["Exp_EconActual_Mejor", "Exp_EconActual_Peor"]
            if all(s in df_macro.columns for s in series):
                df_plot = df_macro[series].dropna()
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df_plot.index, 
                    y=df_plot[series[0]], 
                    name='Mejor', 
                    marker_color='rgba(76, 201, 240, 0.8)',
                    text=[f"{v:.0f}%" if v > 5 else "" for v in df_plot[series[0]]], 
                    textposition='inside',
                    textfont=dict(size=10, color='white'),
                    hovertemplate='Mejor<br>%{x}<br>%{y:.1f}%<extra></extra>'
                ))
                fig.add_trace(go.Bar(
                    x=df_plot.index, 
                    y=df_plot[series[1]], 
                    name='Peor', 
                    marker_color='rgba(255, 154, 162, 0.8)',
                    text=[f"{v:.0f}%" if v > 5 else "" for v in df_plot[series[1]]], 
                    textposition='inside',
                    textfont=dict(size=10, color='white'),
                    hovertemplate='Peor<br>%{x}<br>%{y:.1f}%<extra></extra>'
                ))
                fig.update_layout(
                    barmode='stack', 
                    height=450, 
                    hovermode='x unified', 
                    yaxis_title="(%)", 
                    xaxis_title="Fecha", 
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Fuente: Encuesta de Expectativas - Banxico")
            
            st.divider()
            # ==================== BILLETES Y MONEDAS ====================
            st.markdown("### 💵 Circulante: Billetes y Monedas")
            tab1, tab2 = st.tabs(["💵 Billetes", "🪙 Monedas"])
            
            with tab1:
                st.markdown("**Evolución de Billetes en Circulación**")
                series = [c for c in df_macro.columns if "Billete_" in c]
                if series:
                    df_plot = df_macro[series].dropna()
                    fig = go.Figure()
                    colors = {
                        'Billete_20_Circulacion': 'rgba(255, 224, 130, 0.8)', 
                        'Billete_50_Circulacion': 'rgba(255, 128, 171, 0.8)', 
                        'Billete_100_Circulacion': 'rgba(128, 128, 255, 0.8)', 
                        'Billete_200_Circulacion': 'rgba(128, 222, 234, 0.8)',
                        'Billete_500_Circulacion': 'rgba(165, 214, 167, 0.8)', 
                        'Billete_1000_Circulacion': 'rgba(206, 147, 216, 0.8)'
                    }
                    for col in series:
                        denom = col.replace("Billete_", "").replace("_Circulacion", "")
                        fig.add_trace(go.Scatter(
                            x=df_plot.index, 
                            y=df_plot[col], 
                            name=f"${denom}",
                            line=dict(color=colors.get(col, 'blue'), width=0), 
                            stackgroup='one',
                            fillcolor=colors.get(col, 'blue'),
                            hovertemplate=f'${denom}<br>%{{x}}<br>%{{y:,.0f}} MDP<extra></extra>'
                        ))
                    fig.update_layout(
                        hovermode='x unified', 
                        height=450, 
                        yaxis_title="Millones de Pesos", 
                        xaxis_title="Fecha", 
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("#### 📌 Billetes en Circulación (MDP)")
                cols = st.columns(6)
                denoms_info = [
                    ("20", "#FFE082", "💵"),
                    ("50", "#FF80AB", "💵"),
                    ("100", "#8080FF", "💵"),
                    ("200", "#80DEEA", "💵"),
                    ("500", "#A5D6A7", "💵"),
                    ("1000", "#CE93D8", "💵")
                ]
                for i, (denom, color, icon) in enumerate(denoms_info):
                    s = f"Billete_{denom}_Circulacion"
                    if s in df_macro.columns:
                        val = df_macro[s].dropna().iloc[-1]
                        cols[i].markdown(f"""
                        <div style='background: {color}; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                            <div style='font-size: 24px; font-weight: bold; color: #333; margin-bottom: 5px;'>{icon} ${denom}</div>
                            <div style='font-size: 18px; color: #555; font-weight: 600;'>{val:,.0f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.caption("Fuente: Banco de México | Millones de Pesos")
            
            with tab2:
                st.markdown("**Evolución de Monedas en Circulación**")
                series = [c for c in df_macro.columns if "Moneda_" in c]
                if series:
                    df_plot = df_macro[series].dropna()
                    fig = go.Figure()
                    palette = [
                        'rgba(255, 183, 77, 0.8)',
                        'rgba(255, 138, 101, 0.8)',
                        'rgba(174, 213, 129, 0.8)',
                        'rgba(100, 181, 246, 0.8)',
                        'rgba(149, 117, 205, 0.8)',
                        'rgba(244, 143, 177, 0.8)',
                        'rgba(129, 212, 250, 0.8)',
                        'rgba(206, 147, 216, 0.8)',
                        'rgba(165, 214, 167, 0.8)',
                        'rgba(255, 224, 130, 0.8)',
                        'rgba(128, 222, 234, 0.8)'
                    ]
                    for idx, col in enumerate(series):
                        denom = col.replace("Moneda_", "").replace("_Circulacion", "")
                        label = f"{denom}¢" if "C" in denom else f"${denom}"
                        fig.add_trace(go.Scatter(
                            x=df_plot.index, 
                            y=df_plot[col], 
                            name=label, 
                            stackgroup='one',
                            line=dict(width=0),
                            fillcolor=palette[idx % len(palette)],
                            hovertemplate=f'{label}<br>%{{x}}<br>%{{y:,.0f}} MDP<extra></extra>'
                        ))
                    fig.update_layout(
                        hovermode='x unified', 
                        height=450, 
                        yaxis_title="Millones de Pesos", 
                        xaxis_title="Fecha", 
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("#### 📌 Monedas en Circulación (MDP)")
                denoms = [
                    ("1", "$1", "🪙", "#9575CD"),
                    ("2", "$2", "🪙", "#F48FB1"),
                    ("5", "$5", "🪙", "#81D4FA"),
                    ("10", "$10", "🪙", "#A5D6A7"),
                    ("20", "$20", "🪙", "#FFE082")
                ]
                cols = st.columns(len(denoms))
                for i, (key, label, icon, color) in enumerate(denoms):
                    s = f"Moneda_{key}_Circulacion"
                    if s in df_macro.columns:
                        val = df_macro[s].dropna().iloc[-1]
                        cols[i].markdown(f"""
                        <div style='background: {color}; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                            <div style='font-size: 24px; font-weight: bold; color: #333; margin-bottom: 5px;'>{icon} {label}</div>
                            <div style='font-size: 18px; color: #555; font-weight: 600;'>{val:,.0f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.caption("Fuente: Banco de México | Millones de Pesos")
            
            st.divider()
            
            # ==================== MERCADO LABORAL ====================
            st.markdown("### 👥 Mercado Laboral")
            tab1, tab2 = st.tabs(["💰 Salario Mínimo", "📊 Desocupación"])
            
            with tab1:
                st.markdown("**Salario Mínimo General**")
                if "Salario_Minimo_General" in df_macro.columns:
                    df_plot = df_macro[["Salario_Minimo_General"]].dropna()
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_plot.index, 
                        y=df_plot["Salario_Minimo_General"], 
                        name="Salario Mínimo",
                        line=dict(color='rgb(102, 126, 234)', width=3), 
                        mode='lines+markers',
                        marker=dict(size=5),
                        fill='tozeroy',
                        fillcolor='rgba(102, 126, 234, 0.3)',
                        hovertemplate='%{x}<br>$%{y:.2f}<extra></extra>'
                    ))
                    fig.update_layout(
                        hovermode='x', 
                        height=450, 
                        yaxis_title="Pesos Diarios", 
                        xaxis_title="Fecha",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    val = df_plot["Salario_Minimo_General"].iloc[-1]
                    st.markdown("#### 📌 Proyecciones de Salario")
                    col1, col2, col3 = st.columns(3)
                    col1.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 5px;'>💰 Diario</div>
                        <div style='font-size: 28px; font-weight: bold;'>${val:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    col2.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 5px;'>📅 Mensual</div>
                        <div style='font-size: 28px; font-weight: bold;'>${val * 30:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    col3.markdown(f"""
                    <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 5px;'>📆 Anual</div>
                        <div style='font-size: 28px; font-weight: bold;'>${val * 365:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.caption("Fuente: Banco de México")
            
            with tab2:
                st.markdown("**Tasa de Desocupación Nacional**")
                if "Exp_TasaDesocupacion_Media" in df_macro.columns:
                    df_plot = df_macro[["Exp_TasaDesocupacion_Media"]].dropna()
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_plot.index, 
                        y=df_plot["Exp_TasaDesocupacion_Media"], 
                        name="Desocupación",
                        line=dict(color='rgb(255, 75, 75)', width=3), 
                        mode='lines+markers',
                        marker=dict(size=5),
                        fill='tozeroy',
                        fillcolor='rgba(255, 75, 75, 0.3)',
                        hovertemplate='%{x}<br>%{y:.1f}%<extra></extra>'
                    ))
                    fig.update_layout(
                        hovermode='x', 
                        height=450, 
                        yaxis_title="(%) de PEA", 
                        xaxis_title="Fecha",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("#### 📌 Indicadores de Desocupación")
                    col1, col2, col3, col4 = st.columns(4)
                    if "Exp_TasaDesocupacion_Media" in df_macro.columns:
                        val = df_macro['Exp_TasaDesocupacion_Media'].dropna().iloc[-1]
                        col1.markdown(f"""
                        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 18px; border-radius: 10px; color: white; text-align: center;'>
                            <div style='font-size: 12px; opacity: 0.9; margin-bottom: 5px;'>📊 Actual</div>
                            <div style='font-size: 24px; font-weight: bold;'>{val:.2f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    if "Exp_TasaDesocupacion_Media" in df_macro.columns:
                        val = df_macro['Exp_TasaDesocupacion_Media'].dropna().iloc[-1]
                        col2.markdown(f"""
                        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 18px; border-radius: 10px; color: white; text-align: center;'>
                            <div style='font-size: 12px; opacity: 0.9; margin-bottom: 5px;'>🔮 Media</div>
                            <div style='font-size: 24px; font-weight: bold;'>{val:.2f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    if "Exp_TasaDesocupacion_Minima" in df_macro.columns:
                        val = df_macro['Exp_TasaDesocupacion_Minima'].dropna().iloc[-1]
                        col3.markdown(f"""
                        <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 18px; border-radius: 10px; color: white; text-align: center;'>
                            <div style='font-size: 12px; opacity: 0.9; margin-bottom: 5px;'>📉 Mínima</div>
                            <div style='font-size: 24px; font-weight: bold;'>{val:.2f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    if "Exp_TasaDesocupacion_Maxima" in df_macro.columns:
                        val = df_macro['Exp_TasaDesocupacion_Maxima'].dropna().iloc[-1]
                        col4.markdown(f"""
                        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 18px; border-radius: 10px; color: white; text-align: center;'>
                            <div style='font-size: 12px; opacity: 0.9; margin-bottom: 5px;'>📈 Máxima</div>
                            <div style='font-size: 24px; font-weight: bold;'>{val:.2f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.caption("Fuente: Banco de México")
            
            st.divider()
            
            # ==================== EXPLORADOR AVANZADO ====================
            with st.expander("🔍 **Explorador Avanzado de Series**", expanded=False):
                st.markdown("""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                    <h3 style='color: white; margin: 0;'>📊 Análisis Personalizado</h3>
                    <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;'>Selecciona las series que deseas analizar y compara múltiples indicadores</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([7, 3])
                with col1:
                    selected = st.multiselect(
                        "Selecciona las series a visualizar:", 
                        df_macro.columns.tolist(), 
                        default=[df_macro.columns[0]] if len(df_macro.columns) > 0 else [],
                        help="Puedes seleccionar múltiples series para compararlas"
                    )
                    if selected:
                        fig = go.Figure()
                        colors_custom = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7']
                        for idx, s in enumerate(selected):
                            fig.add_trace(go.Scatter(
                                x=df_macro.index, 
                                y=df_macro[s], 
                                name=s, 
                                mode='lines+markers',
                                line=dict(width=2.5, color=colors_custom[idx % len(colors_custom)]),
                                marker=dict(size=4),
                                hovertemplate='%{x}<br>%{y:.2f}<extra></extra>'
                            ))
                        fig.update_layout(
                            hovermode='x unified', 
                            height=450, 
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="center",
                                x=0.5
                            ),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if selected:
                        st.markdown("""
                        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
                            <h4 style='color: white; margin: 0 0 10px 0;'>📈 Estadísticas</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        for s in selected:
                            data = df_macro[s].dropna()
                            if not data.empty:
                                st.markdown(f"""
                                <div style='background: white; border: 2px solid #667eea; border-radius: 8px; padding: 12px; margin-bottom: 12px;'>
                                    <div style='font-weight: bold; color: #667eea; margin-bottom: 8px; font-size: 13px;'>{s}</div>
                                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px;'>
                                        <div><span style='color: #888;'>Último:</span> <b>{data.iloc[-1]:.2f}</b></div>
                                        <div><span style='color: #888;'>Prom:</span> <b>{data.mean():.2f}</b></div>
                                        <div><span style='color: #888;'>Máx:</span> <b style='color: #43e97b;'>{data.max():.2f}</b></div>
                                        <div><span style='color: #888;'>Mín:</span> <b style='color: #f5576c;'>{data.min():.2f}</b></div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("#### 📋 Datos Tabulares")
                df_visual = df_macro.copy()
                df_visual.index = df_visual.index.date
                st.dataframe(
                    df_visual, 
                    use_container_width=True, 
                    height=400
                )
                
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
                with col_btn1:
                    st.download_button(
                        "📥 Descargar CSV", 
                        df_visual.to_csv(), 
                        "datos_macro.csv", 
                        "text/csv",
                        use_container_width=True
                    )
                with col_btn2:
                    st.download_button(
                        "📊 Descargar Excel", 
                        df_visual.to_csv(), 
                        "datos_macro.xlsx", 
                        "text/csv",
                        use_container_width=True
                    )
    else:
        st.error("❌ Error al conectar con Banxico")


    # ============================================================================
    # CÓDIGO FINAL CON DEBUG - COPIAR Y PEGAR AL FINAL DE TU APARTADO MACRO
    # ============================================================================
    
    from io import BytesIO
    import re
    import plotly.graph_objects as go
    
    def descargar_y_procesar_expectativas(url_github):
        try:
            response = requests.get(url_github, timeout=30)
            response.raise_for_status()
            
            df = pd.read_excel(BytesIO(response.content), engine='openpyxl')
            
            if 'NombreAbsolutoLargo' not in df.columns or 'Dato' not in df.columns:
                return None, None, "Error: Columnas no encontradas"
            
            # Obtener fecha de encuesta
            fecha_encuesta = None
            if 'FechaEncuesta' in df.columns:
                df['FechaEncuesta'] = pd.to_datetime(df['FechaEncuesta'], format='%m/%d/%Y', errors='coerce')
                fecha_encuesta = df['FechaEncuesta'].max()
            
            # Filtrar SOLO las variables necesarias
            df_filtrado = df[
                df['NombreAbsolutoLargo'].str.contains(
                    'Inflación general para|Inflación general al cierre de|Inflación subyacente para|' +
                    'tipo de cambio promedio|tipo de cambio al cierre|desocupación al cierre|' +
                    'cete a 28 días al cierre|clima de negocios|economía del país',
                    case=False, na=False, regex=True
                )
            ].copy()
            
            # Excluir probabilidades
            df_filtrado = df_filtrado[~df_filtrado['NombreAbsolutoLargo'].str.contains('probabilidad', case=False, na=False)]
            
            if len(df_filtrado) == 0:
                return None, None, "No se encontraron variables"
            
            df_filtrado = df_filtrado[['NombreAbsolutoLargo', 'Dato']].copy()
            df_filtrado.columns = ['Variable', 'Valor']
            df_filtrado['Valor'] = pd.to_numeric(df_filtrado['Valor'], errors='coerce')
            df_agrupado = df_filtrado.groupby('Variable')['Valor'].mean().reset_index()
            
            def categorizar(variable):
                v = variable.lower()
                
                # Inflación mensual (tiene meses)
                if 'inflación general para' in v and any(mes in v for mes in ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']):
                    return 'Inflación General - Mensual'
                # Inflación anual (al cierre de)
                elif 'inflación general al cierre de' in v:
                    return 'Inflación General - Anual'
                elif 'inflación subyacente para' in v:
                    return 'Inflación Subyacente - Mensual'
                elif 'tipo de cambio promedio durante' in v:
                    return 'Tipo de Cambio - Mensual'
                elif 'tipo de cambio al cierre de' in v:
                    return 'Tipo de Cambio - Anual'
                elif 'desocupación al cierre de' in v:
                    return 'Desempleo - Anual'
                elif 'cete a 28 días al cierre de' in v:
                    return 'CETE 28 - Anual'
                elif 'clima de negocios' in v and 'mejor' in v and 'permanecerá' not in v and 'empeorará' not in v:
                    return 'Clima de Negocios - Mejorará'
                elif 'clima de negocios' in v and 'permanecerá igual' in v:
                    return 'Clima de Negocios - Igual'
                elif 'clima de negocios' in v and 'empeorará' in v:
                    return 'Clima de Negocios - Empeorará'
                elif 'economía del país' in v and 'mejor' in v and 'sí' in v:
                    return 'Economía del País - Mejor'
                elif 'economía del país' in v and 'mejor' in v and 'no' in v:
                    return 'Economía del País - Peor'
                else:
                    return 'Otros'
            
            def extraer_periodo(variable):
                v = variable.lower()
                
                # Para percepciones, no hay periodo
                if 'percepción' in v or 'clima de negocios' in v or 'economía del país' in v:
                    return 'PERCEPCION'
                
                # Buscar año
                match_anio = re.search(r'(202[5-9]|20[3-9]\d)', variable)
                if match_anio:
                    anio = match_anio.group(1)
                    meses = {'enero':'01','febrero':'02','marzo':'03','abril':'04','mayo':'05','junio':'06',
                            'julio':'07','agosto':'08','septiembre':'09','octubre':'10','noviembre':'11','diciembre':'12'}
                    
                    for mes_nombre, mes_num in meses.items():
                        if mes_nombre in v:
                            return f"{anio}-{mes_num}"
                    
                    return f"{anio}-12"
                
                return "N/A"
            
            df_agrupado['Categoria'] = df_agrupado['Variable'].apply(categorizar)
            df_agrupado['Proyeccion_Para'] = df_agrupado['Variable'].apply(extraer_periodo)
            df_agrupado = df_agrupado[df_agrupado['Categoria'] != 'Otros']
            df_agrupado = df_agrupado.sort_values(['Categoria', 'Proyeccion_Para'])
            
            proyecciones = {}
            for categoria in df_agrupado['Categoria'].unique():
                df_cat = df_agrupado[df_agrupado['Categoria'] == categoria]
                proyecciones[categoria] = df_cat[['Proyeccion_Para', 'Valor', 'Variable']].to_dict('records')
            
            debug_msg = f"Categorías encontradas: {list(proyecciones.keys())}"
            return proyecciones, fecha_encuesta, debug_msg
            
        except Exception as e:
            import traceback
            return None, None, f"Error: {str(e)}\n{traceback.format_exc()}"
    
    st.markdown("---")
    st.markdown("### 🔮 Proyecciones y Expectativas Futuras")
    
    URL_GITHUB_EXPECTATIVAS = "https://raw.githubusercontent.com/imjeiciqu32/precios-por-kg/main/micro.xlsx"
    
    @st.cache_data(ttl=3600)
    def cargar_proyecciones():
        proyecciones, fecha, msg = descargar_y_procesar_expectativas(URL_GITHUB_EXPECTATIVAS)
        return proyecciones, fecha, msg
    
    with st.spinner("📥 Cargando proyecciones..."):
        proyecciones, fecha_encuesta, debug_msg = cargar_proyecciones()
    
    # Mostrar debug
    if debug_msg:
        with st.expander("🔍 Debug Info"):
            st.code(debug_msg)
    
    if fecha_encuesta:
        meses_es = {1:'Enero',2:'Febrero',3:'Marzo',4:'Abril',5:'Mayo',6:'Junio',
                    7:'Julio',8:'Agosto',9:'Septiembre',10:'Octubre',11:'Noviembre',12:'Diciembre'}
        mes_nombre = meses_es[fecha_encuesta.month]
        st.caption(f"Datos de la Encuesta de Expectativas de Banxico - {mes_nombre} {fecha_encuesta.year}")
    else:
        st.caption("Datos de la Encuesta de Expectativas de Banxico - Actualización Mensual")
    
    if proyecciones:
        tab_p1, tab_p2, tab_p3, tab_p4 = st.tabs(["📈 Inflación", "💱 Tipo de Cambio", "👥 Desempleo", "🏢 Economía"])
        
        with tab_p1:
            st.markdown("#### 📊 Proyecciones de Inflación General 2026")
            if 'Inflación General - Mensual' in proyecciones:
                df_infl = pd.DataFrame(proyecciones['Inflación General - Mensual'])
                df_infl['Proyeccion_Para'] = pd.to_datetime(df_infl['Proyeccion_Para'])
                df_infl = df_infl.sort_values('Proyeccion_Para')
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_infl['Proyeccion_Para'], y=df_infl['Valor'], name='Proyección',
                    line=dict(color='rgb(102, 126, 234)', width=3, dash='dot'), mode='lines+markers',
                    marker=dict(size=8), fill='tozeroy', fillcolor='rgba(102, 126, 234, 0.2)',
                    hovertemplate='%{x|%b %Y}<br>%{y:.2f}%<extra></extra>'))
                fig.update_layout(title="Inflación General Proyectada (Mensual 2026)", hovermode='x', height=400,
                    yaxis_title="Inflación (%)", xaxis_title="Periodo",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            if 'Inflación Subyacente - Mensual' in proyecciones:
                st.markdown("#### 📊 Inflación Subyacente 2026")
                df_sub = pd.DataFrame(proyecciones['Inflación Subyacente - Mensual'])
                df_sub['Proyeccion_Para'] = pd.to_datetime(df_sub['Proyeccion_Para'])
                df_sub = df_sub.sort_values('Proyeccion_Para')
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_sub['Proyeccion_Para'], y=df_sub['Valor'], name='Subyacente',
                    line=dict(color='rgb(155, 135, 245)', width=3, dash='dot'), mode='lines+markers',
                    marker=dict(size=8), fill='tozeroy', fillcolor='rgba(155, 135, 245, 0.2)',
                    hovertemplate='%{x|%b %Y}<br>%{y:.2f}%<extra></extra>'))
                fig.update_layout(title="Inflación Subyacente Proyectada (Mensual 2026)", hovermode='x', height=400,
                    yaxis_title="Inflación (%)", xaxis_title="Periodo",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
                st.plotly_chart(fig, use_container_width=True)


             # INFLACIÓN AL CIERRE - SUBMÓDULO SEPARADO
            if 'Inflación General - Anual' in proyecciones:
                st.markdown("---")
                st.markdown("#### 📅 Inflación General al Cierre de Año")
                df_anual = pd.DataFrame(proyecciones['Inflación General - Anual'])
                df_anual = df_anual.sort_values('Proyeccion_Para')
                
                cols = st.columns(len(df_anual))
                for idx, (_, row) in enumerate(df_anual.iterrows()):
                    year = row['Proyeccion_Para'][:4]
                    valor = row['Valor']
                    color = "#43e97b" if valor < 3 else "#FFE082" if valor < 4 else "#f5576c"
                    emoji = "🟢" if valor < 3 else "🟡" if valor < 4 else "🔴"
                    with cols[idx]:
                        st.markdown(f"""<div style='background:{color};padding:20px;border-radius:8px;text-align:center;
                            box-shadow:0 2px 4px rgba(0,0,0,0.1);'>
                            <div style='font-size:16px;font-weight:bold;color:#333;margin-bottom:8px;'>{emoji} Cierre {year}</div>
                            <div style='font-size:32px;font-weight:bold;color:#1a1a1a;'>{valor:.2f}%</div>
                        </div>""", unsafe_allow_html=True)
            else:
                st.warning("⚠️ No se encontraron datos de Inflación General al Cierre")
            
            st.caption("Fuente: Encuesta de Expectativas - Banxico")
        
        with tab_p2:
            st.markdown("#### 💱 Proyecciones de Tipo de Cambio USD/MXN")
            if 'Tipo de Cambio - Mensual' in proyecciones:
                df_tc = pd.DataFrame(proyecciones['Tipo de Cambio - Mensual'])
                df_tc['Proyeccion_Para'] = pd.to_datetime(df_tc['Proyeccion_Para'])
                df_tc = df_tc.sort_values('Proyeccion_Para')
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df_tc['Proyeccion_Para'], 
                    y=df_tc['Valor'], 
                    marker_color='rgba(255, 75, 75, 0.7)',
                    text=[f'${v:.2f}' for v in df_tc['Valor']], 
                    textposition='outside',
                    textfont=dict(size=11, color='#333'),
                    hovertemplate='%{x|%b %Y}<br>$%{y:.2f} MXN<extra></extra>'
                ))
                fig.update_layout(
                    title="Tipo de Cambio Proyectado (Mensual 2026)", 
                    hovermode='x', 
                    height=450,
                    yaxis_title="MXN por USD", 
                    xaxis_title="Periodo",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            if 'Tipo de Cambio - Anual' in proyecciones:
                st.markdown("##### 📅 Proyección al Cierre de Año")
                df_tc_anual = pd.DataFrame(proyecciones['Tipo de Cambio - Anual'])
                df_tc_anual = df_tc_anual.sort_values('Proyeccion_Para')
                cols = st.columns(len(df_tc_anual))
                for idx, (_, row) in enumerate(df_tc_anual.iterrows()):
                    year = row['Proyeccion_Para'][:4]
                    valor = row['Valor']
                    with cols[idx]:
                        st.markdown(f"""<div style='background:linear-gradient(135deg,#f093fb 0%,#f5576c 100%);
                            padding:20px;border-radius:10px;color:white;text-align:center;'>
                            <div style='font-size:14px;opacity:0.9;margin-bottom:5px;'>💱 {year}</div>
                            <div style='font-size:32px;font-weight:bold;'>${valor:.2f}</div>
                            <div style='font-size:12px;opacity:0.8;margin-top:5px;'>MXN/USD</div>
                        </div>""", unsafe_allow_html=True)
            
            # CETES
            if 'CETE 28 - Anual' in proyecciones:
                st.markdown("##### 💰 Tasa CETE 28 días al Cierre de Año")
                df_cete = pd.DataFrame(proyecciones['CETE 28 - Anual'])
                df_cete = df_cete.sort_values('Proyeccion_Para')
                cols = st.columns(len(df_cete))
                for idx, (_, row) in enumerate(df_cete.iterrows()):
                    year = row['Proyeccion_Para'][:4]
                    valor = row['Valor']
                    with cols[idx]:
                        st.markdown(f"""<div style='background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                            padding:20px;border-radius:10px;color:white;text-align:center;'>
                            <div style='font-size:14px;opacity:0.9;margin-bottom:5px;'>📊 {year}</div>
                            <div style='font-size:32px;font-weight:bold;'>{valor:.2f}%</div>
                            <div style='font-size:12px;opacity:0.8;margin-top:5px;'>CETE 28d</div>
                        </div>""", unsafe_allow_html=True)
            else:
                st.warning("⚠️ No se encontraron datos de CETE 28 días")
            
            st.caption("Fuente: Encuesta de Expectativas - Banxico")
        
        with tab_p3:
            st.markdown("#### 👥 Proyecciones de Tasa de Desempleo")
            if 'Desempleo - Anual' in proyecciones:
                df_desemp = pd.DataFrame(proyecciones['Desempleo - Anual'])
                df_desemp = df_desemp.sort_values('Proyeccion_Para')
                
                fig = go.Figure()
                colors = ['rgba(102, 126, 234, 0.8)' if v < 3 else 
                         'rgba(155, 135, 245, 0.8)' if v < 3.5 else 
                         'rgba(186, 104, 200, 0.8)' for v in df_desemp['Valor']]
                
                fig.add_trace(go.Bar(
                    x=[row['Proyeccion_Para'][:4] for _, row in df_desemp.iterrows()],
                    y=df_desemp['Valor'], 
                    marker_color=colors,
                    text=[f"{v:.2f}%" for v in df_desemp['Valor']], 
                    textposition='outside',
                    textfont=dict(size=12, color='#333'),
                    hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'
                ))
                fig.update_layout(
                    title="Tasa de Desocupación Proyectada", 
                    height=400,
                    yaxis_title="(%) de la PEA", 
                    xaxis_title="Año", 
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("##### 📊 Detalle por Año")
                cols = st.columns(len(df_desemp))
                gradients = [
                    "linear-gradient(135deg,#667eea 0%,#764ba2 100%)",
                    "linear-gradient(135deg,#9b87f5 0%,#7e57c2 100%)",
                    "linear-gradient(135deg,#ba68c8 0%,#9c27b0 100%)"
                ]
                for idx, (_, row) in enumerate(df_desemp.iterrows()):
                    year = row['Proyeccion_Para'][:4]
                    valor = row['Valor']
                    gradient = gradients[idx % len(gradients)]
                    with cols[idx]:
                        st.markdown(f"""<div style='background:{gradient};padding:20px;border-radius:8px;text-align:center;
                            box-shadow:0 4px 8px rgba(0,0,0,0.15);'>
                            <div style='font-size:14px;font-weight:bold;color:white;'>{year}</div>
                            <div style='font-size:32px;font-weight:bold;color:white;'>{valor:.2f}%</div>
                            <div style='font-size:11px;color:rgba(255,255,255,0.8);margin-top:5px;'>de la PEA</div>
                        </div>""", unsafe_allow_html=True)
            
            st.caption("Fuente: Encuesta de Expectativas - Banxico")
        
        with tab_p4:
            st.markdown("#### 🏢 Percepciones Económicas")
            
            # Clima de negocios - SIN NORMALIZAR
            val_mejora = val_igual = val_empeora = None
            if 'Clima de Negocios - Mejorará' in proyecciones:
                val_mejora = proyecciones['Clima de Negocios - Mejorará'][0]['Valor']
            if 'Clima de Negocios - Igual' in proyecciones:
                val_igual = proyecciones['Clima de Negocios - Igual'][0]['Valor']
            if 'Clima de Negocios - Empeorará' in proyecciones:
                val_empeora = proyecciones['Clima de Negocios - Empeorará'][0]['Valor']
            
            if val_mejora is not None and val_igual is not None and val_empeora is not None:
                st.markdown("##### Clima de Negocios (Próximos 6 Meses)")
                fig = go.Figure(data=[go.Pie(
                    labels=['Mejorará', 'Permanecerá Igual', 'Empeorará'],
                    values=[val_mejora, val_igual, val_empeora], 
                    hole=.4,
                    marker_colors=['#43e97b', '#667eea', '#f5576c'], 
                    textinfo='label+percent',
                    textfont_size=14, 
                    hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>'
                )])
                fig.update_layout(height=350, showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5))
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""<div style='background:linear-gradient(135deg,#43e97b 0%,#38f9d7 100%);
                        padding:20px;border-radius:10px;color:white;text-align:center;'>
                        <div style='font-size:14px;opacity:0.9;margin-bottom:5px;'>📈 Mejorará</div>
                        <div style='font-size:36px;font-weight:bold;'>{val_mejora:.1f}%</div>
                    </div>""", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""<div style='background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                        padding:20px;border-radius:10px;color:white;text-align:center;'>
                        <div style='font-size:14px;opacity:0.9;margin-bottom:5px;'>➡️ Igual</div>
                        <div style='font-size:36px;font-weight:bold;'>{val_igual:.1f}%</div>
                    </div>""", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""<div style='background:linear-gradient(135deg,#fa709a 0%,#fee140 100%);
                        padding:20px;border-radius:10px;color:white;text-align:center;'>
                        <div style='font-size:14px;opacity:0.9;margin-bottom:5px;'>📉 Empeorará</div>
                        <div style='font-size:36px;font-weight:bold;'>{val_empeora:.1f}%</div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.warning("⚠️ No se encontraron datos de Clima de Negocios")
            
            # Economía del país - SIN NORMALIZAR
            val_si = val_no = None
            if 'Economía del País - Mejor' in proyecciones:
                val_si = proyecciones['Economía del País - Mejor'][0]['Valor']
            if 'Economía del País - Peor' in proyecciones:
                val_no = proyecciones['Economía del País - Peor'][0]['Valor']
            
            if val_si is not None and val_no is not None:
                st.markdown("##### Situación Económica vs Hace un Año")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""<div style='background:linear-gradient(135deg,#43e97b 0%,#38f9d7 100%);
                        padding:25px;border-radius:10px;color:white;text-align:center;'>
                        <div style='font-size:16px;opacity:0.9;margin-bottom:10px;'>✅ Mejor que Hace un Año</div>
                        <div style='font-size:42px;font-weight:bold;'>{val_si:.1f}%</div>
                    </div>""", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""<div style='background:linear-gradient(135deg,#fa709a 0%,#fee140 100%);
                        padding:25px;border-radius:10px;color:white;text-align:center;'>
                        <div style='font-size:16px;opacity:0.9;margin-bottom:10px;'>❌ Peor que Hace un Año</div>
                        <div style='font-size:42px;font-weight:bold;'>{val_no:.1f}%</div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.warning("⚠️ No se encontraron datos de Economía del País")
            
            st.caption("Fuente: Encuesta de Expectativas - Banxico")
        
        st.markdown("---")
        st.info("💡 **Nota:** Estas proyecciones se actualizan automáticamente desde la Encuesta de Expectativas de Banxico. Los valores son promedios de las respuestas de expertos.")
    else:
        st.error("❌ No se pudieron cargar las proyecciones. Revisa el mensaje de debug arriba.")
