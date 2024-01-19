# Web app
import streamlit as st
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
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Función para cargar los datos
@st.cache_data
def load_data(file):
    file = pd.read_csv(file)
    # Convertir NumeroRP a string
    file['NumeroRP'] = file['NumeroRP'].astype(str)
    return file

# Funcion para calcular la edad de un animal, en años y meses
@st.cache_data
def calculate_age_combined(birthdate):
    today = datetime.today()
    years = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    months = today.month - birthdate.month - (today.day < birthdate.day)
    if months < 0:
        months += 12
    age_formatted = f"{years} años, {months} meses"
    return years, months, age_formatted

# Cargar los datos en el cache de la app. Esto se hará solo una vez y todas las páginas tendrán acceso a los datos
if 'lista_completa_vacas' not in st.session_state:
    st.session_state.lista_completa_vacas = load_data("data/Lista_completa_vacas.csv")
    # Converting 'Fecha_nacimiento' to datetime
    st.session_state.lista_completa_vacas['Fecha_nacimiento'] = pd.to_datetime(st.session_state.lista_completa_vacas['Fecha_nacimiento'], format='%Y-%m-%d')

    # Applying the consolidated function
    st.session_state.lista_completa_vacas['Años'], st.session_state.lista_completa_vacas['Meses'], st.session_state.lista_completa_vacas['Edad'] = zip(*st.session_state.lista_completa_vacas['Fecha_nacimiento'].apply(calculate_age_combined))

# Agregar un título e información sobre la app
st.title('App para Gestión de Ganado Bovino')

with st.expander('Acerca de esta aplicación'):
    st.write('''
    Esta aplicación fue desarrollada para facilitar la gestión de ganado bovino en la finca Mata Redonda, ubicada en el Carchi, Ecuador.
    
    **Creditos**
    - Desarrollada por [Sebastián Ayala Ruano](https://sayalaruano.github.io/).
      ''')

st.subheader('Bienvenido/a!')
st.info('Mira el resumen del ganado y los rodeos, gestiona los rodeos, o agrega/elimina ganado', icon='👈')

st.sidebar.header('Datos')
st.sidebar.write('Los datos de esta aplicación son de uso exclusivo de la finca Mata Redonda.')

st.sidebar.header('Disponibilidad de código')
st.sidebar.write('El código de este proyecto está disponible bajo la [licencia MIT](https://mit-license.org/) en este [repositorio GitHub](https://github.com/sayalaruano/Gestion_ganado_bovino_stapp). Si usas o modificas el códifo fuente de este proyecto, por favor provee las atribuciones correspondientes por el trabajo realizado.')

st.sidebar.header('Contacto')
st.sidebar.write('Si tienes algún comentario o sugerencia acerca de este proyecto, por favor [crea an issue](https://github.com/sayalaruano/Gestion_ganado_bovino_stapp/issues/new) en el repositorio de GitHub del proyecto.')
    


