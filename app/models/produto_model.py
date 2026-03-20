from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProdutoModel(Base):
    __tablename__ = "produto"

    id_prod = Column(Integer, primary_key=True, index=True)
    descricao_pro = Column(String(255))
    uf_destino_pro = Column(String(2))
    cidade_destino_pro = Column(String(100))
    payload_json_pro = Column(Text)
    created_at_pro = Column(TIMESTAMP, server_default=func.now())

    id_reg_fk = Column(Integer, ForeignKey("regiao.id_reg"))

    regiao = relationship("RegiaoModel")