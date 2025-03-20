from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import crud_expenses, crud_users
from app import schemas
from app.database.database import get_db


router = APIRouter(tags=['expenses'])


@router.post('/expenses/{user_id}', response_model=schemas.Expense)
async def create_expense(user_id: int, expense: schemas.ExpenseCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud_users.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail='User not found')
    return await crud_expenses.create_expense(db=db, expense=expense, user_id=user_id)


@router.get('/expenses/user/{user_id}/count_in_date_range')
async def count_expenses_in_date_range(
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        db: AsyncSession = Depends(get_db)
):
    count = await crud_expenses.count_expenses_in_date_range(db, user_id=user_id, start_date=start_date,
                                                             end_date=end_date)
    return {'user_id': user_id, 'total_expenses': count}


@router.get('/expenses/user/{user_id}/count_in_date_range_by_category')
async def count_in_date_range_by_category(
        user_id: int,
        category_id: int,
        start_date: datetime,
        end_date: datetime,
        db: AsyncSession = Depends(get_db)
):
    count = await crud_expenses.count_in_date_range_by_category(db, user_id=user_id, category_id=category_id,
                                                                start_date=start_date, end_date=end_date)
    return {'user_id': user_id, 'category_id': category_id, 'total_expenses': count}


@router.get('/expenses/{expense_id}', response_model=schemas.Expense)
async def read_expense(expense_id: int, db: AsyncSession = Depends(get_db)):
    db_expense = await crud_expenses.get_expense(db, expense_id=expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail='Expense not found')
    return db_expense


@router.delete('/expenses/{expense_id}', response_model=schemas.Expense)
async def delete_expense(expense_id: int, db: AsyncSession = Depends(get_db)):
    db_expense = await crud_expenses.delete_expense(db, expense_id=expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail='Expense not found')
    return db_expense


@router.get('/expenses/user/{user_id}/count')
async def count_user_expenses(user_id: int, db: AsyncSession = Depends(get_db)):
    count = await crud_expenses.count_user_expenses(db, user_id=user_id)
    return {'user_id': user_id, 'total_expenses': count}


@router.get('/expenses/user/{user_id}/expenses', response_model=list[schemas.Expense])
async def read_user_expenses(user_id: int, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    db_user = await crud_users.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail='User not found')

    expenses = await crud_expenses.get_user_expenses(db, user_id=user_id, skip=skip, limit=limit)
    return expenses
