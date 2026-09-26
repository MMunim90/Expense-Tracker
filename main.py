from fastapi import FastAPI, HTTPException, Path
import json

app = FastAPI()

def load_data():
    with open('expenses.json', 'r') as f:
        data = json.load(f)
    return data

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