import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO

# Datos iniciales de ejemplo (puedes cargar los tuyos)
data = [
    {"producto": "Papa Barcel 28G", "fabricante": "BARCEL", "ocasion": "BITES", "precio": 357, "gramos": 28},
    {"producto": "Ruffles Retro 34G", "fabricante": "SABRITAS", "ocasion": "BITES", "precio": 441, "gramos": 34},
    {"producto": "Sabritas Retro 30G", "fabricante": "SABRITAS", "ocasion": "BITES", "precio": 500, "gramos": 30},
    {"producto": "Papas Sol 100G", "fabricante": "OTROS", "ocasion": "HAMBRE", "precio": 200, "gramos": 100},
    {"producto": "Barcel Lo Feria 145G", "fabricante": "BARCEL", "ocasion": "COMPARTIR", "precio": 276, "gramos": 145},
    {"producto": "Chips 170G", "fabricante": "OTROS", "ocasion": "FAMILIAR", "precio": 303, "gramos": 170},
]

df = pd.DataFrame(data)

# Calcular precio por kg
df["precio_kg"] = df["precio"] / (df["gramos"] / 1000)

# Colores según fabricante
color_map = {"BARCEL": "blue", "SABRITAS": "yellow", "OTROS": "gray"}
df["color"] = df["fabricante"].apply(lambda x: color_map.get(x, "gray"))

st.title("Gráficos interactivos de precios de productos")

# Sidebar: filtrar por ocasión y producto
ocasion_sel = st.sidebar.multiselect("Selecciona ocasión(es) de consumo", options=df["ocasion"].unique(), default=df["ocasion"].unique())
fabricante_sel = st.sidebar.multiselect("Selecciona fabricante(s)", options=df["fabricante"].unique(), default=df["fabricante"].unique())
productos_sel = st.sidebar.multiselect("Selecciona productos", options=df["producto"].unique(), default=df["producto"].unique())

# Filtrar dataframe
df_filtrado = df[
    (df["ocasion"].isin(ocasion_sel)) &
    (df["fabricante"].isin(fabricante_sel)) &
    (df["producto"].isin(productos_sel))
]

# Ordenar: primero por ocasión, luego por precio (desembolso)
df_filtrado = df_filtrado.sort_values(by=["ocasion", "precio"])

# Crear gráfico de barras con Plotly
fig = go.Figure()

# Agregar barras con colores y etiquetas
for _, row in df_filtrado.iterrows():
    fig.add_trace(go.Bar(
        name=row["producto"],
        x=[row["producto"]],
        y=[row["precio"]],
        marker_color=row["color"],
        text=[f"${row['precio']}"],
        textposition="outside",
        hovertemplate=(
            f"Producto: {row['producto']}<br>"
            f"Ocasión: {row['ocasion']}<br>"
            f"Fabricante: {row['fabricante']}<br>"
            f"Precio desembolso: ${row['precio']}<br>"
            f"Precio/kg: ${row['precio_kg']:.2f}"
        )
    ))

fig.update_layout(
    barmode='group',
    title="Precio desembolso por producto (coloreado por fabricante)",
    yaxis_title="Precio desembolso ($)",
    xaxis_title="Producto",
    xaxis_tickangle=-45,
    height=500,
)

st.plotly_chart(fig, use_container_width=True)

# Exportar datos filtrados a Excel
def to_excel(df_export):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_export.to_excel(writer, index=False, sheet_name='Datos')
        writer.save()
    processed_data = output.getvalue()
    return processed_data

excel_data = to_excel(df_filtrado)

st.download_button(
    label="📥 Descargar datos filtrados (Excel)",
    data=excel_data,
    file_name="datos_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Guardar histórico local en sesión (ejemplo simple)
if "historico" not in st.session_state:
    st.session_state["historico"] = pd.DataFrame()

if st.button("Agregar vista actual al histórico"):
    st.session_state["historico"] = pd.concat([st.session_state["historico"], df_filtrado]).drop_duplicates().reset_index(drop=True)
    st.success("Vista agregada al histórico")

st.write("Histórico acumulado:")
st.dataframe(st.session_state["historico"])
