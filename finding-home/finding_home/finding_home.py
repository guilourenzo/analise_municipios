import streamlit as st
import duckdb
import os
from streamlit_folium import st_folium
import geopandas as gpd
from folium.plugins import MiniMap

DATA_PATH = r"data/"

APP_TITLE = "Finding Home"
APP_SUB_TITLE = "Finding Home: Brazilian Cities Overview"

def web_config():
    st.set_page_config(page_title=APP_TITLE, page_icon="🏠", layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)
    st.markdown("---")

@st.cache_resource
def _map_data():
    return gpd.read_file(os.path.join(DATA_PATH, "BR_Municipios_2022.zip"))

@st.cache_resource
def _dw_data():
    return duckdb.connect(os.path.join(DATA_PATH, "DW.db"))

def get_city_info():
    db = _dw_data()
    city_name = st.session_state.get("city_selected")

    if city_name:
        return db.execute(
            f"SELECT * FROM city_info WHERE UPPER(MUNICIPIO) = '{city_name}'"
        ).df()
    return db.execute("SELECT * FROM city_info ORDER BY UF, MUNICIPIO").df()

@st.cache_data
def get_city_names():
    return (
        _dw_data()
        .execute("SELECT DISTINCT MUNICIPIO FROM city_info ORDER BY MUNICIPIO")
        .df()["MUNICIPIO"]
        .tolist()
    )

def get_city_code():
    city_name = st.session_state.get("city_selected")

    if city_name:
        return (
            _dw_data()
            .execute(
                f"SELECT COD_IBGE FROM city_info WHERE UPPER(MUNICIPIO) = '{city_name}'"
            )
            .fetchone()[0]
        )

def get_city_map():
    municipios = _map_data()
    city_code = get_city_code()

    if city_code:
        mapa_data = municipios[municipios["CD_MUN"] == str(city_code)].explore()

        st_folium(mapa_data, width=500, height=500)

def get_city_info_sidebar():
    city_name = st.session_state.get("city_selected")

    st.sidebar.selectbox(
        label="Select a city",
        options=get_city_names(),
        on_change=get_city_info,
        key="city_selected",
    )
    st.sidebar.markdown("---")

    if city_name:
        city_data = get_city_info()
        container = st.sidebar.container(border=True)
        container.write(
            f"""
                        Região: {city_data["REGIAO"][0]}  
                        Estado: {city_data["UF"][0]}  
                        Município: {city_data["MUNICIPIO"][0]}  
                        População: {city_data["POPULACAO"][0]:,}  
                        """
        )

def footnote():
    st.caption("Fonte de Dados")
    st.caption("---")
    st.caption(
        """
        The map data is based on the [BR_Municipios_2022.zip](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html) file from IBGE.
        """
    )
    st.caption(
        """
        The data is from the [DW.db](https://github.com/duckdb/duckdb/tree/master/examples/data) file.
        """
    )
    st.caption("---")

def main():
    web_config()
    get_city_info_sidebar()

    with st.container():
        st.dataframe(get_city_info().head(15))

    st.markdown("---")
    col_left, col_right = st.columns(2)
    
    with col_left:
        get_city_map()

    with col_right:
        st.write('Testando')

        
    footnote()



if __name__ == "__main__":
    main()
