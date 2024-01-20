# Web app
import streamlit as st
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
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Agregar un título e información sobre la app
st.title('App para Gestión de Ganado Bovino')

# Buscar un animal por su NumeroRP
st.subheader('Buscar el animal que se desea eliminar por su NumeroRP')

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

# Agregar boton para eliminar el registro del animal
if st.button('Eliminar animal por NumeroRP'):
    # Eliminar el registro del animal
    st.session_state.lista_completa_vacas = st.session_state.lista_completa_vacas[st.session_state.lista_completa_vacas['NumeroRP'] != numero_rp]

    # Registrar el cambio en el archivo Resgistro_cambios_database.txt con el numero de rp, rodeo, y la fecha y hora del cambio
    with open("data/Registro_cambios_database.txt", "a") as f:
        f.write(f'Se eliminó la vaca con NumeroRP {numero_rp} el {datetime.now().strftime("%d/%m/%Y")}.\n')
    
    # Resetear el indice
    st.session_state.lista_completa_vacas.reset_index(drop=True, inplace=True)

    # Exportar lista_completa_vacas a csv
    st.session_state.lista_completa_vacas.to_csv("data/Lista_completa_vacas.csv", index=False)
    st.success('Vaca eliminada con éxito.')


# Buscar un animal por su Nombre
st.subheader('Buscar el animal que se desea eliminar por su Nombre')

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

# Agregar boton para eliminar el registro del animal
if st.button('Eliminar animal por Nombre'):
    # Eliminar el registro del animal
    st.session_state.lista_completa_vacas = st.session_state.lista_completa_vacas[st.session_state.lista_completa_vacas['Nombre'] != nombre]

    # Registrar el cambio en el archivo Resgistro_cambios_database.txt con el numero de rp, rodeo, y la fecha y hora del cambio
    with open("data/Registro_cambios_database.txt", "a") as f:
        f.write(f'Se eliminó la vaca con Nombre {nombre} el {datetime.now().strftime("%d/%m/%Y")}.\n')
    
    # Resetear el indice
    st.session_state.lista_completa_vacas.reset_index(drop=True, inplace=True)

    # Exportar lista_completa_vacas a csv
    st.session_state.lista_completa_vacas.to_csv("data/Lista_completa_vacas.csv", index=False)
    st.success('Vaca eliminada con éxito.')

st.sidebar.header('Datos')
st.sidebar.write('Los datos de esta aplicación son de uso exclusivo de la finca Mata Redonda.')

st.sidebar.header('Disponibilidad de código')
st.sidebar.write('El código de este proyecto está disponible bajo la [licencia MIT](https://mit-license.org/) en este [repositorio GitHub](https://github.com/sayalaruano/Gestion_ganado_bovino_stapp). Si usas o modificas el códifo fuente de este proyecto, por favor provee las atribuciones correspondientes por el trabajo realizado.')

st.sidebar.header('Contacto')
st.sidebar.write('Si tienes algún comentario o sugerencia acerca de este proyecto, por favor [crea an issue](https://github.com/sayalaruano/Gestion_ganado_bovino_stapp/issues/new) en el repositorio de GitHub del proyecto.')

