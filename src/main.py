from fastapi import FastAPI

from app.api import api_router

# Инициализация FastAPI приложения
app = FastAPI(
    title="Fast API Template",
    description="Шаблон FastAPI приложения без ORM",
    version="0.1.0",
)

# Подключаем все маршруты API
app.include_router(api_router)


# Корневой эндпоинт для проверки работоспособности
@app.get("/")
async def root():
    return {"message": "API работает!", "status": "ok"}


# Для запуска: uvicorn src.main:app --reload
