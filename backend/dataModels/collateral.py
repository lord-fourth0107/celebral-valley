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
    DEFAULTED = "defaulted"


class CollateralBase(BaseModel):
    """Base collateral model with common fields"""
    user_id: str = Field(..., title="User ID", description="ID of the user who owns this collateral")
    loan_amount: Decimal = Field(..., title="Loan Amount", description="Amount of loan against this collateral", gt=0)
    loan_limit: Decimal = Field(..., title="Loan Limit", description="Maximum loan amount allowed against this collateral", gt=0)
    interest: Decimal = Field(..., title="Interest", description="Interest rate for the loan against this collateral")
    due_date: datetime = Field(..., title="Due Date", description="Due date for the collateral loan")
    images: Optional[List[str]] = Field([], title="Images", description="List of image URLs/paths for the collateral")
    metadata: Optional[dict] = Field(None, title="Metadata", description="Additional collateral metadata")


class CollateralCreateSimple(BaseModel):
    """Simplified model for creating a new collateral - only requires user_id"""
    user_id: str = Field(..., title="User ID", description="ID of the user who owns this collateral")


class CollateralCreateRequest(BaseModel):
    """Request model for creating a new collateral with basic info"""
    user_id: str = Field(..., title="User ID", description="ID of the user who owns this collateral")
    name: str = Field(..., title="Name", description="Name of the collateral", min_length=1, max_length=200)
    description: str = Field(..., title="Description", description="Description of the collateral", min_length=1, max_length=1000)
    images: Optional[List[str]] = Field([], title="Images", description="List of image URLs/paths for the collateral")


class CollateralCreate(CollateralBase):
    """Model for creating a new collateral with full data"""
    pass


class CollateralUpdate(BaseModel):
    """Model for updating a collateral - all fields optional"""
    loan_amount: Optional[Decimal] = Field(None, title="Loan Amount", description="Amount of loan against this collateral", gt=0)
    loan_limit: Optional[Decimal] = Field(None, title="Loan Limit", description="Maximum loan amount allowed against this collateral", gt=0)
    interest: Optional[Decimal] = Field(None, title="Interest", description="Interest rate for the loan against this collateral")
    due_date: Optional[datetime] = Field(None, title="Due Date", description="Due date for the collateral loan")
    status: Optional[CollateralStatus] = Field(None, title="Status", description="Collateral status")
    images: Optional[List[str]] = Field(None, title="Images", description="List of image URLs/paths for the collateral")
    metadata: Optional[dict] = Field(None, title="Metadata", description="Additional collateral metadata")


class CollateralApproveRequest(BaseModel):
    """Request model for approving a collateral and creating a loan"""
    loan_amount: Decimal = Field(..., title="Loan Amount", description="Amount to loan against this collateral", gt=0)


class Collateral(CollateralBase):
    """Complete collateral model with all fields"""
    id: str = Field(..., title="Collateral ID", description="Unique identifier for the collateral")
    status: CollateralStatus = Field(default=CollateralStatus.PENDING, title="Status", description="Collateral status")
    created_at: datetime = Field(..., title="Created At", description="Collateral creation timestamp")
    updated_at: datetime = Field(..., title="Last update timestamp", description="Last update timestamp")

    class Config:
        from_attributes = True


class CollateralResponse(Collateral):
    """Collateral response model - same as Collateral but for API responses"""
    pass


class CollateralListResponse(BaseModel):
    """Response model for listing collaterals"""
    collaterals: list[Collateral] = Field(..., title="Collaterals", description="List of collaterals")
    total: int = Field(..., title="Total", description="Total number of collaterals")
    page: int = Field(..., title="Page", description="Current page number")
    page_size: int = Field(..., title="Page Size", description="Number of collaterals per page")


class CollateralSearchParams(BaseModel):
    """Parameters for searching/filtering collaterals"""
    user_id: Optional[str] = Field(None, title="User ID", description="Filter by user ID")
    status: Optional[CollateralStatus] = Field(None, title="Status", description="Filter by status")
    page: int = Field(default=1, title="Page", description="Page number", ge=1)
    page_size: int = Field(default=20, title="Page Size", description="Number of collaterals per page", ge=1, le=100)


# New models for image analysis integration
class ImageAnalysisRequest(BaseModel):
    """Request model for analyzing an image for collateral assessment"""
    user_id: str = Field(..., title="User ID", description="ID of the user requesting the analysis")
    image_path: str = Field(..., title="Image Path", description="Path to the image file to analyze")
    user_description: Optional[str] = Field("", title="User Description", description="User's description of the item")
    top_k: Optional[int] = Field(3, title="Top K", description="Number of similar images to find", ge=1, le=10)
    score_threshold: Optional[float] = Field(0.0, title="Score Threshold", description="Minimum similarity score threshold")


class SimilarImageAnalysis(BaseModel):
    """Model for similar image analysis results"""
    name: str = Field(..., title="Name", description="Name of the similar image")
    type: str = Field(..., title="Type", description="Type/category of the item")
    user_description: str = Field(..., title="User Description", description="User description of the item")
    similarity_score: float = Field(..., title="Similarity Score", description="Similarity score with input image")
    initial_price: str = Field(..., title="Initial Price", description="Market price of the item")
    collateral_price: str = Field(..., title="Collateral Price", description="Conservative collateral value")
    currency: str = Field(..., title="Currency", description="Currency of the price")
    marketplace: str = Field(..., title="Marketplace", description="Marketplace where price was found")
    confidence: str = Field(..., title="Confidence", description="Confidence level of the analysis")


class InputImageAnalysis(BaseModel):
    """Model for input image analysis results"""
    image_path: str = Field(..., title="Image Path", description="Path to the analyzed image")
    user_description: str = Field(..., title="User Description", description="User's description of the item")
    product_name: str = Field(..., title="Product Name", description="Identified product name")
    initial_price: str = Field(..., title="Initial Price", description="Market price of the item")
    collateral_price: str = Field(..., title="Collateral Price", description="Conservative collateral value")
    currency: str = Field(..., title="Currency", description="Currency of the price")
    marketplace: str = Field(..., title="Marketplace", description="Marketplace where price was found")
    confidence: str = Field(..., title="Confidence", description="Confidence level of the analysis")
    collateral_explanation: Optional[str] = Field(None, title="Collateral Explanation", description="Brief explanation of collateral value calculation")


class ImageAnalysisSummary(BaseModel):
    """Model for analysis summary statistics"""
    total_images_processed: int = Field(..., title="Total Images Processed", description="Total number of images analyzed")
    successful_price_calculations: int = Field(..., title="Successful Price Calculations", description="Number of successful price calculations")
    failed_price_calculations: int = Field(..., title="Failed Price Calculations", description="Number of failed price calculations")
    success_rate: str = Field(..., title="Success Rate", description="Percentage of successful calculations")
    input_image_found: bool = Field(..., title="Input Image Found", description="Whether input image analysis was successful")
    similar_images_found: int = Field(..., title="Similar Images Found", description="Number of similar images found")


class ImageAnalysisResponse(BaseModel):
    """Response model for image analysis results"""
    input_image_analysis: InputImageAnalysis = Field(..., title="Input Image Analysis", description="Analysis results for the input image")
    similar_images_analysis: List[SimilarImageAnalysis] = Field(..., title="Similar Images Analysis", description="Analysis results for similar images")
    summary: ImageAnalysisSummary = Field(..., title="Summary", description="Summary statistics of the analysis")
    metadata: dict = Field(..., title="Metadata", description="Additional metadata about the analysis")
