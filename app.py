import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# Configuración
# ----------------------------
st.set_page_config(
    page_title="Precios por Kg",
    layout="wide"
)

st.title("📊 App interactiva de precios")
st.caption("Ordenado por ocasión, precio y precio por kg")

# ----------------------------
# Estado inicial
# ----------------------------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Producto",
        "Fabricante",
        "Ocasión",
        "Precio ($)",
        "Gramaje (g)",
        "Precio por Kg ($)"
    ])

# ----------------------------
# Formulario
# ----------------------------
st.subheader("➕ Agregar producto")

with st.form("form_producto"):
    c1, c2, c3, c4, c5 = st.columns(5)

    producto = c1.text_input("Producto")
    fabricante = c2.selectbox(
        "Fabricante",
        ["BARCEL", "SABRITAS", "OTROS"]
    )
    ocasion = c3.selectbox(
        "Ocasión",
        ["BITES", "INDIVIDUAL", "HAMBRE", "COMPARTIR", "FAMILIAR"]
    )
    precio = c4.number_input("Precio ($)", min_value=0.0, step=1.0)
    gramaje = c5.number_input("Gramaje (g)", min_value=1.0, step=1.0)

    agregar = st.form_submit_button("Agregar")

    if agregar and producto:
        precio_kg = round(precio / (gramaje / 1000), 0)

        nuevo = pd.DataFrame([{
            "Producto": producto,
            "Fabricante": fabricante,
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
st.subheader("🧾 Productos")

st.session_state.data = st.data_editor(
    st.session_state.data,
    num_rows="dynamic",
    use_container_width=True
)

# ----------------------------
# Orden lógico
# ----------------------------
orden_ocasion = {
    "BITES": 1,
    "INDIVIDUAL": 2,
    "HAMBRE": 3,
    "COMPARTIR": 4,
    "FAMILIAR": 5
}

color_map = {
    "BARCEL": "#0B3C8C",
    "SABRITAS": "#F5C400",
    "OTROS": "#B0B0B0"
}

# ----------------------------
# Gráfico
# ----------------------------
if not st.session_state.data.empty:
    df = st.session_state.data.copy()
    df["Orden"] = df["Ocasión"].map(orden_ocasion)

    # Ordena usando precio/kg, PERO NO lo grafica
    df = df.sort_values(
        by=["Orden", "Precio ($)", "Precio por Kg ($)"],
        ascending=[True, True, True]
    )

    fig = px.bar(
        df,
        x="Producto",
        y="Precio ($)",              # 👈 ahora se grafica el desembolso
        color="Fabricante",
        color_discrete_map=color_map,
        title="Precio desembolso (ordenado por lógica económica)",
        labels={
            "Precio ($)": "Precio ($)",
            "Producto": ""
        }
    )

    # Etiqueta superior (precio)
    fig.update_traces(
        text=df["Precio ($)"].apply(lambda x: f"${int(x)}"),
        textposition="outside"
    )

    # Etiqueta inferior (precio/kg)
    for i, row in df.iterrows():
        fig.add_annotation(
            x=row["Producto"],
            y=0,
            text=f"${int(row['Precio por Kg ($)'])}/kg",
            showarrow=False,
            yshift=10,
            font=dict(color="white", size=10)
        )

    fig.update_layout(
        height=600,
        xaxis_tickangle=-45,
        yaxis_title="Precio ($)"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Agrega productos para visualizar el gráfico.")
