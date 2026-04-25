import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Dashboard Estadístico", page_icon="📊", layout="wide")
st.title("📊 Dashboard de Inteligencia de Amenazas")
st.markdown("Análisis estadístico descriptivo basado en la muestra de infraestructura de red (Mayo 2025 - Enero 2026).")

# ==========================================
# --- DICCIONARIOS GLOBALES ---
# ==========================================
DICCIONARIO_PAISES = {
    "Brazil": "Brasil",
    "United States": "Estados Unidos",
    "China": "China",
    "Russia": "Rusia",
    "France": "Francia",
    "Germany": "Alemania",
    "United Kingdom": "Reino Unido",
    "India": "India",
    "South Korea": "Corea del Sur",
    "Netherlands": "Países Bajos"
}

CATEGORIAS_ABUSEIP = {
    # --- IDs Oficiales Numéricos ---
    '1': 'Compromiso DNS', '2': 'Envenenamiento DNS', '3': 'Fraude',
    '4': 'DDoS', '5': 'Fuerza Bruta FTP', '6': 'Ping of Death',
    '7': 'Phishing', '8': 'Fraude VoIP', '9': 'Proxy Abierto',
    '10': 'Web Spam', '11': 'Email Spam', '12': 'Blog Spam',
    '13': 'IP de VPN', '14': 'Escaneo de Puertos', '15': 'Hacking',
    '16': 'Inyección SQL', '17': 'Spoofing', '18': 'Fuerza Bruta',
    '19': 'Bot Malicioso', '20': 'Host Comprometido', '21': 'Ataque a App Web',
    '22': 'Ataque SSH', '23': 'Ataque IoT',
    
    # --- Etiquetas de Texto Directo (Actualizadas) ---
    "unknown_attack": "Desconocido", 
    "brute_force": "Fuerza Bruta", 
    "port_scan": "Escaneo de Puertos", 
    "ddos": "DDoS", 
    "web_spam": "Spam Web",
    "espionage": "Espionaje",
    "none": "Sin Categoría", 
    "exploit_delivery": "Exploits",
    "phishing": "Phishing",
    "ransomware": "Ransomware"
}

# --- CARGA Y TRANSFORMACIÓN DE DATOS ---
@st.cache_data
def cargar_datos():
    df_raw = pd.read_csv("data/BID_dataset.csv")
    
    # 1. Aplicamos traducciones globales creando columnas nuevas
    df_raw['País_ES'] = df_raw['country'].replace(DICCIONARIO_PAISES)
    
    # Aseguramos que attack_type sea string para que coincida con las llaves del diccionario
    df_raw['Vector_ES'] = df_raw['attack_type'].astype(str).replace(CATEGORIAS_ABUSEIP)
    
    return df_raw

try:
    df = cargar_datos()
except FileNotFoundError:
    st.error("No se encontró el archivo dataset. Verifica que esté en data/BID_dataset.csv")
    st.stop()

# ==========================================
# --- BARRA DE FILTROS (AHORA EN ESPAÑOL) ---
# ==========================================
st.sidebar.header("🔍 Filtros de Análisis")

niveles_amenaza = sorted(df['threat_level'].dropna().unique().tolist())
nivel_seleccionado = st.sidebar.multiselect(
    "Filtrar por Nivel de Amenaza:",
    options=niveles_amenaza,
    default=niveles_amenaza 
)

# Filtro 2: Ahora utilizamos la columna ya traducida (Vector_ES)
tipos_ataque = sorted(df['Vector_ES'].dropna().unique().tolist())
ataque_seleccionado = st.sidebar.multiselect(
    "Filtrar por Tipo de Ataque:",
    options=tipos_ataque,
    default=tipos_ataque
)

# Aplicar filtros
df_filtrado = df[
    (df['threat_level'].isin(nivel_seleccionado)) &
    (df['Vector_ES'].isin(ataque_seleccionado))
]

if df_filtrado.empty:
    st.warning("⚠️ Los filtros seleccionados no arrojaron ningún resultado. Por favor, ajusta tu selección.")
    st.stop() 

# ==========================================
# --- MÉTRICAS PRINCIPALES (KPIs) ---
# ==========================================
st.subheader("1. Resumen de la Muestra (Filtrada)")
col1, col2, col3, col4 = st.columns(4)

total_registros = len(df_filtrado)
maliciosos = len(df_filtrado[df_filtrado['is_malicious'] == 1])
benignos = len(df_filtrado[df_filtrado['is_malicious'] == 0])
tasa_prev = (maliciosos / total_registros) * 100 if total_registros > 0 else 0

col1.metric("Total de Registros", f"{total_registros}")
col2.metric("Infraestructura Benigna", f"{benignos}")
col3.metric("Infraestructura Maliciosa", f"{maliciosos}")
col4.metric("Tasa de Prevalencia P(M)", f"{tasa_prev:.1f}%")

st.markdown("---")

# --- ESTADÍSTICA DESCRIPTIVA ---
st.subheader("2. Estadística Descriptiva (Reputación y Amenaza)")
st.markdown("Análisis de la variable `abuseip_score` según los filtros aplicados.")

media = df_filtrado['abuseip_score'].mean()
mediana = df_filtrado['abuseip_score'].median()
moda_val = df_filtrado['abuseip_score'].mode()
moda = moda_val[0] if not moda_val.empty else 0 
desviacion = df_filtrado['abuseip_score'].std()

