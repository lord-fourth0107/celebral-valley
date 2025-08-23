from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from decimal import Decimal


class AccountStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FROZEN = "frozen"
    CLOSED = "closed"


class Account(BaseModel):
    id: str = Field(..., title="Account ID", description="Unique identifier for the account")
    user_id: str = Field(..., title="User ID", description="ID of the account owner")
    account_number: str = Field(..., title="Account Number", description="Unique account number")
    status: AccountStatus = Field(default=AccountStatus.ACTIVE, title="Status", description="Account status")
    loan_balance: Decimal = Field(default=Decimal('0.00'), title="Loan Balance", description="Current loan balance")
    invested_balance: Decimal = Field(default=Decimal('0.00'), title="Invested Balance", description="Current invested balance")
    interest_rate: Decimal = Field(default=Decimal('0.05'), title="Interest Rate", description="Annual interest rate (5% default)")
    created_at: datetime = Field(default_factory=datetime.utcnow, title="Created At", description="Account creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, title="Updated At", description="Last update timestamp")
    closed_at: Optional[datetime] = Field(None, title="Closed At", description="Account closure timestamp")
