from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import schemas
from app.database import models


async def get_category_by_name(db: AsyncSession, name: str, user_id: int):
    result = await db.execute(
        select(models.Category).filter(models.Category.name == name, models.Category.user_id == user_id)
    )
    return result.scalars().first()


async def create_category(db: AsyncSession, category: schemas.CategoryCreate, user_id: int):
    db_category = models.Category(name=category.name, user_id=user_id)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def get_categories(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Category).filter(models.Category.user_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_category_by_id(db: AsyncSession, category_id: int, user_id: int):
    result = await db.execute(
        select(models.Category).filter(models.Category.id == category_id, models.Category.user_id == user_id)
    )
    return result.scalars().first()


async def delete_category(db: AsyncSession, category_id: int, user_id: int):
    category = await db.execute(
        select(models.Category).filter(models.Category.id == category_id, models.Category.user_id == user_id)
    )
    category = category.scalars().first()
    if category:
        await db.execute(delete(models.Expense).where(models.Expense.category_id == category_id))
        await db.commit()
        await db.delete(category)
        await db.commit()
    else:
        raise HTTPException(status_code=404, detail='Category not found')
