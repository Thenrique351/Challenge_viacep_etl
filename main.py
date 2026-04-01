from src.database import engine, Base


# Recria as tabelas no banco de dados 
# (Atenção: drop_all zera a tabela a cada execução p desativar, basta comentar essa linha)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def main():
    print("Iniciando o Pipeline ETL - Banco PAN")

if __name__ == "__main__":
    main()