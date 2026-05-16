import json
import os
import streamlit as st
from typing import List, Dict, Any

class ExerciseLoader:
    """
    Gestor centralizado para la carga y validación de ejercicios.
    Implementa el patrón de repositorio para aislar la capa de datos de la interfaz de usuario.
    """
    
    @staticmethod
    @st.cache_data(show_spinner=False)
    def load_exercises(filepath: str = "data/exercises.json") -> List[Dict[str, Any]]:
        """
        Carga los ejercicios desde el archivo JSON de forma segura y los cachea en RAM.
        
        Args:
            filepath (str): Ruta relativa al archivo de ejercicios.
            
        Returns:
            List[Dict]: Lista de diccionarios con los datos de cada ejercicio.
            Devuelve una lista vacía si hay un error crítico.
        """
        # 1. Verificación de existencia del archivo en el sistema de ficheros
        if not os.path.exists(filepath):
            st.error(f"❌ Error de Arquitectura: No se encontró la base de datos en '{filepath}'.")
            return []

        try:
            # 2. Lectura segura con manejo de codificación UTF-8 (vital para español)
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # 3. Validación de contrato de datos
                if not isinstance(data, list):
                    st.error("❌ Error de Formato: El archivo JSON debe contener una lista de ejercicios, no un diccionario u otro tipo de dato.")
                    return []
                    
                return data

        except json.JSONDecodeError as e:
            # 4. Manejo granular de errores de formato JSON (comas faltantes, comillas rotas)
            st.error(f"💥 Error crítico de sintaxis en exercises.json (Línea {e.lineno}, Columna {e.colno}).")
            return []
        except Exception as e:
            # Catch-all para errores de I/O
            st.error(f"⚠️ Error inesperado al cargar los datos: {str(e)}")
            return []

    @staticmethod
    def get_exercise_by_id(exercises: List[Dict[str, Any]], exercise_id: int) -> Dict[str, Any]:
        """
        Busca y devuelve un ejercicio específico por su ID.
        Útil para la futura lógica de progreso y gamificación.
        """
        for exercise in exercises:
            if exercise.get("id") == exercise_id:
                return exercise
        return {}