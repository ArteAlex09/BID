import requests
import streamlit as st

def consultar_abuse_ip(ip_address):
    # Obtenemos la key de los secretos de Streamlit o variables de entorno
    api_key = st.secrets["ABUSE_IP_KEY"] 
    
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
            return None
    except Exception as e:
        print(f"Error al consultar API: {e}")
        return None

def reportar_ip_abuse(ip, categorias_ids, comentario="Reportado desde BID UdeG"):
    """
    Envía un reporte de IP maliciosa a AbuseIPDB.
    categorias_ids: lista de números (ej: [18, 22])
    """
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
        # ¡Corregido! Ahora usa exactamente el mismo nombre que arriba
        'Key': st.secrets["ABUSE_IP_KEY"] 
    }
    
    try:
        # Nota que aquí usamos requests.post en lugar de requests.get
        response = requests.post(url=url, headers=headers, data=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": True, "mensaje": response.text, "codigo": response.status_code}
    except Exception as e:
        return {"error": True, "mensaje": str(e)}