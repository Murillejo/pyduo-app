"""
PyDuo — Plataforma educativa de Python
Arquitectura: UI Moderna + BD Local + Content Gating + Tutor IA
"""
import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

# ── 1. Carga del entorno ──────────────────────────────────────────────────────
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# ── 2. Módulos Core ───────────────────────────────────────────────────────────
from modules.execution import CodeEvaluator
from modules.ai_assistant import AIAssistant
from modules.auth import AuthManager
from database.db_setup import SessionLocal
from database.models import Progress

# Importación del IDE con colores (requiere: pip install streamlit-ace)
try:
    from st_ace import st_ace
    HAS_ACE = True
except ImportError:
    HAS_ACE = False

# ── 3. Configuración de página y CSS ──────────────────────────────────────────
st.set_page_config(page_title="PyDuo - Aprende Python", page_icon="🐍", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0d0f14; color: #e8e4d9; }
[data-testid="stSidebar"] { background: #12141a !important; border-right: 1px solid #1e2230 !important; }
[data-testid="stSidebar"] * { color: #e8e4d9 !important; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, #a8c4ff, #7affb4) !important; color: #0d0f14 !important; border: none !important; font-weight: 700 !important; transition: opacity 0.2s; }
.stButton > button[kind="primary"]:hover { opacity: 0.85 !important; }
.stTextArea textarea { background: #0a0c10 !important; color: #a8ff8c !important; font-family: 'Space Mono', monospace !important; border-radius: 10px !important; border: 1px solid #1e2230 !important; }
.stTextArea textarea:focus { border-color: #a8c4ff !important; box-shadow: none !important; }
.contexto-box { background: #12141a; border: 1px solid #1e2230; border-left: 3px solid #a8c4ff; border-radius: 10px; padding: 1.1rem; margin-bottom: 1rem; }

/* Resaltado visual para comandos (ej. `print`, `pprint`) dentro de la explicación */
.contexto-box code { 
    color: #ff79c6 !important; 
    font-weight: 700 !important; 
    background: #282a36 !important; 
    padding: 3px 6px !important; 
    border-radius: 5px !important; 
    border: 1px solid #ff79c640 !important; 
    font-size: 0.9rem !important;
}

.pyduo-logo { font-family: 'Space Mono', monospace; font-size: 1.5rem; font-weight: 700; color: #a8c4ff; text-align: center; margin-bottom: 1rem; }
.pyduo-logo span { color: #7affb4; }
.badge { display: inline-block; font-family: 'Space Mono', monospace; font-size: 0.62rem; padding: 2px 10px; border-radius: 99px; text-transform: uppercase; margin-left: 8px; border: 1px solid #1a4a2e; background: #0a1f15; color: #7affb4; }
[data-testid="stChatMessage"] { background: #12141a !important; border: 1px solid #1e2230 !important; border-radius: 10px !important; margin-bottom: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── 4. Inicialización de Servicios y Datos ────────────────────────────────────
@st.cache_resource
def init_ai():
    try: 
        return AIAssistant()
    except Exception as e: 
        print("Error IA:", e)
        return None

ai_service = init_ai()

def get_db_session():
    return SessionLocal()

try:
    from modules.data_loader import ExerciseLoader
    exercises = ExerciseLoader.load_exercises()
    if not exercises: raise ValueError("Lista vacía")
except Exception as e:
    exercises = [{"id": 1, "titulo": "Error de Datos", "contexto": "No se pudieron cargar los ejercicios.", "codigo_inicial": "# Revisa tu exercises.json", "test": "assert False"}]

# ── 5. Gestión Robusta de Estado (SESSION STATE) ──────────────────────────────
if "user" not in st.session_state: st.session_state.user = None
if "current_ex_index" not in st.session_state: st.session_state.current_ex_index = 0
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "gemini_history" not in st.session_state: st.session_state.gemini_history = []
if "last_result" not in st.session_state: st.session_state.last_result = None
if "editor_code" not in st.session_state: st.session_state.editor_code = exercises[0].get("codigo_inicial", "")

# ── 6. Lógica de Autenticación ────────────────────────────────────────────────
if st.session_state.user is None:
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="pyduo-logo" style="font-size: 3rem; margin-top: 5rem;">Py<span>Duo</span></div>', unsafe_allow_html=True)
        t_log, t_reg = st.tabs(["🔐 Login", "📝 Registro"])
        db = get_db_session()
        
        with t_log:
            with st.form("f_log"):
                u = st.text_input("Usuario")
                p = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Entrar", use_container_width=True):
                    user = AuthManager.authenticate_user(db, u, p)
                    if user:
                        st.session_state.user = {"id": user.id, "username": user.username, "xp": user.xp, "level": user.level}
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas")
        with t_reg:
            with st.form("f_reg"):
                u = st.text_input("Nuevo Usuario")
                p = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Registrar", use_container_width=True):
                    try: 
                        AuthManager.create_user(db, u, p)
                        st.success("Cuenta lista. ¡Inicia sesión!")
                    except Exception as e: 
                        st.error(str(e))
        db.close()
    st.stop()

# ── 7. Plataforma Principal (Sidebar) ─────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="pyduo-logo">Py<span>Duo</span></div>', unsafe_allow_html=True)
    st.markdown("👤 **" + str(st.session_state.user['username']) + "** | Nivel " + str(st.session_state.user['level']))
    st.progress((st.session_state.user['xp'] % 100) / 100.0)
    st.caption("⭐ " + str(st.session_state.user['xp']) + " XP totales")
    st.divider()
    
    db = get_db_session()
    resueltos = [e[0] for e in db.query(Progress.exercise_id).filter(Progress.user_id == st.session_state.user['id']).all()]
    db.close()

    opciones = []
    permitidos = []
    
    for i, ex in enumerate(exercises):
        ex_id = ex.get('id', i+1)
        if ex_id in resueltos: 
            icon, can = "✅", True
        elif i == 0 or (exercises[i-1].get('id', i) in resueltos): 
            icon, can = "▶️", True
        else: 
            icon, can = "🔒", False
            
        opciones.append(icon + " " + str(ex_id) + ". " + str(ex.get('titulo')))
        if can: permitidos.append(i)

    sel = st.selectbox("Mapa de Retos:", opciones, index=st.session_state.current_ex_index)
    idx = opciones.index(sel)
    
    if idx != st.session_state.current_ex_index:
        if idx in permitidos:
            st.session_state.current_ex_index = idx
            st.session_state.editor_code = exercises[idx].get("codigo_inicial", "")
            st.session_state.chat_history = []
            st.session_state.gemini_history = []
            st.session_state.last_result = None
            st.rerun()
        else: 
            st.sidebar.error("Desbloquea el nivel anterior primero.")

    st.divider()
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.user = None
        st.rerun()

# ── 8. Layout Principal (Reto e IDE) ──────────────────────────────────────────
ej = exercises[st.session_state.current_ex_index]
c1, c2 = st.columns([1, 1.25], gap="large")

with c1:
    st.markdown('<h1>' + str(ej.get("titulo")) + ' <span class="badge">Principiante</span></h1>', unsafe_allow_html=True)
    st.markdown('<div class="contexto-box">' + str(ej.get("contexto")) + '</div>', unsafe_allow_html=True)
    
    st.markdown("### 🤖 PyBot Tutor")
    chat_box = st.container(height=350)
    with chat_box:
        for r, m in st.session_state.chat_history:
            with st.chat_message(r): st.markdown(m)

    query = st.chat_input("Pregunta a la IA sobre este reto...")
    if query and ai_service:
        st.session_state.chat_history.append(("user", query))
        
        # ARQUITECTURA BLINDADA CONTRA MARKDOWN DEL CHAT:
        salto = chr(10)
        c_code = chr(96) * 3 
        
        ctx_lista = [
            "Reto: " + str(ej.get("titulo")),
            "Código actual:",
            c_code + "python",
            str(st.session_state.editor_code),
            c_code,
            "Duda: " + str(query)
        ]
        ctx = salto.join(ctx_lista)

        st.session_state.gemini_history.append({"role": "user", "parts": [ctx]})
        
        with chat_box:
            with st.chat_message("user"): st.markdown(query)
            with st.chat_message("assistant"):
                with st.spinner("Pensando..."):
                    ok, resp = ai_service.ask_question(ctx, st.session_state.gemini_history)
                st.markdown(resp)
                if ok:
                    st.session_state.chat_history.append(("assistant", resp))
                    st.session_state.gemini_history.append({"role": "model", "parts": [resp]})

with c2:
    st.markdown("### 💻 IDE Integrado")
    
    if HAS_ACE:
        nuevo_codigo = st_ace(
            value=st.session_state.editor_code,
            language="python",
            theme="tomorrow_night",
            keybinding="vscode",
            font_size=14,
            tab_size=4,
            height=380,
            show_gutter=True,
            key="ace_editor_" + str(st.session_state.current_ex_index)
        )
        st.session_state.editor_code = nuevo_codigo
    else:
        st.text_area(
            "Editor de código (⚠️ Instala streamlit-ace)", 
            height=380, 
            label_visibility="collapsed", 
            key="editor_code"
        )

    if st.button("🚀 Validar", type="primary", use_container_width=True):
        codigo_usuario = str(st.session_state.editor_code).strip()
        codigo_inicial = str(ej.get("codigo_inicial", "")).strip()

        # 🛡️ CAPA 1: GATING DE UX (Anti-trampas pasivo)
        if not codigo_usuario:
            st.session_state.last_result = (False, "", "⚠️ El editor está vacío. ¡Escribe tu código antes de validar!")
        elif codigo_usuario == codigo_inicial:
            st.session_state.last_result = (False, "", "⚠️ El código es idéntico al inicial. ¡Intenta resolver el reto!")
        else:
            # ⚙️ CAPA 2: EVALUACIÓN REAL (Pasa al motor backend)
            ok, cons, feed = CodeEvaluator.evaluate(codigo_usuario, ej.get("test"))
            
            if ok:
                db = get_db_session()
                res = AuthManager.mark_exercise_solved_and_add_xp(db, st.session_state.user["id"], ej.get("id"))
                if res.get("success"):
                    st.session_state.user["xp"] = res["new_xp"]
                    st.session_state.user["level"] = res["new_level"]
                    st.toast("¡Reto completado! +50 XP", icon="⭐")
                db.close()
                
            st.session_state.last_result = (ok, cons, feed)

    if st.session_state.last_result:
        v, o, f = st.session_state.last_result
        st.markdown("**Consola de Salida:**")
        
        if o and o.strip():
            st.code(o, language="python")
        else:
            st.code("Ejecución finalizada sin salidas por consola (print).", language="shell")
            
        if v: 
            st.success(f)
            st.balloons()
        else: 
            st.error(f)