from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from decimal import Decimal


class TransactionType(str, Enum):
    # Investment transactions
    DEPOSIT = "deposit"                      # Debit - Money invested in platform
    WITHDRAWAL = "withdrawal"                # Credit - Money withdrawn from platform
    INTEREST = "interest"                    # Credit - Interest earned on investment
    
    # Loan transactions
    LOAN_DISBURSEMENT = "loan_disbursement"  # Credit - Loan amount disbursed to borrower
    PAYMENT = "payment"                      # Debit - Loan payment made by borrower
    FEE = "fee"                             # Debit - Various fees charged


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"


class TransactionBase(BaseModel):
    """Base transaction model with common fields"""
    account_id: str = Field(..., title="Account ID", description="ID of the account involved")
    user_id: str = Field(..., title="User ID", description="ID of the user making the transaction")
    transaction_type: TransactionType = Field(..., title="Transaction Type", description="Type of transaction")
    amount: Decimal = Field(..., title="Amount", description="Transaction amount")
    description: Optional[str] = Field(None, title="Description", description="Transaction description")
    reference_number: Optional[str] = Field(None, title="Reference Number", description="External reference number")
    collateral_id: Optional[str] = Field(None, title="Collateral ID", description="ID of collateral for loan-related transactions")
    metadata: Optional[dict] = Field(None, title="Metadata", description="Additional transaction metadata")


class TransactionCreate(TransactionBase):
    """Model for creating a new transaction"""
    loan_balance_before: Optional[Decimal] = Field(None, title="Loan Balance Before", description="Loan balance before transaction")
    loan_balance_after: Optional[Decimal] = Field(None, title="Loan Balance After", description="Loan balance after transaction")
    invested_balance_before: Optional[Decimal] = Field(None, title="Invested Balance Before", description="Invested balance before transaction")
    invested_balance_after: Optional[Decimal] = Field(None, title="Invested Balance After", description="Invested balance after transaction")


class TransactionUpdate(BaseModel):
    """Model for updating a transaction - all fields optional"""
    status: Optional[TransactionStatus] = Field(None, title="Status", description="Transaction status")
    description: Optional[str] = Field(None, title="Description", description="Transaction description")
    reference_number: Optional[str] = Field(None, title="Reference Number", description="External reference number")
    metadata: Optional[dict] = Field(None, title="Metadata", description="Additional transaction metadata")
    processed_at: Optional[datetime] = Field(None, title="Processed At", description="Transaction processing timestamp")
    failed_at: Optional[datetime] = Field(None, title="Failed At", description="Transaction failure timestamp")
    failure_reason: Optional[str] = Field(None, title="Failure Reason", description="Reason for transaction failure")


class Transaction(TransactionBase):
    """Complete transaction model with all fields"""
    id: str = Field(..., title="Transaction ID", description="Unique identifier for the transaction")
    status: TransactionStatus = Field(default=TransactionStatus.PENDING, title="Status", description="Transaction status")
    loan_balance_before: Optional[Decimal] = Field(None, title="Loan Balance Before", description="Loan balance before transaction")
    loan_balance_after: Optional[Decimal] = Field(None, title="Loan Balance After", description="Loan balance after transaction")
    invested_balance_before: Optional[Decimal] = Field(None, title="Invested Balance Before", description="Invested balance before transaction")
    invested_balance_after: Optional[Decimal] = Field(None, title="Invested Balance After", description="Invested balance after transaction")
    created_at: datetime = Field(..., title="Created At", description="Transaction creation timestamp")
    updated_at: datetime = Field(..., title="Updated At", description="Last update timestamp")
    processed_at: Optional[datetime] = Field(None, title="Processed At", description="Transaction processing timestamp")
    failed_at: Optional[datetime] = Field(None, title="Failed At", description="Transaction failure timestamp")
    failure_reason: Optional[str] = Field(None, title="Failure Reason", description="Reason for transaction failure")

    class Config:
        from_attributes = True


class TransactionResponse(Transaction):
    """Transaction response model - same as Transaction but for API responses"""
    pass


class TransactionListResponse(BaseModel):
    """Response model for listing transactions"""
    transactions: list[Transaction] = Field(..., title="Transactions", description="List of transactions")
    total: int = Field(..., title="Total", description="Total number of transactions")
    page: int = Field(..., title="Page", description="Current page number")
    page_size: int = Field(..., title="Page Size", description="Number of transactions per page")


