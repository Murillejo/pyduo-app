"""
PyDuo — Plataforma educativa de Python
Arquitectura: UI Moderna + BD Local + Content Gating + Tutor IA
Editor: streamlit-ace (motor CodeMirror con syntax highlighting Python)
"""
from database.db_setup import init_db
init_db()
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

# ── 3. Editor con syntax highlighting ─────────────────────────────────────────
# Instalar con: pip install streamlit-ace
try:
    from streamlit_ace import st_ace
    HAS_ACE = True
except ImportError:
    HAS_ACE = False
    st.sidebar.warning("⚠️ Editor sin colores. Ejecuta: pip install streamlit-ace")

# ── 4. Configuración de página ─────────────────────────────────────────────────
st.set_page_config(
    page_title="PyDuo - Aprende Python",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 5. CSS global ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0d0f14; color: #e8e4d9; }

[data-testid="stSidebar"] {
    background: #12141a !important;
    border-right: 1px solid #1e2230 !important;
}
[data-testid="stSidebar"] * { color: #e8e4d9 !important; }
[data-testid="stMain"] { background: #0d0f14; }

.block-container {
    padding-top: 1.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1400px;
}

h1, h2, h3 {
    font-family: 'Space Mono', monospace !important;
    color: #e8e4d9 !important;
}
h1 { font-size: 1.3rem !important; line-height: 1.4 !important; }
h2 { font-size: 1rem !important; color: #a8c4ff !important; }
h3 { font-size: 0.88rem !important; color: #7affb4 !important; }

.stButton > button {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.78rem !important;
    background: transparent !important;
    border: 1px solid #2a3048 !important;
    color: #a8c4ff !important;
    border-radius: 8px !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #1a1e2e !important;
    border-color: #a8c4ff !important;
    color: #fff !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #a8c4ff, #7affb4) !important;
    color: #0d0f14 !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button[kind="primary"]:hover { opacity: 0.85 !important; }

/* Fallback textarea (cuando no hay streamlit-ace) */
.stTextArea textarea {
    background: #0a0c10 !important;
    color: #a8ff8c !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.84rem !important;
    border-radius: 8px !important;
    border: 1px solid #1e2230 !important;
    line-height: 1.65 !important;
    padding: 1rem !important;
}
.stTextArea textarea:focus {
    border-color: #a8c4ff !important;
    box-shadow: none !important;
}

.stSelectbox > div > div {
    background: #1a1e2e !important;
    border: 1px solid #2a3048 !important;
    color: #e8e4d9 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
}

/* Caja de contexto / enunciado */
.contexto-box {
    background: #12141a;
    border: 1px solid #1e2230;
    border-left: 3px solid #a8c4ff;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    font-size: 0.87rem;
    line-height: 1.8;
    color: #c8d4f0;
    margin-bottom: 1rem;
    white-space: pre-wrap;
}
.contexto-box code {
    color: #ff79c6 !important;
    font-weight: 700 !important;
    background: #282a36 !important;
    padding: 2px 6px !important;
    border-radius: 5px !important;
    border: 1px solid rgba(255,121,198,0.25) !important;
    font-size: 0.88rem !important;
}

/* Caja de explicación post-acierto */
.post-box {
    background: #0d1a2e;
    border: 1px solid #1a3a5c;
    border-left: 3px solid #7affb4;
    border-radius: 10px;
    padding: 1rem 1.3rem;
    font-size: 0.87rem;
    line-height: 1.7;
    color: #c8d4f0;
    margin-top: 0.75rem;
}

/* Barra decorativa encima del editor ace */
.ide-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #1a1e2e;
    border: 1px solid #2a3048;
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    padding: 7px 14px;
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    color: #5a6480;
}
.ide-topbar .dots span {
    display: inline-block;
    width: 10px; height: 10px;
    border-radius: 50%;
    margin-right: 5px;
}
.ide-topbar .lang { color: #a8c4ff; font-size: 0.65rem; letter-spacing: 1px; }

/* Mensajes del chat y barra de texto */
[data-testid="stChatMessage"] {
    background: #12141a !important;
    border: 1px solid #1e2230 !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
    font-size: 1.1rem !important;
}
[data-testid="stChatMessage"] p {
    font-size: 1.1rem !important;
}
[data-testid="stChatInputTextArea"] {
    font-size: 1.1rem !important;
}

/* Consola de salida */
.consola-box {
    background: #0a0c10;
    border: 1px solid #1e2230;
    border-radius: 0 0 8px 8px;
    padding: 0.85rem 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 1.2rem;
    color: #c8d4f0;
    line-height: 1.6;
    min-height: 48px;
    white-space: pre-wrap;
    word-break: break-word;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #2a3048; border-radius: 4px; }

#MainMenu, footer { visibility: hidden; }

.stMarkdown p, .stMarkdown li { color: #c8d4f0 !important; line-height: 1.75 !important; }
.stMarkdown code {
    background: #1a1e2e !important;
    color: #a8c4ff !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.81rem !important;
}
.stMarkdown strong { color: #e8e4d9 !important; }

.pyduo-logo {
    font-family: 'Space Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: #a8c4ff;
    text-align: center;
    margin-bottom: 0.5rem;
}
.pyduo-logo span { color: #7affb4; }

.badge {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    padding: 2px 10px;
    border-radius: 99px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-left: 8px;
    vertical-align: middle;
}
.badge-principiante { background: #0a1f15; color: #7affb4; border: 1px solid #1a4a2e; }
.badge-intermedio    { background: #1a1400; color: #ffd97a; border: 1px solid #3a2e00; }
.badge-avanzado      { background: #1f0a0a; color: #ff9a8c; border: 1px solid #4a1a1a; }
</style>
""", unsafe_allow_html=True)


# ── 6. Servicios y datos ───────────────────────────────────────────────────────
@st.cache_resource
def init_ai():
    try:
        return AIAssistant()
    except Exception as e:
        print("Error IA:", e)
        return None

ai_service = init_ai()

def get_db():
    return SessionLocal()

try:
    from modules.data_loader import ExerciseLoader
    exercises = ExerciseLoader.load_exercises()
    if not exercises:
        raise ValueError("Lista vacía")
except Exception:
    exercises = [{
        "id": 1,
        "titulo": "Error de datos",
        "contexto": "No se pudieron cargar los ejercicios. Revisa data/exercises.json",
        "codigo_inicial": "# Revisa tu exercises.json",
        "test": "assert False, 'No hay ejercicios cargados'",
        "explicacion_post": "",
        "difficulty": "Principiante",
    }]


# ── 7. Estado de sesión ────────────────────────────────────────────────────────
defaults = {
    "user": None,
    "current_ex_index": 0,
    "chat_history": [],
    "gemini_history": [],
    "last_result": None,
    "editor_code": exercises[0].get("codigo_inicial", ""),
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# PANTALLA DE LOGIN / REGISTRO
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.user is None:
    _, col_c, _ = st.columns([1, 1.5, 1])
    with col_c:
        st.markdown(
            '<div class="pyduo-logo" style="font-size:3rem;margin-top:4rem;">Py<span>Duo</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="text-align:center;color:#5a6480;font-size:0.82rem;'
            'font-family:\'Space Mono\',monospace;margin-bottom:2rem;">'
            'Aprende Python. Nivel por nivel.</p>',
            unsafe_allow_html=True,
        )

        tab_login, tab_reg = st.tabs(["🔐 Iniciar sesión", "📝 Registro"])
        db = get_db()

        with tab_login:
            with st.form("form_login"):
                username = st.text_input("Usuario", placeholder="tu_usuario")
                password = st.text_input("Contraseña", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Entrar →", use_container_width=True, type="primary")
                if submitted:
                    user = AuthManager.authenticate_user(db, username, password)
                    if user:
                        st.session_state.user = {
                            "id": user.id,
                            "username": user.username,
                            "xp": user.xp,
                            "level": user.level,
                        }
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")

        with tab_reg:
            with st.form("form_reg"):
                new_u = st.text_input("Nuevo usuario", placeholder="elige_un_nombre")
                new_p = st.text_input("Contraseña", type="password", placeholder="mínimo 6 caracteres")
                if st.form_submit_button("Crear cuenta →", use_container_width=True, type="primary"):
                    try:
                        AuthManager.create_user(db, new_u, new_p)
                        st.success("✅ Cuenta creada. Ya puedes iniciar sesión.")
                    except Exception as e:
                        st.error(str(e))

        db.close()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# PLATAFORMA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

# ── 8. Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="pyduo-logo">Py<span>Duo</span></div>', unsafe_allow_html=True)
    st.markdown(
        f'👤 **{st.session_state.user["username"]}** | Nivel {st.session_state.user["level"]}',
    )
    st.progress((st.session_state.user["xp"] % 100) / 100.0)
    st.caption(f'⭐ {st.session_state.user["xp"]} XP totales')
    st.divider()

    # Progreso del usuario desde BD
    db = get_db()
    resueltos = [
        r[0]
        for r in db.query(Progress.exercise_id)
        .filter(Progress.user_id == st.session_state.user["id"])
        .all()
    ]
    db.close()

    # Construir lista de ejercicios con iconos de estado
    opciones = []
    permitidos = []
    for i, ex in enumerate(exercises):
        ex_id = ex.get("id", i + 1)
        if ex_id in resueltos:
            icon, can = "✅", True
        elif i == 0 or exercises[i - 1].get("id", i) in resueltos:
            icon, can = "▶️", True
        else:
            icon, can = "🔒", False
        titulo_corto = ex.get("titulo", f"Ejercicio {ex_id}")
        opciones.append(f"{icon} {ex_id}. {titulo_corto}")
        if can:
            permitidos.append(i)

    sel = st.selectbox(
        "Mapa de Retos:",
        opciones,
        index=st.session_state.current_ex_index,
        label_visibility="visible",
    )
    idx_sel = opciones.index(sel)

    if idx_sel != st.session_state.current_ex_index:
        if idx_sel in permitidos:
            st.session_state.current_ex_index = idx_sel
            st.session_state.editor_code = exercises[idx_sel].get("codigo_inicial", "")
            st.session_state.chat_history = []
            st.session_state.gemini_history = []
            st.session_state.last_result = None
            st.rerun()
        else:
            st.error("🔒 Completa el nivel anterior primero.")

    st.divider()

    # Estado de la IA
    if ai_service:
        st.markdown(
            '<p style="font-family:\'Space Mono\',monospace;font-size:0.68rem;color:#7affb4;">'
            '● Tutor IA activo</p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<p style="font-family:\'Space Mono\',monospace;font-size:0.68rem;color:#ff8c8c;">'
            '● Tutor IA inactivo — revisa .env</p>',
            unsafe_allow_html=True,
        )

    if st.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state.user = None
        st.rerun()


# ── 9. Datos del ejercicio activo ──────────────────────────────────────────────
ej = exercises[st.session_state.current_ex_index]

titulo     = ej.get("titulo")         or ej.get("title",        "Sin título")
contexto   = ej.get("contexto")       or ej.get("description",  "")
cod_init   = ej.get("codigo_inicial") or ej.get("starter_code", "")
test_code  = ej.get("test")           or ej.get("tests_code",   "assert True")
solucion   = ej.get("solucion")       or ej.get("solution",     "")
exp_post   = ej.get("explicacion_post", "")
dificultad = ej.get("difficulty", "Principiante")

badge_class = {
    "Principiante": "badge-principiante",
    "Intermedio":   "badge-intermedio",
    "Avanzado":     "badge-avanzado",
}.get(dificultad, "badge-principiante")


# ── 10. Explicación a pantalla completa ────────────────────────────────────────
st.markdown(
    f'<h1 style="font-size: 2.2rem; margin-bottom: 1rem;">{titulo} <span class="badge {badge_class}" style="font-size: 0.8rem;">{dificultad}</span></h1>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="contexto-box" style="font-size: 1.15rem; line-height: 1.9; margin-bottom: 2rem; padding: 1.5rem;">{contexto}</div>',
    unsafe_allow_html=True,
)

# ── 11. Layout de dos columnas (Chat y Editor) ─────────────────────────────────
col_izq, col_der = st.columns([1, 1.25], gap="large")

# ─────────────────────── COLUMNA IZQUIERDA (Chat IA) ──────────────────────────
with col_izq:
    st.markdown("### 🤖 PyBot — Tutor IA")
    st.markdown('<p style="font-size: 1.1rem; color: #8b949e; margin-bottom: 1.5rem;">Pregúntame cualquier duda sobre este ejercicio. No te daré la solución directa, pero sí las pistas que necesitas.</p>', unsafe_allow_html=True)

    chat_box = st.container(height=320)
    with chat_box:
        for role, msg in st.session_state.chat_history:
            with st.chat_message(role):
                st.markdown(msg)

    query = st.chat_input(
        "Escribe tu duda aquí..." if ai_service
        else "Tutor no disponible — revisa GEMINI_API_KEY en .env"
    )

    if query:
        if not ai_service:
            st.error("El tutor IA no está disponible. Comprueba tu GEMINI_API_KEY en el archivo .env")
        else:
            st.session_state.chat_history.append(("user", query))

            nl = "\n"
            ctx_ia = (
                f"Ejercicio: {titulo}{nl}"
                f"Enunciado: {contexto[:400]}{nl}"
                f"Código actual del alumno:{nl}```python{nl}"
                f"{st.session_state.editor_code}{nl}```{nl}"
                f"Pregunta: {query}"
            )
            st.session_state.gemini_history.append({"role": "user", "parts": [ctx_ia]})

            with chat_box:
                with st.chat_message("user"):
                    st.markdown(query)
                with st.chat_message("assistant"):
                    with st.spinner("PyBot está pensando..."):
                        ok, resp = ai_service.ask_question(ctx_ia, st.session_state.gemini_history)
                    st.markdown(resp)
                    if ok:
                        st.session_state.chat_history.append(("assistant", resp))
                        st.session_state.gemini_history.append({"role": "model", "parts": [resp]})
                    else:
                        st.session_state.chat_history.append(("assistant", f"❌ {resp}"))


# ─────────────────────── COLUMNA DERECHA ──────────────────────────────────────
with col_der:

    # ── Barra decorativa estilo VS Code ──────────────────────────────────────
    st.markdown(
        '<div class="ide-topbar">'
        '<div class="dots">'
        '<span style="background:#ff5f57;"></span>'
        '<span style="background:#febc2e;"></span>'
        '<span style="background:#28c840;"></span>'
        '</div>'
        '<span>ejercicio.py</span>'
        '<span class="lang">PYTHON</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Editor con syntax highlighting (streamlit-ace) ────────────────────────
    if HAS_ACE:
        # st_ace devuelve el contenido actual del editor en cada interacción.
        # Usamos una key única por ejercicio para que el editor se reinicie
        # cuando el usuario cambia de reto.
        codigo_editor = st_ace(
            value=st.session_state.editor_code,
            language="python",
            theme="tomorrow_night",       # tema oscuro estilo VS Code
            keybinding="vscode",          # atajos de teclado de VS Code
            font_size=20,
            tab_size=4,
            show_gutter=True,             # números de línea
            show_print_margin=False,
            wrap=False,
            auto_update=True,             # actualiza sin perder el foco
            height=380,
            key=f"ace_{st.session_state.current_ex_index}",
        )
        # Guardar en session_state SOLO si el editor devolvió algo
        # (evita resetear el código cuando el componente no ha cargado aún)
        if codigo_editor is not None:
            st.session_state.editor_code = codigo_editor

    else:
        # Fallback: textarea verde sin colores
        fallback = st.text_area(
            label="editor_fallback",
            value=st.session_state.editor_code,
            height=380,
            label_visibility="collapsed",
            key=f"fallback_{st.session_state.current_ex_index}",
        )
        st.session_state.editor_code = fallback

    # ── Botones de acción ─────────────────────────────────────────────────────
    col_run, col_sol = st.columns([2, 1])
    with col_run:
        ejecutar = st.button("🚀 Ejecutar y Validar", type="primary", use_container_width=True)
    with col_sol:
        ver_sol = st.button("💡 Solución", use_container_width=True)

    # ── Lógica de validación ──────────────────────────────────────────────────
    if ejecutar:
        codigo_usuario = str(st.session_state.editor_code).strip()
        codigo_inicial = str(cod_init).strip()

        # Capa 1: validaciones de UX (anti-trampas pasivo)
        if not codigo_usuario:
            st.session_state.last_result = (False, "", "⚠️ El editor está vacío. ¡Escribe tu código antes de validar!")
        elif codigo_usuario == codigo_inicial:
            st.session_state.last_result = (False, "", "⚠️ El código es idéntico al código inicial. ¡Intenta resolver el reto!")
        else:
            # Capa 2: evaluación real
            ok, consola, feedback = CodeEvaluator.evaluate(codigo_usuario, test_code)

            if ok:
                # Registrar progreso en BD y sumar XP
                db = get_db()
                try:
                    res = AuthManager.mark_exercise_solved_and_add_xp(
                        db, st.session_state.user["id"], ej.get("id")
                    )
                    if res.get("success"):
                        st.session_state.user["xp"]    = res["new_xp"]
                        st.session_state.user["level"] = res["new_level"]
                        st.toast("¡Reto completado! +50 XP ⭐", icon="🎉")
                except Exception as e:
                    print(f"Error guardando progreso: {e}")
                finally:
                    db.close()

            st.session_state.last_result = (ok, consola, feedback)

    # ── Mostrar resultado ─────────────────────────────────────────────────────
    if st.session_state.last_result is not None:
        ok, consola, feedback = st.session_state.last_result

        # Consola de salida (texto plano, sin colores raros)
        st.markdown(
            '<p style="font-family:\'Space Mono\',monospace;font-size:0.7rem;'
            'color:#5a6480;text-transform:uppercase;letter-spacing:1px;margin-top:0.75rem;">'
            'Consola de salida</p>',
            unsafe_allow_html=True,
        )
        salida = consola.strip() if consola and consola.strip() else "(sin salida en consola)"
        st.markdown(f'<div class="consola-box">{salida}</div>', unsafe_allow_html=True)

        if ok:
            st.success(feedback)
            st.balloons()

            # Explicación didáctica post-acierto
            if exp_post:
                st.markdown(
                    f'<div class="post-box">💡 <strong>Para que no lo olvides:</strong>'
                    f'<br><br>{exp_post}</div>',
                    unsafe_allow_html=True,
                )

            # Botón siguiente ejercicio
            hay_siguiente = st.session_state.current_ex_index < len(exercises) - 1
            if hay_siguiente:
                if st.button("Siguiente ejercicio →", type="primary", use_container_width=True):
                    sig = st.session_state.current_ex_index + 1
                    st.session_state.current_ex_index = sig
                    st.session_state.editor_code = exercises[sig].get("codigo_inicial", "")
                    st.session_state.chat_history = []
                    st.session_state.gemini_history = []
                    st.session_state.last_result = None
                    st.rerun()
            else:
                st.success("🏆 ¡Has completado todos los ejercicios disponibles!")
        else:
            st.error(feedback)

    # ── Ver solución ──────────────────────────────────────────────────────────
    if ver_sol:
        st.session_state[f"show_sol_{st.session_state.current_ex_index}"] = True

    if st.session_state.get(f"show_sol_{st.session_state.current_ex_index}") and solucion:
        st.markdown(
            '<p style="font-family:\'Space Mono\',monospace;font-size:0.7rem;'
            'color:#ffd97a;margin-top:1rem;">── SOLUCIÓN ──</p>',
            unsafe_allow_html=True,
        )
        st.code(solucion, language="python")