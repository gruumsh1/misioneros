import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
	page_title="Comidas misioneros - Apizaco y Tlaxco", layout="wide"
)

st.title("🍽️ Calendario de Comidas para Misioneros")

# Barra lateral: Filtros de Zona y Mes
st.sidebar.header("Filtros de Visualización")
zona = st.sidebar.selectbox(
    "Selecciona el Compañerismo:",
    [
        "Apizaco 1 (Hno. Ulises / Galaviz)",
        "Apizaco 2 (Hno. Jorge Álvarez)",
        "Apizaco 3 (Hno. Jorge Luis Pérez)",
        "Tlaxco",
    ],
)

meses_nombres = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}

col_m, col_a = st.sidebar.columns(2)
with col_m:
    mes_sel = st.selectbox(
        "Mes", options=list(meses_nombres.keys()), format_func=lambda x: meses_nombres[x], index=8 # Septiembre por defecto (2026)
    )
with col_a:
    anio_sel = st.selectbox("Año", options=[2026, 2027], index=0)

# Base de datos simulada en sesión (posteriormente la conectamos a Google Sheets o SQLite)
if "db" not in st.session_state:
    st.session_state.db = pd.DataFrame(
        columns=[
            "Compañerismo",
            "Mes-Año",
            "Fecha",
            "Familia / Hermano",
            "Teléfono",
            "Notas",
        ]
    )

st.header(f"Agenda para: {zona} — {meses_nombres[mes_sel]} {anio_sel}")

tab1, tab2 = st.tabs(["📅 Ver Calendario del Mes", "✍️ Apuntarse a una fecha"])

with tab1:
    st.subheader(f"Registros de {meses_nombres[mes_sel]} {anio_sel}")
    
    periodo_str = f"{anio_sel}-{str(mes_sel).zfill(2)}"
    df_filtrado = st.session_state.db[
        (st.session_state.db["Compañerismo"] == zona) & 
        (st.session_state.db["Mes-Año"] == periodo_str)
    ]

    if df_filtrado.empty:
        st.info(f"Aún no hay familias registradas para {meses_nombres[mes_sel]} {anio_sel} en este compañerismo.")
    else:
        st.dataframe(df_filtrado[["Fecha", "Familia / Hermano", "Teléfono", "Notas"]], use_container_width=True)

        if st.button("🖨️ Generar vista para imprimir este mes"):
            st.success("¡Vista lista para imprimir este mes sin tachones!")

with tab2:
    st.subheader("Regístrate para darles de comer")
    with st.form("form_registro_mes"):
        f_fecha = st.date_input(
            "Fecha de la comida", 
            datetime.date(anio_sel, mes_sel, 1)
        )
        f_nombre = st.text_input("Nombre de la Familia / Persona")
        f_tel = st.text_input("Número de Teléfono (WhatsApp)")
        f_notas = st.text_area("Notas adicionales (ej. hora acordada, restricciones)")

        submitted = st.form_submit_button("Guardar Registro")
        if submitted:
            if f_nombre and f_tel:
                if f_fecha.month == mes_sel and f_fecha.year == anio_sel:
                    nuevo_registro = pd.DataFrame(
                        [
                            {
                                "Compañerismo": zona,
                                "Mes-Año": periodo_str,
                                "Fecha": str(f_fecha),
                                "Familia / Hermano": f_nombre,
                                "Teléfono": f_tel,
                                "Notas": f_notas,
                            }
                        ]
                    )
                    st.session_state.db = pd.concat(
                        [st.session_state.db, nuevo_registro], ignore_index=True
                    )
                    st.success(f"¡Gracias {f_nombre}! Registrado para el {f_fecha}.")
                    st.rerun()
                else:
                    st.warning(f"La fecha seleccionada no corresponde a {meses_nombres[mes_sel]} {anio_sel}.")
            else:
                st.error("Por favor completa al menos tu nombre y teléfono.")
