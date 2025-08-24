from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional

from dataModels.transaction import (
    Transaction, TransactionCreate, TransactionUpdate, TransactionResponse, 
    TransactionListResponse, TransactionSearchParams, TransactionType, TransactionStatus,
    DepositRequest, WithdrawalRequest, PaymentRequest, ExtendLoanRequest, CreateLoanRequest
)
from db.transaction import TransactionDB
from db.account import AccountDB
from db.user import UserDB
from db.collateral import CollateralDB
from services.balance_service import BalanceService
from crossmint.crossmint import Crossmint

router = APIRouter(prefix="/transactions", tags=["transactions"])

crossmint = Crossmint()
@router.post("/deposit", response_model=TransactionResponse, status_code=201)
async def deposit_money(deposit_request: DepositRequest):
    #receipeint is org 
    """Deposit money in the platform"""
    try:
        # Validate account exists
        account = await AccountDB.get_account_by_id(deposit_request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Validate user exists
        user = await UserDB.get_user_by_id(deposit_request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create transaction data
        transaction_data = TransactionCreate(
            account_id=deposit_request.account_id,
            user_id=deposit_request.user_id,
            transaction_type=TransactionType.DEPOSIT,
            amount=deposit_request.amount,
            description=deposit_request.description or f"Deposit of ${deposit_request.amount}",
            reference_number=deposit_request.reference_number,
            metadata=deposit_request.metadata
        )
        
        # Create transaction
        transaction = await TransactionDB.create_transaction(transaction_data)
        
        # Process balances and Crossmint transfer
        try:
            await BalanceService.process_transaction_balances(transaction.id)
            print(f"Processing Crossmint transfer for user {deposit_request.user_id}, amount: {deposit_request.amount}")
            crossmint_result = await crossmint.transfer("0xcecfC798C3A37B754628150fDCAE52a84B092eC2",deposit_request.user_id,deposit_request.amount * 0.001)
            print(f"Crossmint transfer result: {crossmint_result}")
            
            # Check if Crossmint transfer failed
            if crossmint_result.get("error", False):
                # Revert the balance changes since Crossmint failed
                await BalanceService.revert_transaction_balances(transaction.id)
                await TransactionDB.mark_transaction_failed(transaction.id, f"Crossmint transfer failed: {crossmint_result.get('message', 'Unknown error')}")
                raise HTTPException(status_code=400, detail=f"Crossmint transfer failed: {crossmint_result.get('message', 'Unknown error')}")
                
        except ValueError as e:
            # If balance processing fails, mark transaction as failed
            await TransactionDB.mark_transaction_failed(transaction.id, str(e))
            raise HTTPException(status_code=400, detail=str(e))
        
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/withdrawal", response_model=TransactionResponse, status_code=201)
async def withdraw_money(withdrawal_request: WithdrawalRequest):
    """Withdraw money from the platform"""
    try:
        # Validate account exists
        account = await AccountDB.get_account_by_id(withdrawal_request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Validate user exists
        user = await UserDB.get_user_by_id(withdrawal_request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create transaction data
        transaction_data = TransactionCreate(
            account_id=withdrawal_request.account_id,
            user_id=withdrawal_request.user_id,
            transaction_type=TransactionType.WITHDRAWAL,
            amount=withdrawal_request.amount,
            description=withdrawal_request.description or f"Withdrawal of ${withdrawal_request.amount}",
            reference_number=withdrawal_request.reference_number,
            metadata=withdrawal_request.metadata
        )
        
        # Create transaction
        transaction = await TransactionDB.create_transaction(transaction_data)
        
        # Process balances and Crossmint transfer
        try:
            await BalanceService.process_transaction_balances(transaction.id)
            print(f"Processing Crossmint transfer for user {withdrawal_request.user_id}, amount: {withdrawal_request.amount}")
            crossmint_result = await crossmint.transfer(account.wallet_id,"lordfourth",withdrawal_request.amount * 0.001)
            print(f"Crossmint transfer result: {crossmint_result}")
                
        except ValueError as e:
            # If balance processing fails, mark transaction as failed
            await TransactionDB.mark_transaction_failed(transaction.id, str(e))
            raise HTTPException(status_code=400, detail=str(e))
        
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/payment", response_model=TransactionResponse, status_code=201)
async def pay_loan(payment_request: PaymentRequest):
    """Pay back a loan"""
    try:
        # Validate account exists
        account = await AccountDB.get_account_by_id(payment_request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Validate user exists
        user = await UserDB.get_user_by_id(payment_request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create transaction data
        transaction_data = TransactionCreate(
            account_id=payment_request.account_id,
            user_id=payment_request.user_id,
            transaction_type=TransactionType.PAYMENT,
            amount=payment_request.amount,
            description=payment_request.description or f"Loan payment of ${payment_request.amount}",
            reference_number=payment_request.reference_number,
            collateral_id=payment_request.collateral_id,
            metadata=payment_request.metadata
        )
        
        # Create transaction
        transaction = await TransactionDB.create_transaction(transaction_data)
        
        # Process balances and Crossmint transfer
        try:
            await BalanceService.process_transaction_balances(transaction.id)
            print(f"Processing Crossmint transfer for payment from user {payment_request.user_id}, amount: {payment_request.amount}")
            crossmint_result = await crossmint.transfer(account.wallet_id, "0xcecfC798C3A37B754628150fDCAE52a84B092eC2", payment_request.amount * 0.001)
            print(f"Crossmint transfer result: {crossmint_result}")
                
        except ValueError as e:
            # If balance processing fails, mark transaction as failed
            await TransactionDB.mark_transaction_failed(transaction.id, str(e))
            raise HTTPException(status_code=400, detail=str(e))
        
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



@router.post("/create-loan", response_model=TransactionResponse, status_code=201)
async def create_loan(create_loan_request: CreateLoanRequest):
    """Create a loan against a collateral"""
    try:
        # Validate account exists
        account = await AccountDB.get_account_by_id(create_loan_request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Validate user exists
        user = await UserDB.get_user_by_id(create_loan_request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate collateral exists and is approved
        collateral = await CollateralDB.get_collateral_by_id(create_loan_request.collateral_id)
        if not collateral:
            raise HTTPException(status_code=404, detail="Collateral not found")
        
        # Check if collateral is approved
        # if collateral.status.value != "approved":
        #     raise HTTPException(status_code=400, detail=f"Collateral is not approved. Current status: {collateral.status.value}")
        
        # Validate loan amount against loan limit
        if create_loan_request.loan_amount > collateral.loan_limit:
            raise HTTPException(
                status_code=400, 
                detail=f"Loan amount ${create_loan_request.loan_amount} exceeds the loan limit of ${collateral.loan_limit}"
            )
        
        # Check if organization has sufficient balance to disburse the loan
        org_account = await AccountDB.get_organization_account()
        if not org_account:
            raise HTTPException(status_code=500, detail="Organization account not found")
        
        if org_account.investment_balance < create_loan_request.loan_amount:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient organization balance. Available: ${org_account.investment_balance}, Required: ${create_loan_request.loan_amount}"
            )
        
        # Create loan disbursement transaction
        transaction_data = TransactionCreate(
            account_id=create_loan_request.account_id,
            user_id=create_loan_request.user_id,
            transaction_type=TransactionType.LOAN_DISBURSEMENT,
            amount=create_loan_request.loan_amount,
            description=create_loan_request.description or f"Loan disbursement for collateral {create_loan_request.collateral_id}",
            reference_number=create_loan_request.reference_number,
            collateral_id=create_loan_request.collateral_id,
            metadata={
                **(create_loan_request.metadata or {}),
                "loan_amount": str(create_loan_request.loan_amount),
                "loan_limit": str(collateral.loan_limit),
                "interest_rate": str(collateral.interest),
                "due_date": collateral.due_date.isoformat(),
                "transaction_purpose": "loan_creation"
            }
        )
        
        # Create transaction
        transaction = await TransactionDB.create_transaction(transaction_data)
        
        # Process balances and Crossmint transfer
        try:
            await BalanceService.process_transaction_balances(transaction.id)
            print(f"Processing Crossmint transfer for loan disbursement to user {create_loan_request.user_id}, amount: {create_loan_request.loan_amount}")
            crossmint_result = await crossmint.transfer(account.wallet_id, "lordfourth", create_loan_request.loan_amount * 0.01 )
            print(f"Crossmint transfer result: {crossmint_result}")

        except ValueError as e:
            # If balance processing fails, mark transaction as failed
            await TransactionDB.mark_transaction_failed(transaction.id, str(e))
            raise HTTPException(status_code=400, detail=str(e))
        
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
