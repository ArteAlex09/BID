import ast
import streamlit as st
from motor_bayesiano import ejecutar_inferencia
# Asegúrate de tener una función que agrupe la consulta a AbuseIPDB e IP-API
from consultas_api import consultar_perfil_completo 

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador de IPs", page_icon="📡", layout="wide")
st.title("📡 Simulador Probabilístico de IPs")

# Proteger la API: La caché guarda la IP analizada por 1 hora
@st.cache_data(ttl=3600)
def obtener_inteligencia_cache(ip):
    # Esta función debe retornar un diccionario con las 8 variables consolidadas
    return consultar_perfil_completo(ip) 

# --- INTERFAZ DEL BUSCADOR ---
st.markdown("Ingresa una dirección IP y ajusta los parámetros del modelo Bayesiano.")

ip_input = st.text_input("Dirección IP a analizar:", placeholder="Ej: 118.25.6.39")

st.markdown("### ⚙️ Parámetros del Modelo Bayesiano")
st.caption("Activa o desactiva las variables para observar su peso específico en la probabilidad matemática.")

# Matriz de interruptores (8 variables en orden)
col1, col2, col3, col4 = st.columns(4)

with col1:
    v_score = st.checkbox("Puntaje de Abuso (Score)", value=True)
    v_usage = st.checkbox("Tipo de Uso", value=True)
with col2:
    v_cats = st.checkbox("Categorías de Ataque", value=True)
    v_users = st.checkbox("Usuarios Distintos (Reportes)", value=True)
with col3:
    v_last = st.checkbox("Última vez reportada", value=True)
    v_country = st.checkbox("País de Origen", value=True)
with col4:
    v_isp = st.checkbox("Proveedor de Internet (ISP)", value=True)
    v_owner = st.checkbox("Propietario de Infraestructura", value=True)

# Mapeo de interruptores a las columnas reales de tu CSV
mapa_variables = {
    'abuseip_score': v_score,
    'usage_type': v_usage,
    'abuseip_categories': v_cats,
    'abuseip_distinct_users': v_users,
    'abuseip_last_reported': v_last,
    'country': v_country,
    'isp': v_isp,
    'infra_owner': v_owner
}

variables_activas = [var for var, activa in mapa_variables.items() if activa]

