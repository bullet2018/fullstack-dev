# FastAPI To-Do (финальный проект)

Простой веб-API для управления списком задач (in-memory), созданный на **FastAPI**.

## Возможности API
- `GET /tasks/` — список задач
- `GET /tasks/{task_id}` — задача по id
- `POST /tasks/` — создать задачу
- `PUT /tasks/{task_id}` — обновить задачу
- `DELETE /tasks/{task_id}` — удалить задачу

Документация (Swagger UI): http://127.0.0.1:8000/docs

---

## Установка и запуск

### Вариант A: Poetry
```bash
uv run uvicorn main:app --reload
