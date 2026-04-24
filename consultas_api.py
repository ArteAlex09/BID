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
