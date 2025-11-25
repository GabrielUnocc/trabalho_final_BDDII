from flask import Flask, render_template, request, redirect, url_for, flash
import redis
import json
# Importamos o script de ETL que criamos no passo anterior para poder rodar ele pelo botão
import etl_integration 

app = Flask(__name__)
app.secret_key = "segredo_apresentacao" # Necessário para mensagens de feedback (flash)

# Configuração do Redis
REDIS_CONFIG = {"host": "localhost", "port": 6379, "password": "senha123", "decode_responses": True}

def get_redis_data():
    """Função auxiliar para pegar todos os dados do Redis"""
    r = redis.Redis(**REDIS_CONFIG)
    keys = r.keys("cliente:*") # Pega todas as chaves de clientes
    dados = []
    for key in keys:
        json_data = r.get(key)
        if json_data:
            dados.append(json.loads(json_data))
    
    # Ordenar por ID para ficar bonito na tela
    dados.sort(key=lambda x: x['id'])
    return dados

@app.route('/')
def index():
    """Rota principal: Dashboard com todas as opções"""
    return render_template('index.html', view="home")

@app.route('/consultas/<tipo>')
def consultas(tipo):
    """
    Atende aos requisitos de visualização:
    1. Todos os clientes [cite: 30]
    2. Clientes e Amigos [cite: 31]
    3. Clientes e Compras [cite: 32]
    4. Recomendações [cite: 33]
    """
    dados = get_redis_data()
    return render_template('index.html', view=tipo, dados=dados)

@app.route('/atualizar')
def atualizar():
    """Rota para o botão 'Sincronizar Dados' [cite: 36]"""
    try:
        # Chama a função main() do seu script etl_integration.py
        etl_integration.main()
        flash("Sucesso! O banco Redis foi limpo e atualizado com os dados do PostgreSQL, Mongo e Neo4j.", "success")
    except Exception as e:
        flash(f"Erro ao atualizar: {str(e)}", "danger")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Roda o servidor na porta 5000
    app.run(debug=True, port=5000)
