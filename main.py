from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import models
from models import Users, Expense
from database import engine, SessionLocal
from fastapi.responses import JSONResponse
from router import auth, admin
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
    amount: Annotated[Optional[int], Field(default=None)]
    type: Annotated[Optional[str], Field(default=None)]
    category: Annotated[Optional[str], Field(default=None)]
    date: Annotated[Optional[str], Field(default=None)]



models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(admin.router)

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


@app.get("/view")
def view_expenses(user : user_dependency, db : db_dependency):

    if user is None:
        raise HTTPException(status_code=401, detail="User didnot loged in yet!!!")
    
    return db.query(Expense).filter(Expense.owner_id == user.get('id')).all()

@app.get("/view/{expense_id}")
def view_specific_expenses(user : user_dependency, db : db_dependency, expense_id: int = Path(..., description='Id of the expenses', example='1')):
    if user is None:
        raise HTTPException(status_code=401, detail="User didnot loged in yet!!!")
    
    specific_expense = db.query(Expense).filter(Expense.owner_id == user.get('id')).filter(Expense.id == expense_id).first()

    if specific_expense is not None:
        return specific_expense
    else:
        raise HTTPException(status_code=404, detail='Expense Not Found')
    
    
@app.get("/sort")
def view_sorted_expenses(sorted_by: str, order: str):
    data = load_data()
    sorted_data = list(data.values())
    if order == 'asc':
        sorted_data.sort(key = lambda x: x[sorted_by])
    else:
        sorted_data.sort(key = lambda x: x[sorted_by], reverse=True)
    return sorted_data


@app.post("/create")
def create_expenses(expense: Expense):
    data = load_data()
    if expense.id in data:
        raise HTTPException(status_code=400, detail="Expense id already exists")
    data[expense.id] = expense.model_dump(exclude=['id'])
    save_data(data)
    raise HTTPException(status_code=200, detail="Expense created successfully!!!")
    
    

@app.put("/edit-expenses/{expense_id}")
def update_expenses(expense_id: int, expense: UpdateExpense):
    data = load_data()
    if expense_id not in data:
        raise HTTPException(status_code=404, detail="Expense not found!!!")
    data[expense_id].update(expense.model_dump(exclude_unset=True))
    save_data(data)
    raise HTTPException(status_code=200, detail="Expense updated successfully!!!")



@app.delete("/delete-expenses/{expense_id}")
def delete_expenses(expense_id: int):
    data = load_data()
    if expense_id not in data:
        raise HTTPException(status_code=404, detail="Expense not found!!!")
    del data[expense_id]
    save_data(data)
    raise HTTPException(status_code=200, detail="Expense deleted successfully!!!")