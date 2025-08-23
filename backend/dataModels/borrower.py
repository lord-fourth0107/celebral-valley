from pydantic import BaseModel, Field


class Borrower(BaseModel):
    name: str = Field(..., title="Borrower name", description="The name of the borrower"  )
    email: str = Field(..., title="Borrower email", description="The email of the borrower"  )
    phone:  str = Field(..., title="Borrower phone", description="The phone number of the borrower"  )
    current_loan : str = Field(..., title="Current loan", description="The current loan of the borrower")
    max_allowed_loan : str = Field(..., title="Max allowed loan", description="The max loan of the borrower")
