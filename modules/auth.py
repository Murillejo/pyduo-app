# modules/auth.py
import bcrypt
from sqlalchemy.orm import Session
from database.models import User, Progress

class AuthManager:
    """
    Gestor de Autenticación y Gamificación.
    Decisión Arquitectónica: Hashing con bcrypt y Gating de ejercicios.
    """
    @staticmethod
    def hash_password(p: str) -> str:
        return bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(p: str, h: str) -> bool:
        return bcrypt.checkpw(p.encode('utf-8'), h.encode('utf-8'))

    @classmethod
    def create_user(cls, db: Session, u: str, p: str) -> User:
        if db.query(User).filter(User.username == u).first():
            raise ValueError("Usuario ya existe")
        user = User(username=u, password_hash=cls.hash_password(p), xp=0, level=1)
        db.add(user); db.commit(); db.refresh(user)
        return user

    @classmethod
    def authenticate_user(cls, db: Session, u: str, p: str) -> User:
        user = db.query(User).filter(User.username == u).first()
        return user if user and cls.verify_password(p, user.password_hash) else None

    @classmethod
    def mark_exercise_solved_and_add_xp(cls, db: Session, uid: int, eid: int, xp: int = 50) -> dict:
        """Suma XP solo si es la primera vez que se resuelve el ID del ejercicio."""
        if db.query(Progress).filter_by(user_id=uid, exercise_id=eid).first():
            return {"success": False}
        
        db.add(Progress(user_id=uid, exercise_id=eid))
        user = db.query(User).filter(User.id == uid).first()
        user.xp += xp
        old_lvl = user.level
        user.level = (user.xp // 100) + 1
        db.commit(); db.refresh(user)
        return {"success": True, "new_xp": user.xp, "new_level": user.level, "level_up": user.level > old_lvl}