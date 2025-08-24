from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import List, Optional
from datetime import datetime, timedelta
import base64
import re
import os
import uuid

from dataModels.collateral import (
    Collateral, CollateralCreateRequest, CollateralCreateSimple, CollateralUpdate, CollateralResponse, 
    CollateralListResponse, CollateralSearchParams, CollateralStatus, CollateralApproveRequest,
    ImageAnalysisRequest, ImageAnalysisResponse
)
from dataModels.transaction import (
    TransactionCreate, TransactionType, ExtendLoanRequest, TransactionResponse
)
from db.collateral import CollateralDB
from db.user import UserDB
from db.account import AccountDB
from db.transaction import TransactionDB
from services.balance_service import BalanceService
from rag3_llampi_integration import integrate_rag3_with_llampi

router = APIRouter(prefix="/collaterals", tags=["collaterals"])


@router.post("/analyze-image", response_model=ImageAnalysisResponse, status_code=200)
async def analyze_image_for_collateral(request: ImageAnalysisRequest):
    """Analyze an image for collateral assessment using RAG3-LLAMPI integration"""
    try:
        # Validate user exists
        user = await UserDB.get_user_by_id(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Run the RAG3-LLAMPI integration
        results = integrate_rag3_with_llampi(
            input_image_path=request.image_path,
            user_description=request.user_description,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            verbose=False,  # No console output for API
            return_json=True  # Return JSON format
        )
        
        if "error" in results:
            raise HTTPException(status_code=500, detail=f"Analysis failed: {results['error']}")
        
        # Convert the results to match our response model
        # The results are already in JSON format from the integration
        return ImageAnalysisResponse(**results)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.post("/", response_model=CollateralResponse, status_code=201)
async def create_collateral(collateral_data: CollateralCreateRequest):
    """Create a new collateral with RAG3 image analysis and LLM pricing"""
    try:
        # Validate user exists
        user = await UserDB.get_user_by_id(collateral_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not collateral_data.images:
            raise HTTPException(status_code=400, detail="No images provided")
        
        # Initialize RAG3 system for image analysis
        try:
            from rag3 import ImageRAGSystem
            rag_system = ImageRAGSystem()
            print(f"✅ RAG3 system initialized for user {collateral_data.user_id}")
        except Exception as e:
            print(f"❌ Failed to initialize RAG3 system: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize image analysis system: {str(e)}")
        
        # Initialize LLM client for pricing
        try:
            from llmapi import AnthropicClient
            llm_client = AnthropicClient()
            print(f"✅ LLM client initialized for pricing analysis")
        except Exception as e:
            print(f"❌ Failed to initialize LLM client: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize pricing system: {str(e)}")
        
        # Process each image through RAG3 and get pricing
        image_analyses = []
        total_estimated_value = 0.0
        
        for i, image_path in enumerate(collateral_data.images):
            try:
                print(f"🔍 Processing image {i+1}/{len(collateral_data.images)}: {image_path}")
                
                # Step 1: Find similar images using RAG3
                similar_images = rag_system.find_similar_images(
                    query_image_source=image_path,
                    top_k=3,
                    score_threshold=0.7,
                    exclude_query_image=True
                )
                print(f"   Found {len(similar_images)} similar images")
                
                # Step 2: Get pricing for the current image using LLM
                # Convert image to base64 for LLM API
                with open(image_path, "rb") as image_file:
                    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
                
                # Get pricing using comprehensive search
                pricing_result = llm_client.comprehensive_product_search(
                    image_base64=image_base64,
                    image_format="jpeg",  # You might want to detect this dynamically
                    product_description=collateral_data.description,
                    search_context=f"Collateral item: {collateral_data.name}"
                )
                
                print(f"   💰 Price analysis: {pricing_result.price_range} {pricing_result.currency}")
                
                # Step 3: Calculate loan limit (typically 60-80% of estimated value)
                # Extract numeric value from price range
                price_match = re.search(r'[\d,]+', pricing_result.price_range)
                if price_match:
                    estimated_value = float(price_match.group().replace(',', ''))
                    loan_limit = estimated_value * 0.7  # 70% of estimated value
                    total_estimated_value += estimated_value
                else:
                    estimated_value = 1000.0  # Default fallback
                    loan_limit = 700.0
                
                # Step 4: Compile image analysis results
                image_analysis = {
                    "image_path": image_path,
                    "similar_images": similar_images,
                    "pricing_analysis": {
                        "product_name": pricing_result.product_name,
                        "price_range": pricing_result.price_range,
                        "currency": pricing_result.currency,
                        "marketplace": pricing_result.marketplace,
                        "confidence": pricing_result.confidence,
                        "estimated_value": estimated_value,
                        "loan_limit": loan_limit
                    },
                    "rag3_metadata": {
                        "similar_images_found": len(similar_images),
                        "top_similarity_score": max([img['score'] for img in similar_images]) if similar_images else 0.0
                    }
                }
                
                image_analyses.append(image_analysis)
                
            except Exception as e:
                print(f"❌ Error processing image {image_path}: {e}")
                # Continue with other images instead of failing completely
                image_analysis = {
                    "image_path": image_path,
                    "error": str(e),
                    "pricing_analysis": {
                        "estimated_value": 1000.0,
                        "loan_limit": 700.0
                    }
                }
                image_analyses.append(image_analysis)
        
        # Calculate overall loan parameters
        if total_estimated_value > 0:
            overall_loan_limit = total_estimated_value * 0.7
            interest_rate = 0.12  # 12% annual interest
            due_date = datetime.now() + timedelta(days=365)  # 1 year loan
        else:
            overall_loan_limit = 1000.0
            interest_rate = 0.15  # Higher interest for uncertain valuation
            due_date = datetime.now() + timedelta(days=180)  # 6 month loan
        
        # Create the collateral with calculated values
        collateral = await CollateralDB.create_collateral_simple(CollateralCreateSimple(
            user_id=collateral_data.user_id
        ))
        
        # Update with comprehensive analysis results
        update_data = CollateralUpdate(
            images=collateral_data.images,
            loan_limit=overall_loan_limit,
            interest=interest_rate,
            due_date=due_date,
            metadata={
                "name": collateral_data.name,
                "description": collateral_data.description,
                "original_images": collateral_data.images,
                "status": "pending",
                "image_analyses": image_analyses,
                "total_estimated_value": total_estimated_value,
                "overall_loan_limit": overall_loan_limit,
                "interest_rate": interest_rate,
                "due_date": due_date.isoformat(),
                "analysis_timestamp": datetime.now().isoformat(),
                "rag3_integration": True
            }
        )
        
        updated_collateral = await CollateralDB.update_collateral(collateral.id, update_data)
        
        print(f"Collateral created successfully for user {collateral_data.user_id}")
        print(f"   Total estimated value: ${total_estimated_value:,.2f}")
        print(f"   Loan limit: ${overall_loan_limit:,.2f}")
        print(f"   Interest rate: {interest_rate*100}%")
        
        return updated_collateral
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Collateral creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create collateral: {str(e)}")


@router.post("/{collateral_id}/approve", response_model=CollateralResponse)
async def approve_collateral(collateral_id: str, approve_request: CollateralApproveRequest):
    """Approve a collateral and create a loan transaction"""
    try:
        # Check if collateral exists
        existing_collateral = await CollateralDB.get_collateral_by_id(collateral_id)
        if not existing_collateral:
            raise HTTPException(status_code=404, detail="Collateral not found")
        
        approved_collateral = await CollateralDB.approve_collateral(collateral_id, approve_request)
        return approved_collateral
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/", response_model=CollateralListResponse)
async def list_collaterals(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status: Optional[CollateralStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of collaterals per page")
):
    """Get all collaterals with filtering and pagination"""
    try:
        search_params = CollateralSearchParams(
            user_id=user_id,
            status=status,
            page=page,
            page_size=page_size
        )
        
        result = await CollateralDB.list_collaterals(search_params)
        return CollateralListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{collateral_id}", response_model=CollateralResponse)
async def get_collateral(collateral_id: str):
    """Get a specific collateral by ID"""
    try:
        collateral = await CollateralDB.get_collateral_by_id(collateral_id)
        if not collateral:
            raise HTTPException(status_code=404, detail="Collateral not found")
        return collateral
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.put("/{collateral_id}", response_model=CollateralResponse)
async def update_collateral(collateral_id: str, collateral_data: CollateralUpdate):
    """Update a collateral"""
    try:
        # Check if collateral exists
        existing_collateral = await CollateralDB.get_collateral_by_id(collateral_id)
        if not existing_collateral:
            raise HTTPException(status_code=404, detail="Collateral not found")
        
        updated_collateral = await CollateralDB.update_collateral(collateral_id, collateral_data)
        if not updated_collateral:
            raise HTTPException(status_code=500, detail="Failed to update collateral")
        
        return updated_collateral
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/{collateral_id}/extend-loan", response_model=TransactionResponse, status_code=201)
async def extend_loan(collateral_id: str, extend_loan_request: ExtendLoanRequest):
    """Extend a loan - creates a fee transaction and updates collateral loan amount"""
    try:
        # Validate collateral exists and is approved
        collateral = await CollateralDB.get_collateral_by_id(collateral_id)
        if not collateral:
            raise HTTPException(status_code=404, detail="Collateral not found")
        
        if collateral.status.value != "approved":
            raise HTTPException(status_code=400, detail=f"Collateral is not approved. Current status: {collateral.status.value}")
        
        # Validate account exists
        account = await AccountDB.get_account_by_id(extend_loan_request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Validate user exists
        user = await UserDB.get_user_by_id(extend_loan_request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create fee transaction data
        transaction_data = TransactionCreate(
            account_id=extend_loan_request.account_id,
            user_id=extend_loan_request.user_id,
            transaction_type=TransactionType.FEE,
            amount=extend_loan_request.fee,
            description=extend_loan_request.description or f"Loan extension fee for {extend_loan_request.extension_days} days",
            reference_number=extend_loan_request.reference_number,
            collateral_id=collateral_id,
            metadata={
                **(extend_loan_request.metadata or {}),
                "extension_days": extend_loan_request.extension_days,
                "extension_fee": str(extend_loan_request.fee),
                "transaction_purpose": "loan_extension"
            }
        )
        
        # Create transaction
        transaction = await TransactionDB.create_transaction(transaction_data)
        
        # Process loan extension (fee increases loan balance, not investment balance)
        try:
            # Get current account balances
            account = await AccountDB.get_account_by_id(extend_loan_request.account_id)
            current_loan_balance = account.loan_balance
            current_investment_balance = account.investment_balance
            
            # For loan extension, fee increases loan balance
            new_loan_balance = float(current_loan_balance) + float(extend_loan_request.fee)
            
            # Update account balances directly
            await AccountDB.update_account_balances(
                account_id=extend_loan_request.account_id,
                loan_balance=new_loan_balance,
                investment_balance=current_investment_balance
            )
            
            # Update transaction with balance information
            await TransactionDB.update_transaction_balances(
                transaction_id=transaction.id,
                loan_balance_before=float(current_loan_balance),
                loan_balance_after=float(new_loan_balance),
                invested_balance_before=float(current_investment_balance),
                invested_balance_after=float(current_investment_balance)
            )
            
            # Mark transaction as completed
            await TransactionDB.mark_transaction_completed(transaction.id)
            
            # Update collateral loan amount by adding the fee
            new_loan_amount = float(collateral.loan_amount) + float(extend_loan_request.fee)
            await CollateralDB.update_loan_amount(collateral_id, new_loan_amount)
            
            print(f"✅ Loan extended successfully:")
            print(f"   - Fee: ${extend_loan_request.fee}")
            print(f"   - Extension days: {extend_loan_request.extension_days}")
            print(f"   - New loan amount: ${new_loan_amount}")
            print(f"   - New loan balance: ${new_loan_balance}")
            
        except Exception as e:
            # If processing fails, mark transaction as failed
            await TransactionDB.mark_transaction_failed(transaction.id, str(e))
            raise HTTPException(status_code=400, detail=str(e))
        
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image file and save it to the data folder"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(data_dir, unique_filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Return the relative path from backend root
        relative_path = os.path.join('data', unique_filename)
        
        return {
            "success": True,
            "message": "Image uploaded successfully",
            "file_path": relative_path,
            "original_filename": file.filename,
            "size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
