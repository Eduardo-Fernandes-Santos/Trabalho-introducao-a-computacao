from flask import Flask, render_template, request, redirect, url_for
import tasks  # módulo de tarefas

app = Flask(__name__)

# Página inicial: lista todas as tarefas
@app.route("/")
def index():
    all_tasks = tasks.get_tasks()
    return render_template("index.html", tasks=all_tasks)

# Adicionar nova tarefa
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description", "")
        tasks.add_task(title, description)
        return redirect(url_for("index"))
    return render_template("add.html")

# Atualizar tarefa
@app.route("/update/<task_id>", methods=["GET", "POST"])
def update(task_id):
    task = tasks.get_task(task_id)
    if not task:
        return "Tarefa não encontrada", 404

    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description", "")
        status = request.form.get("status", "pending")
        tasks.update_task(task_id, title, description, status)
        return redirect(url_for("index"))

    return render_template("update.html", task=task)

# Excluir tarefa
@app.route("/delete/<task_id>")
def delete(task_id):
    tasks.delete_task(task_id)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
