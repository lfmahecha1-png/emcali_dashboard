import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from io import BytesIO
import openpyxl

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Portafolio EMCALI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Dashboard Portafolio de Proyectos EMCALI")
st.markdown("---")

# Función para cargar datos
@st.cache_data
def load_data():
    # URL del Google Sheets (publicado como CSV)
    sheet_id = "1TwBj1Pj8XIXuwoTA94nTJ7G8vLJ-Xll-vVD1bQlanLs"
    sheet_name = "datos_generales"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

# Cargar datos
df = load_data()

# Verificar si los datos se cargaron correctamente
if df.empty:
    st.warning("No se pudieron cargar los datos. Por favor, verifica la conexión.")
else:
    # Sidebar con filtros
    st.sidebar.header("Filtros")

    # Filtro por Gerencia
    gerencias = df['GERENCIAS'].unique()
    selected_gerencias = st.sidebar.multiselect(
        'Seleccione Gerencias:',
        options=gerencias,
        default=gerencias
    )

    # Filtro por Servicio
    servicios = df['SERVICIOS'].unique()
    selected_servicios = st.sidebar.multiselect(
        'Seleccione Servicios:',
        options=servicios,
        default=servicios
    )

    # Filtro por Estado
    estados = df['ESTADO'].unique()
    selected_estados = st.sidebar.multiselect(
        'Seleccione Estados:',
        options=estados,
        default=estados
    )

    # Aplicar filtros
    filtered_df = df[
        (df['GERENCIAS'].isin(selected_gerencias)) &
        (df['SERVICIOS'].isin(selected_servicios)) &
        (df['ESTADO'].isin(selected_estados))
    ]

    # Mostrar métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_proyectos = len(filtered_df)
        st.metric("Total Proyectos", total_proyectos)
    
    with col2:
        proyectos_ejecucion = len(filtered_df[filtered_df['ESTADO'].str.contains('EJECUCIÓN', na=False)])
        st.metric("En Ejecución", proyectos_ejecucion)
    
    with col3:
        capex_total = filtered_df['CAPEX / OPEX'].str.contains('CAPEX', na=False).sum()
        st.metric("Proyectos CAPEX", capex_total)
    
    with col4:
        opex_total = filtered_df['CAPEX / OPEX'].str.contains('OPEX', na=False).sum()
        st.metric("Proyectos OPEX", opex_total)

    st.markdown("---")

    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de distribución por estado
        fig_estado = px.bar(
            filtered_df['ESTADO'].value_counts().reset_index(),
            x='ESTADO',
            y='count',
            title="Distribución de Proyectos por Estado",
            labels={'ESTADO': 'Estado', 'count': 'Número de Proyectos'}
        )
        st.plotly_chart(fig_estado, use_container_width=True)
    
    with col2:
        # Gráfico de distribución por servicio
        fig_servicio = px.pie(
            filtered_df,
            names='SERVICIOS',
            title="Distribución de Proyectos por Servicio"
        )
        st.plotly_chart(fig_servicio, use_container_width=True)

    # Gráfico de distribución por gerencia
    fig_gerencia = px.bar(
        filtered_df['GERENCIAS'].value_counts().reset_index(),
        x='GERENCIAS',
        y='count',
        title="Distribución de Proyectos por Gerencia",
        labels={'GERENCIAS': 'Gerencia', 'count': 'Número de Proyectos'}
    )
    st.plotly_chart(fig_gerencia, use_container_width=True)

    # Mostrar datos filtrados
    st.subheader("Datos de Proyectos Filtrados")
    st.dataframe(filtered_df)

    # Botones de exportación
    col1, col2 = st.columns(2)
    
    with col1:
        # Exportar a Excel
        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='openpyxl')
            df.to_excel(writer, index=False, sheet_name='Proyectos')
            writer.save()
            processed_data = output.getvalue()
            return processed_data
        
        excel_data = to_excel(filtered_df)
        st.download_button(
            label="📊 Descargar Excel",
            data=excel_data,
            file_name="proyectos_emcali.xlsx",
            mime="application/vnd.ms-excel"
        )
    
    with col2:
        # Exportar a CSV
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Descargar CSV",
            data=csv_data,
            file_name="proyectos_emcali.csv",
            mime="text/csv"
        )

# Información adicional
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Nota:** Esta es una versión inicial del dashboard. 
    Los datos se cargan directamente desde Google Sheets.
    """
)