if st.button("Ejecutar Análisis Dimensional"):
    if not variables_activas:
        st.error("Debes seleccionar al menos una variable para el cálculo Bayesiano.")
    elif ip_input:
        with st.spinner("Correlacionando inteligencia de amenazas con el modelo..."):
            perfil_ip = obtener_inteligencia_cache(ip_input)
            
            if perfil_ip:
                # El frontend delega las matemáticas al motor
                p_m, p_posterior = ejecutar_inferencia(perfil_ip, variables_activas)
                
                # --- RENDERIZADO DE RESULTADOS ---
                st.success("Análisis completado.")
                st.markdown("---")
                
                c1, c2 = st.columns([1, 2])
                
                with c1:
                    st.info("📊 Inferencia Bayesiana")
                    st.metric("Priors $P(M)$", f"{p_m*100:.1f}%")
                    
                    # Mostrar delta visual (cuánto subió o bajó la probabilidad)
                    delta = (p_posterior - p_m) * 100
                    # st.metric("Posterior $P(M|E_1...E_n)$", f"{p_posterior*100:.2f}%", f"{delta:+.1f}% desde la línea base")

                    # Regla de límite asintótico para evitar el 100% absoluto
                    prob_porcentaje = p_posterior * 100
                    if prob_porcentaje > 99.9:
                        texto_prob = "> 99.9%"
                    else:
                        texto_prob = f"{prob_porcentaje:.2f}%"

                    st.metric("Posterior $P(M|E_1...E_n)$", texto_prob, f"{delta:+.1f}% desde la línea base")
                    
                    st.caption(f"Variables activas evaluadas: {len(variables_activas)}")

                with c2:
                    st.warning("🌐 Telemetría Detectada")
                    
                    # 1. DICCIONARIOS DE TRADUCCIÓN (Ajustados a nombres en inglés)
                    CATEGORIAS_ABUSEIP = {
                        '1': 'Compromiso DNS',
                        '2': 'Envenenamiento DNS',
                        '3': 'Fraude',
                        '4': 'DDoS',
                        '5': 'Fuerza Bruta FTP',
                        '6': 'Ping of Death',
                        '7': 'Phishing',
                        '8': 'Fraude VoIP',
                        '9': 'Proxy Abierto',
                        '10': 'Web Spam',
                        '11': 'Email Spam',
                        '12': 'Blog Spam',
                        '13': 'IP de VPN',
                        '14': 'Escaneo de Puertos',
                        '15': 'Hacking',
                        '16': 'Inyección SQL',
                        '17': 'Spoofing',
                        '18': 'Fuerza Bruta',
                        '19': 'Bot Malicioso',
                        '20': 'Host Comprometido',
                        '21': 'Ataque a App Web',
                        '22': 'Ataque SSH',
                        '23': 'Ataque IoT'
                    }

                    TRADUCCION_USO = {
                        'Commercial': 'Comercial',
                        'Content Delivery Network': 'Red de Distribución de Contenido (CDN)',
                        'Data Center/Web Hosting/Transit': 'Data Center / Hosting',
                        'Fixed Line ISP': 'Proveedor de Línea Fija',
                        'Mobile ISP': 'Proveedor de Red Móvil',
                        'Library': 'Biblioteca',
                        'Government': 'Gubernamental',
                        'Education': 'Educativo',
                        'Reserved': 'Reservada (Privada)',
                        'Unknown': 'Desconocido'
                    }

                    # Traducción basada en nombres completos en inglés
                    # Diccionario extendido de traducción de países (Nombres en Inglés -> Español)
                    TRADUCCION_PAISES = {
                        # América
                        'Mexico': 'México 🇲🇽',
                        'United States': 'Estados Unidos 🇺🇸',
                        'Canada': 'Canadá 🇨🇦',
                        'Brazil': 'Brasil 🇧🇷',
                        'Argentina': 'Argentina 🇦🇷',
                        'Colombia': 'Colombia 🇨🇴',
                        'Chile': 'Chile 🇨🇱',
                        'Peru': 'Perú 🇵🇪',
                        'Costa Rica': 'Costa Rica 🇨🇷',
                        'Panama': 'Panamá 🇵🇦',
                        
                        # Europa
                        'Spain': 'España 🇪🇸',
                        'Germany': 'Alemania 🇩🇪',
                        'France': 'Francia 🇫🇷',
                        'United Kingdom': 'Reino Unido 🇬🇧',
                        'Italy': 'Italia 🇮🇹',
                        'Netherlands': 'Países Bajos 🇳🇱',
                        'Russia': 'Rusia 🇷🇺',
                        'Russian Federation': 'Rusia 🇷🇺',
                        'Ukraine': 'Ucrania 🇺🇦',
                        'Poland': 'Polonia 🇵🇱',
                        'Switzerland': 'Suiza 🇨🇭',
                        'Sweden': 'Suecia 🇸🇪',
                        'Norway': 'Noruega 🇳🇴',
                        'Ireland': 'Irlanda 🇮🇪',
                        
                        # Asia y Oceanía
                        'China': 'China 🇨🇳',
                        'Japan': 'Japón 🇯🇵',
                        'Korea (South)': 'Corea del Sur 🇰🇷',
                        'South Korea': 'Corea del Sur 🇰🇷',
                        'India': 'India 🇮🇳',
                        'Singapore': 'Singapur 🇸🇬',
                        'Vietnam': 'Vietnam 🇻🇳',
                        'Taiwan': 'Taiwán 🇹🇼',
                        'Hong Kong': 'Hong Kong 🇭🇰',
                        'Australia': 'Australia 🇦🇺',
                        'New Zealand': 'Nueva Zelanda 🇳🇿',
                        'Thailand': 'Tailandia 🇹🇭',
                        'Indonesia': 'Indonesia 🇮🇩',
                        'Israel': 'Israel 🇮🇱',
                        'Turkey': 'Turquía 🇹🇷',
                        
                        # África y Medio Oriente
                        'South Africa': 'Sudáfrica 🇿🇦',
                        'Egypt': 'Egipto 🇪🇬',
                        'Nigeria': 'Nigeria 🇳🇬',
                        'United Arab Emirates': 'Emiratos Árabes 🇦🇪',
                        'Saudi Arabia': 'Arabia Saudita 🇸🇦'
                    }

                    # 2. RENDERIZADO DE VARIABLES
                    for var in mapa_variables.keys():
                        valor = perfil_ip.get(var, 'N/A')
                        
                        # --- FORMATO DE CATEGORÍAS ---
                        if var == 'abuseip_categories':
                            if valor in ['No_Reports', 'Unknown', 'N/A', '[]']:
                                st.write("**Categorías de Ataque:** Sin reportes")
                            else:
                                try:
                                    lista_ids = ast.literal_eval(valor)
                                    nombres_cat = [CATEGORIAS_ABUSEIP.get(str(cat_id), f"Cat {cat_id}") for cat_id in lista_ids]
                                    with st.expander(f"**Categorías de Ataque ({len(nombres_cat)})**"):
                                        for nombre in nombres_cat:
                                            st.markdown(f"- {nombre}")
                                except:
                                    st.write(f"**Categorías:** {valor}")

                        # --- FORMATO DE FECHA ---
                        elif var == 'abuseip_last_reported':
                            if valor == 'Never_Reported':
                                st.write("**Último Reporte:** Jamás reportada")
                            else:
                                try:
                                    # Formato esperado: "2024-03-20T15:30:00+00:00"
                                    fecha_limpia = valor.split('T')[0] 
                                    ano, mes, dia = fecha_limpia.split('-')
                                    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                                             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                                    st.write(f"**Último Reporte:** {dia} de {meses[int(mes)-1]}, {ano}")
                                except:
                                    st.write(f"**Último Reporte:** {valor}")

                        # --- TRADUCCIÓN DE PAÍS Y USO ---
                        elif var == 'country':
                            # Busca la traducción; si no existe, deja el nombre original en inglés
                            st.write(f"**País de Origen:** {TRADUCCION_PAISES.get(valor, valor)}")
                        
                        elif var == 'usage_type':
                            st.write(f"**Tipo de Uso:** {TRADUCCION_USO.get(valor, valor)}")

                        # --- RESTO DE VARIABLES ---
                        else:
                            # Limpieza de títulos: 'abuseip_score' -> 'Score'
                            titulo = var.replace('abuseip_', '').replace('_', ' ').title()
                            # Traducir específicamente los títulos más comunes
                            titulos_es = {
                                'Score': 'Puntaje de Abuso',
                                'Distinct Users': 'Usuarios que reportaron',
                                'Isp': 'Proveedor (ISP)',
                                'Infra Owner': 'Dueño de Infraestructura'
                            }
                            st.write(f"**{titulos_es.get(titulo, titulo)}:** {valor}")

