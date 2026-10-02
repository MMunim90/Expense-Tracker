from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import models
from models import Users, Expenses
from database import engine, SessionLocal
from fastapi.responses import JSONResponse
from router import auth
from router.auth import get_current_user

app = FastAPI()

class Expense(BaseModel):
    id: Annotated[int, Field(..., description='Id of the expenses', example='1')]
    title: Annotated[str, Field(..., description='Title of the expenses', example='Lunch')]
    amount: Annotated[float, Field(..., description='Amount of the expenses', example='500')]
    type: Annotated[str, Field(..., description='Type of the expenses', example='income')]
    category: Annotated[str, Field(..., description='Category of the expenses', example='Food')]
    date: Annotated[str, Field(..., description='Date of the expenses', example='2026-09-05')]


class UpdateExpense(BaseModel):
    title: Annotated[Optional[str], Field(default=None)]
    amount: Annotated[Optional[float], Field(default=None)]
    type: Annotated[Optional[str], Field(default=None)]
    category: Annotated[Optional[str], Field(default=None)]
    date: Annotated[Optional[str], Field(default=None)]



models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@app.get("/")
def main():
    return "Expense Tracker Backend"


@app.get("/all_transactions")
def view_all_expenses(user : user_dependency, db : db_dependency):

    if user is None:
        raise HTTPException(status_code=401, detail="User didnot loged in yet!!!")
    
    return db.query(Expenses).filter(Expenses.owner_id == user.get('id')).all()


@app.get("/specific_transaction/{expense_id}")
def view_specific_expenses(user : user_dependency, db : db_dependency, expense_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="User didnot loged in yet!!!")
    
    specific_expense = db.query(Expenses).filter(Expenses.owner_id == user.get('id')).filter(Expenses.id == expense_id).first()

    if specific_expense is not None:
        return specific_expense
    else:
        raise HTTPException(status_code=404, detail='Expense Not Found')
    
    
@app.get("/sort_transactions/filter")
def view_sorted_expenses(user : user_dependency, db : db_dependency, type: str, category: str):
    if user is None:
            raise HTTPException(status_code=401, detail="User didnot loged in yet!!!")
        
    income_categories = ["Salary", "Freelance"]

    expense_categories = [
        "Food",
        "Transport",
        "Grocery",
        "Bills",
        "Education"
    ]
    
    if category not in income_categories and category not in expense_categories:
        raise HTTPException(status_code=404, detail=f"Invalid category. Income options: {income_categories}, Expense options: {expense_categories}")
    
    if type not in ['income', 'expense']:
        raise HTTPException(status_code=404, detail="Invalid type. Choose between income or expense")
    
    data = db.query(Expenses).filter(Expenses.owner_id == user.get('id'), Expenses.type == type, Expenses.category == category).all()
    
    return data


@app.post("/create_transactions")
def create_expenses(user : user_dependency, db : db_dependency, expense: Expense):
    if user is None:
        raise HTTPException(status_code=401, detail="User didnot loged in yet!!!")

    expense_model = Expenses(**expense.model_dump(), owner_id = user.get('id'))
    db.add(expense_model)
    db.commit()

    return JSONResponse(status_code=201, content={'message' : 'Expense created successfully'})
    
    

@app.put("/update_transactions/{expense_id}")
def update_expenses(user : user_dependency, db : db_dependency, expense_id: int, update_expense: UpdateExpense):
    if user is None:
        raise HTTPException(status_code=401, detail="User didnot loged in yet!!!")

    expense = db.query(Expenses).filter(Expenses.owner_id == user.get('id')).filter(Expenses.id == expense_id).first()

    if expense is None:
        raise HTTPException(status_code=404, detail='Expense Not Found')

    update_data = update_expense.model_dump(exclude_unset=True)

    for key,value in update_data.items():
        setattr(expense,key,value)

    db.commit()
    return JSONResponse(status_code=200, content={'message' : 'Expense updated successfully'})



@app.delete("/delete_transactions/{expense_id}")
def delete_expenses(user : user_dependency, db : db_dependency, expense_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="User didnot loged in yet!!!")

    expense = db.query(Expenses).filter(Expenses.owner_id == user.get('id')).filter(Expenses.id == expense_id).first()

    if expense is None:
        raise HTTPException(status_code=404, detail='Expense Not Found')

    db.query(Expenses).filter(Expenses.owner_id == user.get('id')).filter(Expenses.id == expense_id).delete()

    db.commit()
    return JSONResponse(status_code=200, content={'message' : 'Expense deleted successfully'})



@app.get('/user_profile')
def get_user_profile(user : user_dependency, db : db_dependency):

    if user is None:
        raise HTTPException(status_code=401, detail="User didnot loged in yet!!!")
    
    return db.query(Users).filter(Users.id == user.get('id')).first()