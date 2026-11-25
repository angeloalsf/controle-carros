# Sistema de Controle de Carros

Trabalho 6 — Integração do MongoDB com uma aplicação simples  
Disciplina: Tópicos Especiais em Banco de Dados  
Professor: Leonardo Fiório Soares  
Grupo: Angelo, Lorrayne e Rui

## 1. Objetivo

Desenvolver uma aplicação simples para gerenciar veículos, proprietários e manutenções, utilizando MongoDB como banco de dados.

## 2. Tecnologias

- Python
- Streamlit (interface web)
- MongoDB
- PyMongo (integração Python/MongoDB)

## 3. Estrutura do banco

O banco utilizado chama-se `controle_carros` e possui três coleções:

### `carros`
Campos: `marca`, `modelo`, `ano`, `cor`, `placa`, `quilometragem`, `combustivel` e `proprietario_id`.

### `proprietarios`
Campos: `nome`, `cpf`, `telefone` e `email`.

### `manutencoes`
Campos: `carro_id`, `tipo`, `descricao`, `data`, `quilometragem` e `valor`.

Os campos `proprietario_id` e `carro_id` armazenam referências `ObjectId` para relacionar os documentos das coleções.

## 4. Funcionalidades

A aplicação oferece operações de inserir, listar, atualizar e remover nas três coleções:
- Carros
- Proprietários
- Manutenções

Há validações para evitar placas e CPFs duplicados. O sistema também impede a exclusão de proprietários com veículos vinculados e de veículos com manutenções vinculadas.

## 5. Consultas implementadas

1. Buscar veículo pela placa.
2. Buscar veículos por marca.
3. Buscar veículos a partir de determinado ano.
4. Buscar veículos de um proprietário.
5. Consultar o histórico de manutenção de um veículo.
6. Agregar o total gasto em manutenção por veículo, utilizando `$group` e `$lookup`.

## 6. Requisitos para executar

- Python 3.10 ou superior.
- MongoDB em execução localmente ou uma instância MongoDB Atlas.
- Acesso ao terminal.

## 7. Instalação e execução

Escolha **uma** das opções abaixo. Não é necessário utilizar Conda e `venv` ao mesmo tempo.

### Opção A — Conda

1. Extraia o arquivo ZIP.
2. Abra o Anaconda Prompt ou terminal na pasta do projeto.
3. Crie o ambiente a partir do arquivo `environment.yml`:

```bash
conda env create -f environment.yml
```

4. Ative o ambiente:

```bash
conda activate controle-carros
```

5. (Já configurado no arquivo `.env` — pode pular este passo.) Para usar outra conexão, a aplicação aceita:

```text
mongodb://localhost:27017
```

Se utilizar outra conexão, configure a variável de ambiente `MONGODB_URI` antes de executar.

No PowerShell:

```powershell
$env:MONGODB_URI="mongodb://localhost:27017"
```

No Anaconda Prompt (Windows):

```bat
set MONGODB_URI=mongodb://localhost:27017
```

Para MongoDB Atlas, utilize a connection string fornecida pelo serviço e mantenha-a privada.

6. (Opcional) Insira dados fictícios para demonstração:

```bash
python seed.py
```

7. Inicie a aplicação:

```bash
streamlit run app.py
```

O Streamlit exibirá um endereço local no terminal, normalmente `http://localhost:8501`.

Para sair do ambiente Conda:

```bash
conda deactivate
```

### Opção B — venv (Python padrão)

1. Extraia o arquivo ZIP.
2. Abra o terminal na pasta do projeto.
3. Crie o ambiente virtual:

```bash
python -m venv .venv
```

4. Ative o ambiente.

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

No Windows CMD:

```bat
.venv\Scripts\activate.bat
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

5. Instale as dependências:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

6. (Já configurado no arquivo `.env` — pode pular este passo.) Para usar outra conexão, a aplicação aceita:

```text
mongodb://localhost:27017
```

Se utilizar outra conexão, configure a variável de ambiente `MONGODB_URI` antes de executar. Exemplo no PowerShell:

```powershell
$env:MONGODB_URI="mongodb://localhost:27017"
```

Para MongoDB Atlas, utilize a connection string fornecida pelo serviço e mantenha-a privada.

7. (Opcional) Insira dados fictícios para demonstração:

```bash
python seed.py
```

8. Inicie a aplicação:

```bash
streamlit run app.py
```

O Streamlit exibirá um endereço local no terminal, normalmente `http://localhost:8501`.

Para sair do ambiente virtual:

```bash
deactivate
```

## 8. Configuração do MongoDB

O projeto usa o MongoDB Atlas do grupo. A connection string fica no arquivo `.env`, lido automaticamente pelo `config.py`. **Não é preciso configurar variável de ambiente**: basta instalar as dependências, rodar `python seed.py` e `streamlit run app.py`.

Ordem usada para encontrar a conexão:

1. Variável de ambiente `MONGODB_URI`, se estiver definida no terminal.
2. Linha `MONGODB_URI=...` do arquivo `.env`.
3. MongoDB local em `mongodb://localhost:27017`.

**Baixou pelo GitHub?** O `.env` não vai para o repositório, porque contém a senha. Copie o `.env.example` para `.env` e cole na linha `MONGODB_URI` a connection string completa (peça ao grupo).

Para usar outro banco, edite a linha `MONGODB_URI` do `.env`. O arquivo `.env` contém a senha do banco: não o publique (ele já está no `.gitignore`).

## 9. Observações

- O banco `controle_carros` e as coleções são criados automaticamente quando a aplicação insere os primeiros documentos.
- O script `seed.py` adiciona dados fictícios apenas quando as coleções correspondentes estão vazias.
- Não utilize dados pessoais reais na apresentação; os dados incluídos são fictícios.
- A aplicação não inclui autenticação de usuários, pois o foco do trabalho é a integração com MongoDB e as operações CRUD.

## 10. Roteiro sugerido para apresentação

1. Apresentar o objetivo do Sistema de Controle de Carros.
2. Mostrar o banco `controle_carros` e suas três coleções no MongoDB.
3. Demonstrar o cadastro, listagem, edição e exclusão de um proprietário.
4. Demonstrar o cadastro e a edição de um veículo.
5. Registrar uma manutenção para o veículo.
6. Executar as cinco consultas exigidas.
7. Mostrar a consulta de agregação com `$group` e `$lookup`.
