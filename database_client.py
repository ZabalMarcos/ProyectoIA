import pandas as pd
import pyodbc
import streamlit as st
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseClient:
    """Cliente para ejecutar consultas en la base de datos"""
    
    def __init__(self):
        self.connection_string = None
        self._load_connection_from_env()
    
    def _load_connection_from_env(self):
        """Carga la cadena de conexión desde el archivo .env"""
        connection_string = os.getenv('DB_CONNECTION_STRING')
        if connection_string:
            self.set_connection_string(connection_string)
    
    def set_connection_string(self, connection_string: str):
        """Configura la cadena de conexión"""
        self.connection_string = connection_string
        if self.test_connection():
            st.sidebar.success("✅ Conexión a BD configurada y probada")
        else:
            st.sidebar.error("❌ No se pudo conectar a la base de datos")
    
    def is_configured(self) -> bool:
        """Verifica si el cliente está configurado"""
        return self.connection_string is not None and len(self.connection_string) > 0
    
    def execute_query(self, sql_query: str) -> Optional[pd.DataFrame]:
        """Ejecuta una consulta SQL y devuelve los resultados"""
        if not self.is_configured():
            st.error("❌ Cadena de conexión no configurada. Verifica el archivo .env")
            return None
        
        try:
            conn = pyodbc.connect(self.connection_string)
            df = pd.read_sql_query(sql_query, conn)
            conn.close()
            
            st.success(f"✅ Consulta ejecutada: {len(df)} filas obtenidas")
            return df
            
        except Exception as e:
            st.error(f"❌ Error ejecutando consulta: {str(e)}")
            return None
    
    def test_connection(self) -> bool:
        """Prueba la conexión a la base de datos"""
        if not self.is_configured():
            return False
        
        try:
            conn = pyodbc.connect(self.connection_string)
            conn.close()
            return True
        except Exception as e:
            st.sidebar.error(f"❌ Error de conexión: {str(e)}")
            return False