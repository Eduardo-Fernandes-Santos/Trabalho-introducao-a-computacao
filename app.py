import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATA_FILE = "tasks.json"

# ---------- Funções auxiliares ----------
def carregar_tarefas():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_tarefas(tarefas):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=4, ensure_ascii=False)

# Carrega ao iniciar
tarefas = carregar_tarefas()

def mensagem_motivacional():
    total = len(tarefas)
    feitas = sum(1 for t in tarefas if t["feito"])
    pendentes = total - feitas

    if total == 0:
        return "Tudo pronto, aproveite o dia! 😎"
    elif pendentes == 0:
        return "Parabéns, todas as tarefas do dia foram concluídas! 🎉"
    elif pendentes > 5:
        return "Hora de focar! 💪"
    else:
        return "Continue no ritmo, você consegue! 🚀"

# ---------- Rotas ----------
@app.route("/")
def index():
    global tarefas
    tarefas = carregar_tarefas()
    total = len(tarefas)
    feitas = sum(1 for t in tarefas if t["feito"])
    pendentes = total - feitas
    msg = mensagem_motivacional()
    return render_template("index.html", tarefas=tarefas, total=total, feitas=feitas, pendentes=pendentes, msg=msg)

@app.route("/add", methods=["GET", "POST"])
def add():
    global tarefas
    if request.method == "POST":
        novo_id = max([t["id"] for t in tarefas], default=0) + 1
        titulo = request.form["titulo"]
        descricao = request.form["descricao"]
        tarefas.append({"id": novo_id, "titulo": titulo, "descricao": descricao, "feito": False})
        salvar_tarefas(tarefas)
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/toggle/<int:id>")
def toggle(id):
    global tarefas
    for t in tarefas:
        if t["id"] == id:
            t["feito"] = not t["feito"]
            break
    salvar_tarefas(tarefas)
    return redirect(url_for("index"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    global tarefas
    for t in tarefas:
        if t["id"] == id:
            if request.method == "POST":
                t["titulo"] = request.form["titulo"]
                t["descricao"] = request.form["descricao"]
                salvar_tarefas(tarefas)
                return redirect(url_for("index"))
            return render_template("edit.html", tarefa=t)
    return redirect(url_for("index"))

@app.route("/delete/<int:id>")
def delete(id):
    global tarefas
    tarefas = [t for t in tarefas if t["id"] != id]
    salvar_tarefas(tarefas)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
