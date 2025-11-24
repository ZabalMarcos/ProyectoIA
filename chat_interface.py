import streamlit as st
from datetime import datetime

class ChatInterface:
    """Gestiona la interfaz del chat para Pubs SQL"""
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Inicializar el estado de sesión"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
    
    def add_message(self, role: str, content: str):
        """Añade un mensaje al historial"""
        st.session_state.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def display_messages(self):
        """Muestra todos los mensajes del chat"""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                # Si el mensaje contiene código SQL, formatearlo adecuadamente
                if "```sql" in message["content"]:
                    # Extraer y mostrar el SQL con formato
                    parts = message["content"].split("```sql")
                    if len(parts) > 1:
                        sql_part = parts[1].split("```")[0]
                        text_part = parts[0]
                        
                        if text_part.strip():
                            st.markdown(text_part)
                        st.code(sql_part, language="sql")
                    else:
                        st.markdown(message["content"])
                else:
                    st.markdown(message["content"])
    
    def display_chat_stats(self):
        """Muestra estadísticas en la barra de estado"""
        total_messages = len(st.session_state.messages)
        user_messages = len([m for m in st.session_state.messages if m['role'] == "user"])
        
        st.metric("💬 Mensajes Totales", total_messages)
        st.metric("❓ Preguntas Realizadas", user_messages)
        
        # Mostrar ejemplos rápidos
        if total_messages == 0:
            st.markdown("---")
            st.markdown("**💡 Ejemplos:**")
            examples = [
                "Autores de California",
                "Libros de negocios", 
                "Top 5 libros más vendidos",
                "Autores con contrato"
            ]
            for example in examples:
                if st.button(f"💬 {example}", key=f"ex_{example}", use_container_width=True):
                    st.session_state.quick_example = example
    
    def clear_chat(self):
        """Limpia el historial del chat"""
        st.session_state.messages = []
        st.rerun()
    
    def export_chat(self):
        """Exporta el historial del chat"""
        if not st.session_state.messages:
            return "No hay mensajes para exportar"
        
        export_text = "# Historial de Chat - Pubs SQL Assistant\n\n"
        export_text += f"Exportado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for i, message in enumerate(st.session_state.messages):
            role_icon = "👤" if message["role"] == "user" else "🤖"
            role_text = "Usuario" if message["role"] == "user" else "Assistant"
            
            export_text += f"## {role_icon} {role_text} - Mensaje {i+1}\n\n"
            export_text += f"{message['content']}\n\n"
            export_text += "---\n\n"
        
        return export_text