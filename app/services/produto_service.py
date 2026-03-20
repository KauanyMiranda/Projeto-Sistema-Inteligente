from sqlalchemy.orm import Session
from app.models.produto_model import ProdutoModel
from app.models.regiao_model import RegiaoModel
import json

from app.schemas import item

def salvar_produto(db: Session, item):

    regiao = db.query(RegiaoModel).filter(
        RegiaoModel.nome_reg == item.regiao_destino
    ).first()

    if not regiao:
        raise Exception("Regiao nao encontrada")

    novo_produto = ProdutoModel(
        descricao_pro=item.descricao,
        uf_destino_pro=item.uf_destino,
        cidade_destino_pro=item.cidade_destino,
        payload_json_pro=item.model_dump_json(),
        id_reg_fk=regiao.id_reg
    )

    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)

    return novo_produto