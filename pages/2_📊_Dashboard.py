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

# --- SECCIÓN 13: VISUALIZACIÓN DE DATOS ---
st.subheader("3. Visualización de Patrones de Amenaza")

col_graf1, col_graf2 = st.columns(2)

# IMPORTANTE: Reemplazar 'df' por 'df_filtrado' en esta sección
df_maliciosos_filt = df_filtrado[df_filtrado['is_malicious'] == 1]

with col_graf1:
    st.markdown("**Distribución por Tipo de Ataque**")
    if not df_maliciosos_filt.empty:
        fig_ataques = px.histogram(df_maliciosos_filt, y="attack_type", color="attack_type", 
                                   orientation='h')
        fig_ataques.update_layout(showlegend=False)
        st.plotly_chart(fig_ataques, use_container_width=True)
    else:
        st.write("No hay datos maliciosos para mostrar con estos filtros.")

with col_graf2:
    st.markdown("**Infraestructura Comprometida**")
    if not df_maliciosos_filt.empty:
        infra_counts = df_maliciosos_filt['threat_theme'].value_counts().reset_index()
        infra_counts.columns = ['Infraestructura', 'Conteo']
        fig_infra = px.pie(infra_counts, values='Conteo', names='Infraestructura', hole=0.4)
        st.plotly_chart(fig_infra, use_container_width=True)
    else:
        st.write("No hay datos de infraestructura para mostrar.")

st.markdown("**Distribución del Puntaje de Abuso (Histograma)**")
fig_score = px.histogram(df_filtrado, x="abuseip_score", nbins=20, 
                         color="is_malicious", 
                         labels={"abuseip_score": "Puntaje AbuseIPDB", "is_malicious": "Es Maliciosa"},
                         title="Comparativa de Scores: Benignas vs Maliciosas")
st.plotly_chart(fig_score, use_container_width=True)