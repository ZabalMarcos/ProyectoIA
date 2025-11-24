
import google.generativeai as genai
import streamlit as st
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class SQLGenerator:
    """Genera consultas SQL a partir de lenguaje natural"""
    
    def __init__(self):
        self.model = None
        self.api_key = None
        self._load_api_key_from_env()
        
        # Esquema de la base de datos Pubs
        self.pubs_schema = """
        ### ESQUEMA DE LA BASE DE DATOS PUBS ###

        **TABLAS PRINCIPALES:**

        1. **authors**
           - au_id (varchar) - ID único del autor
           - au_lname (varchar) - Apellido
           - au_fname (varchar) - Nombre
           - phone (char) - Teléfono
           - address (varchar) - Dirección
           - city (varchar) - Ciudad
           - state (char) - Estado
           - zip (char) - Código postal
           - contract (bit) - Si tiene contrato

        2. **publishers**
           - pub_id (char) - ID editorial
           - pub_name (varchar) - Nombre editorial
           - city (varchar) - Ciudad
           - state (char) - Estado
           - country (varchar) - País

        3. **titles**
           - title_id (varchar) - ID título
           - title (varchar) - Título libro
           - type (char) - Tipo (business, psychology, etc.)
           - pub_id (char) - ID editorial (FK a publishers)
           - price (money) - Precio
           - advance (money) - Adelanto
           - royalty (int) - Regalías
           - ytd_sales (int) - Ventas año actual
           - notes (varchar) - Notas
           - pubdate (datetime) - Fecha publicación

        4. **titleauthor**
           - au_id (varchar) - ID autor (FK a authors)
           - title_id (varchar) - ID título (FK a titles)
           - au_ord (tinyint) - Orden autor
           - royaltyper (int) - Porcentaje regalías

        5. **sales**
           - stor_id (char) - ID tienda
           - ord_num (varchar) - Número orden
           - ord_date (datetime) - Fecha orden
           - qty (smallint) - Cantidad
           - payterms (varchar) - Términos pago
           - title_id (varchar) - ID título (FK a titles)

        6. **stores**
           - stor_id (char) - ID tienda
           - stor_name (varchar) - Nombre tienda
           - stor_address (varchar) - Dirección
           - city (varchar) - Ciudad
           - state (char) - Estado
           - zip (char) - Código postal

        **RELACIONES:**
        - authors ↔ titleauthor ↔ titles
        - publishers → titles
        - titles → sales → stores
        """
    
    def _load_api_key_from_env(self):
        """Carga la API Key desde el archivo .env"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            api_key = os.getenv('GOOGLE_AI_KEY')
        
        if api_key:
            self.set_api_key(api_key)
    
    def set_api_key(self, api_key: str):
        """Configura la API key y inicializa el modelo"""
        try:
            self.api_key = api_key
            genai.configure(api_key=api_key)
            
            # Intentar obtener un modelo compatible
            self.model = self._get_compatible_model()
            
            if self.model:
                st.sidebar.success("✅ Modelo Gemini configurado")
            else:
                st.sidebar.error("❌ No se pudo inicializar el modelo Gemini")
                
            return True
        except Exception as e:
            st.sidebar.error(f"❌ Error configurando Gemini: {str(e)}")
            return False
    
    def _get_compatible_model(self):
        """Obtiene un modelo compatible"""
        try:
            models = genai.list_models()
            available_models = [model.name for model in models]
            
            # Modelos preferidos en orden de prioridad
            preferred_models = [
                'gemini-1.5-pro',
                'gemini-1.5-flash', 
                'gemini-1.0-pro',
                'gemini-pro'
            ]
            
            # Buscar modelo preferido disponible
            for preferred in preferred_models:
                for available in available_models:
                    if preferred in available:
                        st.sidebar.info(f"🎯 Modelo seleccionado: {available}")
                        return genai.GenerativeModel(available)
            
            # Usar el primer modelo disponible
            if available_models:
                st.sidebar.warning(f"⚡ Usando modelo disponible: {available_models[0]}")
                return genai.GenerativeModel(available_models[0])
            
            return None
        except Exception as e:
            st.sidebar.error(f"Error detectando modelos: {str(e)}")
            return None
    
    def is_configured(self) -> bool:
        """Verifica si el generador está configurado"""
        return self.model is not None and self.api_key is not None
    
    def generate_sql(self, natural_language_query: str) -> str:
        """Genera una consulta SQL a partir de lenguaje natural"""
        if not self.is_configured():
            return "Error: API Key no configurada. Verifica el archivo .env"
        
        prompt = self._create_sql_prompt(natural_language_query)
        
        try:
            response = self.model.generate_content(prompt)
            sql_query = response.text.strip()
            
            # Limpiar la respuesta
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            # Validar SQL básico
            if self._validate_sql(sql_query):
                return sql_query
            else:
                return f"Error: Consulta SQL no válida generada: {sql_query}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _create_sql_prompt(self, user_query: str) -> str:
        """Crea el prompt para generar SQL"""
        return f"""
        Eres un experto en SQL Server y la base de datos Pubs. 
        Convierte la siguiente pregunta en lenguaje natural a una consulta SQL válida para SQL Server.
        
        ESQUEMA DE LA BASE DE DATOS:
        {self.pubs_schema}
        
        REGLAS IMPORTANTES:
        1. Devuelve SOLO el código SQL, sin explicaciones
        2. Usa JOINs cuando sea necesario para relacionar tablas
        3. Incluye los campos relevantes según la pregunta
        4. Usa WHERE para filtrar cuando sea apropiado
        5. Usa ORDER BY para ordenar cuando sea relevante
        6. Usa funciones de agregación (COUNT, SUM, AVG) cuando sea necesario
        7. Asegúrate de que la sintaxis sea válida para SQL Server
        8. No incluyas texto adicional, solo el código SQL
        
        PREGUNTA: {user_query}
        
        SQL:
        """
    
    def _validate_sql(self, sql_query: str) -> bool:
        """Valida sintaxis SQL básica"""
        if not sql_query or sql_query.startswith("Error:"):
            return False
        
        sql_upper = sql_query.upper()
        required_keywords = ["SELECT", "FROM"]
        
        for keyword in required_keywords:
            if keyword not in sql_upper:
                return False
        
        return True