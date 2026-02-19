# Web app
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

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


# Función para cargar los datos
def load_data_gsheets(worksheet_name):

    # Crear un objeto de conexión
    conn = st.connection("gsheets", type=GSheetsConnection)

    if worksheet_name == "Lista_vacas":
        file = conn.read(
            worksheet=worksheet_name,
            ttl=0,
            usecols=list(range(17)),
        )
        # Convertir NumeroRP a string
        file["NumeroRP"] = file["NumeroRP"].astype(str)

        # Delete rows with nan values in all columns
        file.dropna(how="all", inplace=True)

        # Delete rows with "nan" string in specific columns
        file = file[~file["NumeroRP"].str.contains("nan")]

        # Resetear el indice
        file.reset_index(drop=True, inplace=True)

        return file

    elif (
        worksheet_name == "Registro_cambios_ganado"
        or worksheet_name == "Registro_cambios_leche"
    ):
        file = conn.read(
            worksheet=worksheet_name,
            ttl=0,
            usecols=list(range(1)),
        )

        return file

    elif worksheet_name == "Produccion_leche":
        file = conn.read(
            worksheet=worksheet_name,
            ttl=0,
            usecols=list(range(3)),
        )

        return file


# Funcion para calcular la edad de un animal, en años y meses
# @st.cache_data
def calculate_age_combined(birthdate):
    today = datetime.today()
    years = (
        today.year
        - birthdate.year
        - ((today.month, today.day) < (birthdate.month, birthdate.day))
    )
    months = today.month - birthdate.month - (today.day < birthdate.day)
    if months < 0:
        months += 12
    age_formatted = f"{years} años, {months} meses"
    return years, months, age_formatted


# Cargar los datos en el cache de la app. Esto se hará solo una vez y todas las páginas tendrán acceso a los datos
# Pestaña de lista de vacas
if "lista_completa_vacas" not in st.session_state:
    st.session_state.lista_completa_vacas = load_data_gsheets("Lista_vacas")

    # Convertir 'Fecha_nacimiento' a datetime
    st.session_state.lista_completa_vacas["Fecha_nacimiento"] = pd.to_datetime(
        st.session_state.lista_completa_vacas["Fecha_nacimiento"], format="mixed"
    )

    # Aplicar la función calculate_age_combined a la columna 'Fecha_nacimiento'
    (
        st.session_state.lista_completa_vacas["Años"],
        st.session_state.lista_completa_vacas["Meses"],
        st.session_state.lista_completa_vacas["Edad"],
    ) = zip(
        *st.session_state.lista_completa_vacas["Fecha_nacimiento"].apply(
            calculate_age_combined
        )
    )

# Pestaña de registro de cambios
if "registro_cambios_ganado" not in st.session_state:
    st.session_state.registro_cambios_ganado = load_data_gsheets(
        "Registro_cambios_ganado"
    )

if "producccion_leche" not in st.session_state:
    st.session_state.producccion_leche = load_data_gsheets("Produccion_leche")

    # Elimina filas donde 'Fecha' es nulo
    st.session_state.producccion_leche = st.session_state.producccion_leche.dropna(
        subset=["Fecha"]
    )

    # Convertir 'Fecha' a datetime
    st.session_state.producccion_leche["Fecha"] = pd.to_datetime(
        st.session_state.producccion_leche["Fecha"]
    )

if "registro_cambios_leche" not in st.session_state:
    st.session_state.registro_cambios_leche = load_data_gsheets(
        "Registro_cambios_leche"
    )

# Agregar un título e información sobre la app
st.title("App para Gestión de Ganado Bovino")

st.write(
    """Los datos de esta aplicación son de uso exclusivo de la finca Mata Redonda."""
)

with st.expander("Acerca de esta aplicación"):
    st.write(
        """
    Esta aplicación fue desarrollada para facilitar la gestión de ganado bovino en la finca Mata Redonda, ubicada en el Carchi, Ecuador.
    
    **Creditos**
    - Desarrollada por [Sebastián Ayala Ruano](https://sayalaruano.github.io/).
    - El código de este proyecto está disponible bajo la [licencia MIT](https://mit-license.org/) en este [repositorio GitHub](https://github.com/sayalaruano/Gestion_ganado_bovino_stapp). Si usas o modificas el códifo fuente de este proyecto, por favor provee las atribuciones correspondientes por el trabajo realizado.
    - Si tienes algún comentario o sugerencia acerca de este proyecto, por favor [crea an issue](https://github.com/sayalaruano/Gestion_ganado_bovino_stapp/issues/new) en el repositorio de GitHub del proyecto.
      """
    )

st.subheader("Bienvenido/a!")
st.info(
    "Mira el resumen del ganado y los rodeos, gestiona los rodeos, o agrega/elimina ganado",
    icon="👈",
)
