import psycopg2
from pymongo import MongoClient
from neo4j import GraphDatabase
import redis
import json

# --- CONFIGURAÇÕES DE CONEXÃO ---
# (Mesmas do seed.py)
PG_CONFIG = {
    "host": "localhost", "database": "loja_relacional", 
    "user": "aluno", "password": "senha123"
}
MONGO_URI = "mongodb://aluno:senha123@localhost:27017/"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "senha12345")
REDIS_CONFIG = {"host": "localhost", "port": 6379, "password": "senha123", "decode_responses": True}

def get_pg_connection():
    return psycopg2.connect(**PG_CONFIG)

def main():
    print("--- INICIANDO INTEGRAÇÃO (ETL) ---")
    
    # 1. Conexões
    pg_conn = get_pg_connection()
    pg_cur = pg_conn.cursor()
    
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client["loja_documentos"]
    
    neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    
    r = redis.Redis(**REDIS_CONFIG)
    
    # [cite_start]2. Limpar Redis (Requisito do trabalho: "limpando a base de cache") [cite: 36]
    print("Limpando base Redis antiga...")
    r.flushall()

    # [cite_start]3. Buscar Clientes no Relacional (Base Principal) [cite: 10]
    print("Buscando dados do PostgreSQL...")
    pg_cur.execute("SELECT id, nome, email, cidade FROM Clientes")
    clientes_sql = pg_cur.fetchall() # Lista de tuplas
    
    for cliente in clientes_sql:
        c_id, c_nome, c_email, c_cidade = cliente
        print(f"Processando Cliente ID {c_id}: {c_nome}...")
        
        # [cite_start]--- BUSCAR DADOS DO MONGO (Interesses) [cite: 16] ---
        doc_interesses = mongo_db["interesses"].find_one({"id_cliente": c_id})
        lista_interesses = doc_interesses["interesses"] if doc_interesses else []
        
        # [cite_start]--- BUSCAR DADOS DO NEO4J (Amigos) [cite: 18] ---
        # Query: Quem são os amigos desse cliente?
        query_amigos = """
        MATCH (c:Cliente {id: $id})-[:AMIGO_DE]->(amigo)
        RETURN amigo.id AS id, amigo.nome AS nome
        """
        ids_amigos = []
        lista_amigos_nomes = []
        
        with neo4j_driver.session() as session:
            result = session.run(query_amigos, id=c_id)
            for record in result:
                ids_amigos.append(record["id"])
                lista_amigos_nomes.append(record["nome"])
        
        # [cite_start]--- GERAR RECOMENDAÇÕES (SQL) [cite: 6, 23] ---
        # Lógica: O que os amigos desse cliente compraram?
        lista_recomendacoes = []
        if ids_amigos:
            # Converter lista python para tupla SQL (1, 2, 3)
            ids_tuple = tuple(ids_amigos)
            # Se tiver só 1 amigo, o python cria tupla (1,) que o SQL entende, mas precisa tratar caso vazio
            if len(ids_tuple) == 1:
                ids_tuple = f"({ids_tuple[0]})"
            else:
                ids_tuple = str(ids_tuple)
            
            query_rec = f"""
                SELECT DISTINCT p.produto 
                FROM Compras c
                JOIN Produtos p ON c.id_produto = p.id
                WHERE c.id_cliente IN {ids_tuple}
            """
            pg_cur.execute(query_rec)
            produtos_amigos = pg_cur.fetchall()
            lista_recomendacoes = [p[0] for p in produtos_amigos]

        # [cite_start]--- BUSCAR COMPRAS DO PRÓPRIO CLIENTE (Histórico) [cite: 13] ---
        pg_cur.execute("""
            SELECT p.produto, c.data 
            FROM Compras c 
            JOIN Produtos p ON c.id_produto = p.id 
            WHERE c.id_cliente = %s
        """, (c_id,))
        compras_historico = [{"produto": row[0], "data": str(row[1])} for row in pg_cur.fetchall()]

        # [cite_start]--- CONSOLIDAR TUDO E SALVAR NO REDIS [cite: 22, 24] ---
        objeto_final = {
            "id": c_id,
            "nome": c_nome,
            "email": c_email,
            "cidade": c_cidade,
            "interesses": lista_interesses,      # Veio do Mongo
            "amigos": lista_amigos_nomes,        # Veio do Neo4j
            "historico_compras": compras_historico, # Veio do SQL
            "recomendacoes": lista_recomendacoes # Processado (Amigos -> SQL)
        }
        
        # Salvando como JSON no Redis
        chave = f"cliente:{c_id}"
        r.set(chave, json.dumps(objeto_final))
        print(f" -> Salvo no Redis: {chave}")

    # Fechar conexões
    pg_cur.close()
    pg_conn.close()
    mongo_client.close()
    neo4j_driver.close()
    r.close()
    print("--- INTEGRAÇÃO CONCLUÍDA ---")

if __name__ == "__main__":
    main()
