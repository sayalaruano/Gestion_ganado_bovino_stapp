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

# Buscar un animal por su NumeroRP
st.subheader("Buscar el animal que se desea eliminar por su NumeroRP")

# Añadir text input para buscar un animal por su NumeroRP
numero_rp = st.text_input(
    "Ingresa el NumeroRP del animal",
    value="",
    label_visibility="collapsed",
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

# Agregar boton para eliminar el registro del animal
if st.button("Eliminar animal por NumeroRP"):
    # Eliminar el registro del animal
    st.session_state.lista_completa_vacas = st.session_state.lista_completa_vacas[
        st.session_state.lista_completa_vacas["NumeroRP"] != numero_rp
    ]

    # Resetear el indice
    st.session_state.lista_completa_vacas.reset_index(drop=True, inplace=True)

    # Registrar el cambio en la pestaña de Registro de cambios
    # Crear un df con la información del cambio
    nuevo_cambio = {
        "Cambio": f'Se eliminó la vaca con NumeroRP {numero_rp} el {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}.\n'
    }
    df = pd.DataFrame(nuevo_cambio, index=[0])

    # Crear un objecto de conexión
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Leer el historial más reciente de la nube para evitar sobrescribir datos
    try:
        historial_nube = conn.read(worksheet="Registro_cambios_ganado", ttl=0)
    except:
        historial_nube = pd.DataFrame(columns=["Cambio"])

    # Juntar el df con la información del cambio con el historial real de la nube
    st.session_state.registro_cambios_ganado = pd.concat(
        [df, historial_nube], ignore_index=True
    ).dropna(how="all")

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
    st.success("Vaca eliminada con éxito.")


# Buscar un animal por su Nombre
st.subheader("Buscar el animal que se desea eliminar por su Nombre")

# Añadir text input para buscar un animal por su Nombre
nombre = st.text_input(
    "Ingresa el Nombre del animal",
    value="",
    label_visibility="collapsed",
    max_chars=None,
    key=None,
    type="default",
)

# Buscar el animal en la lista de vacas por el Nombre
animal_Nombre = st.session_state.lista_completa_vacas[
    st.session_state.lista_completa_vacas["Nombre"] == nombre
]

# Mostrar el animal encontrado
st.dataframe(
    animal_Nombre,
    width=1500,
)

# Agregar boton para eliminar el registro del animal
if st.button("Eliminar animal por Nombre"):
    # Eliminar el registro del animal
    st.session_state.lista_completa_vacas = st.session_state.lista_completa_vacas[
        st.session_state.lista_completa_vacas["Nombre"] != nombre
    ]

    # Resetear el indice
    st.session_state.lista_completa_vacas.reset_index(drop=True, inplace=True)

    # Registrar el cambio en la pestaña de Registro de cambios
    # Crear un df con la información del cambio
    nuevo_cambio = {
        "Cambio": f'Se eliminó la vaca con Nombre {nombre} el {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}.\n'
    }
    df = pd.DataFrame(nuevo_cambio, index=[0])

    # Crear un objecto de conexión
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Leer el historial más reciente de la nube para evitar sobrescribir datos
    try:
        historial_nube = conn.read(worksheet="Registro_cambios_ganado", ttl=0)
    except:
        historial_nube = pd.DataFrame(columns=["Cambio"])

    # Juntar el df con la información del cambio con el historial real de la nube
    st.session_state.registro_cambios_ganado = pd.concat(
        [df, historial_nube], ignore_index=True
    ).dropna(how="all")

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
    st.success("Vaca eliminada con éxito.")
