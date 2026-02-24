# Web app
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

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


# Función para cargar los datos
def load_data_gsheets(worksheet_name):
    # Crear un objeto de conexión
    conn = st.connection("gsheets", type=GSheetsConnection)

    if worksheet_name == "Lista_vacas":
        file = conn.read(
            worksheet=worksheet_name,
            ttl=0,
            usecols=list(range(23)),
        )
        # Convertir NumeroRP a string
        file["NumeroRP"] = file["NumeroRP"].astype(str)

        # Limpieza de datos - eliminar filas vacias y con "nan"
        file.dropna(how="all", inplace=True)
        file = file[~file["NumeroRP"].str.contains("nan")]

        # Resetear el indice
        file.reset_index(drop=True, inplace=True)
        return file

    elif worksheet_name.startswith("Registro_"):
        # Carga genérica para hojas de registro de varios cambios
        file = conn.read(
            worksheet=worksheet_name,
            ttl=0,
            usecols=[0],
        )
        return file

    elif worksheet_name == "Produccion_leche":
        file = conn.read(
            worksheet=worksheet_name,
            ttl=0,
            usecols=list(range(3)),
        )

        return file


# Funcion para calcular la edad de un animal, en años y meses
def calculate_age_combined(birthdate):
    if pd.isnull(birthdate):
        return None, None, "N/A"

    today = datetime.today()
    years = (
        today.year
        - birthdate.year
        - ((today.month, today.day) < (birthdate.month, birthdate.day))
    )
    months = today.month - birthdate.month - (today.day < birthdate.day)
    if months < 0:
        months += 12
    age_formatted = f"{years} años, {months} meses"
    return years, months, age_formatted


# Funcion para calcular meses de prenez a partir de la fecha de inseminación y el estado de preñez
def calculate_pregnancy_months(row):
    # Caso 1: Está preñada y hay fecha de inseminación (Cálculo automático)
    if row["Estado_preñez"] == "Preñada" and pd.notnull(
        row["Fecha_ultima_inseminacion"]
    ):
        try:
            f_insem = pd.to_datetime(row["Fecha_ultima_inseminacion"])
            dias = (datetime.today() - f_insem).days
            meses = round(dias / 30.44, 1)
            return min(meses, 10.0)
        except:
            return row["Meses_preñez"]

    # Caso 2: Está preñada pero no hay fecha de inseminación (Mantener lo ingresado manualmente)
    elif row["Estado_preñez"] == "Preñada":
        valor_actual = row["Meses_preñez"]
        return valor_actual if pd.notnull(valor_actual) else 0.0

    # Caso 3: No está preñada
    return 0.0


def calculate_expected_date_parto(row):
    if row["Estado_preñez"] == "Preñada":
        try:
            hoy = datetime.today()
            # 1. Si hay fecha de inseminación, sumamos 283 días
            if pd.notnull(row["Fecha_ultima_inseminacion"]):
                f_insem = pd.to_datetime(row["Fecha_ultima_inseminacion"])
                return (f_insem + pd.Timedelta(days=283)).date()

            # 2. Si NO hay fecha pero hay meses estimados
            elif pd.notnull(row["Meses_preñez"]) and row["Meses_preñez"] > 0:
                # Calculamos cuánto le falta para llegar a 9.3 meses (gestación completa)
                meses_faltantes = 9.3 - row["Meses_preñez"]
                dias_faltantes = meses_faltantes * 30.44
                return (hoy + pd.Timedelta(days=int(dias_faltantes))).date()
        except:
            return None
    return None


