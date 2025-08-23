from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from decimal import Decimal


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    INTEREST = "interest"
    LOAN_DISBURSEMENT = "loan_disbursement"
    PAYMENT = "payment"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"


class Transaction(BaseModel):
    id: str = Field(..., title="Transaction ID", description="Unique identifier for the transaction")
    account_id: str = Field(..., title="Account ID", description="ID of the account involved")
    user_id: str = Field(..., title="User ID", description="ID of the user making the transaction")
    transaction_type: TransactionType = Field(..., title="Transaction Type", description="Type of transaction")
    status: TransactionStatus = Field(default=TransactionStatus.PENDING, title="Status", description="Transaction status")
    amount: Decimal = Field(..., title="Amount", description="Transaction amount")
    description: Optional[str] = Field(None, title="Description", description="Transaction description")
    reference_number: Optional[str] = Field(None, title="Reference Number", description="External reference number")
    collateral_id: Optional[str] = Field(None, title="Collateral ID", description="ID of collateral for loan-related transactions")
    loan_balance_before: Optional[Decimal] = Field(None, title="Loan Balance Before", description="Loan balance before transaction")
    loan_balance_after: Optional[Decimal] = Field(None, title="Loan Balance After", description="Loan balance after transaction")
    invested_balance_before: Optional[Decimal] = Field(None, title="Invested Balance Before", description="Invested balance before transaction")
    invested_balance_after: Optional[Decimal] = Field(None, title="Invested Balance After", description="Invested balance after transaction")
    metadata: Optional[dict] = Field(None, title="Metadata", description="Additional transaction metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, title="Created At", description="Transaction creation timestamp")
    processed_at: Optional[datetime] = Field(None, title="Processed At", description="Transaction processing timestamp")
    failed_at: Optional[datetime] = Field(None, title="Failed At", description="Transaction failure timestamp")
    failure_reason: Optional[str] = Field(None, title="Failure Reason", description="Reason for transaction failure")
