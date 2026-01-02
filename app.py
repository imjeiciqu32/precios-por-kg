import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# Configuración de la página
# ----------------------------
st.set_page_config(
    page_title="Precios por Kg",
    layout="wide"
)

st.title("📊 App interactiva de precios por kg")
st.caption("Agrega productos, calcula precio/kg automáticamente y ordénalos por ocasión de consumo")

# ----------------------------
# Estado inicial
# ----------------------------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Producto",
        "Ocasión",
        "Precio ($)",
        "Gramaje (g)",
        "Precio por Kg ($)"
    ])

# ----------------------------
# Formulario para agregar productos
# ----------------------------
st.subheader("➕ Agregar producto")

with st.form("form_producto"):
    col1, col2, col3, col4 = st.columns(4)

    producto = col1.text_input("Producto")
    ocasion = col2.selectbox(
        "Ocasión de consumo",
        ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"]
    )
    precio = col3.number_input("Precio ($)", min_value=0.0, step=1.0)
    gramaje = col4.number_input("Gramaje (g)", min_value=1.0, step=1.0)

    agregar = st.form_submit_button("Agregar")

    if agregar and producto:
        precio_kg = round(precio / (gramaje / 1000), 0)

        nuevo = pd.DataFrame([{
            "Producto": producto,
            "Ocasión": ocasion,
            "Precio ($)": precio,
            "Gramaje (g)": gramaje,
            "Precio por Kg ($)": precio_kg
        }])

        st.session_state.data = pd.concat(
            [st.session_state.data, nuevo],
            ignore_index=True
        )

# ----------------------------
# Tabla editable
# ----------------------------
st.subheader("🧾 Productos (puedes editar o borrar filas)")

st.session_state.data = st.data_editor(
    st.session_state.data,
    num_rows="dynamic",
    use_container_width=True
)

# ----------------------------
# Orden lógico de ocasión
# ----------------------------
orden_ocasion = {
    "BITES": 1,
    "INDIVIDUAL": 2,
    "HAMBRE": 3,
    "COMPARTIR": 4,
    "FAMILIAR": 5
}

# ----------------------------
# Gráfico
# ----------------------------
if not st.session_state.data.empty:
    df = st.session_state.data.copy()
    df["Orden"] = df["Ocasión"].map(orden_ocasion)

    df = df.sort_values(
        by=["Orden", "Precio ($)", "Precio por Kg ($)"],
        ascending=[True, True, True]
    )

    fig = px.bar(
        df,
        x="Producto",
        y="Precio por Kg ($)",
        color="Ocasión",
        text="Precio ($)",
        title="Precio por Kg ordenado automáticamente",
        labels={
            "Precio por Kg ($)": "Precio por Kg ($)",
            "Producto": ""
        }
    )

    fig.update_traces(
        texttemplate='$%{text}',
        textposition='outside'
    )

    fig.update_layout(
        height=600,
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Agrega productos para que aparezca el gráfico.")
