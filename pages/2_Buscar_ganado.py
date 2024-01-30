# Web app
import streamlit as st

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

# Agregar un título e información sobre la app
st.title('App para Gestión de Ganado Bovino')

st.write('''Los datos de esta aplicación son de uso exclusivo de la finca Mata Redonda.''')

# Buscar un animal por su NumeroRP
st.subheader('Buscar un animal por su NumeroRP')

# Añadir text input para buscar un animal por su NumeroRP
numero_rp = st.text_input(
    'Ingresa el NumeroRP del animal',
    value='',
    max_chars=None,
    key=None,
    type='default'
)

# Buscar el animal en la lista de vacas por el NumeroRP
animal_NumeroRP = st.session_state.lista_completa_vacas[st.session_state.lista_completa_vacas['NumeroRP'] == numero_rp]

# Mostrar el animal encontrado
st.dataframe(
    animal_NumeroRP,
    width = 1500,
    )

# Buscar un animal por su Nombre
st.subheader('Buscar un animal por su Nombre')

# Añadir text input para buscar un animal por su Nombre
nombre = st.text_input(
    'Ingresa el Nombre del animal',
    value='',
    max_chars=None,
    key=None,
    type='default'
)

# Buscar el animal en la lista de vacas por el Nombre
animal_Nombre = st.session_state.lista_completa_vacas[st.session_state.lista_completa_vacas['Nombre'] == nombre]

# Mostrar el animal encontrado
st.dataframe(
    animal_Nombre,
    width = 1500,
    )

