from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from fastapi.responses import Response

app = FastAPI()

BALANCE = {}

class OperationsRequest(BaseModel):
    wallet_name: str = Field(..., max_length=127)
    amount: float
    description: str | None = Field(None, max_length=255)

    @field_validator('amount')
    def amount_must_be_positive(cls, v:float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v
    
    @field_validator('wallet_name')
    def wallet_name_not_empty(cls, v: str) -> str:
        # removing edge spaces
        v = v.strip()

        if not v:
            raise ValueError("Value must be not empty")
        
        return v
    

class CreateWalletRequest(BaseModel):
    name: str = Field(..., max_length=127)
    initial_balance: float = 0

    @field_validator('initial_balance')
    def balance_not_negative(cls, v:float) -> float:
        if v < 0:
            raise ValueError("Amount must nonnegative")
        return v
    
    @field_validator('name')
    def name_not_empty(cls, v: str) -> str:
        # removing edge spaces
        v = v.strip()

        if not v:
            raise ValueError("Value must be not empty")
        
        return v



@app.get("/balance")
def get_balance(wallet_name: str | None = None):
    # if name is not mentioned show total
    if wallet_name is None:
        return {"total_balance": sum(BALANCE.values())}

    if wallet_name not in BALANCE:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet '{wallet_name}' not found"
        )

    return {"wallet": wallet_name, "balance": BALANCE[wallet_name]}

@app.post("/wallets")
def create_wallet(wallet: CreateWalletRequest):
    if wallet.name in BALANCE:
        raise HTTPException(
            status_code=400,
            detail=f"Wallet exists"
        )
    BALANCE[wallet.name] = wallet.initial_balance
    return {
        "message": f"Wallet created",
        "wallet": wallet.name,
        "balance": BALANCE[wallet.name]
    }

@app.post("/operations/income")
def add_income(operation: OperationsRequest):
    # ? exist
    if operation.wallet_name not in BALANCE:
        raise HTTPException(
            status_code=404,
            detail=f"wallet doesn't exist"
        )

    # add value to wallet
    BALANCE[operation.wallet_name] += operation.amount

    # return msg
    return {
        "message": f"Income operation added to wallet",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "desc": operation.description,
        "new_balance": BALANCE[operation.wallet_name]
    }


@app.post("/operations/expense")
def add_expense(operation: OperationsRequest):
    if operation.wallet_name not in BALANCE:
        raise HTTPException(
            status_code=404,
            detail=f"wallet doesn't exist"
        )
    
    if(BALANCE[operation.wallet_name] < operation.amount):
        raise HTTPException(
            status_code=400,
            detail=f"insufficient funds: Available: {BALANCE[operation.amount]}"
        )
    
    BALANCE[operation.wallet_name] -= operation.amount

    return {
        "message": f"Expense operation done",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "desc": operation.description,
        "new_balance": BALANCE[operation.wallet_name]
    }


# def receive_money(name: str, amount: int):
#     # if absent -> 0
#     if name not in BALANCE:
#         BALANCE[name] = 0

#     BALANCE[name] += amount

#     return {
#         "message": f"Added {amount} to {name}",
#         "wallet": name,
#         "new_balance": BALANCE[name]
#     }
