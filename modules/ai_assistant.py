# modules/ai_assistant.py
import os
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
from typing import Tuple

class AIAssistant:
    """
    Gestor centralizado de IA para PyDuo.
    Arquitectura: Enlace Dinámico Estricto (Strict Auto-Discovery).
    Garantiza 0% de errores 404 al usar solo modelos listados por la API.
    """

    def __init__(self):
        # ── 1. Carga de Credenciales ─────────────────────────────────────────
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "Error Crítico: GEMINI_API_KEY no encontrada en el entorno.\n"
                "Comprueba que tu archivo .env contiene: GEMINI_API_KEY=tu_clave"
            )

        genai.configure(api_key=api_key)

        # ── 2. Configuración Core ────────────────────────────────────────────
        self.generation_config = {
            "temperature": 0.4,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 512,
        }

        self.system_instruction = (
            "Eres PyBot, el tutor de programación de PyDuo. "
            "Responde SIEMPRE en español. Sé paciente y motivador. "
            "NUNCA des la solución completa directamente: guía con pistas y analogías. "
            "Si hay un error en el código, señala la línea problemática pero no la corrijas tú. "
            "Limita las respuestas a 120 palabras máximo."
        )

        # ── 3. Auto-Descubrimiento Estricto de Modelos ───────────────────────
        self.model_name = self._get_valid_model_name()
        
        # ── 4. Instanciación Adaptativa ──────────────────────────────────────
        try:
            # Intento de instanciación moderna (con System Instruction)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config,
                system_instruction=self.system_instruction
            )
            self.is_legacy = False
        except Exception:
            # Fallback si el modelo descubierto es antiguo y no soporta System Instruction
            print(f"⚠️ [Arquitectura AI] El modelo {self.model_name} no soporta personalidad nativa. Modo Legacy activado.")
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config
            )
            self.is_legacy = True

    def _get_valid_model_name(self) -> str:
        """
        Consulta en tiempo real la API de Google y extrae EXACTAMENTE los 
        nombres permitidos para esta API Key específica.
        """
        try:
            # Obtenemos TODOS los modelos a los que tiene acceso tu API KEY
            valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if not valid_models:
                raise Exception("Tu API Key no tiene permisos para modelos de texto.")

            # Prioridad de modelos (si existen en TU lista)
            for preferred in ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]:
                if preferred in valid_models:
                    print(f"🤖 [Arquitectura AI] Modelo óptimo detectado: {preferred}")
                    return preferred
            
            # Si Google cambió todos los nombres, cogemos el primero que funcione
            fallback_model = valid_models[0]
            print(f"🤖 [Arquitectura AI] Usando modelo dinámico de contingencia: {fallback_model}")
            return fallback_model

        except Exception as e:
            raise RuntimeError(f"Fallo crítico al escanear modelos de Google: {str(e)}")

    def ask_question(self, prompt: str, chat_history: list = None) -> Tuple[bool, str]:
        """Ejecuta la consulta manejando inyección de contexto si es necesario."""
        try:
            final_prompt = prompt
            
            # Si estamos en modo Legacy, inyectamos la personalidad manualmente
            if self.is_legacy:
                final_prompt = f"INSTRUCCIONES DEL SISTEMA:\n{self.system_instruction}\n\nMENSAJE DEL USUARIO:\n{prompt}"

            if chat_history:
                chat = self.model.start_chat(history=chat_history[:-1]) 
                response = chat.send_message(final_prompt)
            else:
                response = self.model.generate_content(final_prompt)
                
            return True, response.text

        except GoogleAPIError as e:
            return False, f"Error de la API de Google: {str(e)}"
        except Exception as e:
            return False, f"Error interno de ejecución: {str(e)}"