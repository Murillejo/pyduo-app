import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("--- BUSCANDO MODELOS DISPONIBLES PARA TU CLAVE ---")
try:
    models = genai.list_models()
    count = 0
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ MODELO ENCONTRADO: {m.name}")
            count += 1
    if count == 0:
        print("❌ Tu clave no tiene acceso a modelos de generación.")
except Exception as e:
    print(f"❌ Error de conexión: {e}")