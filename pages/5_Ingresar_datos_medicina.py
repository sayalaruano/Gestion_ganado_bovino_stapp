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
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Agregar un título e información sobre la app
st.title('App para Gestión de Ganado Bovino')

st.write('''Los datos de esta aplicación son de uso exclusivo de la finca Mata Redonda.''')

# Ingresar datos de medicina y tratamientos
st.subheader('Ingresar datos de medicina y tratamientos')

col1, col2 = st.columns(2)

with col1:
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

with col2:
    # Agragar date input para ingresar la fecha de tratamiento o medicina
    fecha_medic = st.date_input(
        'Ingresa la fecha de tratamiento o medicina (Año-Mes-Dia)',
        value=datetime.now()
    )

    # Agregar text input para ingresar observactiones sobre tratamiento o medicina
    observaciones_medic = st.text_area(
        'Ingresa observaciones sobre el tratamiento o medicina',
        value='Nombre medicina o tratamiento: \nTiempo tratamiento: \nOtras observaciones: \n',
    )

    # Cambiar el rodeo del animal
    if st.button('Agregar datos de tratamientos o medicina'):
        st.session_state.lista_completa_vacas.loc[st.session_state.lista_completa_vacas['NumeroRP'] == numero_rp, 'Fecha_ultima_medicina'] = fecha_medic
        st.session_state.lista_completa_vacas.loc[st.session_state.lista_completa_vacas['NumeroRP'] == numero_rp, 'Observaciones_medicina'] = observaciones_medic

        # Registrar el cambio en la pestaña de Registro de cambios
        # Crear un df con la información del cambio
        nuevo_cambio = {
            'Cambio': f'Se agregó datos de tratamientos o medicina del animal con NumeroRP {numero_rp} el {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}.\n'
        }
        df = pd.DataFrame(nuevo_cambio, index=[0])
        
        # Juntar el df con la información del cambio con el df de la pestaña de Registro de cambios
        st.session_state.registro_cambios = pd.concat([df, st.session_state.registro_cambios], ignore_index=True)
            
        # Mostrar el animal modificado
        st.dataframe(
            st.session_state.lista_completa_vacas[st.session_state.lista_completa_vacas['NumeroRP'] == numero_rp],
            width = 1500,
            )
        
        # Crear un objecto de conexión
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Actualizar los datos de la pestaña de Registro de cambios
        conn.update(
            worksheet="Registro_cambios_basedatos",
            data=st.session_state.registro_cambios,
        )
        
        # Actualizar los datos de la pestaña de Lista_vacas
        conn.update(
            worksheet="Lista_vacas",
            data=st.session_state.lista_completa_vacas,
        )

        st.success('Se agregaron los datos de tratamientos o medicina del animal con NumeroRP ' + numero_rp + ' correctamente.')
