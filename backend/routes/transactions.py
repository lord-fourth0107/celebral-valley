from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional

from dataModels.transaction import (
    Transaction, TransactionCreate, TransactionUpdate, TransactionResponse, 
    TransactionListResponse, TransactionSearchParams, TransactionType, TransactionStatus,
    InvestRequest, WithdrawRequest, PayLoanRequest, ExtendLoanRequest
)
from db.transaction import TransactionDB
from db.account import AccountDB
from db.user import UserDB

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/invest", response_model=TransactionResponse, status_code=201)
async def invest_money(invest_request: InvestRequest):
    """Invest money in the platform"""
    try:
        # Validate account exists
        account = await AccountDB.get_account_by_id(invest_request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Validate user exists
        user = await UserDB.get_user_by_id(invest_request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create transaction data
        transaction_data = TransactionCreate(
            account_id=invest_request.account_id,
            user_id=invest_request.user_id,
            transaction_type=TransactionType.INVEST,
            amount=invest_request.amount,
            description=invest_request.description or f"Investment of ${invest_request.amount}",
            reference_number=invest_request.reference_number,
            metadata=invest_request.metadata
        )
        
        # TODO: Add business logic here (e.g., check available balance, update account balances)
        
        transaction = await TransactionDB.create_transaction(transaction_data)
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/withdraw", response_model=TransactionResponse, status_code=201)
async def withdraw_money(withdraw_request: WithdrawRequest):
    """Withdraw money from the platform"""
    try:
        # Validate account exists
        account = await AccountDB.get_account_by_id(withdraw_request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Validate user exists
        user = await UserDB.get_user_by_id(withdraw_request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create transaction data
        transaction_data = TransactionCreate(
            account_id=withdraw_request.account_id,
            user_id=withdraw_request.user_id,
            transaction_type=TransactionType.WITHDRAW,
            amount=withdraw_request.amount,
            description=withdraw_request.description or f"Withdrawal of ${withdraw_request.amount}",
            reference_number=withdraw_request.reference_number,
            metadata=withdraw_request.metadata
        )
        
        # TODO: Add business logic here (e.g., check available balance, update account balances)
        
        transaction = await TransactionDB.create_transaction(transaction_data)
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/pay-loan", response_model=TransactionResponse, status_code=201)
async def pay_loan(pay_loan_request: PayLoanRequest):
    """Pay back a loan"""
    try:
        # Validate account exists
        account = await AccountDB.get_account_by_id(pay_loan_request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Validate user exists
        user = await UserDB.get_user_by_id(pay_loan_request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create transaction data
        transaction_data = TransactionCreate(
            account_id=pay_loan_request.account_id,
            user_id=pay_loan_request.user_id,
            transaction_type=TransactionType.PAY_LOAN,
            amount=pay_loan_request.amount,
            description=pay_loan_request.description or f"Loan payment of ${pay_loan_request.amount}",
            reference_number=pay_loan_request.reference_number,
            collateral_id=pay_loan_request.collateral_id,
            metadata=pay_loan_request.metadata
        )
        
        # TODO: Add business logic here (e.g., validate loan exists, check payment amount, update loan balance)
        
        transaction = await TransactionDB.create_transaction(transaction_data)
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/extend-loan", response_model=TransactionResponse, status_code=201)
async def extend_loan(extend_loan_request: ExtendLoanRequest):
    """Extend a loan"""
    try:
        # Validate account exists
        account = await AccountDB.get_account_by_id(extend_loan_request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Validate user exists
        user = await UserDB.get_user_by_id(extend_loan_request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create transaction data with extension fee as amount
        amount = extend_loan_request.fee or 0
        transaction_data = TransactionCreate(
            account_id=extend_loan_request.account_id,
            user_id=extend_loan_request.user_id,
            transaction_type=TransactionType.EXTEND_LOAN,
            amount=amount,
            description=extend_loan_request.description or f"Loan extension for {extend_loan_request.extension_days} days",
            reference_number=extend_loan_request.reference_number,
            collateral_id=extend_loan_request.collateral_id,
            metadata={
                **(extend_loan_request.metadata or {}),
                "extension_days": extend_loan_request.extension_days,
                "extension_fee": str(extend_loan_request.fee) if extend_loan_request.fee else None
            }
        )
        
        # TODO: Add business logic here (e.g., validate loan exists, check if extension is allowed, update loan due date)
        
        transaction = await TransactionDB.create_transaction(transaction_data)
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/", response_model=TransactionListResponse)
async def list_transactions(
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    status: Optional[TransactionStatus] = Query(None, description="Filter by status"),
    reference_number: Optional[str] = Query(None, description="Filter by reference number"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of transactions per page")
):
    """Get all transactions with filtering and pagination"""
    try:
        search_params = TransactionSearchParams(
            account_id=account_id,
            user_id=user_id,
            transaction_type=transaction_type,
            status=status,
            reference_number=reference_number,
            page=page,
            page_size=page_size
        )
        
        result = await TransactionDB.list_transactions(search_params)
        return TransactionListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str):
    """Get a specific transaction by ID"""
    try:
        transaction = await TransactionDB.get_transaction_by_id(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/account/{account_id}", response_model=List[TransactionResponse])
async def get_transactions_by_account(account_id: str):
    """Get all transactions for an account"""
    try:
        # Validate account exists
        account = await AccountDB.get_account_by_id(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        transactions = await TransactionDB.get_transactions_by_account_id(account_id)
        return transactions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/user/{user_id}", response_model=List[TransactionResponse])
async def get_transactions_by_user(user_id: str):
    """Get all transactions for a user"""
    try:
        # Validate user exists
        user = await UserDB.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        transactions = await TransactionDB.get_transactions_by_user_id(user_id)
        return transactions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/type/{transaction_type}", response_model=List[TransactionResponse])
async def get_transactions_by_type(transaction_type: TransactionType):
    """Get all transactions by type"""
    try:
        transactions = await TransactionDB.get_transactions_by_type(transaction_type)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/user/{user_id}/summary")
async def get_user_transaction_summary(user_id: str):
    """Get transaction summary for a user"""
    try:
        # Validate user exists
        user = await UserDB.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        summary = await TransactionDB.get_transaction_summary_by_user(user_id)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
