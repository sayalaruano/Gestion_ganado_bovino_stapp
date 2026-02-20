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

# Ingresar datos de inseminación y preñez
st.subheader("Ingresar datos de inseminación y preñez")

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
    # Agragar date input para ingresar la fecha de inseminación
    fecha_insem = st.date_input(
        "Ingresa la última fecha de inseminación (Año-Mes-Dia)", value=datetime.now()
    )

    # Agregar selectbox para ingresar estado de preñez
    estado_preñez = st.selectbox(
        " ",
        ["Vacia", "Preñada", "Aborto"],
        index=None,
        placeholder="Selecciona el estado de preñez",
        label_visibility="collapsed",
    )

    # Agregar text input para ingresar observactiones sobre inseminación y preñez
    observaciones_insem = st.text_area(
        "Ingresa observaciones sobre inseminación y preñez",
        value="Nombre del toro o pajuela: \nRepeticiones: \nNúmero partos: \nOtras observaciones:",
    )

    # Agregar datos de inseminación y preñez del animal con el NumeroRP ingresado
    if st.button("Agregar datos de inseminación y preñez"):
        st.session_state.lista_completa_vacas.loc[
            st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp,
            "Fecha_ultima_inseminacion",
        ] = fecha_insem
        st.session_state.lista_completa_vacas.loc[
            st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp,
            "Estado_preñez",
        ] = estado_preñez
        st.session_state.lista_completa_vacas.loc[
            st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp,
            "Observaciones_inseminacion",
        ] = observaciones_insem

        # Registrar el cambio en la pestaña de Registro de cambios
        # Abrir conexión para leer y escribir en Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Leer el historial más reciente de la nube para evitar sobrescribir datos
        try:
            historial_nube = conn.read(worksheet="Registro_cambios_ganado", ttl=0)
        except:
            historial_nube = pd.DataFrame(columns=["Cambio"])

        # Crear un df con la información del cambio
        nuevo_cambio = {
            "Cambio": f'Se agregó datos de inseminación y preñez del animal con NumeroRP {numero_rp} el {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}.\n'
        }
        df = pd.DataFrame(nuevo_cambio, index=[0])

        # Juntar el df con la información del cambio con el df de la pestaña de Registro de cambios
        # Concatenamos con historial_nube para asegurar la integridad del log
        st.session_state.registro_cambios_ganado = pd.concat(
            [df, historial_nube], ignore_index=True
        ).dropna(how="all")

        # Mostrar el animal modificado
        st.dataframe(
            st.session_state.lista_completa_vacas[
                st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp
            ],
            width=1500,
        )

        # Actualizar los datos de la pestaña de Registro de cambios
        conn.update(
            worksheet="Registro_cambios_ganado",
            data=st.session_state.registro_cambios_ganado,
        )

        # Actualizar los datos de la pestaña de Lista_vacas
        conn.update(
            worksheet="Lista_vacas",
            data=st.session_state.lista_completa_vacas,
        )

        st.success(
            "Se agregaron los datos de inseminación y preñez del animal con NumeroRP "
            + numero_rp
            + " correctamente."
        )
