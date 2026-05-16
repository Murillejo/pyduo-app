# database/db_setup.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

# Construimos la ruta absoluta para la base de datos para evitar errores de pathing
DB_PATH = os.path.join(os.path.dirname(__file__), "bibliocademy.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Creamos el Engine. connect_args={'check_same_thread': False} es necesario
# en SQLite cuando se usa con frameworks multihilo/asíncronos como Streamlit.
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False # Cambiar a True si quieres ver las consultas SQL en la terminal
)

# Fábrica de sesiones (Session local)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Inicializa la base de datos creando todas las tablas definidas en models.py.
    Es seguro llamarla múltiples veces; no sobrescribirá datos existentes.
    """
    Base.metadata.create_all(bind=engine)
    print(f"📦 Base de datos inicializada correctamente en: {DB_PATH}")

def get_db():
    """
    Generador de sesiones para asegurar que las conexiones se cierran correctamente.
    Útil para inyección de dependencias en arquitecturas limpias.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()