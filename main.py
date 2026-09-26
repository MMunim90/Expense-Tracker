from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field
from typing import Annotated, Optional
import json

app = FastAPI()

class Expense(BaseModel):
    id: Annotated[str, Field(..., description='Id of the expenses', example='E001')]
    name: Annotated[str, Field(..., description='Name of the expenses', example='Lunch')]
    amount: Annotated[int, Field(..., description='Amount of the expenses', example='500')]
    category: Annotated[str, Field(..., description='Category of the expenses', example='Food')]
    date: Annotated[str, Field(..., description='Date of the expenses', example='2026-09-05')]
    description: Annotated[str, Field(..., description='Description of the expenses', example='Lunch at Restaurant')]


class UpdateExpense(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    amount: Annotated[Optional[int], Field(default=None)]
    category: Annotated[Optional[str], Field(default=None)]
    date: Annotated[Optional[str], Field(default=None)]
    description: Annotated[Optional[str], Field(default=None)]



def load_data():
    with open('expenses.json', 'r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('expenses.json', 'w') as f:
        json.dump(data, f)

@app.get("/")
def main():
    return "Expense Tracker Backend"


@app.get("/view")
def view_expenses():
    data = load_data()
    return data

@app.get("/view/{expense_id}")
def view_specific_expenses(expense_id: str = Path(..., description='Id of the expenses', example='E001')):
    data = load_data()
    if expense_id in data:
        return data[expense_id]
    else:
        raise HTTPException(status_code=404, detail="Expenses not found!!!")
    
    
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
def update_expenses(expense_id: str, expense: UpdateExpense):
    data = load_data()
    if expense_id not in data:
        raise HTTPException(status_code=404, detail="Expense not found!!!")
    data[expense_id].update(expense.model_dump(exclude_unset=True))
    save_data(data)
    raise HTTPException(status_code=200, detail="Expense updated successfully!!!")