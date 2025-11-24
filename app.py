import streamlit as st
from chat_interface import ChatInterface
from sql_generator import SQLGenerator
from database_client import DatabaseClient
from dotenv import load_dotenv
import os

load_dotenv()

class PubsSQLChatApp:
    """Aplicación principal del ChatBot SQL para Pubs"""
    
    def __init__(self):
        self.chat_interface = ChatInterface()
        self.sql_generator = SQLGenerator()
        self.db_client = DatabaseClient()
        self._initialize_components()
        
    def _initialize_components(self):
        """Inicializa los componentes con las configuraciones del .env"""
        # Cargar API Key desde .env
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            self.sql_generator.set_api_key(api_key)
        
        # Cargar conexión a BD desde .env
        db_connection = os.getenv('DB_CONNECTION_STRING')
        if db_connection:
            self.db_client.set_connection_string(db_connection)
    
    def setup_sidebar(self):
        """Configura la barra lateral"""
        st.sidebar.title("🍺 Pubs SQL Chat")
        
        # Información de configuración
        st.sidebar.subheader("🔧 Configuración")
        
        # Estado de la API Key
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            st.sidebar.success("✅ API Key cargada desde .env")
            st.sidebar.info(f"Clave: {api_key[:8]}...{api_key[-4:]}")
        else:
            st.sidebar.error("❌ No se encontró GOOGLE_API_KEY en .env")
            # Opción para ingresar manualmente
            api_key_manual = st.sidebar.text_input(
                "Google AI API Key (manual):",
                type="password",
                help="Si no está en .env, ingrésala manualmente"
            )
            if api_key_manual:
                self.sql_generator.set_api_key(api_key_manual)
        
        # Estado de la conexión a BD
        db_connection = os.getenv('DB_CONNECTION_STRING')
        if db_connection:
            st.sidebar.success("✅ Conexión BD cargada desde .env")
        else:
            st.sidebar.warning("⚠️ No se encontró DB_CONNECTION_STRING en .env")
            db_connection_manual = st.sidebar.text_input(
                "Cadena de conexión (manual):",
                placeholder="DRIVER={SQL Server};SERVER=...",
                help="Si no está en .env, ingrésala manualmente"
            )
            if db_connection_manual:
                self.db_client.set_connection_string(db_connection_manual)
        
        # Información del archivo .env
        with st.sidebar.expander("📁 Configuración .env"):
            st.code("""
# Contenido esperado del archivo .env:
GOOGLE_API_KEY=AIzaSyD-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxptn8
DB_CONNECTION_STRING=DRIVER={SQL Server};SERVER=servidor;DATABASE=pubs;
            """)
            st.info("El archivo .env debe estar en la misma carpeta que app.py")
        
        # Estadísticas
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Estadísticas")
        self.chat_interface.display_chat_stats()
        
        # Acciones
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔧 Acciones")
        
        if st.sidebar.button("🗑️ Limpiar Historial", use_container_width=True):
            self.chat_interface.clear_chat()
        
        # Exportar chat
        export_data = self.chat_interface.export_chat()
        st.sidebar.download_button(
            label="💾 Exportar Chat",
            data=export_data,
            file_name=f"pubs_chat_export.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        # Ejemplos rápidos
        st.sidebar.markdown("---")
        st.sidebar.subheader("💡 Ejemplos Rápidos")
        ejemplos = [
            "Autores de California",
            "Libros de negocios",
            "Top 5 libros más vendidos",
            "Autores con contrato",
            "Ventas por tienda"
        ]
        
        for ejemplo in ejemplos:
            if st.sidebar.button(f"💬 {ejemplo}", key=f"ex_{hash(ejemplo)}", use_container_width=True):
                # Usar el método de entrada del usuario directamente
                self.process_user_input(ejemplo)
    
    def process_user_input(self, user_input: str):
        """Procesa la entrada del usuario y genera respuesta"""
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Añadir al historial
        self.chat_interface.add_message("user", user_input)
        
        # Generar respuesta
        if self.sql_generator.is_configured():
            with st.chat_message("assistant"):
                with st.spinner("🤖 Generando consulta SQL..."):
                    # Generar SQL
                    sql_query = self.sql_generator.generate_sql(user_input)
                    
                    if sql_query and not sql_query.startswith("Error:"):
                        # Mostrar SQL
                        st.markdown("**Consulta SQL generada:**")
                        st.code(sql_query, language="sql")
                        
                        # Añadir al historial
                        self.chat_interface.add_message("assistant", f"Consulta SQL generada:\n```sql\n{sql_query}\n```")
                        
                        # Opción para ejecutar la consulta
                        if self.db_client.is_configured():
                            if st.button("🚀 Ejecutar Consulta", key=f"run_{len(st.session_state.messages)}"):
                                with st.spinner("Ejecutando consulta en la base de datos..."):
                                    results = self.db_client.execute_query(sql_query)
                                    if results is not None:
                                        st.markdown("**Resultados:**")
                                        st.dataframe(results)
                                        
                                        # Añadir resultados al historial
                                        results_text = f"Resultados ({len(results)} filas, {len(results.columns)} columnas):\n"
                                        results_text += results.to_string(max_rows=10)
                                        self.chat_interface.add_message("assistant", results_text)
                    else:
                        st.error(f"❌ Error generando SQL: {sql_query}")
                        self.chat_interface.add_message("assistant", f"Error: {sql_query}")
        else:
            with st.chat_message("assistant"):
                error_msg = "❌ Por favor, configura tu API Key de Google AI en el archivo .env"
                st.error(error_msg)
                self.chat_interface.add_message("assistant", error_msg)
    
    def run(self):
        """Ejecuta la aplicación principal"""
        st.title("💬 Pubs SQL Chat Assistant")
        st.markdown("""
        Chatea con la IA para generar consultas SQL para la base de datos **Pubs**. 
        Escribe tu pregunta en lenguaje natural y obtén la consulta SQL correspondiente.
        
        **Configuración automática desde .env:**
        - ✅ API Key de Google AI
        - ✅ Conexión a base de datos
        """)
        
        # Configurar sidebar
        self.setup_sidebar()
        
        # Mostrar historial de mensajes
        self.chat_interface.display_messages()
        
        # Manejar entrada del usuario desde chat input
        if user_input := st.chat_input("Escribe tu pregunta sobre la base de datos Pubs..."):
            self.process_user_input(user_input)

if __name__ == "__main__":
    app = PubsSQLChatApp()
    app.run()