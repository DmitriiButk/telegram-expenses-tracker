from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.core import crud_users
from app.database.database import get_db


router = APIRouter(tags=['users'])


@router.post('/users/', response_model=schemas.UserCreate)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud_users.get_user(db, user_id=user.id)
    if db_user:
        return db_user
    return await crud_users.create_user(db=db, user=user)


@router.get('/users/{user_id}')
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud_users.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return db_user
