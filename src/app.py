from bson import ObjectId
from flask import Flask, render_template,redirect,url_for, request
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user,current_user

client = MongoClient("mongodb://localhost:27017/")
db = client["examen-juny"]

app = Flask(__name__)
app.secret_key = "nano"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self,id,email):
        self.id = id
        self.email = email
        


@login_manager.user_loader
def load_user(id):
    comprovar = db.users.find_one({"_id":ObjectId(id)})
    if comprovar:
        return User(str(comprovar["_id"]),(comprovar["email"]))
    return None
    

@app.route("/")
def index():
    
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        comprovar_email = db.users.find_one({"email":email})
        if comprovar_email and check_password_hash(comprovar_email["password"],password):
            user = User(str(comprovar_email["_id"]),(comprovar_email["email"]))
            login_user(user)

            print("usuario encontrado")
            return redirect(url_for("perfil"))
        else:
            print("datos incorrectos")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        imagen = request.form["imagen"]
        comprovar_email = db.users.find_one({"email":email})
        if imagen == "perro":
            imagen = "https://static.wikia.nocookie.net/reinoanimalia/images/e/ed/Golden_retriver.png/revision/latest?cb=20130303080930&path-prefix=es"
        elif imagen == "gato":
            imagen = "https://static.nationalgeographic.es/files/styles/image_3200/public/75552.ngsversion.1422285553360.jpg?w=1900&h=1267"
        else:
            imagen = "https://cdn0.bioenciclopedia.com/es/posts/4/8/3/tortuga_marina_384_600.jpg"
        if not comprovar_email and email and password:
            hashed_password = generate_password_hash(password)
            db.users.insert_one({"email":email,"password":hashed_password,"imagen":imagen})
            print("datos añadidos correctamente")
            return redirect(url_for("login"))
        else:
            return "datos incorrectos"
    
    return render_template("register.html")

@app.route("/perfil", methods=["GET","POST"])
@login_required
def perfil():
    datos = db.publicaciones.find()
    id = current_user.id
    email = current_user.email
    if request.method == "POST":
        imagen = request.form["imagen"]
        nombre = request.form["nombre"]
        categoria = request.form["categoria"]
        id = current_user.id
        comentarios = ""
        if imagen and categoria and nombre:
            db.publicaciones.insert_one({"imagen":imagen,"categoria":categoria,"nombre":nombre,"id":id, "comentarios":comentarios})
            print("publicacion creada con exito")
            return redirect(url_for("perfil"))
        else:
            return "datos invalidos"
    
    return render_template("perfil.html",datos = datos, id = id, email=email)

@app.route("/delete/<string:id>", methods=["GET","POST"])
def delete(id):
    db.publicaciones.delete_one({"_id":ObjectId(id)})
    return redirect(url_for("perfil"))

@app.route("/edit/<string:id>", methods=["GET","POST"])
def edit(id):
    dato = db.publicaciones.find_one({"_id":ObjectId(id)})
    if request.method == "POST":
        imagen = request.form["imagen"]
        nombre = request.form["nombre"]
        categoria = request.form["categoria"]
        if imagen and categoria and nombre:
            db.publicaciones.update_one({"_id":ObjectId(id)},{"$set":{"imagen":imagen,"categoria":categoria,"nombre":nombre}})
            return redirect(url_for("perfil"))
    return render_template("edit.html", dato=dato)

@app.route("/inicio", methods=["GET","POST"])
def inicio():
    datos = db.publicaciones.find()
    if request.method == "POST":
        comentario = request.form["comentario"]
        id = request.form["id"]
        print(comentario, id)
        if comentario:
            db.publicaciones.update_one({"_id":ObjectId(id)},{"$set":{"comentarios":comentario}})
        return redirect(url_for("inicio"))
    return render_template("inicio.html",datos = datos)

@app.route("/usuario/<string:id>")
def usuario(id):
    dato = db.publicaciones.find()
    email = db.users.find_one({"_id":ObjectId(id)})

    return render_template("usuario.html",dato = dato, id = id, email = email)

@app.errorhandler(404)
def error(e):
    return render_template("404.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")