# Cargar los datos en el cache de la app. Esto se hará solo una vez y todas
# las páginas tendrán acceso a los datos
# Pestaña de lista de vacas y cálculo de edades
if "lista_completa_vacas" not in st.session_state:
    df_vacas = load_data_gsheets("Lista_vacas")

    # Convertir 'Fecha_nacimiento' a datetime
    df_vacas["Fecha_nacimiento"] = pd.to_datetime(
        df_vacas["Fecha_nacimiento"], format="mixed", errors="coerce"
    )

    # Aplicar la función de edad
    res_edades = df_vacas["Fecha_nacimiento"].apply(calculate_age_combined)
    df_vacas["Años"], df_vacas["Meses"], df_vacas["Edad"] = zip(*res_edades)

    # Aplicar la función de cálculo de meses de preñez
    df_vacas["Fecha_ultima_inseminacion"] = pd.to_datetime(
        df_vacas["Fecha_ultima_inseminacion"], errors="coerce"
    )
    df_vacas["Meses_preñez"] = df_vacas.apply(calculate_pregnancy_months, axis=1)

    st.session_state.lista_completa_vacas = df_vacas

# Pestaña de producción de leche
if "producccion_leche" not in st.session_state:
    df_leche = load_data_gsheets("Produccion_leche")

    # Elimina filas donde 'Fecha' es nulo
    df_leche = df_leche.dropna(subset=["Fecha"])

    # Convertir 'Fecha' a datetime
    df_leche["Fecha"] = pd.to_datetime(df_leche["Fecha"], errors="coerce")
    st.session_state.producccion_leche = df_leche

# Pestañas de registro de cambios
reg_cambios = {
    "registro_cambios_ganado": "Registro_cambios_ganado",
    "registro_prenez": "Registro_prenez",
    "registro_inseminacion": "Registro_inseminacion",
    "registro_medicina": "Registro_medicina",
    "registro_cambios_leche": "Registro_cambios_leche",
}

for state_key, sheet_name in reg_cambios.items():
    if state_key not in st.session_state:
        st.session_state[state_key] = load_data_gsheets(sheet_name)


# Agregar un título e información sobre la app
st.title("App para Gestión de Ganado Bovino")

st.write(
    """Los datos de esta aplicación son de uso exclusivo de la finca Mata Redonda."""
)

with st.expander("Acerca de esta aplicación"):
    st.write(
        """
    Esta aplicación fue desarrollada para facilitar la gestión de ganado bovino en la finca Mata Redonda, ubicada en el Carchi, Ecuador.
    
    **Creditos**
    - Desarrollada por [Sebastián Ayala Ruano](https://sayalaruano.github.io/).
    - El código de este proyecto está disponible bajo la [licencia MIT](https://mit-license.org/) en este [repositorio GitHub](https://github.com/sayalaruano/Gestion_ganado_bovino_stapp). Si usas o modificas el códifo fuente de este proyecto, por favor provee las atribuciones correspondientes por el trabajo realizado.
    - Si tienes algún comentario o sugerencia acerca de este proyecto, por favor [crea an issue](https://github.com/sayalaruano/Gestion_ganado_bovino_stapp/issues/new) en el repositorio de GitHub del proyecto.
      """
    )

st.subheader("Bienvenido/a!")
st.info(
    "Mira el resumen del ganado y los rodeos, gestiona los rodeos, eventos de preñez, inseminación o medicina, o agrega/elimina ganado",
    icon="👈",
)

st.subheader("⚠️ Alertas de Manejo")

# Calculamos la fecha estimada para todas
df_vacas["Fecha_aprox_parto"] = df_vacas.apply(calculate_expected_date_parto, axis=1)

# Filtramos las que paren en los próximos 15 días
hoy = datetime.today().date()
proximos_15 = hoy + pd.Timedelta(days=15)

alertas_parto = df_vacas[
    (df_vacas["Fecha_aprox_parto"] >= hoy)
    & (df_vacas["Fecha_aprox_parto"] <= proximos_15)
]

if not alertas_parto.empty:
    st.error(f"Se aproximan {len(alertas_parto)} partos en las próximas 2 semanas")
    # Mostramos una tablita simple con lo importante
    st.dataframe(
        alertas_parto[["NumeroRP", "Nombre", "Rodeo", "Fecha_aprox_parto"]].sort_values(
            "Fecha_aprox_parto"
        ),
        hide_index=True,
    )
else:
    st.success("No hay partos programados para las próximas 2 semanas.")
