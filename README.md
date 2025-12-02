# Sistema de Recomendação de Compras - Integração de Bases de Dados

Este projeto foi desenvolvido como requisito avaliativo da disciplina de **Banco de Dados II** do curso de Ciência da Computação/Sistemas de Informação da **Unochapecó**.

O objetivo é demonstrar a integração de quatro paradigmas de banco de dados (Relacional, Documentos, Grafos e Chave-Valor) em um único sistema de recomendação de produtos.

---

## 📋 O Desafio

O sistema simula um cenário de e-commerce onde é necessário recomendar produtos para um cliente baseando-se nas compras realizadas por seus amigos. O desafio reside na natureza distribuída dos dados:

1. **Dados Cadastrais e Compras:** Armazenados em banco **Relacional**.
2. **Interesses Pessoais:** Armazenados em banco orientado a **Documentos**.
3. **Rede de Amigos:** Armazenada em banco orientado a **Grafos**.
4. **Cache/Consulta:** Todos os dados devem ser consolidados e disponibilizados em alta velocidade em um banco **Chave-Valor**.

## 🏗️ Arquitetura da Solução

A solução foi implementada utilizando **Python** e **Docker**. O fluxo de dados funciona através de um processo de ETL (Extract, Transform, Load) customizado:

1. **Extração:** O script conecta simultaneamente no PostgreSQL, MongoDB e Neo4j.
2. **Transformação:**
    * Cruza os IDs dos clientes entre as bases.
    * Identifica os amigos no grafo.
    * Busca o histórico de compras desses amigos no relacional.
    * Gera a lista de recomendação ("Seus amigos compraram X").
3. **Carga:** Salva um objeto JSON consolidado no **Redis**, que serve como única fonte de verdade para a interface do usuário.

### Tecnologias Utilizadas
* **Linguagem:** Python 3.12
* **Interface:** Flask (Web)
* **Bancos de Dados:**
    * 🐘 **PostgreSQL 15** (Relacional)
    * 🍃 **MongoDB 6.0** (Documentos)
    * 🕸️ **Neo4j 5.12** (Grafos)
    * ⚡ **Redis 7.0** (Chave-Valor)
* **Infraestrutura:** Docker & Docker Compose

---

## 🐳 Por que Docker?

A escolha do Docker para este projeto foi fundamental para garantir a integridade e facilidade de execução do ambiente. Os principais motivos foram:

1. **Orquestração de Múltiplos Serviços:** O projeto exige quatro servidores de banco de dados distintos rodando simultaneamente. O Docker Compose permite subir toda essa infraestrutura com um único comando, sem necessidade de instalações manuais complexas no sistema operacional.
2. **Isolamento e Compatibilidade:** Garante que todos os membros do grupo e o professor avaliador executem o projeto com as mesmas versões exatas dos bancos de dados, eliminando erros de compatibilidade ou conflitos de porta na máquina local.
3. **Facilidade de "Reset":** Como o trabalho envolve testes de integração e limpeza de cache, o Docker permite destruir e recriar o ambiente em segundos, garantindo um estado limpo para apresentação.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
* Docker e Docker Compose instalados.
* Python 3 instalado.

### Passo 1: Subir a Infraestrutura
Na raiz do projeto, execute o comando para baixar as imagens e iniciar os bancos:

```bash
docker-compose up -d
```
*Aguarde cerca de 30 segundos para que todos os bancos (principalmente Neo4j e Postgres) estejam prontos para conexão.*

### Passo 2: Configurar o Ambiente Python
Recomenda-se o uso de um ambiente virtual para instalar as dependências:

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente (Linux/Mac)
source venv/bin/activate

# Ativar ambiente (Windows)
venv\Scripts\activate

# Instalar bibliotecas necessárias
pip install flask psycopg2-binary pymongo neo4j redis
```

### Passo 3: Povoar os Bancos (Seed)
Execute o script responsável por criar as tabelas e inserir os dados iniciais de teste nas bases 1, 2 e 3:

```bash
python seed.py
```

### Passo 4: Executar a Integração (ETL)
Execute o script que lê das bases de origem, processa as recomendações e salva no Redis:

```bash
python etl_integration.py
```

### Passo 5: Iniciar a Aplicação
Inicie a interface web desenvolvida em Flask:

```bash
python app.py
```

Acesse no seu navegador: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🖥️ Funcionalidades da Interface

A interface web consulta exclusivamente o **Redis**, demonstrando a eficiência da integração.

* **Clientes:** Visualiza os dados cadastrais unificados com os interesses.
* **Amigos:** Exibe a lista de amigos recuperada do grafo.
* **Histórico:** Mostra as compras realizadas pelo cliente.
* **Recomendações:** Exibe os produtos sugeridos com base nas compras da rede de amigos.
* **♻️ Sincronizar Bases:** Um botão na interface permite rodar o script de integração novamente. Isso é útil para demonstração: você insere uma compra no PostgreSQL manualmente, clica em Sincronizar e vê a recomendação aparecer na tela instantaneamente.

---

## 👥 Autores

Trabalho desenvolvido pelos acadêmicos:
**Gabriel**
João Minski

**Professor:** Monica Tissiani De Toni Pereira
