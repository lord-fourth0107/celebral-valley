from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal


class CollateralStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    RELEASED = "released"


class Collateral(BaseModel):
    id: str = Field(..., title="Collateral ID", description="Unique identifier for the collateral")
    user_id: str = Field(..., title="User ID", description="ID of the collateral owner")
    status: CollateralStatus = Field(default=CollateralStatus.PENDING, title="Status", description="Collateral status")
    loan_amount: Decimal = Field(..., title="Loan Amount", description="Amount of loan against this collateral")
    loan_limit: Decimal = Field(..., title="Loan Limit", description="Maximum loan amount allowed against this collateral")
    interest: Decimal = Field(..., title="Interest", description="Interest rate for the loan against this collateral")
    metadata: Optional[dict] = Field(None, title="Metadata", description="Additional collateral metadata")