#######################################################################################         
                # with c2:
                #     st.warning("🌐 Telemetría Detectada")
                    
                #     # Diccionario oficial de categorías de AbuseIPDB
                #     # Diccionario oficial completo de categorías de AbuseIPDB
                    # CATEGORIAS_ABUSEIP = {
                    #     '1': 'Compromiso DNS',
                    #     '2': 'Envenenamiento DNS',
                    #     '3': 'Fraude',
                    #     '4': 'DDoS',
                    #     '5': 'Fuerza Bruta FTP',
                    #     '6': 'Ping of Death',
                    #     '7': 'Phishing',
                    #     '8': 'Fraude VoIP',
                    #     '9': 'Proxy Abierto',
                    #     '10': 'Web Spam',
                    #     '11': 'Email Spam',
                    #     '12': 'Blog Spam',
                    #     '13': 'IP de VPN',
                    #     '14': 'Escaneo de Puertos',
                    #     '15': 'Hacking',
                    #     '16': 'Inyección SQL',
                    #     '17': 'Spoofing',
                    #     '18': 'Fuerza Bruta',
                    #     '19': 'Bot Malicioso',
                    #     '20': 'Host Comprometido',
                    #     '21': 'Ataque a App Web',
                    #     '22': 'Ataque SSH',
                    #     '23': 'Ataque IoT'
                    # }

                #     # Desplegar los datos crudos obtenidos de la API
                #     for var in mapa_variables.keys():
                #         valor = perfil_ip.get(var, 'N/A')
                        
                #         # Interceptar y formatear la variable de categorías
                #         if var == 'abuseip_categories':
                #             if valor in ['No_Reports', 'Unknown', 'N/A', '[]']:
                #                 st.write("**Categorías de Ataque:** Sin reportes")
                #             else:
                #                 try:
                #                     # Convertir el texto "['14', '15']" de vuelta a una lista de Python
                #                     lista_ids = ast.literal_eval(valor)
                                    
                #                     # Traducir los números a nombres
                #                     nombres_cat = [CATEGORIAS_ABUSEIP.get(str(cat_id), f"Categoría {cat_id}") for cat_id in lista_ids]
                                    
                #                     # Mostrar en un menú desplegable elegante
                #                     with st.expander(f"**Categorías de Ataque ({len(nombres_cat)})**"):
                #                         for nombre in nombres_cat:
                #                             st.markdown(f"- {nombre}")
                #                 except Exception as e:
                #                     st.write(f"**Categorías de Ataque:** {valor}")
                        
                #         # Formateo normal para el resto de variables
                        
                #         # Formateo y traducción para el resto de variables
                #         else:
                #             # Diccionario para traducir los títulos de las variables
                #             TRADUCCION_TITULOS = {
                #                 'abuseip_score': 'Puntaje de Abuso (Score)',
                #                 'usage_type': 'Tipo de Uso',
                #                 'abuseip_distinct_users': 'Usuarios Distintos (Reportes)',
                #                 'abuseip_last_reported': 'Última vez reportada',
                #                 'country': 'País de Origen',
                #                 'isp': 'Proveedor de Internet (ISP)',
                #                 'infra_owner': 'Propietario de Infraestructura'
                #             }
                            
                #             # Traducir el título
                #             titulo_espanol = TRADUCCION_TITULOS.get(var, var)
                            
                #             # Traducir valores comunes en inglés que devuelve la API
                #             if valor == 'Never_Reported':
                #                 valor = 'Nunca ha sido reportada'
                #             elif valor == 'No_Reports':
                #                 valor = 'Sin reportes recientes'
                #             elif valor == 'Unknown':
                #                 valor = 'Desconocido'
                #             elif valor == 'Data Center/Web Hosting/Transit':
                #                 valor = 'Data Center / Hosting / Tránsito'
                                
                #             st.write(f"**{titulo_espanol}:** {valor}")
