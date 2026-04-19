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