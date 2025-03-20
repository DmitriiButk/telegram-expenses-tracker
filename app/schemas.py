from typing import Optional
from pydantic import BaseModel, field_validator
from datetime import datetime


class User(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    id: int
    name: str


class ExpenseCreate(BaseModel):
    description: str
    amount: float
    category_id: int


class ExpenseUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    category_id: Optional[int] = None


class Expense(ExpenseCreate):
    id: int
    date: datetime

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    name: str


class Category(BaseModel):
    id: int
    name: str
    user_id: int

    class Config:
        from_attributes = True


class DateValidation(BaseModel):
    date: str

    @field_validator('date')
    @classmethod
    def validate_date_format(cls, date_str: str) -> str:
        import re
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            raise ValueError('Неверный формат даты. Используйте формат ГГГГ-ММ-ДД (например, 2023-05-21)')

        return date_str