###################################################################################################
                        # else:
                        #     # Pequeña mejora estética para quitar los guiones bajos de los títulos
                        #     titulo_limpio = var.replace('abuseip_', '').replace('_', ' ').title()
                        #     st.write(f"**{titulo_limpio}:** {valor}")

                # with c2:
                #     st.warning("🌐 Telemetría Detectada")
                    
                #     # Diccionario oficial de categorías de AbuseIPDB
                #     CATEGORIAS_ABUSEIP = {
                #         '3': 'Fraude', '4': 'DDoS', '9': 'Proxy Abierto', '10': 'Web Spam', 
                #         '11': 'Email Spam', '14': 'Escaneo de Puertos', '15': 'Hacking', 
                #         '18': 'Fuerza Bruta', '19': 'Bot Malicioso', '20': 'Host Comprometido', 
                #         '21': 'Ataque a App Web', '22': 'Ataque SSH', '23': 'Ataque IoT'
                #     }

                #     # Desplegar los datos crudos obtenidos de la API
                #     for var in mapa_variables.keys():
                #         valor = perfil_ip.get(var, 'N/A')
                        
                #         # Interceptar y formatear la variable de categorías
                #         if var == 'abuseip_categories':
                #             if valor in ['No_Reports', 'Unknown', 'N/A', '[]']:
                #                 st.write("**Categorías de Ataque:** Sin reportes")
                #             else:
                #                 try:
                #                     # Convertir el texto "['14', '15']" de vuelta a una lista de Python
                #                     lista_ids = ast.literal_eval(valor)
                                    
                #                     # Traducir los números a nombres
                #                     nombres_cat = [CATEGORIAS_ABUSEIP.get(str(cat_id), f"Categoría {cat_id}") for cat_id in lista_ids]
                                    
                #                     # Mostrar en un menú desplegable elegante
                #                     with st.expander(f"**Categorías de Ataque ({len(nombres_cat)})**"):
                #                         for nombre in nombres_cat:
                #                             st.markdown(f"- {nombre}")
                #                 except Exception as e:
                #                     st.write(f"**Categorías de Ataque:** {valor}")
                        
                #         # Formateo normal para el resto de variables
                #         else:
                #             # Pequeña mejora estética para quitar los guiones bajos de los títulos
                #             titulo_limpio = var.replace('abuseip_', '').replace('_', ' ').title()
                #             st.write(f"**{titulo_limpio}:** {valor}")

                # with c2:
                #     st.warning("🌐 Telemetría Detectada")
                #     # Desplegar los datos crudos obtenidos de la API
                #     for var in mapa_variables.keys():
                #         valor = perfil_ip.get(var, 'N/A')
                #         st.write(f"**{var}:** {valor}")
