import pandas as pd
from .models import Endereco
from sqlalchemy.orm import Session


class DataLoader:
    def __init__(self, output_dir="data/output/"):
        self.output_dir = output_dir
        import os
        os.makedirs(self.output_dir, exist_ok=True)

    def load_to_database(self, db: Session, success_data: list):
        """Salva os dados válidos no banco de dados usando Bulk Insert."""
        if not success_data:
            return

        # Prepara os dicionários ignorando chaves não mapeadas no modelo
        valid_keys = [column.name for column in Endereco.__table__.columns]
        registros = []

        for item in success_data:
            registro_limpo = {k: v for k, v in item.items() if k in valid_keys}
            registros.append(Endereco(**registro_limpo))

        db.bulk_save_objects(registros)
        db.commit()
        print(f"[DB] {len(registros)} registros inseridos com sucesso.")

    def export_success_files(self, success_data: list):
        """Gera os arquivos de saída JSON e XML."""
        if not success_data:
            return

        df = pd.DataFrame(success_data)

        # Exporta para JSON
        json_path = f"{self.output_dir}enderecos_validos.json"
        df.to_json(json_path, orient='records', force_ascii=False, indent=4)
        print(f"[FILE] Arquivo JSON gerado: {json_path}")

        # Exporta para XML usando Pandas
        xml_path = f"{self.output_dir}enderecos_validos.xml"
        df.to_xml(xml_path, index=False, root_name='enderecos', row_name='endereco')
        print(f"[FILE] Arquivo XML gerado: {xml_path}")

    def export_errors(self, error_data: list):
        """Gera o CSV contendo os erros das consultas."""
        if not error_data:
            print("[FILE] Nenhum erro para registrar.")
            return

        df_errors = pd.DataFrame(error_data)
        error_path = f"{self.output_dir}erros_consulta.csv"
        df_errors.to_csv(error_path, index=False, sep=';', encoding='utf-8')
        print(f"[FILE] Arquivo de erros gerado: {error_path}")
