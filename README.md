# Case Técnico: Engenheiro de Dados Python

Este repositório contém a solução desenvolvida para o desafio técnico de Engenharia de Dados. O objetivo do projeto é processar um arquivo CSV contendo 10.000 CEPs, enriquecer esses dados consumindo a API pública do ViaCEP e, por fim, distribuir os resultados estruturados em três fontes distintas: um banco de dados relacional e arquivos nos formatos JSON e XML.

## Decisões de Arquitetura e Engenharia

Para garantir que o código fosse escalável e de fácil manutenção, estruturei a solução seguindo o padrão de um pipeline ETL (Extract, Transform, Load), separando as responsabilidades em módulos específicos.

* **Extração (Paralelismo e Resiliência):** Como o maior gargalo do processo é o tempo de resposta da rede (I/O bound), optei por não fazer requisições síncronas. Implementei um motor assíncrono usando `asyncio` e `aiohttp`. Para não sobrecarregar a API do ViaCEP e evitar bloqueios de IP (HTTP 429), configurei um `Semaphore` limitando o processamento a 50 requisições concorrentes, além de adicionar lógica de *retries* e *exponential backoff*.
* **Transformação:** Utilizei a biblioteca `pandas` para a ingestão, limpeza e padronização dos dados brutos do CSV de origem.
* **Carga e Armazenamento:** A persistência no banco de dados foi construída utilizando o ORM `SQLAlchemy`. Configurei o projeto para rodar com SQLite por padrão para facilitar a avaliação local por parte dos revisores, mas a modelagem está pronta para ser conectada a um SQL Server ou PostgreSQL (bastando alterar a string de conexão e subir um container Docker). O sistema também realiza a exportação automática para `.json` e `.xml`.
* **Tratamento de Erros (Dead Letter):** Apliquei o conceito de segregação de falhas. CEPs inexistentes ou requisições que sofreram *timeout* não interrompem o fluxo principal. Eles são capturados, isolados e exportados para um arquivo `erros_consulta.csv` para auditoria posterior.

## Escalabilidade na Nuvem: AWS Glue Jobs e Lambdas

Pensando na evolução deste script para um ambiente produtivo na AWS, a arquitetura atual pode ser facilmente adaptada:

### AWS Lambda (Abordagem Orientada a Eventos)
A lógica assíncrona isolada no módulo `extractor.py` tem o perfil exato de uma função Lambda. Em um cenário de processamento contínuo (streaming), novos CEPs poderiam ser publicados em uma fila do Amazon SQS (atuando de forma semelhante a um broker como o RabbitMQ). Essa fila acionaria a Lambda, que faria o *fetch* no ViaCEP e gravaria o resultado diretamente no banco. Essa abordagem *serverless* garante escalabilidade horizontal automática e baixo custo.

### AWS Glue (Abordagem Batch)
Para cargas massivas e programadas, como o processamento de milhões de registros históricos de uma só vez, o AWS Glue é a ferramenta mais adequada. Como o Glue opera sobre clusters Apache Spark, a lógica de transformação que construí com o Pandas seria convertida para PySpark ou AWS Glue DynamicFrames. O fluxo ideal consistiria no Glue lendo os arquivos CSV brutos a partir de um *bucket* do Amazon S3, aplicando as regras de validação de forma distribuída e carregando o dado limpo em um *Data Warehouse* (Redshift) ou num banco relacional (Amazon RDS).

##  Como executar o projeto localmente

### 1. Pré-requisitos
* Python 3.9 ou superior.
* Um arquivo CSV contendo os CEPs dentro da pasta `data/input/` (ex: `ceps_brasil_10000.csv`).

### 2. Configurando o Ambiente
Clone o repositório e crie um ambiente virtual:

# Ativando no ambiente

python -m venv venv

# Ativando no Windows
venv\Scripts\activate

# Ativando no Linux/Mac
source venv/bin/activate

# Instale as dependências:

pip install -r requirements.txt

### 4. Resultados Esperados
Após a execução (que exibirá uma barra de progresso no terminal), os seguintes artefatos estarão disponíveis:

viacep_data.db: Banco de dados SQLite populado com os registros válidos.

data/output/enderecos_validos.json: Exportação dos dados de sucesso.

data/output/enderecos_validos.xml: Exportação dos dados de sucesso.

data/output/erros_consulta.csv: Relatório detalhado dos CEPs que falharam ou não foram encontrados.