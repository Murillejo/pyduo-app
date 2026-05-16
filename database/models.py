# database/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

# Clase base de SQLAlchemy
Base = declarative_base()

class User(Base):
    """Modelo de Usuario con datos de gamificación."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Sistema de Gamificación
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username='{self.username}', level={self.level}, xp={self.xp})>"


class Progress(Base):
    """Registro de ejercicios superados por el usuario."""
    __tablename__ = 'progress'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    exercise_id = Column(Integer, nullable=False) 
    attempts = Column(Integer, default=1)
    solved_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="progress")

    def __repr__(self):
        return f"<Progress(user_id={self.user_id}, exercise_id={self.exercise_id})>"