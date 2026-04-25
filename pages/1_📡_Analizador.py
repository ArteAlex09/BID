import ast
import streamlit as st
from motor_bayesiano import ejecutar_inferencia
from consultas_api import consultar_perfil_completo 

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador de IPs", page_icon="📡", layout="wide")
st.title("📡 Simulador Probabilístico de IPs")

# Proteger la API: La caché guarda la IP analizada por 1 hora
@st.cache_data(ttl=3600)
def obtener_inteligencia_cache(ip):
    return consultar_perfil_completo(ip) 

# --- INTERFAZ DEL BUSCADOR ---
st.markdown("Ingresa una dirección IP y ajusta los parámetros del modelo Bayesiano.")

ip_input = st.text_input("Dirección IP a analizar:", placeholder="Ej: 118.25.6.39")

st.markdown("### ⚙️ Parámetros del Modelo Bayesiano")
st.caption("Activa o desactiva las variables para observar su peso específico en la probabilidad matemática.")

# Matriz de interruptores (8 variables)
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
                p_m, p_posterior = ejecutar_inferencia(perfil_ip, variables_activas)
                
                st.success("Análisis completado.")
                st.markdown("---")
                
                c1, c2 = st.columns([1, 2])
                
                with c1:
                    st.info("📊 Inferencia Bayesiana")
                    st.metric("Priors $P(M)$", f"{p_m*100:.1f}%")
                    
                    delta = (p_posterior - p_m) * 100
                    prob_porcentaje = p_posterior * 100
                    texto_prob = "> 99.9%" if prob_porcentaje > 99.9 else f"{prob_porcentaje:.2f}%"

                    st.metric("Posterior $P(M|E_1...E_n)$", texto_prob, f"{delta:+.1f}% desde la línea base")
                    st.caption(f"Variables activas evaluadas: {len(variables_activas)}")

                with c2:
                    st.warning("🌐 Telemetría Detectada")
                    
                    # --- DICCIONARIOS DE TRADUCCIÓN ---
                    CATEGORIAS_ABUSEIP = {
                        '1': 'Compromiso DNS', '2': 'Envenenamiento DNS', '3': 'Fraude',
                        '4': 'DDoS', '5': 'Fuerza Bruta FTP', '6': 'Ping of Death',
                        '7': 'Phishing', '8': 'Fraude VoIP', '9': 'Proxy Abierto',
                        '10': 'Web Spam', '11': 'Email Spam', '12': 'Blog Spam',
                        '13': 'IP de VPN', '14': 'Escaneo de Puertos', '15': 'Hacking',
                        '16': 'Inyección SQL', '17': 'Spoofing', '18': 'Fuerza Bruta',
                        '19': 'Bot Malicioso', '20': 'Host Comprometido', '21': 'Ataque a App Web',
                        '22': 'Ataque SSH', '23': 'Ataque IoT'
                    }

                    TRADUCCION_USO = {
                        'Commercial': 'Comercial',
                        'Content Delivery Network': 'Red de Distribución de Contenido (CDN)',
                        'Data Center/Web Hosting/Transit': 'Data Center / Hosting',
                        'Fixed Line ISP': 'Proveedor de Línea Fija',
                        'Mobile ISP': 'Proveedor de Red Móvil',
                        'Reserved': 'Reservada (Privada)',
                        'Unknown': 'Desconocido'
                    }

                    # Diccionario con Tuplas: (Nombre en Español, Código ISO para la bandera)
                    TRADUCCION_PAISES = {
                        'Mexico': ('México', 'mx'),
                        'United States': ('Estados Unidos', 'us'),
                        'Canada': ('Canadá', 'ca'),
                        'Brazil': ('Brasil', 'br'),
                        'Argentina': ('Argentina', 'ar'),
                        'Colombia': ('Colombia', 'co'),
                        'Chile': ('Chile', 'cl'),
                        'Spain': ('España', 'es'),
                        'Germany': ('Alemania', 'de'),
                        'France': ('Francia', 'fr'),
                        'United Kingdom': ('Reino Unido', 'gb'),
                        'China': ('China', 'cn'),
                        'Japan': ('Japón', 'jp'),
                        'Russia': ('Rusia', 'ru'),
                        'Russian Federation': ('Rusia', 'ru'),
                        'South Korea': ('Corea del Sur', 'kr'),
                        'Netherlands': ('Países Bajos', 'nl'),
                        'India': ('India', 'in')
                    }

                    for var in mapa_variables.keys():
                        valor = perfil_ip.get(var, 'N/A')
                        
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

                        elif var == 'abuseip_last_reported':
                            if valor == 'Never_Reported':
                                st.write("**Último Reporte:** Jamás reportada")
                            else:
                                try:
                                    fecha_limpia = valor.split('T')[0] 
                                    ano, mes, dia = fecha_limpia.split('-')
                                    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                                             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                                    st.write(f"**Último Reporte:** {dia} de {meses[int(mes)-1]}, {ano}")
                                except:
                                    st.write(f"**Último Reporte:** {valor}")

                        elif var == 'country':
                            datos_pais = TRADUCCION_PAISES.get(valor)
                            if datos_pais:
                                nombre_es, iso = datos_pais
                                # Inyección de bandera mediante HTML para compatibilidad con Windows
                                bandera_url = f"https://flagcdn.com/24x18/{iso}.png"
                                st.markdown(
                                    f"**País de Origen:** {nombre_es} "
                                    f"<img src='{bandera_url}' width='20' style='vertical-align: middle; margin-left: 5px;'>", 
                                    unsafe_allow_html=True
                                )
                            else:
                                st.write(f"**País de Origen:** {valor}")
                        
                        elif var == 'usage_type':
                            st.write(f"**Tipo de Uso:** {TRADUCCION_USO.get(valor, valor)}")

                        else:
                            titulo = var.replace('abuseip_', '').replace('_', ' ').title()
                            titulos_es = {
                                'Score': 'Puntaje de Abuso',
                                'Distinct Users': 'Usuarios que reportaron',
                                'Isp': 'Proveedor (ISP)',
                                'Infra Owner': 'Dueño de Infraestructura'
                            }
                            st.write(f"**{titulos_es.get(titulo, titulo)}:** {valor}")