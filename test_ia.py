import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. Cargar entorno
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print("--- INICIANDO TEST DE INFRAESTRUCTURA GEMINI ---")

if not api_key:
    print("❌ ERROR: No se encontró GEMINI_API_KEY en el archivo .env")
    exit()

print(f"🔑 API Key detectada: {api_key[:10]}... (resto oculto por seguridad)")

# 2. Configurar SDK
genai.configure(api_key=api_key)

# 3. Test 1: El modelo moderno (1.5 Flash)
print("\n📡 TEST 1: Conectando a 'gemini-1.5-flash'...")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Responde solo con las palabras: 'Conexión 1.5 exitosa'")
    print(f"✅ ÉXITO 1.5-flash: {response.text}")
except Exception as e:
    print(f"❌ FALLO TEST 1: {str(e)}")
    
    # 4. Test 2: El modelo Legacy (Si el 1 falla, probamos el antiguo)
    print("\n📡 TEST 2: Fallback a modelo legacy 'gemini-pro'...")
    try:
        model_legacy = genai.GenerativeModel('gemini-pro')
        response_legacy = model_legacy.generate_content("Responde solo con: 'Conexión legacy exitosa'")
        print(f"✅ ÉXITO Legacy: {response_legacy.text}")
    except Exception as e2:
         print(f"❌ FALLO TEST 2: {str(e2)}")
         
print("\n--- FIN DEL TEST ---")