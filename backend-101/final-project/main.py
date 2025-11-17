from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional

from pydantic import BaseModel, EmailStr

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



# ---- МОДЕЛИ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ----

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    """Модель для создания пользователя (без id)."""
    pass

class UserUpdate(BaseModel):
    """Модель для обновления пользователя (все поля необязательны)."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

class User(UserBase):
    id: int


# Простое in-memory хранилище
users: List[User] = []
_next_user_id_user = 1


def _get_next_user_id() -> int:
    global _next_user_id_user
    val = _next_user_id_user
    _next_user_id_user += 1
    return val


def _find_user_index(user_id: int) -> int:
    """Возвращает индекс пользователя в списке или -1, если не найден."""
    for i, u in enumerate(users):
        if u.id == user_id:
            return i
    return -1

# ---- CRUD ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ----

@app.post(
    "/users/",
    response_model=User,
    status_code=201,
    summary="Создать пользователя",
    description="Создаёт нового пользователя с уникальным email."
)
def create_user(user: UserCreate) -> User:
    # Проверка уникальности email
    for u in users:
        if u.email == user.email:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    new_user = User(
        id=_get_next_user_id(),
        name=user.name,
        email=user.email,
        role=user.role,
    )
    users.append(new_user)
    return new_user


@app.get(
    "/users/",
    response_model=List[User],
    summary="Получить список пользователей",
    description="Возвращает всех пользователей из памяти."
)
def list_users() -> List[User]:
    return users


@app.get(
    "/users/{user_id}",
    response_model=User,
    summary="Получить пользователя по id",
    description="Возвращает пользователя по его идентификатору."
)
def get_user(user_id: int) -> User:
    idx = _find_user_index(user_id)
    if idx == -1:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return users[idx]


@app.put(
    "/users/{user_id}",
    response_model=User,
    summary="Обновить пользователя",
    description="Полностью или частично обновляет данные пользователя."
)
def update_user(user_id: int, data: UserUpdate) -> User:
    idx = _find_user_index(user_id)
    if idx == -1:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    existing = users[idx]

    # Если передали email — проверяем уникальность (кроме текущего пользователя)
    if data.email is not None:
        for u in users:
            if u.email == data.email and u.id != user_id:
                raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    updated_user = User(
        id=existing.id,
        name=data.name if data.name is not None else existing.name,
        email=data.email if data.email is not None else existing.email,
        role=data.role if data.role is not None else existing.role,
    )

    users[idx] = updated_user
    return updated_user


@app.delete(
    "/users/{user_id}",
    status_code=204,
    summary="Удалить пользователя",
    description="Удаляет пользователя по его идентификатору."
)
def delete_user(user_id: int):
    idx = _find_user_index(user_id)
    if idx == -1:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    users.pop(idx)
    # 204 — без тела ответа
    return
