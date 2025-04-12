# -*- coding: utf-8 -*-
"""
Script para probar que todas las dependencias estén instaladas correctamente
"""

def test_dependencies():
    """Prueba que todas las dependencias estén instaladas correctamente"""
    try:
        # Dependencias principales
        import ccxt
        import pandas as pd
        import numpy as np
        import plotly
        from dotenv import load_dotenv
        
        # Visualización y UI
        import streamlit
        
        # Telegram
        import telegram
        
        # Utilidades
        import requests
        from dateutil import parser
        import pytz
        
        print("✅ Todas las dependencias están instaladas correctamente")
        return True
        
    except ImportError as e:
        print(f"❌ Error: {str(e)}")
        print("Por favor, instala las dependencias faltantes usando:")
        print("pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    test_dependencies() 