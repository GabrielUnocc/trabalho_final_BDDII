import psycopg2
from pymongo import MongoClient
from neo4j import GraphDatabase
import datetime

# --- CONFIGURAÇÕES DE CONEXÃO (Conforme docker-compose) ---

# 1. PostgreSQL
PG_HOST = "localhost"
PG_DB = "loja_relacional"
PG_USER = "aluno"
PG_PASS = "senha123"

# 2. MongoDB
MONGO_URI = "mongodb://aluno:senha123@localhost:27017/"

# 3. Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "senha12345"

def seed_postgres():
    print("--- Iniciando PostgreSQL ---")
    conn = psycopg2.connect(host=PG_HOST, database=PG_DB, user=PG_USER, password=PG_PASS)
    cur = conn.cursor()
    
    # Limpar e Criar Tabelas conforme especificado [cite: 12, 13, 14]
    cur.execute("DROP TABLE IF EXISTS Compras CASCADE;")
    cur.execute("DROP TABLE IF EXISTS Clientes CASCADE;")
    cur.execute("DROP TABLE IF EXISTS Produtos CASCADE;")
    
    # Tabela Produtos [cite: 14]
    cur.execute("""
        CREATE TABLE Produtos (
            id SERIAL PRIMARY KEY,
            produto VARCHAR(100),
            valor DECIMAL(10, 2),
            quantidade INTEGER,
            tipo VARCHAR(50)
        );
    """)
    
    # Tabela Clientes [cite: 12]
    cur.execute("""
        CREATE TABLE Clientes (
            id SERIAL PRIMARY KEY,
            cpf VARCHAR(14) UNIQUE,
            nome VARCHAR(100),
            endereco VARCHAR(150),
            cidade VARCHAR(50),
            uf VARCHAR(2),
            email VARCHAR(100)
        );
    """)
    
    # Tabela Compras [cite: 13]
    cur.execute("""
        CREATE TABLE Compras (
            id SERIAL PRIMARY KEY,
            id_produto INTEGER REFERENCES Produtos(id),
            data DATE,
            id_cliente INTEGER REFERENCES Clientes(id)
        );
    """)
    
    # Inserir Dados
    print("Inserindo Produtos...")
    produtos = [
        ("Notebook Gamer", 4500.00, 10, "Eletronicos"),
        ("Mouse Sem Fio", 150.00, 50, "Acessorios"),
        ("Teclado Mecanico", 300.00, 30, "Acessorios"),
        ("Monitor 24pol", 900.00, 20, "Eletronicos"),
        ("Cadeira Gamer", 1200.00, 15, "Moveis")
    ]
    for p in produtos:
        cur.execute("INSERT INTO Produtos (produto, valor, quantidade, tipo) VALUES (%s, %s, %s, %s)", p)

    print("Inserindo Clientes...")
    # IDs serão 1, 2, 3, 4, 5
    clientes = [
        ("111.111.111-11", "João Silva", "Rua A, 10", "Chapecó", "SC", "joao@email.com"),
        ("222.222.222-22", "Maria Oliveira", "Rua B, 20", "Chapecó", "SC", "maria@email.com"),
        ("333.333.333-33", "Pedro Souza", "Rua C, 30", "Xanxerê", "SC", "pedro@email.com"),
        ("444.444.444-44", "Ana Costa", "Rua D, 40", "Chapecó", "SC", "ana@email.com"),
        ("555.555.555-55", "Carlos Lima", "Rua E, 50", "Concórdia", "SC", "carlos@email.com")
    ]
    for c in clientes:
        cur.execute("INSERT INTO Clientes (cpf, nome, endereco, cidade, uf, email) VALUES (%s, %s, %s, %s, %s, %s)", c)

    print("Inserindo Compras...")
    # (id_produto, data, id_cliente)
    # João (1) comprou Notebook (1)
    # Maria (2) comprou Mouse (2)
    # Pedro (3) comprou Teclado (3)
    compras = [
        (1, '2025-11-01', 1),
        (2, '2025-11-02', 2),
        (3, '2025-11-03', 3),
        (1, '2025-11-04', 4), # Ana comprou notebook
        (5, '2025-11-05', 1)  # João comprou cadeira também
    ]
    for cp in compras:
        cur.execute("INSERT INTO Compras (id_produto, data, id_cliente) VALUES (%s, %s, %s)", cp)

    conn.commit()
    cur.close()
    conn.close()
    print("PostgreSQL Finalizado.\n")

def seed_mongo():
    print("--- Iniciando MongoDB ---")
    client = MongoClient(MONGO_URI)
    db = client["loja_documentos"]
    collection = db["interesses"] # [cite: 16]
    
    # Limpar coleção
    collection.delete_many({})
    
    print("Inserindo Interesses...")
    # Importante: id_cliente tem que bater com o PostgreSQL
    dados = [
        {"id_cliente": 1, "nome": "João Silva", "interesses": ["Tecnologia", "Jogos", "Hardware"]},
        {"id_cliente": 2, "nome": "Maria Oliveira", "interesses": ["Escritorio", "Leitura", "Acessorios"]},
        {"id_cliente": 3, "nome": "Pedro Souza", "interesses": ["Jogos", "Streaming", "Teclados"]},
        {"id_cliente": 4, "nome": "Ana Costa", "interesses": ["Tecnologia", "Design", "Apple"]},
        {"id_cliente": 5, "nome": "Carlos Lima", "interesses": ["Conforto", "Saude", "Moveis"]}
    ]
    
    collection.insert_many(dados)
    client.close()
    print("MongoDB Finalizado.\n")

def seed_neo4j():
    print("--- Iniciando Neo4j ---")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    
    def criar_dados(tx):
        # Limpar base
        tx.run("MATCH (n) DETACH DELETE n")
        
        print("Criando Nós (Pessoas)...") # [cite: 18, 19]
        # Criando nós com ID do SQL para referência
        pessoas = [
            {"id": 1, "nome": "João Silva", "cpf": "111.111.111-11"},
            {"id": 2, "nome": "Maria Oliveira", "cpf": "222.222.222-22"},
            {"id": 3, "nome": "Pedro Souza", "cpf": "333.333.333-33"},
            {"id": 4, "nome": "Ana Costa", "cpf": "444.444.444-44"},
            {"id": 5, "nome": "Carlos Lima", "cpf": "555.555.555-55"}
        ]
        
        for p in pessoas:
            tx.run("CREATE (p:Cliente {id: $id, nome: $nome, cpf: $cpf})", id=p['id'], nome=p['nome'], cpf=p['cpf'])
            
        print("Criando Relacionamentos (Amizades)...")
        # Definindo quem é amigo de quem
        # João (1) amigo de Maria (2) e Pedro (3)
        # Maria (2) amiga de Ana (4)
        amizades = [
            (1, 2), (1, 3),
            (2, 4),
            (3, 5),
            (4, 1) # Ana também é amiga do João
        ]
        
        for p1, p2 in amizades:
            query = """
            MATCH (a:Cliente {id: $id1}), (b:Cliente {id: $id2})
            CREATE (a)-[:AMIGO_DE]->(b)
            """
            tx.run(query, id1=p1, id2=p2)

    with driver.session() as session:
        session.execute_write(criar_dados)
    
    driver.close()
    print("Neo4j Finalizado.\n")

if __name__ == "__main__":
    try:
        seed_postgres()
        seed_mongo()
        seed_neo4j()
        print("--- SEED COMPLETO COM SUCESSO! ---")
    except Exception as e:
        print(f"Erro ao rodar seed: {e}")
