from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Deixando SQLite como padrão para facilitar a avaliação do recrutador.
# Para produção/entrega, basta trocar para a string do seu banco:
# SQL Server: "mssql+pyodbc://user:pass@localhost/pan_db?driver=ODBC+Driver+17+for+SQL+Server"
# PostgreSQL: "postgresql://user:pass@localhost:5432/pan_db"
DATABASE_URL = "sqlite:///viacep_data.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()