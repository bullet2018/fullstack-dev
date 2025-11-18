from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Optional
import bcrypt
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, field_validator
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from uuid import uuid4

load_dotenv()

# Конфигурация для JWT
secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
active_refresh_tokens = {}

def create_access_token(data: dict):
    # Добавляем дату истечения токена
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=access_token_expire_minutes)
    to_encode.update({"exp": expire})  # Поле "exp" указывает, когда токен истечет

    # Генерируем токен
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload  # Возвращаем данные токена, если он валиден
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# def create_refresh_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.now(timezone.utc) + timedelta(days=refresh_token_expire_days)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, secret_key, algorithm=algorithm)

def create_refresh_token(data: dict):
    token_id = str(uuid4())  # Генерируем уникальный идентификатор
    email = data["sub"]
    expire = datetime.now(timezone.utc) + timedelta(days=refresh_token_expire_days)
    to_encode = {"sub": email, "id": token_id, "exp": expire}
    refresh_token = jwt.encode(to_encode, secret_key, algorithm=algorithm)

    # Сохраняем токен как активный
    active_refresh_tokens[token_id] = {"email": email, "expires_at": expire}
    return refresh_token

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

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

    # Валидация полей
    @field_validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Имя не может быть пустым")
        return v

    @field_validator("password")
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError("Пароль должен быть длиной минимум 6 символов")
        return v



class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

# Простое in-memory хранилище
users: List[User] = []
_next_user_id_user = 1

# Хранилище паролей: email -> password
user_passwords: Dict[str, str] = {}


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

@app.post(
    "/auth/register",
    response_model=User,
    status_code=201,
    summary="Регистрация пользователя",
    description="Регистрирует нового пользователя с валидацией данных."
)
def register_user(data: RegisterRequest) -> User:
    # Проверка уникальности email
    for u in users:
        if u.email == data.email:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    # Создаём пользователя
    new_user = User(
        id=_get_next_user_id(),
        name=data.name.strip(),
        email=data.email,
        role=data.role,
    )
    users.append(new_user)
    hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    # Сохраняем пароль
    user_passwords[data.email] = hashed_password

    return new_user

@app.post(
    "/auth/login",
    summary="Логин пользователя",
    description="Проверяет email и пароль и возвращает приветственное сообщение."
)
def login_user(data: LoginRequest):
    if not data.email or not data.password:
        raise HTTPException(status_code=400, detail="Email и пароль обязательны")

    # Проверяем, есть ли такой пользователь
    user = None
    for u in users:
        if u.email == data.email:
            user = u
            break

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь с таким email не найден")

    # Проверяем пароль
    saved_password = user_passwords.get(data.email)

    if saved_password is None or not bcrypt.checkpw(data.password.encode('utf-8'), saved_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")

    tokens_to_revoke = [key for key, value in active_refresh_tokens.items() if value["email"] == data.email]
    for token_id in tokens_to_revoke:
        del active_refresh_tokens[token_id]
        
    token = create_access_token({"sub": user.email, "role": user.role, "name": user.name})
    refresh_token = create_refresh_token({"sub": user.email})
    return {
        "message": f"Добро пожаловать, {user.name}!", 
        "access_token": token,
        "refresh_token": refresh_token,
        
    }

@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    # Проверяем токен
    user_data = verify_access_token(token)
    return {"message": f"Welcome, your role is {user_data['role']}"}

@app.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Проверяем токен
    user_data = verify_access_token(token)
    return {
        "email": user_data["sub"],
        "name": user_data["name"],
        "role": user_data["role"]
    }
    
def check_user_role(token_data: dict, required_role: str):
    user_role = token_data.get("role")
    if user_role != required_role:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: requires {required_role} role"
        )

@app.post("/auth/refresh")
def refresh_access_token(body: RefreshRequest):
    refresh_token = body.refresh_token
    try:
        # Проверяем валидность Refresh Token
        payload = jwt.decode(refresh_token, secret_key, algorithms=[algorithm])
        token_id = payload.get("id")
        email = payload.get("sub")
        
        if token_id not in active_refresh_tokens:
            raise HTTPException(status_code=401, detail="Refresh token is not active")
        
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Находим пользователя по email
        user = next((u for u in users if u.email == email), None)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        del active_refresh_tokens[token_id]
        # Генерируем новый Access Token
        new_access_token = create_access_token({
            "sub": user.email,
            "role": user.role,
            "name": user.name,
        })
        return {"access_token": new_access_token}

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@app.get("/admin")
def admin_route(token: str = Depends(oauth2_scheme)):
    user_data = verify_access_token(token)
    check_user_role(user_data, "admin")
    return {"message": "Welcome, Admin! You have full access."}

@app.get("/user-resource")
def user_resource(token: str = Depends(oauth2_scheme)):
    user_data = verify_access_token(token)
    check_user_role(user_data, "user")
    return {"message": f"Welcome, {user_data['name']}! This resource is for users only."}

from datetime import datetime

@app.get("/debug-token")
def debug_token(token: str):
    payload = jwt.decode(
        token,
        secret_key,
        algorithms=[algorithm],
        options={"verify_exp": False},
    )

    exp_ts = payload.get("exp")

    return {
        "payload": payload,
        "exp_raw": exp_ts,
        "exp_as_utc": datetime.fromtimestamp(exp_ts, tz=timezone.utc).isoformat() if exp_ts else None,
        "server_now_utc": datetime.now(timezone.utc).isoformat(),
        "server_now_local": datetime.now().isoformat(),
    }