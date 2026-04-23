import streamlit as st
import pandas as pd
from consultas_api import consultar_abuse_ip

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador de IPs", page_icon="📡", layout="wide")
st.title("📡 Analizador Probabilístico de IPs")

# --- LÓGICA DE BAYES (Basado en tu Dataset) ---
@st.cache_data
def cargar_modelo_bayes():
    # 1. Cargar el dataset que armó tu compañero
    df = pd.read_csv("data/BID_dataset.csv") 
    
    # 2. Calcular Probabilidades Base
    total_ips = len(df)
    maliciosas = len(df[df['is_malicious'] == 1])
    benignas = len(df[df['is_malicious'] == 0])
    
    # P(M) y P(~M)
    p_m = maliciosas / total_ips
    p_no_m = benignas / total_ips
    
    # 3. Calcular Likelihoods (Evidencia: Tener un score > 0)
    # P(E|M): Probabilidad de tener score dado que es maliciosa
    p_e_dado_m = len(df[(df['is_malicious'] == 1) & (df['abuseip_score'] > 0)]) / maliciosas
    
    # P(E|~M): Probabilidad de tener score dado que es benigna (Falso Positivo)
    p_e_dado_no_m = len(df[(df['is_malicious'] == 0) & (df['abuseip_score'] > 0)]) / benignas
    
    # P(~E|M): Amenaza sigilosa (Es mala pero no tiene reportes)
    p_no_e_dado_m = 1 - p_e_dado_m
    
    # P(~E|~M): Es buena y no tiene reportes
    p_no_e_dado_no_m = 1 - p_e_dado_no_m

    return p_m, p_no_m, p_e_dado_m, p_e_dado_no_m, p_no_e_dado_m, p_no_e_dado_no_m

# Cargar las variables del modelo
p_m, p_no_m, p_e_dado_m, p_e_dado_no_m, p_no_e_dado_m, p_no_e_dado_no_m = cargar_modelo_bayes()

# --- INTERFAZ DEL BUSCADOR ---
st.markdown("Ingresa una dirección IP para consultar fuentes globales y calcular su probabilidad real de amenaza.")

ip_input = st.text_input("Dirección IP a analizar:", placeholder="Ej: 118.25.6.39")

if st.button("Ejecutar Análisis"):
    if ip_input:
        with st.spinner("Correlacionando datos externos con el modelo bayesiano..."):
            datos_abuse = consultar_abuse_ip(ip_input)
            
            if datos_abuse:
                score_api = datos_abuse['abuseConfidenceScore']
                
                # --- APLICACIÓN DEL TEOREMA DE BAYES ---
                # Si la API dice que hay evidencia (Score > 0)
                if score_api > 0:
                    numerador = p_e_dado_m * p_m
                    denominador = numerador + (p_e_dado_no_m * p_no_m)
                    p_posterior = numerador / denominador
                    evidencia_txt = "IP con reportes previos en la comunidad."
                
                # Si la API dice que NO hay evidencia (Score == 0) - "Amenaza Sigilosa"
                else:
                    numerador = p_no_e_dado_m * p_m
                    denominador = numerador + (p_no_e_dado_no_m * p_no_m)
                    p_posterior = numerador / denominador
                    evidencia_txt = "IP sin reportes, evaluando riesgo residual (Amenaza Sigilosa)."
                
 # --- RENDERIZADO DE RESULTADOS ---
                st.success("Análisis completado exitosamente.")
                
                # Diccionario oficial de AbuseIPDB traducido al español
                categorias_map = {
                    3: "Fraude", 4: "DDoS", 9: "Proxy Abierto", 10: "Web Spam", 
                    11: "Email Spam", 14: "Escaneo de Puertos", 15: "Hacking", 
                    18: "Fuerza Bruta", 19: "Bot Malicioso", 20: "Host Comprometido", 
                    21: "Ataque a App Web", 22: "Ataque SSH", 23: "Ataque IoT"
                }
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.info("📊 Modelo Matemático")
                    st.metric("Probabilidad Previa P(M)", f"{p_m*100:.1f}%")
                    st.metric("Probabilidad Bayesiana P(M|E)", f"{p_posterior*100:.1f}%")
                    st.caption(f"Evidencia: {evidencia_txt}")
                    
                with col2:
                    st.warning("🌐 Inteligencia Externa (API)")
                    st.metric("Confianza de Abuso", f"{score_api}%")
                    st.write(f"**Reportes Totales:** {datos_abuse.get('totalReports', 0)}")
                    st.write(f"**Usuarios Distintos:** {datos_abuse.get('numDistinctUsers', 0)}")
                    
                    # Formatear la fecha para que se vea limpia
                    ultima_vez = datos_abuse.get('lastReportedAt')
                    if ultima_vez: # Verificamos que no sea None ni esté vacío
                        ultima_vez = ultima_vez[:10] + " a las " + ultima_vez[11:16]
                    else:
                        ultima_vez = "Nunca"
                        
                    st.write(f"**Última vez reportada:** {ultima_vez}")
                    
                with col3:
                    st.success("📍 Contexto Geográfico y Técnico")
                    st.write(f"**País:** {datos_abuse.get('countryCode', 'N/A')}")
                    st.write(f"**ISP:** {datos_abuse.get('isp', 'N/A')}")
                    st.write(f"**Tipo de Uso:** {datos_abuse.get('usageType', 'N/A')}")
                    
                    # Extraer y traducir las categorías de los reportes
                    categorias_encontradas = set()
                    if 'reports' in datos_abuse:
                        for reporte in datos_abuse['reports']:
                            for cat in reporte.get('categories', []):
                                categorias_encontradas.add(cat)
                    
                    if categorias_encontradas:
                        # Traducir IDs a nombres, si no está en el dic, mostrar el ID
                        nombres_cat = [categorias_map.get(c, f"Categoría {c}") for c in categorias_encontradas]
                        st.write(f"**Categorías de Ataque:** {', '.join(nombres_cat)}")
                    else:
                        st.write("**Categorías de Ataque:** Ninguna registrada")