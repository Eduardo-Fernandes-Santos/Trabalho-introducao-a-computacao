# tasks.py
"""
Módulo simples para gerenciar tarefas com persistência em JSON.
Fornece as operações básicas de CRUD usadas pelo Flask depois.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
import json
import uuid
import os
from typing import List, Optional

# Arquivo de armazenamento (no mesmo diretório deste arquivo)
TASKS_FILE = os.path.join(os.path.dirname(__file__), "tasks.json")


@dataclass
class Task:
    id: str
    title: str
    description: str = ""
    status: str = "pending"   # "pending" ou "done"
    created_at: str = ""      # ISO timestamp


def _now_iso() -> str:
    """Retorna timestamp em ISO (UTC)."""
    return datetime.utcnow().isoformat() + "Z"


def _load_tasks_raw() -> List[dict]:
    """Carrega lista de dicionários do arquivo JSON (retorna lista vazia se não existir)."""
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_tasks_raw(tasks: List[dict]) -> None:
    """Salva lista de dicionários no arquivo JSON (cria/reescreve)."""
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


# CRUD público ------------------------------------------------------------

def get_tasks(status: Optional[str] = None) -> List[Task]:
    """
    Retorna todas as tarefas como objetos Task.
    Se status for fornecido ('pending' ou 'done'), filtra pelo status.
    """
    raw = _load_tasks_raw()
    tasks = [Task(**t) for t in raw]
    if status:
        tasks = [t for t in tasks if t.status == status]
    return tasks


def get_task(task_id: str) -> Optional[Task]:
    """Retorna uma tarefa pelo id ou None se não existir."""
    for t in _load_tasks_raw():
        if t.get("id") == task_id:
            return Task(**t)
    return None


def add_task(title: str, description: str = "") -> Task:
    """Cria e salva uma nova tarefa, retornando o objeto Task."""
    new = Task(
        id=str(uuid.uuid4()),
        title=title,
        description=description,
        status="pending",
        created_at=_now_iso(),
    )
    tasks = _load_tasks_raw()
    tasks.append(asdict(new))
    _save_tasks_raw(tasks)
    return new


def update_task(task_id: str,
                title: Optional[str] = None,
                description: Optional[str] = None,
                status: Optional[str] = None) -> Optional[Task]:
    """
    Atualiza campos fornecidos da tarefa (non-destructive).
    Retorna a tarefa atualizada ou None se não existir.
    """
    tasks = _load_tasks_raw()
    modified = False
    for t in tasks:
        if t.get("id") == task_id:
            if title is not None:
                t["title"] = title
            if description is not None:
                t["description"] = description
            if status is not None:
                if status not in ("pending", "done"):
                    raise ValueError("status deve ser 'pending' ou 'done'")
                t["status"] = status
            modified = True
            updated = Task(**t)
            break
    if modified:
        _save_tasks_raw(tasks)
        return updated
    return None


def delete_task(task_id: str) -> bool:
    """Remove a tarefa pelo id. Retorna True se removida, False caso não encontrada."""
    tasks = _load_tasks_raw()
    new = [t for t in tasks if t.get("id") != task_id]
    if len(new) == len(tasks):
        return False
    _save_tasks_raw(new)
    return True


# Pequeno demo/manual test quando executado diretamente --------------
if __name__ == "__main__":
    print("Demo rápido do tasks.py")
    # limpa (apenas para demo)
    if os.path.exists(TASKS_FILE):
        os.remove(TASKS_FILE)

    t1 = add_task("Comprar leite", "Ir ao mercado depois do trabalho")
    t2 = add_task("Estudar Flask", "Montar MVP do gerenciador de tarefas")
    print("Tarefas adicionadas:")
    for t in get_tasks():
        print("-", t)

    print("\nMarcando a primeira como concluída...")
    update_task(t1.id, status="done")

    print("\nTarefas pendentes:")
    for t in get_tasks(status="pending"):
        print("-", t)

    print("\nRemovendo a segunda tarefa...")
    delete_task(t2.id)

    print("\nEstado final das tarefas:")
    for t in get_tasks():
        print("-", t)
