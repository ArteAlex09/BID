import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Dashboard Estadístico", page_icon="📊", layout="wide")
st.title("📊 Dashboard de Inteligencia de Amenazas")
st.markdown("Análisis estadístico descriptivo basado en la muestra de infraestructura de red (Mayo 2025 - Enero 2026).")

# --- CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    return pd.read_csv("data/BID_dataset.csv")

try:
    df = cargar_datos()
except FileNotFoundError:
    st.error("No se encontró el archivo dataset. Verifica que esté en data/BID_dataset.csv")
    st.stop()

# ==========================================
# --- NUEVA SECCIÓN: BARRA DE FILTROS ---
# ==========================================
st.sidebar.header("🔍 Filtros de Análisis")

# Filtro 1: Nivel de Amenaza (threat_level)
# Obtenemos los valores únicos, quitamos nulos y ordenamos
niveles_amenaza = sorted(df['threat_level'].dropna().unique().tolist())
nivel_seleccionado = st.sidebar.multiselect(
    "Filtrar por Nivel de Amenaza:",
    options=niveles_amenaza,
    default=niveles_amenaza # Por defecto mostramos todos
)

# Filtro 2: Tipo de Ataque (attack_type)
tipos_ataque = sorted(df['attack_type'].dropna().unique().tolist())
ataque_seleccionado = st.sidebar.multiselect(
    "Filtrar por Tipo de Ataque:",
    options=tipos_ataque,
    default=tipos_ataque
)

# APLICAR LOS FILTROS AL DATAFRAME
# Creamos una copia filtrada basada en lo que el usuario eligió
df_filtrado = df[
    (df['threat_level'].isin(nivel_seleccionado)) &
    (df['attack_type'].isin(ataque_seleccionado))
]

# Mensaje de advertencia si el usuario desmarca todo
if df_filtrado.empty:
    st.warning("⚠️ Los filtros seleccionados no arrojaron ningún resultado. Por favor, ajusta tu selección.")
    st.stop() # Detiene la ejecución para no mostrar gráficas vacías

# ==========================================
# --- EL RESTO DE TU CÓDIGO (Usando df_filtrado) ---
# ==========================================

# --- MÉTRICAS PRINCIPALES (KPIs) ---
st.subheader("1. Resumen de la Muestra (Filtrada)")
col1, col2, col3, col4 = st.columns(4)

total_registros = len(df_filtrado)
maliciosos = len(df_filtrado[df_filtrado['is_malicious'] == 1])
benignos = len(df_filtrado[df_filtrado['is_malicious'] == 0])

# Prevenir división por cero si no hay registros
tasa_prev = (maliciosos / total_registros) * 100 if total_registros > 0 else 0

col1.metric("Total de Registros", f"{total_registros}")
col2.metric("Infraestructura Benigna", f"{benignos}")
col3.metric("Infraestructura Maliciosa", f"{maliciosos}")
col4.metric("Tasa de Prevalencia P(M)", f"{tasa_prev:.1f}%")

st.markdown("---")

# --- SECCIÓN 6: ESTADÍSTICA DESCRIPTIVA ---
st.subheader("2. Estadística Descriptiva (Reputación y Amenaza)")
st.markdown("Análisis de la variable `abuseip_score` según los filtros aplicados.")

media = df_filtrado['abuseip_score'].mean()
mediana = df_filtrado['abuseip_score'].median()
# La moda puede devolver múltiples valores o vacío, manejamos eso de forma segura
moda_val = df_filtrado['abuseip_score'].mode()
moda = moda_val[0] if not moda_val.empty else 0 
desviacion = df_filtrado['abuseip_score'].std()

col_est1, col_est2, col_est3, col_est4 = st.columns(4)
col_est1.metric("Media (Promedio)", f"{media:.4f}")
col_est2.metric("Mediana", f"{mediana:.1f}")
col_est3.metric("Moda", f"{moda:.1f}")
col_est4.metric("Desviación Estándar", f"{desviacion:.4f}")

st.info("💡 **Interpretación dinámica:** Observa cómo las métricas centrales (Media, Mediana, Moda) cambian al aislar ataques específicos, lo que demuestra la variabilidad de la reputación en distintos escenarios de amenaza.")

