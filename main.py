import time
from src.database import engine, Base, SessionLocal
from src.transformer import DataTransformer
from src.extractor import ViaCepExtractor
from src.loader import DataLoader

# Recria as tabelas no banco de dados
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def main():
    print("Iniciando o Pipeline ETL - ViaCEP")
    start_time = time.time()

    # 1. Transformação: Ler CEPs
    print("\n[1/3] Lendo arquivo CSV de entrada...")
    transformer = DataTransformer(input_path="data/input/ceps_brasil_10000.csv")
    try:
        lista_ceps = transformer.read_ceps(column_name='CEP')
        print(f"Total de CEPs carregados: {len(lista_ceps)}")
    except Exception as e:
        print(f"Erro ao ler o CSV: {e}")
        return

    # 2. Extração: Consultar ViaCEP (Paralelizado)
    print("\n[2/3] Consultando API do ViaCEP (Processamento Assíncrono)...")
    extractor = ViaCepExtractor(max_concurrent_requests=50)
    success_data, error_data = extractor.run_extraction(lista_ceps)
    print(f"Consultas com sucesso: {len(success_data)}")
    print(f"Consultas com erro: {len(error_data)}")

    # 3. Carga: Gravar no Banco e Arquivos
    print("\n[3/3] Carregando dados nos destinos...")
    loader = DataLoader(output_dir="data/output/")

    # Grava no Banco
    db = SessionLocal()
    try:
        loader.load_to_database(db, success_data)
    finally:
        db.close()

    # Grava XML e JSON
    loader.export_success_files(success_data)

    # Grava CSV de erros
    loader.export_errors(error_data)

    end_time = time.time()
    print(f"\nPipeline finalizado com sucesso em {end_time - start_time:.2f} segundos.")


if __name__ == "__main__":
    main()