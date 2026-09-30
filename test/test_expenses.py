from test.test_main import client
from main import app
from fastapi import status
from router.auth import get_current_user
from database import SessionLocal
from models import Expenses

def override_get_current_user():
    return {
        'id' : 10,
        'username' : 'testuser'
    }
    
    
def test_expense():
    db = SessionLocal()
    
    # remove old test data if its exists
    db.query(Expenses).filter(Expenses.id == 1011).delete()
    
    expense = Expenses(
        id = 1011,
        title = 'Testing',
        amount = 540,
        type = 'income',
        category = 'Testing',
        date = '2026-01-01',
        owner_id = 10
    )
    
    db.add(expense)
    db.commit()

app.dependency_overrides[get_current_user] = override_get_current_user

def test_view_all_expenses():
    response = client.get('/transactions')
    assert response.status_code == status.HTTP_200_OK
    
    
def test_view_specific_expenses():
    response = client.get('/transactions/1011')
    assert response.status_code == status.HTTP_200_OK
    
    
def test_create_expenses():
    db = SessionLocal()
    db.query(Expenses).filter(Expenses.id == 500).delete()
    db.commit()
    
    request_data = {
        "id": 500,
        "title": "string",
        "amount": 770,
        "type": 'income',
        "category": 'string',
        "date": '2026-01-01',
    }
    response = client.post('/transactions', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {'message' : 'Expense created successfully'}
    
    
    
def test_update_expenses():
    request_data = {
        "title": "Testing updated",
    }
    response = client.put('/transactions/1011', json=request_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message' : 'Expense updated successfully'}
    
    
    
def test_delete_expenses():
    response = client.delete('/transactions/1011')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message' : 'Expense deleted successfully'}