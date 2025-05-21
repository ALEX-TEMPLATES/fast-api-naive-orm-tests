"""
Модуль DTO (Data Transfer Objects).

Содержит Pydantic-модели для передачи данных между слоями приложения.
"""

from app.dto.base import BaseDTO
from app.dto.example import ExampleCreateDTO, ExampleDTO

__all__ = ["BaseDTO", "ExampleDTO", "ExampleCreateDTO"]
