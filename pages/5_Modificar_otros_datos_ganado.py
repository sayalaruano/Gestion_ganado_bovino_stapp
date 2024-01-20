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
st.subheader('Mofiicar datos de un animal')

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

# Check if an animal was found
if not animal_NumeroRP.empty:
    with st.form("form_modificar_vaca"):
        numero_rp = st.text_input('Número RP', value=animal_NumeroRP['NumeroRP'].values[0])
        nombre = st.text_input('Nombre', value=animal_NumeroRP['Nombre'].values[0])
        especie = st.selectbox('Especie', ['Bovina', 'Otra'], index=0)
        fecha_nacimiento_dt = pd.to_datetime(animal_NumeroRP['Fecha_nacimiento'].values[0])
        fecha_nacimiento = st.text_input('Fecha de Nacimiento (Año-Mes-Dia)', value=fecha_nacimiento_dt.strftime('%Y-%m-%d'))
        raza = st.text_input('Raza', value=animal_NumeroRP['Raza'].values[0])
        sexo = st.selectbox('Sexo', ['Hembra', 'Macho'], index=0)
        observaciones = st.text_area('Observaciones', value=animal_NumeroRP['Observaciones'].values[0])
        fecha_muerte = st.text_input('Fecha de Muerte (Año-Mes-Dia)', value=animal_NumeroRP['Fecha_muerte'].values[0])
        años = st.text_input('Años', value=animal_NumeroRP['Años'].values[0])
        meses = st.text_input('Meses', value=animal_NumeroRP['Meses'].values[0])
        edad = st.text_input('Edad (Años, Meses)', value=animal_NumeroRP['Edad'].values[0])
        rodeo = animal_NumeroRP['Rodeo'].values[0]

        submit_button = st.form_submit_button(label='Modificar Vaca')

        if submit_button:
            vaca_modif = {
                "NumeroRP": numero_rp,
                "Nombre": nombre,
                "Especie": especie,
                "Fecha_nacimiento": fecha_nacimiento,
                "Raza": raza,
                "Sexo": sexo,
                "Rodeo": rodeo,
                "Observaciones": observaciones,
                "Fecha_muerte": fecha_muerte,
                "Años": años,
                "Meses": meses,
                "Edad": edad
            }

            vaca_modif = pd.DataFrame(vaca_modif, index=[0])

            try:
                # Reemplazar la fila previa del animal con el nuevo registro con loc y el indice
                st.session_state.lista_completa_vacas.loc[st.session_state.lista_completa_vacas[st.session_state.lista_completa_vacas['NumeroRP'] == numero_rp].index[0]] = vaca_modif.loc[0]
                
                # Imprimir el registro modificado
                st.dataframe(
                    st.session_state.lista_completa_vacas[st.session_state.lista_completa_vacas['NumeroRP'] == numero_rp],
                    width = 1500,
                    )

                # Registrar el cambio en el archivo Resgistro_cambios_database.txt con el numero de rp, rodeo, y la fecha y hora del cambio
                with open("data/Registro_cambios_database.txt", "a") as f:
                    f.write(f'Se modificó la vaca con NumeroRP {numero_rp} del rodeo {rodeo} el {datetime.now().strftime("%d/%m/%Y")}.\n')
                
                # Resetear el indice
                st.session_state.lista_completa_vacas.reset_index(drop=True, inplace=True)

                # Exportar lista_completa_vacas a csv
                st.session_state.lista_completa_vacas.to_csv("data/Lista_completa_vacas.csv", index=False)
                st.success('Vaca modificada con éxito.')
            
            except Exception as e:
                st.error(f'Ocurrió un error: {e}')
else:
    st.warning("Por favor, ingresa un Número RP válido para buscar un animal.")

st.sidebar.header('Datos')
st.sidebar.write('Los datos de esta aplicación son de uso exclusivo de la finca Mata Redonda.')

st.sidebar.header('Disponibilidad de código')
st.sidebar.write('El código de este proyecto está disponible bajo la [licencia MIT](https://mit-license.org/) en este [repositorio GitHub](https://github.com/sayalaruano/Gestion_ganado_bovino_stapp). Si usas o modificas el códifo fuente de este proyecto, por favor provee las atribuciones correspondientes por el trabajo realizado.')

st.sidebar.header('Contacto')
st.sidebar.write('Si tienes algún comentario o sugerencia acerca de este proyecto, por favor [crea an issue](https://github.com/sayalaruano/Gestion_ganado_bovino_stapp/issues/new) en el repositorio de GitHub del proyecto.')