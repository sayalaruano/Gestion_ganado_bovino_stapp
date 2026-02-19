# Web app
import streamlit as st
import plotly.express as px

# Manejo de archivos
from PIL import Image

# Opciones generales
im = Image.open("img/cow.ico")
st.set_page_config(
    page_title="App para Gestión de Ganado Bovino",
    page_icon=im,
    layout="wide",
)

# Adjuntar estilo css personalizado
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Agregar un título e información sobre la app
st.title("App para Gestión de Ganado Bovino")

# Crear un resumen de los datos
st.subheader("Número de vacas por rodeo")

# Obtener el numero de vacas por Rodeo
numero_vacas_por_rodeo = (
    st.session_state.lista_completa_vacas.groupby("Rodeo")["NumeroRP"]
    .count()
    .reset_index()
)
numero_vacas_por_rodeo.columns = ["Rodeo", "Numero_vacas"]

# Resetear el indice
numero_vacas_por_rodeo.reset_index(drop=True, inplace=True)

# Mostrar el dataframe
st.data_editor(
    numero_vacas_por_rodeo,
    width=1000,
    column_config={
        "widgets": st.column_config.TextColumn(
            f"Resumen de vacas por rodeo",
            help=f"Resumen de vacas por rodeo",
        )
    },
    hide_index=True,
)

# Resumen de ganado  por rodeo
st.subheader("Resumen de ganado por rodeo")
# Añadir un selectbox para seleccionar el rodeo, incluyendo las vacas vendidas y muertas
rodeo_seleccionado = st.selectbox(
    " ",
    numero_vacas_por_rodeo["Rodeo"].unique(),
    index=None,
    placeholder="Selecciona el rodeo",
    label_visibility="collapsed",
)

# Mostrar el dataframe filtrado por el rodeo seleccionado
st.data_editor(
    st.session_state.lista_completa_vacas[
        st.session_state.lista_completa_vacas["Rodeo"] == rodeo_seleccionado
    ].reset_index(drop=True),
    width=1500,
    column_config={
        "widgets": st.column_config.TextColumn(
            f"Resumen de vacas por {rodeo_seleccionado}",
            help=f"Resumen de vacas por {rodeo_seleccionado}",
        )
    },
    hide_index=True,
)

# Verificar si un rodeo fue seleccionado antes de mostrar plots
if rodeo_seleccionado:

    # Crear bar plot con las edades de las vacas por rodeo seleccionado
    st.subheader("Edades de las vacas por rodeo")

    # Obtener el numero de vacas por Rodeo
    edades_por_rodeo = (
        st.session_state.lista_completa_vacas[
            st.session_state.lista_completa_vacas["Rodeo"] == rodeo_seleccionado
        ]
        .groupby("Años")["NumeroRP"]
        .count()
        .reset_index()
    )

    # Renombrar las columnas
    edades_por_rodeo.columns = ["Años", "Numero_vacas"]

    barplot_edades = px.bar(
        edades_por_rodeo,
        x="Años",
        y="Numero_vacas",
        opacity=0.8,
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )

    barplot_edades.update_layout(
        xaxis=dict(title="Años", tickfont=dict(size=18), titlefont=dict(size=20)),
        yaxis=dict(
            title="Numero de vacas", tickfont=dict(size=18), titlefont=dict(size=20)
        ),
    ).update_xaxes(showgrid=False).update_yaxes(showgrid=False)

    st.plotly_chart(barplot_edades, use_container_width=True)

    # Crear pie plot con las razas por rodeo seleccionado
    st.subheader("Razas por rodeo")
    # Obtener el numero de vacas por Rodeo
    razas_por_rodeo = (
        st.session_state.lista_completa_vacas[
            st.session_state.lista_completa_vacas["Rodeo"] == rodeo_seleccionado
        ]
        .groupby("Raza")["NumeroRP"]
        .count()
        .reset_index()
    )
    razas_por_rodeo.columns = ["Raza", "Numero_vacas"]

    pie_plot_razas = px.pie(
        values=razas_por_rodeo["Numero_vacas"],
        names=razas_por_rodeo["Raza"],
        opacity=0.8,
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )

    pie_plot_razas.update_traces(
        textposition="inside", textinfo="value", insidetextfont=dict(size=18)
    ).update_layout(
        legend_title=dict(text="Raza", font=dict(size=24)),
        legend=dict(font=dict(size=20)),
    )

    st.plotly_chart(pie_plot_razas, use_container_width=True)

else:
    st.info(
        "Por favor, selecciona un rodeo arriba para ver el resumen de ganado por rodeo, edades y razas."
    )
