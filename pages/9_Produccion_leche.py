# Web app
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import plotly.express as px

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

# Mostrar datos de producción de leche de la finca 
st.subheader('Datos de la producción de leche')

# Agrupa los datos de producción de leche por año
st.session_state.producccion_leche['Año'] = st.session_state.producccion_leche['Fecha'].dt.year.astype(int)

# Crear widget para seleccionar el año
año_seleccionado = st.selectbox(' ', 
                                st.session_state.producccion_leche['Año'].unique(),
                                index=None,
                                placeholder="Selecciona el año",
                                label_visibility='collapsed',)

# Filtrar los datos de producción de leche por año
produccion_leche_año = st.session_state.producccion_leche[st.session_state.producccion_leche['Año'] == año_seleccionado]

# Crear grafico de linea con los datos de producción de leche por año
st.subheader(f'Producción de leche en el año {año_seleccionado}')

prod_leche = px.line(produccion_leche_año, x='Fecha', y='Cantidad (Litros)', 
                    color_discrete_sequence=px.colors.qualitative.Plotly)

prod_leche.update_layout(
    xaxis=dict(title='Fecha', tickfont=dict(size=18), titlefont=dict(size=20)),
    yaxis=dict(title='Cantidad (Litros)', tickfont=dict(size=18), titlefont=dict(size=20))
    ).update_xaxes(
        showgrid=False
    ).update_yaxes(
        showgrid=True)

# Mostrar el grafico de linea
st.plotly_chart(prod_leche, use_container_width=True)

# Agregar datos de producción de leche por una fecha determinada
st.subheader('Agregar datos de producción de leche')

# Crear un widget para seleccionar la fecha
fecha = st.date_input('Fecha', datetime.now())

# Crear un widget para ingresar la cantidad de leche producida
cantidad = st.number_input('Cantidad (Litros)', min_value=0, max_value=1000, value=0, step=1)

# Agregar los datos de producción de leche
if st.button('Agregar datos de producción de leche'):
    st.session_state.producccion_leche.loc[st.session_state.producccion_leche['Fecha'] == fecha, 'Cantidad (Litros)'] = cantidad

    # Registrar el cambio en la pestaña de Registro de cambios leche
    # Crear un df con la información del cambio
    nuevo_cambio = {
        'Cambio': f'Se agregó datos de producción de leche de {fecha.strftime("%d/%m/%Y")} el día {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}.\n'
    }

    # Convertir el diccionario en un df
    df = pd.DataFrame(nuevo_cambio, index=[0])

    # Juntar el df con la información del cambio con el df de la pestaña de Registro de cambios
    st.session_state.registro_cambios_leche = pd.concat([df, st.session_state.registro_cambios_leche], ignore_index=True)

    # Mostrar el registro modificado de producción de leche
    st.dataframe(
        st.session_state.producccion_leche[st.session_state.producccion_leche['Fecha'] == fecha],
        width = 1500,
    )

    # Crear un objecto de conexión
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Actualizar los datos de la pestaña de Registro de cambios
    conn.update(
        worksheet="Registro_cambios_leche",
        data=st.session_state.registro_cambios_leche,
    )
    
    # Actualizar los datos de la pestaña de producción de leche
    conn.update(
        worksheet="Produccion_leche",
        data=st.session_state.producccion_leche,
    )

    st.success('Se agregaron los datos de producción de leche de ' + fecha.strftime("%d/%m/%Y") + ' correctamente.')
        
