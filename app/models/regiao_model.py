from sqlalchemy import Column, Integer, String
from app.core.database import Base

class RegiaoModel(Base):
    __tablename__ = "regiao"

    id_reg = Column(Integer, primary_key=True, index=True)
    nome_reg = Column(String(20), nullable=False, unique=True)