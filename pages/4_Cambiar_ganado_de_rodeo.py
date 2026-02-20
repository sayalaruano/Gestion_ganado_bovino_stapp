# Web app
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pandas as pd

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

st.write(
    """Los datos de esta aplicación son de uso exclusivo de la finca Mata Redonda."""
)

# Cambiar el rodeo de un animal por su NumeroRP
st.subheader("Cambiar el rodeo de un animal por su NumeroRP")

col1, col2 = st.columns(2)

with col1:
    # Añadir text input para buscar un animal por su NumeroRP
    numero_rp = st.text_input(
        "Ingresa el NumeroRP del animal",
        value="",
        max_chars=None,
        key=None,
        type="default",
    )

    # Buscar el animal en la lista de vacas por el NumeroRP
    animal_NumeroRP = st.session_state.lista_completa_vacas[
        st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp
    ]

    # Mostrar el animal encontrado
    st.dataframe(
        animal_NumeroRP,
        width=1500,
    )

with col2:
    # Añadir selectbox para seleccionar el rodeo
    rodeo_seleccionado = st.selectbox(
        "Selecciona el rodeo al que quieres cambiar el animal",
        st.session_state.lista_completa_vacas["Rodeo"].unique(),
        index=None,
        placeholder="Selecciona el rodeo",
        label_visibility="collapsed",
    )

    if (
        rodeo_seleccionado == "Animales vendidos"
        or rodeo_seleccionado == "Animales muertos"
    ):
        # Agragar un date input para ingresar la fecha de venta o muerte
        fecha_muerte = st.date_input(
            "Ingresa la fecha de venta o muerte (Año-Mes-Dia)", value=datetime.now()
        )

    # Cambiar el rodeo del animal
    if st.button("Cambiar el rodeo del animal"):

        # Abrir conexión para leer y escribir en Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Actualizar la lista en memoria con el nuevo rodeo del animal
        st.session_state.lista_completa_vacas.loc[
            st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp, "Rodeo"
        ] = rodeo_seleccionado

        if rodeo_seleccionado in ["Animales vendidos", "Animales muertos"]:
            st.session_state.lista_completa_vacas.loc[
                st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp,
                "Fecha_muerte_venta",
            ] = fecha_muerte.strftime("%m/%d/%Y")

        # Leer log de cambios en Google Sheets
        try:
            historial_nube = conn.read(worksheet="Registro_cambios_ganado", ttl=0)
        except:
            historial_nube = pd.DataFrame(columns=["Cambio"])

        # Crear y concatenar el nuevo mensaje
        nuevo_texto = f'Se cambió el rodeo del animal con NumeroRP {numero_rp} de {animal_NumeroRP["Rodeo"].values[0]} a {rodeo_seleccionado} el {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}.\n'
        df_nuevo = pd.DataFrame({"Cambio": [nuevo_texto]})

        # Juntar el df con la información del cambio con el df de la pestaña de Registro de cambios
        st.session_state.registro_cambios_ganado = pd.concat(
            [df_nuevo, historial_nube], ignore_index=True
        ).dropna(how="all")

        # Mostrar el animal cambiado a su nuevo rodeo
        st.dataframe(
            st.session_state.lista_completa_vacas[
                st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp
            ],
            width=1500,
        )

        # Actualizar los datos de la pestaña de Registro de cambios y Lista_vacas en Google Sheets
        conn.update(
            worksheet="Registro_cambios_ganado",
            data=st.session_state.registro_cambios_ganado,
        )
        conn.update(worksheet="Lista_vacas", data=st.session_state.lista_completa_vacas)

        st.success("Se cambió la vaca de rodeo y se registró en el historial.")