col_est1, col_est2, col_est3, col_est4 = st.columns(4)
col_est1.metric("Media (Promedio)", f"{media:.4f}")
col_est2.metric("Mediana", f"{mediana:.1f}")
col_est3.metric("Moda", f"{moda:.1f}")
col_est4.metric("Desviación Estándar", f"{desviacion:.4f}")

st.info("💡 **Interpretación dinámica:** Observa cómo las métricas centrales cambian al aislar ataques específicos, demostrando la variabilidad de la reputación en distintos escenarios.")

st.markdown("---")

# ==========================================
# --- VISUALIZACIÓN DE DATOS ---
# ==========================================
st.subheader("3. Visualización de Patrones de Amenaza")

df_maliciosos_filt = df_filtrado[df_filtrado['is_malicious'] == 1].copy()

if not df_maliciosos_filt.empty:
    
    # 1. MAPA DE CALOR (GEO)
    st.markdown("### 🗺️ Origen Geográfico de las Amenazas")
    
    # Agrupamos conservando ambas columnas de país (Inglés para Plotly, Español para la UI)
    df_geo = df_maliciosos_filt.groupby(['country', 'País_ES']).agg(
        Ataques=('country', 'size'),
        # Ya no necesitamos traducir aquí, solo sacamos la moda de la columna ya traducida
        Vector_Principal=('Vector_ES', lambda x: x.mode()[0] if not x.mode().empty else 'N/A'),
        ISP_Principal=('isp', lambda x: x.mode()[0] if not x.mode().empty else 'N/A')
    ).reset_index()
    
    fig_geo = px.choropleth(
        df_geo, 
        locations="country",          # Inglés (Obligatorio para la geometría del mapa)
        locationmode="country names",
        color="Ataques", 
        hover_name="País_ES",         # Español (Para el título del tooltip)
        custom_data=["Ataques", "Vector_Principal", "ISP_Principal"], 
        color_continuous_scale="Reds"
    )

    fig_geo.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br><br>" +                  
            "Total de Ataques: %{customdata[0]}<br>" +       
            "Vector Frecuente: %{customdata[1]}<br>" +       
            "ISP Atacante: %{customdata[2]}" +               
            "<extra></extra>"                                
        )
    )

    fig_geo.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',  
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_showscale=False      
    )

    fig_geo.update_geos(
        showframe=False, showcoastlines=True,
        coastlinecolor="rgba(127, 127, 127, 0.5)", countrycolor="rgba(127, 127, 127, 0.3)",
        projection_type='natural earth', bgcolor='rgba(0,0,0,0)',       
        showland=True, landcolor='rgba(127, 127, 127, 0.1)' 
    )

    st.plotly_chart(fig_geo, use_container_width=True, theme="streamlit")

    # 2. SERIE DE TIEMPO
    st.markdown("### 📈 Tendencia Temporal")
    df_maliciosos_filt['date'] = pd.to_datetime(df_maliciosos_filt['date'], errors='coerce')
    df_time = df_maliciosos_filt.groupby(df_maliciosos_filt['date'].dt.date).size().reset_index(name='Ataques')
    
    fig_time = px.line(df_time, x='date', y='Ataques', markers=True,
                       title="Serie de Tiempo: Picos de actividad sospechosa por día",
                       labels={'date': 'Fecha del incidente', 'Ataques': 'Número de Amenazas'})
    fig_time.update_traces(line_color='red') 
    st.plotly_chart(fig_time, use_container_width=True)

    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        # 3. GRÁFICO DE BARRAS - Vectores de Ataque
        st.markdown("### 🛡️ Vectores de Ataque")
        fig_ataques = px.histogram(
            df_maliciosos_filt, 
            y="Vector_ES", 
            color="Vector_ES", 
            orientation='h', 
            title="Distribución por Tipo de Ataque"
        )
        
        # --- MAGIA DEL HOVERTEMPLATE (Consistencia Visual SOC) ---
        fig_ataques.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br><br>" +              # Título en negrita (El vector de ataque)
                "Total de Ataques: %{x}" +           # Variable seguida de dos puntos
                "<extra></extra>"                    # Oculta la caja secundaria
            )
        )
        
        # --- DISEÑO LIMPIO Y TRANSPARENCIAS ---
        fig_ataques.update_layout(
            showlegend=False, 
            yaxis_title="Tipo de Ataque", 
            xaxis_title="Conteo",
            paper_bgcolor='rgba(0,0,0,0)',       # Fondo transparente para modo dark/light
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_ataques, use_container_width=True, theme="streamlit")

    with col_graf2:
        # 4. TREEMAP
        st.markdown("### 🏢 Infraestructura Atacante")
        df_tree = df_maliciosos_filt.dropna(subset=['isp'])
        df_tree_grouped = df_tree.groupby('isp').size().reset_index(name='Ataques')
        
        fig_tree = px.treemap(df_tree_grouped, path=[px.Constant("ISPs"), 'isp'], values='Ataques',
                              title="TreeMap: ISPs que alojan IPs atacantes",
                              color='Ataques', color_continuous_scale="Reds")
        st.plotly_chart(fig_tree, use_container_width=True)

else:
    st.warning("No hay datos de actividad maliciosa para mostrar con los filtros actuales.")

st.markdown("---")
st.markdown("### ⚖️ Comparativa de Reputación (Score AbuseIPDB)")
fig_score = px.histogram(df_filtrado, x="abuseip_score", nbins=20, 
                         color="is_malicious", 
                         labels={"abuseip_score": "Puntaje AbuseIPDB", "is_malicious": "Es Maliciosa"},
                         title="Score de Amenazas Sigilosas vs Benignas")
st.plotly_chart(fig_score, use_container_width=True)