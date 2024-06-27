from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect
import os


#Criando um banco de dados
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///padaria.db"
db = SQLAlchemy()
db.init_app(app)



class Product(db.Model):
    __tablename__ = 'produto'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(500))
    ingredientes = db.Column(db.String(500))
    origem = db.Column(db.String(100))
    imagem = db.Column(db.String(100))

    def __init__(self,
                 nome:str,
                 descricao:str,
                 ingredientes:str,
                 origem:str,
                 imagem:str
                 ) -> None:
        self.nome = nome
        self.descricao = descricao
        self.ingredientes = ingredientes
        self.origem = origem
        self.imagem = imagem

        
#Criando a Rota da API
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/listar_produtos", methods=["POST", "GET"])
def listar_produtos():
    if request.method == 'POST':
        termo = request.form['pesquisa']
        resultado = db.session.execute(db.select(Product).filter(Product.nome.like(f"%{termo}%"))).scalars()
        return render_template("listar_produtos.html", produtos=resultado)
    else:
        #Passar banco de dados para uma variável
        produtos = db.session.execute(db.select(Product)).scalars()
        return render_template("listar_produtos.html", produtos=produtos)

@app.route("/cadastrar_produtos", methods=["GET", "POST"])
def cadastrar_produtos():
    
    if request.method == "POST":
        status = {"type":"sucesso", "message":"Produto cadastrado com sucesso!"}
        dados = request.form
        imagem = request.files['imagem']
        try:
            produto = Product(dados['nome'], 
                        dados['descricao'],
                        dados['ingredientes'],
                        dados['origem'],
                        imagem.filename)
            #Salvar imagem na pasta
            imagem.save(os.path.join('static/imagens', imagem.filename))
            #Gravar no banco de dados
            db.session.add(produto)
            db.session.commit()
        except:
            status = {"type":"erro", "message": f"Houve um problema ao cadastrar o produto {dados['nome']}"}
        return render_template("cadastrar_produtos.html", status=status)
    else:     
        return render_template("cadastrar_produtos.html")

@app.route("/editar_produtos/<int:id>", methods=["GET", "POST"])
def editar_produtos(id):
    
    if request.method == "POST":
        status = {"type":"sucesso", "message":"Produto atualizado com sucesso!"}
        dados_editados = request.form
        imagem = request.files['imagem']
        try:
            produto = db.session.execute(db.select(Product).filter(Product.id == id)).scalar()
            produto.nome = dados_editados['nome']
            produto.descricao = dados_editados['descricao']
            produto.ingredientes = dados_editados['ingredientes']
            produto.origem = dados_editados['origem']

            if imagem.filename:
                produto.imagem = imagem.filename
        
            db.session.commit()
            return redirect("/listar_produtos")
        except:
            status = {"type":"erro", "message":f"Houve problema para atualizar o produto {dados_editados['nome']}"}
    else:
        produto_editado = db.session.execute(db.select(Product).filter(Product.id == id)).scalar()
        return render_template("editar_produtos.html", produto = produto_editado)

@app.route("/deletar_produto/<int:id>")
def deletar_produto(id):
    produto_deletado = db.session.execute(db.select(Product).filter(Product.id == id)).scalar()
    db.session.delete(produto_deletado)
    db.session.commit()
    return redirect("/listar_produtos")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)



