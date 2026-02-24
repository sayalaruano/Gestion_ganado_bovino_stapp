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

# Resumen de ganado por rodeo
st.subheader("Resumen de ganado por rodeo")
# Añadir un selectbox para seleccionar el rodeo, incluyendo las vacas vendidas y muertas
rodeo_seleccionado = st.selectbox(
    "Selecciona el rodeo para ver detalles:",
    numero_vacas_por_rodeo["Rodeo"].unique(),
    index=None,
    placeholder="Selecciona el rodeo",
    label_visibility="collapsed",
)

# Verificar si un rodeo fue seleccionado antes de mostrar plots
if rodeo_seleccionado:
    # Filtrar el df por rodeo seleccionado
    df_filt = st.session_state.lista_completa_vacas[
        st.session_state.lista_completa_vacas["Rodeo"] == rodeo_seleccionado
    ].copy()

    # Mostrar el dataframe filtrado por el rodeo seleccionado
    df_filt["Meses_preñez"] = df_filt["Meses_preñez"].fillna(0)
    st.dataframe(
        df_filt,
        width=1500,
        column_config={
            "Meses_preñez": st.column_config.ProgressColumn(
                "Progreso Gestación",
                help="Barra basada en los 9 meses de gestación bovina",
                format="%.1f meses",
                min_value=0,
                max_value=9.0,  # El límite de la barra
            ),
        },
        hide_index=True,
    )

    # Alertar si hay vacas con la barra de preñez casi llena (más de 8 meses)
    proximas_parto = df_filt[df_filt["Meses_preñez"] >= 8]

    if not proximas_parto.empty:
        st.warning(
            f"📢 **Recordatorio:** Tienes {len(proximas_parto)} vaca(s) a punto de parto (mas de 8 meses)"
        )

    # Crear un histograma de meses de preñez para las vacas preñadas del rodeo seleccionado
    # Solo incluimos vacas que tienen meses de preñez calculados (mayores a 0)
    df_preñadas_plot = df_filt[
        (df_filt["Estado_preñez"] == "Preñada") & (df_filt["Meses_preñez"] > 0)
    ]
    # Crear plot solo si hay vacas preñadas con meses de preñez calculados
    if not df_preñadas_plot.empty:
        st.subheader("Meses de preñez de las vacas por rodeo")

        # Contar el número de vacas por rango de meses de preñez
        preñez_por_rodeo = (
            df_preñadas_plot.groupby("Meses_preñez")["NumeroRP"].count().reset_index()
        )
        preñez_por_rodeo.columns = ["Meses_preñez", "Numero_vacas"]

        # Crear el bar plot
        barplot_preg = px.bar(
            preñez_por_rodeo,
            x="Meses_preñez",
            y="Numero_vacas",
            labels={
                "Meses_preñez": "Meses de gestación",
                "Numero_vacas": "Numero de vacas",
            },
            opacity=0.8,
            color_discrete_sequence=["#27AE60"],
        )

        barplot_preg.update_xaxes(
            showgrid=False, tickfont=dict(size=18), title_font=dict(size=20), dtick=1
        )
        barplot_preg.update_yaxes(
            showgrid=False, tickfont=dict(size=18), title_font=dict(size=20)
        )
        st.plotly_chart(barplot_preg, use_container_width=True)

    # Crear bar plot con las edades de las vacas por rodeo seleccionado
    st.subheader("Edades de las vacas por rodeo")

    # Asegurar que "Años" es numerico y eliminar NANs
    df_filt = df_filt.dropna(subset=["Años"])
    df_filt["Años"] = df_filt["Años"].astype(int)

    # Obtener el numero de vacas por Rodeo
    edades_por_rodeo = df_filt.groupby("Años")["NumeroRP"].count().reset_index()

    # Renombrar las columnas
    edades_por_rodeo.columns = ["Años", "Numero_vacas"]

    barplot_edades = px.bar(
        edades_por_rodeo,
        x="Años",
        y="Numero_vacas",
        labels={"Años": "Años", "Numero_vacas": "Numero de vacas"},
        opacity=0.8,
        color_discrete_sequence=["#2E86C1"],
    )

    barplot_edades.update_xaxes(
        showgrid=False, tickfont=dict(size=18), title_font=dict(size=20)
    )
    barplot_edades.update_yaxes(
        showgrid=False, tickfont=dict(size=18), title_font=dict(size=20)
    )

    st.plotly_chart(barplot_edades, use_container_width=True)

    # Crear pie plot con las razas por rodeo seleccionado
    st.subheader("Razas por rodeo")
    # Obtener el numero de vacas por Rodeo
    razas_por_rodeo = df_filt.groupby("Raza")["NumeroRP"].count().reset_index()
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
