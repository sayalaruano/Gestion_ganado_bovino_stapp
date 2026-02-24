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

            st.info(f"Resultado: **{meses_final} meses** de preñez calculados.")
        else:
            meses_final = st.number_input(
                "Ingresa meses estimados de preñez",
                min_value=0.0,
                max_value=10.0,
                step=0.5,
            )

    elif estado_preñez in ["Parida", "Aborto", "Seca"]:
        fecha_evento = st.date_input(
            f"Fecha del último {estado_preñez.lower()}", value=datetime.now()
        )

    # Agregar datos de preñez del animal con el NumeroRP ingresado
    if st.button("Actualizar diagnóstico de preñez"):

        # Obtener nombre de animal para el registro
        if not animal_NumeroRP.empty:
            nombre_animal = animal_NumeroRP["Nombre"].values[0]
        else:
            nombre_animal = "Desconocido"

        # Calculo de fecha aproximada de parto para animales preñados
        # Obtenemos la fecha de inseminación actual para no borrarla si no hay cambios
        fecha_insem_actual = animal_NumeroRP["Fecha_ultima_inseminacion"].values[0]
        fecha_aprox_parto = ""  # Valor por defecto

        if estado_preñez == "Preñada":
            if metodo_registro == "Calcular por fecha de inseminación":
                # Usamos la fecha de inseminación confirmada arriba
                # Gestación promedio: 283 días
                f_parto = pd.to_datetime(f_insem_conf) + pd.Timedelta(days=283)
                fecha_aprox_parto = f_parto.strftime("%d/%m/%Y")
                fecha_insem_actual = f_insem_conf.strftime("%m/%d/%Y")
            else:
                # Si el ingreso es manual por meses estimados
                # Calculamos cuánto falta para los 9.3 meses (aprox 283 días)
                meses_faltantes = 9.3 - meses_final
                dias_faltantes = meses_faltantes * 30.44
                f_parto = datetime.now() + pd.Timedelta(days=int(dias_faltantes))
                fecha_aprox_parto = f_parto.strftime("%d/%m/%Y")

        # Actualizar datos de lista de vacas
        st.session_state.lista_completa_vacas.loc[
            st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp,
            [
                "Estado_preñez",
                "Meses_preñez",
                "Fecha_aprox_parto",
                "Fecha_ultima_inseminacion",
            ],
        ] = [estado_preñez, meses_final, fecha_aprox_parto, fecha_insem_actual]

        # Actualizar fechas de eventos (Parida, Aborto, Seca)
        if estado_preñez in ["Parida", "Aborto", "Seca"]:
            columna_fecha = f"Fecha_ultimo_{estado_preñez.lower()}"
            st.session_state.lista_completa_vacas.loc[
                st.session_state.lista_completa_vacas["NumeroRP"] == numero_rp,
                columna_fecha,
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
            f"✅ Se actualizó correctamente el estado de preñez de {nombre_animal} ({numero_rp}) a {estado_preñez}."
        )
    else:
        st.error("❌ No se encontró el animal. Verifica el NumeroRP.")
