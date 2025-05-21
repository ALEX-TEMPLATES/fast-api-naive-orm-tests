"""
DTO объекты для работы с моделью Example.
"""
from datetime import datetime

from app.dto.base import BaseDTO


class ExampleCreateDTO(BaseDTO):
    """DTO для создания новой записи Example."""
    
    name: str


class ExampleDTO(BaseDTO):
    """DTO для полного представления записи Example."""
    
    id: int
    name: str
    created_at: datetime
