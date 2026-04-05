import pandas as pd
import os


class DataTransformer:
    def __init__(self, input_path):
        self.input_path = input_path

    def read_ceps(self, column_name='cep'):
        """Lê o arquivo CSV e retorna uma lista de CEPs limpos."""
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.input_path}")

        # Leitura do CSV usando Pandas
        df = pd.read_csv(self.input_path)

        if column_name not in df.columns:
            raise ValueError(f"Coluna '{column_name}' não encontrada no CSV.")

        # Padroniza os CEPs (remove hífens e garante 8 dígitos)
        df['cep_clean'] = df[column_name].astype(str).str.replace(r'\D', '', regex=True)
        df['cep_clean'] = df['cep_clean'].str.zfill(8)

        return df['cep_clean'].tolist()