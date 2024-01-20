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

# Agregar un animal a la lista de vacas
st.subheader('Agregar nuevo animal a la lista de ganado')

with st.form("form_nueva_vaca"):
    numero_rp = st.text_input('Número RP')
    nombre = st.text_input('Nombre')
    especie = st.selectbox('Especie', ['Bovina', 'Otra'])
    fecha_nacimiento = st.date_input('Fecha de Nacimiento (Año-Mes-Dia)', datetime.today())
    raza = st.text_input('Raza')
    sexo = st.selectbox('Sexo', ['Hembra', 'Macho'])
    rodeo = st.selectbox('Rodeo', st.session_state.lista_completa_vacas['Rodeo'].unique())
    observaciones = st.text_area('Observaciones')

    submit_button = st.form_submit_button(label='Registrar Vaca')

    if submit_button:
        nueva_vaca = {
            "NumeroRP": numero_rp,
            "Nombre": nombre,
            "Especie": especie,
            "Fecha_nacimiento": fecha_nacimiento.strftime('%Y-%m-%d'),
            "Raza": raza,
            "Sexo": sexo,
            "Rodeo": rodeo,
            "Observaciones": observaciones,
            "Fecha_muerte": None,
            "Años": None,
            "Meses": None,
            "Edad": None
        }

        nueva_vaca = pd.DataFrame(nueva_vaca, index=[0])

        try:
            # Agrergar la nueva vaca a la lista de vacas
            st.session_state.lista_completa_vacas = pd.concat([st.session_state.lista_completa_vacas, nueva_vaca], ignore_index=True)
            
            # Registrar el cambio en el archivo Resgistro_cambios_database.txt con el numero de rp, rodeo, y la fecha y hora del cambio
            with open("data/Registro_cambios_database.txt", "a") as f:
                f.write(f'Se agregó la vaca con NumeroRP {numero_rp} al rodeo {rodeo} el {datetime.now().strftime("%d/%m/%Y")}.\n')
            
            # Resetear el indice
            st.session_state.lista_completa_vacas.reset_index(drop=True, inplace=True)

            # Exportar lista_completa_vacas a csv
            st.session_state.lista_completa_vacas.to_csv("data/Lista_completa_vacas.csv", index=False)
            st.success('Vaca registrada con éxito.')
        except Exception as e:
            st.error(f'Ocurrió un error: {e}')

st.sidebar.header('Datos')
st.sidebar.write('Los datos de esta aplicación son de uso exclusivo de la finca Mata Redonda.')

st.sidebar.header('Disponibilidad de código')
st.sidebar.write('El código de este proyecto está disponible bajo la [licencia MIT](https://mit-license.org/) en este [repositorio GitHub](https://github.com/sayalaruano/Gestion_ganado_bovino_stapp). Si usas o modificas el códifo fuente de este proyecto, por favor provee las atribuciones correspondientes por el trabajo realizado.')

st.sidebar.header('Contacto')
st.sidebar.write('Si tienes algún comentario o sugerencia acerca de este proyecto, por favor [crea an issue](https://github.com/sayalaruano/Gestion_ganado_bovino_stapp/issues/new) en el repositorio de GitHub del proyecto.')