class TransactionSearchParams(BaseModel):
    """Parameters for searching/filtering transactions"""
    account_id: Optional[str] = Field(None, title="Account ID", description="Filter by account ID")
    user_id: Optional[str] = Field(None, title="User ID", description="Filter by user ID")
    transaction_type: Optional[TransactionType] = Field(None, title="Transaction Type", description="Filter by transaction type")
    status: Optional[TransactionStatus] = Field(None, title="Status", description="Filter by status")
    reference_number: Optional[str] = Field(None, title="Reference Number", description="Filter by reference number")
    page: int = Field(default=1, title="Page", description="Page number", ge=1)
    page_size: int = Field(default=20, title="Page Size", description="Number of transactions per page", ge=1, le=100)


# Specific transaction request models
class DepositRequest(BaseModel):
    """Request model for deposit transaction"""
    account_id: str = Field(..., title="Account ID", description="ID of the account to deposit to")
    user_id: str = Field(..., title="User ID", description="ID of the user making the deposit")
    amount: Decimal = Field(..., title="Amount", description="Amount to deposit", gt=0)
    description: Optional[str] = Field(None, title="Description", description="Deposit description")
    reference_number: Optional[str] = Field(None, title="Reference Number", description="External reference number")
    metadata: Optional[dict] = Field(None, title="Metadata", description="Additional deposit metadata")


class WithdrawalRequest(BaseModel):
    """Request model for withdrawal transaction"""
    account_id: str = Field(..., title="Account ID", description="ID of the account to withdraw from")
    user_id: str = Field(..., title="User ID", description="ID of the user making the withdrawal")
    amount: Decimal = Field(..., title="Amount", description="Amount to withdraw", gt=0)
    description: Optional[str] = Field(None, title="Description", description="Withdrawal description")
    reference_number: Optional[str] = Field(None, title="Reference Number", description="External reference number")
    metadata: Optional[dict] = Field(None, title="Metadata", description="Additional withdrawal metadata")


class PaymentRequest(BaseModel):
    """Request model for payment transaction"""
    account_id: str = Field(..., title="Account ID", description="ID of the account making the payment")
    user_id: str = Field(..., title="User ID", description="ID of the user making the payment")
    amount: Decimal = Field(..., title="Amount", description="Payment amount", gt=0)
    collateral_id: Optional[str] = Field(None, title="Collateral ID", description="ID of the collateral being paid for")
    description: Optional[str] = Field(None, title="Description", description="Payment description")
    reference_number: Optional[str] = Field(None, title="Reference Number", description="External reference number")
    metadata: Optional[dict] = Field(None, title="Metadata", description="Additional payment metadata")


class ExtendLoanRequest(BaseModel):
    """Request model for loan extension transaction - creates a fee transaction"""
    account_id: str = Field(..., title="Account ID", description="ID of the account extending the loan")
    user_id: str = Field(..., title="User ID", description="ID of the user extending the loan")
    collateral_id: str = Field(..., title="Collateral ID", description="ID of the collateral to extend")
    extension_days: int = Field(..., title="Extension Days", description="Number of days to extend the loan", gt=0)
    fee: Decimal = Field(..., title="Extension Fee", description="Fee for extending the loan", gt=0)
    description: Optional[str] = Field(None, title="Description", description="Extension description")
    reference_number: Optional[str] = Field(None, title="Reference Number", description="External reference number")
    metadata: Optional[dict] = Field(None, title="Metadata", description="Additional extension metadata")


class CreateLoanRequest(BaseModel):
    """Request model for creating a loan against a collateral"""
    account_id: str = Field(..., title="Account ID", description="ID of the account receiving the loan")
    user_id: str = Field(..., title="User ID", description="ID of the user receiving the loan")
    collateral_id: str = Field(..., title="Collateral ID", description="ID of the collateral to loan against")
    loan_amount: Decimal = Field(..., title="Loan Amount", description="Amount to loan against the collateral", gt=0)
    description: Optional[str] = Field(None, title="Description", description="Loan description")
    reference_number: Optional[str] = Field(None, title="Reference Number", description="External reference number")
    metadata: Optional[dict] = Field(None, title="Metadata", description="Additional loan metadata")
