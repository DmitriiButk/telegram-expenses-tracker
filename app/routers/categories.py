from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import crud_categories, crud_users
from app import schemas
from app.database.database import get_db


router = APIRouter(tags=['categories'])


@router.post('/categories/')
async def create_category(category: schemas.CategoryCreate, user_id: int, db: AsyncSession = Depends(get_db)):
    db_category = await crud_categories.get_category_by_name(db, name=category.name, user_id=user_id)
    if db_category:
        raise HTTPException(status_code=400, detail='Category already exists')
    return await crud_categories.create_category(db=db, category=category, user_id=user_id)


@router.get('/categories/', response_model=list[schemas.Category])
async def read_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                          user_id: int = Query(...)):
    user = await crud_users.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return await crud_categories.get_categories(db, user_id=user_id, skip=skip, limit=limit)


@router.delete('/categories/{category_id}')
async def delete_category(category_id: int, user_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    db_category = await crud_categories.get_category_by_id(db, category_id, user_id=user_id)
    if not db_category:
        raise HTTPException(status_code=404, detail='Category not found')
    await crud_categories.delete_category(db, category_id, user_id=user_id)
    return db_category