st.markdown("---")

# --- SECCIÓN 13: VISUALIZACIÓN DE DATOS (DASHBOARDS INTEGRADOS) ---
st.subheader("3. Visualización de Patrones de Amenaza")
st.markdown("Análisis avanzado de la infraestructura atacante basado en los filtros seleccionados.")

# Filtramos solo los datos maliciosos para los nuevos gráficos
# Usamos .copy() para poder modificar las fechas sin advertencias de Pandas
df_maliciosos_filt = df_filtrado[df_filtrado['is_malicious'] == 1].copy()

if not df_maliciosos_filt.empty:
    
    # 1. MAPA DE CALOR (GEO) - Concentración de tráfico malicioso
    st.markdown("### 🗺️ Origen Geográfico de las Amenazas")
    df_geo = df_maliciosos_filt.groupby('country').size().reset_index(name='Ataques')
    # Nota: Plotly grafica automáticamente si detecta nombres de países o códigos ISO
    fig_geo = px.choropleth(df_geo, locations="country", locationmode="country names",
                            color="Ataques", hover_name="country", color_continuous_scale="Reds",
                            title="Mapa de Calor: Países con mayor volumen de ataques")
    st.plotly_chart(fig_geo, use_container_width=True)

    # 2. SERIE DE TIEMPO - Detección de picos
    st.markdown("### 📈 Tendencia Temporal")
    # Convertimos la columna 'date' a formato fecha real para ordenarla bien
    df_maliciosos_filt['date'] = pd.to_datetime(df_maliciosos_filt['date'], errors='coerce')
    df_time = df_maliciosos_filt.groupby(df_maliciosos_filt['date'].dt.date).size().reset_index(name='Ataques')
    
    fig_time = px.line(df_time, x='date', y='Ataques', markers=True,
                       title="Serie de Tiempo: Picos de actividad sospechosa por día",
                       labels={'date': 'Fecha del incidente', 'Ataques': 'Número de Amenazas'})
    # Pintamos la línea roja para mantener la temática de "amenaza"
    fig_time.update_traces(line_color='red') 
    st.plotly_chart(fig_time, use_container_width=True)

    # Dividimos la pantalla en dos columnas para los últimos dos gráficos
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        # 3. GRÁFICO DE BARRAS - Tipos de ataque (identificar el problema principal)
        st.markdown("### 🛡️ Vectores de Ataque")
        fig_ataques = px.histogram(df_maliciosos_filt, y="attack_type", color="attack_type", 
                                   orientation='h', title="Distribución por Tipo de Ataque")
        fig_ataques.update_layout(showlegend=False, yaxis_title="Tipo de Ataque", xaxis_title="Conteo")
        st.plotly_chart(fig_ataques, use_container_width=True)

    with col_graf2:
        # 4. TREEMAP - Proveedores de Internet / Infraestructura
        st.markdown("### 🏢 Infraestructura Atacante")
        # Quitamos los nulos para que el mapa se vea limpio
        df_tree = df_maliciosos_filt.dropna(subset=['isp'])
        df_tree_grouped = df_tree.groupby('isp').size().reset_index(name='Ataques')
        
        fig_tree = px.treemap(df_tree_grouped, path=[px.Constant("ISPs"), 'isp'], values='Ataques',
                              title="TreeMap: ISPs que alojan IPs atacantes",
                              color='Ataques', color_continuous_scale="Reds")
        st.plotly_chart(fig_tree, use_container_width=True)

else:
    st.warning("No hay datos de actividad maliciosa para mostrar con los filtros actuales. Intenta cambiar tu selección en la barra lateral.")

# Histograma general comparativo (Benignas vs Maliciosas)
st.markdown("---")
st.markdown("### ⚖️ Comparativa de Reputación (Score AbuseIPDB)")
fig_score = px.histogram(df_filtrado, x="abuseip_score", nbins=20, 
                         color="is_malicious", 
                         labels={"abuseip_score": "Puntaje AbuseIPDB", "is_malicious": "Es Maliciosa"},
                         title="Score de Amenazas Sigilosas vs Benignas")
st.plotly_chart(fig_score, use_container_width=True)