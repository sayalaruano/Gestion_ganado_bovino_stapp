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

# Agregar un animal a la lista de vacas
st.subheader('Modificar otros datos de un animal')

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
        rodeo = animal_NumeroRP['Rodeo'].values[0]
        nombremadre = st.text_input('Nombre de la madre', value=animal_NumeroRP['Nombre_Madre'].values[0])
        numeromadre = st.text_input('Número de la madre', value=animal_NumeroRP['Numero_Madre'].values[0])
        fecha_ultima_insem_dt = pd.to_datetime(animal_NumeroRP['Fecha_ultima_inseminacion'].values[0])
        fecha_ultima_insem = st.text_input('Fecha Última Inseminación (Año-Mes-Dia)', value=fecha_ultima_insem_dt)
        estado_preñez = st.selectbox('Estado de preñez',  ['Vacia', 'Preñada', 'Aborto'], index=0)
        observaciones_insem = st.text_area('Observaciones inseminación', value=animal_NumeroRP['Observaciones_inseminacion'].values[0])
        observaciones_nacim = st.text_area('Observaciones nacimiento', value=animal_NumeroRP['Observaciones_nacimiento'].values[0])
        fecha_ultima_med_dt = pd.to_datetime(animal_NumeroRP['Fecha_ultima_medicina'].values[0])
        fecha_ultima_med = st.text_input('Fecha Última Medicina (Año-Mes-Dia)', value=fecha_ultima_med_dt)
        observaciones_medic = st.text_area('Observaciones medicina', value=animal_NumeroRP['Observaciones_medicina'].values[0])
        fecha_muerte = st.text_input('Fecha de Muerte (Año-Mes-Dia)', value=animal_NumeroRP['Fecha_muerte_venta'].values[0])
        años = st.text_input('Años', value=animal_NumeroRP['Años'].values[0])
        meses = st.text_input('Meses', value=animal_NumeroRP['Meses'].values[0])
        edad = st.text_input('Edad (Años, Meses)', value=animal_NumeroRP['Edad'].values[0])

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
                "Nombre_Madre": nombremadre,
                "Numero_Madre": numeromadre,
                "Fecha_ultima_inseminacion": fecha_ultima_insem,
                "Estado_preñez": estado_preñez,
                "Observaciones_inseminacion": observaciones_insem,
                "Observaciones_nacimiento": observaciones_nacim,
                "Fecha_ultima_medicina": fecha_ultima_med,
                "Observaciones_medicina": observaciones_medic,
                "Fecha_muerte_venta": fecha_muerte,
                "Años": años,
                "Meses": meses,
                "Edad": edad
            }

            vaca_modif = pd.DataFrame(vaca_modif, index=[0])

            try:
                # Reemplazar la fila previa del animal con el nuevo registro con loc y el indice
                st.session_state.lista_completa_vacas.loc[st.session_state.lista_completa_vacas[st.session_state.lista_completa_vacas['NumeroRP'] == numero_rp].index[0]] = vaca_modif.loc[0]
                
                # Resetear el indice
                st.session_state.lista_completa_vacas.reset_index(drop=True, inplace=True)

                # Imprimir el registro modificado
                st.dataframe(
                    st.session_state.lista_completa_vacas[st.session_state.lista_completa_vacas['NumeroRP'] == numero_rp],
                    width = 1500,
                    )
                
                # Registrar el cambio en la pestaña de Registro de cambios
                # Crear un df con la información del cambio
                nuevo_cambio = {
                    'Cambio': f'Se modificó la vaca con NumeroRP {numero_rp} y Nombre {nombre} al rodeo {rodeo} el {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}.\n'
                }

                df = pd.DataFrame(nuevo_cambio, index=[0])

                # Crear un objecto de conexión
                conn = st.connection("gsheets", type=GSheetsConnection)
                
                # Juntar el df con la información del cambio con el df de la pestaña de Registro de cambios
                st.session_state.registro_cambios_ganado = pd.concat([df, st.session_state.registro_cambios_ganado], ignore_index=True)
                
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
                st.success('Registro de vaca modificado con éxito.')
            
            except Exception as e:
                st.error(f'Ocurrió un error: {e}')
else:
    st.warning("Por favor, ingresa un Número RP válido para buscar un animal.")
