from fastapi import FastAPI, HTTPException
from typing import List, Dict

app = FastAPI(
    title="To-Do API (FastAPI, in-memory)",
    description="Простой CRUD по задачам",
    version="1.0.0",
)

tasks: List[Dict] = []
_next_id = 1

def _get_next_id() -> int:
    global _next_id
    val = _next_id
    _next_id += 1
    return val

@app.get("/tasks/", summary="Получить список задач", description="Возвращает все задачи из памяти.")
def list_tasks() -> List[Dict]:
    return tasks

@app.get("/tasks/{task_id}", summary="Получить задачу по id", description="Возвращает одну задачу по её идентификатору.")
def get_task(task_id: int) -> Dict:
    for t in tasks:
        if t["id"] == task_id:
            return t
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks/", summary="Создать новую задачу", description="Создаёт задачу. Ожидает словарь: {'title': str, 'completed': bool?}.", status_code=201)
def create_task(body: Dict) -> Dict:
    title = body.get("title", "").strip()
    completed = bool(body.get("completed", False))
    description = body.get("description")  # может отсутствовать

    if not title:
        raise HTTPException(status_code=400, detail="Field 'title' is required")

    task = {
        "id": _get_next_id(),
        "title": title,
        "completed": completed,
    }
    if description is not None:
        task["description"] = description

    tasks.append(task)
    return task

@app.put("/tasks/{task_id}", summary="Обновить задачу", description="Полностью обновляет поля задачи (простая логика, без моделей).")
def update_task(task_id: int, body: Dict) -> Dict:
    for t in tasks:
        if t["id"] == task_id:
            if "title" in body:
                t["title"] = str(body["title"])
            if "completed" in body:
                t["completed"] = bool(body["completed"])
            if "description" in body:
                t["description"] = body["description"]
            return t
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}", summary="Удалить задачу", description="Удаляет задачу по идентификатору.", status_code=204)
def delete_task(task_id: int):
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail="Task not found")

@app.get("/health", summary="Проверка работоспособности", description="Возвращает статус сервиса.")
def health_check():
    return {"status": "ok"}
