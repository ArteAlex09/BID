import streamlit as st
import pandas as pd
from consultas_api import consultar_abuse_ip

# 1. Configuración de la página
st.set_page_config(page_title="BID - Inteligencia Estadística", page_icon="🛡️")

st.title("🛡️ Inteligencia Estadística de IPs Maliciosas")
st.markdown("""
Este portal calcula la probabilidad de que una IP sea una amenaza utilizando el **Teorema de Bayes** y compara los resultados con fuentes globales como **AbuseIPDB**.
""")

# 2. Barra de búsqueda
ip_input = st.text_input("Ingresa la dirección IP a consultar:", placeholder="Ej: 118.25.6.39")

# 3. Lógica del Botón (Unificado)
if st.button("Analizar IP"):
    if ip_input:
        st.info(f"Iniciando análisis de: {ip_input}")
        
        with st.spinner("Consultando bases de datos globales..."):
            # Llamada a la función que configuramos en consultas_api.py
            datos_abuse = consultar_abuse_ip(ip_input)
            
            if datos_abuse:
                st.success("¡Análisis de fuentes externas completado!")
                
                # Creamos las columnas para mostrar resultados
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Modelo Probabilístico")
                    # Placeholder para cuando programemos Bayes
                    st.metric(label="Probabilidad Bayesiana", value="Pendiente", help="Cálculo basado en datasets locales")
                    
                    # Mostramos el score de la API como referencia
                    score = datos_abuse['abuseConfidenceScore']
                    st.metric(label="Confianza de Abuso (AbuseIPDB)", value=f"{score}%")
                    st.progress(score / 100)
                
                with col2:
                    st.subheader("Detalles de la IP (API)")
                    st.write(f"**País:** {datos_abuse.get('countryCode', 'N/A')}")
                    st.write(f"**ISP:** {datos_abuse.get('isp', 'N/A')}")
                    st.write(f"**Total Reportes:** {datos_abuse.get('totalReports', 0)}")
                    st.write(f"**Último Reporte:** {datos_abuse.get('lastReportedAt', 'N/A')}")
            else:
                st.error("No se pudo obtener información. Verifica tu API Key o la conexión.")
    else:
        st.warning("Por favor, ingresa una IP válida antes de analizar.")