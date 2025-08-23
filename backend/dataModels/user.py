from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    VERIFIER = "verifier"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_VERIFICATION = "pending_verification"


class User(BaseModel):
    id: str = Field(..., title="User ID", description="Unique identifier for the user")
    email: str = Field(..., title="Email", description="User's email address")
    username: str = Field(..., title="Username", description="Unique username for the user")
    first_name: str = Field(..., title="First Name", description="User's first name")
    last_name: str = Field(..., title="Last Name", description="User's last name")
    phone: Optional[str] = Field(None, title="Phone", description="User's phone number")
    date_of_birth: Optional[datetime] = Field(None, title="Date of Birth", description="User's date of birth")
    address: Optional[str] = Field(None, title="Address", description="User's residential address")
    city: Optional[str] = Field(None, title="City", description="User's city")
    state: Optional[str] = Field(None, title="State", description="User's state/province")
    country: Optional[str] = Field(None, title="Country", description="User's country")
    postal_code: Optional[str] = Field(None, title="Postal Code", description="User's postal code")
    role: UserRole = Field(..., title="Role", description="User's role in the system")
    status: UserStatus = Field(default=UserStatus.PENDING_VERIFICATION, title="Status", description="User's account status")
    kyc_verified: bool = Field(default=False, title="KYC Verified", description="Whether user's KYC is verified")
    created_at: datetime = Field(default_factory=datetime.utcnow, title="Created At", description="Account creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, title="Updated At", description="Last update timestamp")

