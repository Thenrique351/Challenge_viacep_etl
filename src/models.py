from sqlalchemy import Column, Integer, String
from .database import Base

class Endereco(Base):
    __tablename__ = "enderecos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cep = Column(String(10), index=True, nullable=False)
    logradouro = Column(String(255))
    complemento = Column(String(255))
    unidade = Column(String(50))
    bairro = Column(String(255))
    localidade = Column(String(255))
    uf = Column(String(2))
    estado = Column(String(100))
    regiao = Column(String(100))
    ibge = Column(String(20))
    gia = Column(String(20))
    ddd = Column(String(5))
    siafi = Column(String(20))