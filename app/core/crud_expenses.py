from datetime import datetime
from sqlalchemy import select, func
from app import schemas
from app.database import models
from sqlalchemy.ext.asyncio import AsyncSession


async def create_expense(db: AsyncSession, expense: schemas.ExpenseCreate, user_id: int):
    db_expense = models.Expense(**expense.dict(), user_id=user_id)
    db.add(db_expense)
    await db.commit()
    await db.refresh(db_expense)
    return db_expense


async def get_expense(db: AsyncSession, expense_id: int):
    result = await db.execute(select(models.Expense).filter(models.Expense.id == expense_id))
    return result.scalars().first()


async def get_expenses(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Expense).offset(skip).limit(limit))
    return result.scalars().all()


async def delete_expense(db: AsyncSession, expense_id: int):
    db_expense = await get_expense(db, expense_id)
    if db_expense:
        await db.delete(db_expense)
        await db.commit()
    return db_expense


async def count_user_expenses(db: AsyncSession, user_id: int):
    result = await db.execute(select(func.sum(models.Expense.amount)).filter(models.Expense.user_id == user_id))
    return result.scalar() or 0


async def count_expenses_in_date_range(db: AsyncSession, user_id: int, start_date: datetime, end_date: datetime):
    result = await db.execute(
        select(func.sum(models.Expense.amount))
        .filter(models.Expense.user_id == user_id)
        .filter(models.Expense.date >= start_date)
        .filter(models.Expense.date <= end_date)
    )
    return result.scalar() or 0


async def count_in_date_range_by_category(db: AsyncSession, user_id: int, category_id: int, start_date: datetime,
                                          end_date: datetime):
    result = await db.execute(
        select(func.sum(models.Expense.amount))
        .filter(models.Expense.user_id == user_id)
        .filter(models.Expense.category_id == category_id)
        .filter(models.Expense.date >= start_date)
        .filter(models.Expense.date <= end_date)
    )
    return result.scalar() or 0


async def get_user_expenses(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    query = select(models.Expense).where(models.Expense.user_id == user_id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
