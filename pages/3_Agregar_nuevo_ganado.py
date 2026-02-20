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

# Agregar un animal a la lista de vacas
st.subheader("Agregar nuevo animal a la lista de ganado")

with st.form("form_nueva_vaca"):
    numero_rp = st.text_input("Número RP")
    nombre = st.text_input("Nombre")
    especie = st.selectbox("Especie", ["Bovina", "Otra"])
    fecha_nacimiento = st.date_input(
        "Fecha de Nacimiento (Año-Mes-Dia)", datetime.today()
    )
    raza_opciones = [
        "Holstein",
        "Holstein rojo",
        "Jersey",
        "Jersey negra",
        "Pisanga",
        "Normanda",
    ]
    raza_seleccionada = st.selectbox(
        "Raza",
        raza_opciones,
        index=None,
        placeholder="Escoge la raza, o si no está en la lista, escríbela",
        accept_new_options=True,
    )
    sexo = st.selectbox("Sexo", ["Hembra", "Macho"])
    rodeo = st.selectbox(
        "Rodeo", st.session_state.lista_completa_vacas["Rodeo"].unique()
    )
    nombre_madre = st.text_input("Nombre de la madre")
    numero_madre = st.text_input("Número de la madre")
    fecha_insem = st.date_input("Fecha de última inseminación (Año-Mes-Dia)", None)
    estado_preñez = st.selectbox(
        "Estado de preñez", ["Preñada", "Vacia", "Parida", "Aborto", "Seca"]
    )
    observaciones_insem = st.text_area("Observaciones inseminación")
    observaciones_nacim = st.text_area("Observaciones nacimiento")
    fecha_ultima_medicina = st.date_input(
        "Fecha de última medicina (Año-Mes-Dia)", None
    )
    observaciones_medicina = st.text_area("Observaciones medicina")

    submit_button = st.form_submit_button(label="Registrar Vaca")
    if submit_button:
        nueva_vaca = {
            "NumeroRP": numero_rp,
            "Nombre": nombre,
            "Especie": especie,
            "Fecha_nacimiento": fecha_nacimiento.strftime("%m/%d/%Y"),
            "Raza": raza_seleccionada,
            "Sexo": sexo,
            "Rodeo": rodeo,
            "Nombre_Madre": nombre_madre,
            "Numero_Madre": numero_madre,
            "Fecha_ultima_inseminacion": fecha_insem,
            "Estado_preñez": estado_preñez,
            "Observaciones_inseminacion": observaciones_insem,
            "Observaciones_nacimiento": observaciones_nacim,
            "Fecha_ultima_medicina": fecha_ultima_medicina,
            "Observaciones_medicina": observaciones_medicina,
            "Fecha_muerte_venta": None,
            "Años": None,
            "Meses": None,
            "Edad": None,
        }

        nueva_vaca = pd.DataFrame(nueva_vaca, index=[0])

        try:
            # Agrergar la nueva vaca a la lista de vacas
            st.session_state.lista_completa_vacas = pd.concat(
                [st.session_state.lista_completa_vacas, nueva_vaca], ignore_index=True
            )

            # Resetear el indice
            st.session_state.lista_completa_vacas.reset_index(drop=True, inplace=True)

            # Registrar el cambio en la pestaña de Registro de cambios
            # Crear un df con la información del cambio
            nuevo_cambio = {
                "Cambio": f'Se agregó la vaca con NumeroRP {numero_rp} y Nombre {nombre} al rodeo {rodeo} el {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}.\n'
            }
            df = pd.DataFrame(nuevo_cambio, index=[0])

            # Crear un objecto de conexión
            conn = st.connection("gsheets", type=GSheetsConnection)

            # Leer el historial más reciente de la nube antes de actualizar
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
            st.success("Vaca registrada con éxito.")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
