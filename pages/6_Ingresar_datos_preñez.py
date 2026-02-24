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

# Ingresar datos de preñez
st.subheader("Ingresar diagnóstico de preñez")

col1, col2 = st.columns(2)

with col1:
    # Añadir text input para buscar un animal por su NumeroRP
    numero_rp = st.text_input(
        "Ingresa el NumeroRP del animal",
        value="",
        max_chars=None,
        key="busqueda_rp_prenez",
        type="default",
    )

    # Buscar el animal en la lista de vacas por el NumeroRP
    animal_NumeroRP = st.session_state.lista_completa_vacas[
        st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp
    ]

    # Mostrar el animal encontrado
    st.dataframe(
        animal_NumeroRP,
        width=1500,
    )

with col2:
    # Agregar selectbox para ingresar estado de preñez con las nuevas categorías
    estado_preñez = st.selectbox(
        "Selecciona el estado de preñez",
        ["Preñada", "Vacia", "Parida", "Aborto", "Seca"],
        index=None,
        placeholder="Estado de diagnóstico",
    )

    # Variables para almacenar los datos nuevos
    meses_final = 0.0
    fecha_evento = None

    # Logica para mostrar inputs adicionales según el estado de preñez seleccionado
    if estado_preñez == "Preñada":
        metodo_registro = st.radio(
            "¿Cómo deseas registrar el tiempo de preñez?",
            ["Calcular por fecha de inseminación", "Ingresar meses estimados"],
        )

        if metodo_registro == "Calcular por fecha de inseminación":
            if not animal_NumeroRP.empty:
                fecha_previa = animal_NumeroRP["Fecha_ultima_inseminacion"].values[0]
                fecha_defecto = (
                    pd.to_datetime(fecha_previa)
                    if pd.notnull(fecha_previa)
                    else datetime.now()
                )
            else:
                fecha_defecto = datetime.now()

            f_insem_conf = st.date_input(
                "Confirmar fecha de inseminación", value=fecha_defecto
            )
            dias_transcurridos = (datetime.now().date() - f_insem_conf).days
            meses_final = round(dias_transcurridos / 30.44, 1)

            # Actualizamos la fecha de inseminación
            st.session_state.lista_completa_vacas.loc[
                st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp,
                "Fecha_ultima_inseminacion",
            ] = f_insem_conf

            st.info(f"Resultado: **{meses_final} meses** de preñez calculados.")
        else:
            meses_final = st.number_input(
                "Ingresa meses estimados de preñez",
                min_value=0.0,
                max_value=10.0,
                step=0.5,
            )

    elif estado_preñez == "Parida":
        fecha_evento = st.date_input("Fecha del último parto", value=datetime.now())

    elif estado_preñez == "Aborto":
        fecha_evento = st.date_input("Fecha del último aborto", value=datetime.now())

    elif estado_preñez == "Seca":
        fecha_evento = st.date_input("Fecha del último secado", value=datetime.now())

    # Agregar datos de preñez del animal con el NumeroRP ingresado
    if st.button("Actualizar diagnóstico de preñez"):

        # Obtener nombre de animal para el registro
        if not animal_NumeroRP.empty:
            nombre_animal = animal_NumeroRP["Nombre"].values[0]
        else:
            nombre_animal = "Desconocido"
        # 1. Actualizar estado y meses
        st.session_state.lista_completa_vacas.loc[
            st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp,
            "Estado_preñez",
        ] = estado_preñez
        st.session_state.lista_completa_vacas.loc[
            st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp,
            "Meses_preñez",
        ] = meses_final

        # 2. Actualizar fechas específicas según el estado
        if estado_preñez == "Parida":
            st.session_state.lista_completa_vacas.loc[
                st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp,
                "Fecha_ultimo_parto",
            ] = fecha_evento.strftime("%m/%d/%Y")
        elif estado_preñez == "Aborto":
            st.session_state.lista_completa_vacas.loc[
                st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp,
                "Fecha_ultimo_aborto",
            ] = fecha_evento.strftime("%m/%d/%Y")
        elif estado_preñez == "Seca":
            st.session_state.lista_completa_vacas.loc[
                st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp,
                "Fecha_ultimo_secado",
            ] = fecha_evento.strftime("%m/%d/%Y")

        # Registrar el cambio en la pestaña de Registro de cambios
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Leer el historial más reciente de la nube
        try:
            historial_nube = conn.read(worksheet="Registro_prenez", ttl=0)
        except:
            historial_nube = pd.DataFrame(columns=["Cambio"])

        # Crear el log indicando el estado y la fecha si aplica
        detalle_fecha = f" con fecha {fecha_evento}" if fecha_evento else ""
        nuevo_cambio = {
            "Cambio": f"Se actualizó diagnóstico a {estado_preñez}{detalle_fecha} "
            f"(Meses: {meses_final}) para el animal {nombre_animal} (NumeroRP {numero_rp}) "
            f'el {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}.\n'
        }
        df = pd.DataFrame(nuevo_cambio, index=[0])

        # Juntar logs
        st.session_state.registro_prenez = pd.concat(
            [df, historial_nube], ignore_index=True
        ).dropna(how="all")

        # Mostrar el animal modificado
        st.dataframe(
            st.session_state.lista_completa_vacas[
                st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp
            ],
            width=1500,
        )

        # Actualizar Google Sheets
        conn.update(
            worksheet="Registro_prenez",
            data=st.session_state.registro_prenez,
        )
        conn.update(worksheet="Lista_vacas", data=st.session_state.lista_completa_vacas)

        st.success(
            f"Se actualizó correctamente el estado a {estado_preñez} para el animal {numero_rp}."
        )
