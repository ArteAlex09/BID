import requests
import streamlit as st
import os

def obtener_api_key():
    """
    Intenta obtener la llave desde las variables de entorno (Docker/.env).
    Si no está ahí, busca en la configuración local de Streamlit (.toml).
    """
    return os.getenv("ABUSE_IP_KEY") or st.secrets.get("ABUSE_IP_KEY")

def consultar_abuse_ip(ip_address):
    api_key = obtener_api_key()
    
    # Validación de seguridad antes de hacer la petición
    if not api_key:
        st.error("⚠️ Error crítico: La API Key de AbuseIPDB no está configurada.")
        return None
        
    url = 'https://api.abuseipdb.com/api/v2/check'
    
    params = {
        'ipAddress': ip_address,
        'maxAgeInDays': '90',
        'verbose': True
    }
    
    headers = {
        'Accept': 'application/json',
        'Key': api_key
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()['data']
        else:
            # Es útil imprimir el código de error para depurar si la API rechaza la petición
            print(f"La API respondió con código: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error al consultar API: {e}")
        return None

def reportar_ip_abuse(ip, categorias_ids, comentario="Reportado desde BID UdeG"):
    """
    Envía un reporte de IP maliciosa a AbuseIPDB.
    categorias_ids: lista de números (ej: [18, 22])
    """
    api_key = obtener_api_key()
    
    if not api_key:
        return {"error": True, "mensaje": "API Key no configurada", "codigo": 500}

    url = 'https://api.abuseipdb.com/api/v2/report'
    
    # AbuseIPDB pide que las categorías sean un string separado por comas: "18,22"
    categorias_str = ",".join(map(str, categorias_ids))
    
    params = {
        'ip': ip,
        'categories': categorias_str,
        'comment': comentario
    }
    
    headers = {
        'Accept': 'application/json',
        'Key': api_key
    }
    
    try:
        response = requests.post(url=url, headers=headers, data=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": True, "mensaje": response.text, "codigo": response.status_code}
    except Exception as e:
        return {"error": True, "mensaje": str(e)}

import requests

def consultar_perfil_completo(ip):
    """
    Consolida la telemetría de AbuseIPDB e IP-API en un solo diccionario 
    con las llaves exactas que requiere el Motor Bayesiano.
    """
    # 1. Consulta de reputación (Usando la función que ya tienes programada)
    # Asumimos que consultar_abuse_ip(ip) está definida más arriba en este mismo archivo
    datos_abuse = consultar_abuse_ip(ip)
    
    # Si la IP es inválida, privada, o falla la API de AbuseIPDB, abortamos
    if not datos_abuse:
        return None
        
    # 2. Consulta Geográfica y Organizacional (IP-API)
    # Para el simulador en tiempo real es mejor una petición individual que por lotes
    try:
        url_ip_api = f"http://ip-api.com/json/{ip}?fields=status,message,country,isp,org"
        respuesta_geo = requests.get(url_ip_api, timeout=5)
        if respuesta_geo.status_code == 200:
            datos_geo = respuesta_geo.json()
        else:
            datos_geo = {}
    except requests.exceptions.RequestException:
        datos_geo = {}

    # 3. Empaquetado de Datos
    # Extraemos las categorías de todos los reportes y las guardamos como texto
    categorias_encontradas = set()
    for reporte in datos_abuse.get('reports', []):
        for cat in reporte.get('categories', []):
            categorias_encontradas.add(str(cat))
    
    # Formateamos la fecha para evitar errores de tipo nulo
    fecha_reporte = datos_abuse.get('lastReportedAt')
    if not fecha_reporte:
        fecha_reporte = 'Unknown'

    # Construimos el diccionario con las llaves que espera motor_bayesiano.py
    perfil_consolidado = {
        'abuseip_score': str(datos_abuse.get('abuseConfidenceScore', '0')),
        'usage_type': str(datos_abuse.get('usageType', 'Unknown')),
        # Alineación estricta con tu CSV:
        'abuseip_categories': str(list(categorias_encontradas)) if categorias_encontradas else 'No_Reports',
        'abuseip_distinct_users': str(datos_abuse.get('numDistinctUsers', '0')),
        'abuseip_last_reported': fecha_reporte if fecha_reporte != 'Unknown' else 'Never_Reported',
        'country': str(datos_geo.get('country', 'Unknown')),
        'isp': str(datos_geo.get('isp', 'Unknown')),
        'infra_owner': str(datos_geo.get('org', 'Unknown'))
    # }

    # # Construimos el diccionario con las llaves que espera motor_bayesiano.py
    # perfil_consolidado = {
    #     'abuseip_score': str(datos_abuse.get('abuseConfidenceScore', '0')),
    #     'usage_type': str(datos_abuse.get('usageType', 'Unknown')),
    #     'abuseip_categories': str(list(categorias_encontradas)) if categorias_encontradas else 'Unknown',
    #     'abuseip_distinct_users': str(datos_abuse.get('numDistinctUsers', '0')),
    #     'abuseip_last_reported': fecha_reporte,
    #     'country': str(datos_geo.get('country', 'Unknown')),
    #     'isp': str(datos_geo.get('isp', 'Unknown')),
    #     'infra_owner': str(datos_geo.get('org', 'Unknown'))
    }
    
    return perfil_consolidado
