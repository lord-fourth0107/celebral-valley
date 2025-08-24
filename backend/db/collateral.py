"""
Collateral database operations

This module handles all database operations related to collaterals.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
import json
import os
import shutil
from pathlib import Path

from dataModels.collateral import Collateral, CollateralCreate, CollateralCreateSimple, CollateralUpdate, CollateralSearchParams, CollateralApproveRequest
from dataModels.transaction import TransactionCreate, TransactionType
from database import db_manager


class CollateralDB:
    """Database operations for collaterals"""
    
    # File storage configuration
    FILES_BASE_PATH = Path("files/collaterals")
    
    @staticmethod
    def _ensure_files_directory():
        """Ensure the files directory exists"""
        CollateralDB.FILES_BASE_PATH.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def _save_image_to_files(image_data: str, collateral_id: str, image_index: int) -> str:
        """Save image data to files folder and return the file path"""
        CollateralDB._ensure_files_directory()
        
        # Create collateral-specific directory
        collateral_dir = CollateralDB.FILES_BASE_PATH / collateral_id
        collateral_dir.mkdir(exist_ok=True)
        
        # Generate filename
        file_extension = "jpg"  # Default, could be determined from image data
        filename = f"image_{image_index:03d}.{file_extension}"
        file_path = collateral_dir / filename
        
        # TODO: Process image data (base64, URL, or file upload)
        # For now, we'll assume it's a file path that needs to be copied
        if os.path.exists(image_data):
            # Copy existing file
            shutil.copy2(image_data, file_path)
        else:
            # TODO: Handle base64 or URL image data
            # For now, create a placeholder file
            with open(file_path, 'w') as f:
                f.write(f"Placeholder for image {image_index}")
        
        return str(file_path.relative_to(CollateralDB.FILES_BASE_PATH))

    @staticmethod
    async def create_collateral_simple(collateral_data: CollateralCreateSimple) -> Collateral:
        """Create a new collateral with mocked data - only requires user_id"""
        collateral_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Mock data for initial collateral creation
        # TODO: Replace with actual data from image processing/valuation
        mock_loan_amount = 5000.00
        mock_loan_limit = 7500.00
        mock_interest = 0.0550
        mock_due_date = now + timedelta(days=90)  # 90 days from now
        
        query = """
            INSERT INTO collaterals (
                id, user_id, status, loan_amount, loan_limit, interest, due_date,
                image_paths, metadata, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            collateral_id,
            collateral_data.user_id,
            "pending",  # Default status
            mock_loan_amount,
            mock_loan_limit,
            mock_interest,
            mock_due_date,
            None,  # No images initially
            json.dumps({"description": "Collateral pending valuation", "status": "awaiting_processing"}),
            now,
            now
        )

        async with db_manager.get_connection() as conn:
            await conn.execute(query, params)
            await conn.commit()
        
        # Fetch the created collateral
        created_collateral = await CollateralDB.get_collateral_by_id(collateral_id)
        if not created_collateral:
            raise Exception("Failed to create collateral")
        
        return created_collateral

    @staticmethod
    async def create_collateral(collateral_data: CollateralCreate) -> Collateral:
        """Create a new collateral with full data"""
        collateral_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Process and save images to files folder
        processed_image_paths = []
        if collateral_data.images:
            for i, image_data in enumerate(collateral_data.images):
                try:
                    file_path = CollateralDB._save_image_to_files(image_data, collateral_id, i)
                    processed_image_paths.append(file_path)
                except Exception as e:
                    print(f"Warning: Failed to process image {i}: {e}")
        
        # TODO: Additional image processing logic here:
        # - Validate image formats (jpg, png, etc.)
        # - Resize images to standard sizes
        # - Generate thumbnails
        # - Store in cloud storage (AWS S3, etc.) - optional
        # - Update image_paths with processed URLs
        
        query = """
            INSERT INTO collaterals (
                id, user_id, status, loan_amount, loan_limit, interest, due_date,
                image_paths, metadata, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            collateral_id,
            collateral_data.user_id,
            "pending",  # Default status
            collateral_data.loan_amount,
            collateral_data.loan_limit,
            collateral_data.interest,
            collateral_data.due_date,
            json.dumps(processed_image_paths) if processed_image_paths else None,
            json.dumps(collateral_data.metadata) if collateral_data.metadata else None,
            now,
            now
        )

        async with db_manager.get_connection() as conn:
            await conn.execute(query, params)
            await conn.commit()
        
        # Fetch the created collateral
        created_collateral = await CollateralDB.get_collateral_by_id(collateral_id)
        if not created_collateral:
            raise Exception("Failed to create collateral")
        
        return created_collateral

    @staticmethod
    async def approve_collateral(collateral_id: str, approve_request: CollateralApproveRequest) -> Collateral:
        """Approve a collateral and create a loan transaction"""
        # Get the collateral
        collateral = await CollateralDB.get_collateral_by_id(collateral_id)
        if not collateral:
            raise Exception("Collateral not found")
        
        if collateral.status != "pending":
            raise Exception("Collateral is not in pending status")
        
        if approve_request.loan_amount > collateral.loan_limit:
            raise Exception(f"Loan amount {approve_request.loan_amount} exceeds limit {collateral.loan_limit}")
        
        # Update collateral status to approved
        now = datetime.utcnow()
        query = """
            UPDATE collaterals 
            SET status = %s, loan_amount = %s, updated_at = %s
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            await conn.execute(query, ("approved", approve_request.loan_amount, now, collateral_id))
            await conn.commit()
        
        # Create loan disbursement transaction
        # TODO: Get account_id from user - for now using a placeholder
        # In real implementation, you'd get the user's account
        from db.account import AccountDB
        user_account = await AccountDB.get_account_by_user_id(collateral.user_id)
        if not user_account:
            raise Exception("User account not found")
        
        transaction_data = TransactionCreate(
            account_id=user_account.id,
            user_id=collateral.user_id,
            transaction_type=TransactionType.LOAN_DISBURSEMENT,
            amount=approve_request.loan_amount,
            description=f"Loan disbursement for collateral {collateral_id}",
            reference_number=f"LOAN-{collateral_id[:8]}",
            collateral_id=collateral_id,
            metadata={
                "collateral_id": collateral_id,
                "loan_type": "collateral_loan",
                "interest_rate": str(collateral.interest),
                "due_date": collateral.due_date.isoformat()
            }
        )
        
        from db.transaction import TransactionDB
        await TransactionDB.create_transaction(transaction_data)
        
        # Fetch the updated collateral
        updated_collateral = await CollateralDB.get_collateral_by_id(collateral_id)
        if not updated_collateral:
            raise Exception("Failed to update collateral")
        
        return updated_collateral

    @staticmethod
    async def get_collateral_by_id(collateral_id: str) -> Optional[Collateral]:
        """Get a collateral by ID"""
        query = """
            SELECT id, user_id, status, loan_amount, loan_limit, interest, due_date,
                   image_paths, metadata, created_at, updated_at
            FROM collaterals 
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (collateral_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            
            # Parse JSON fields and map image_paths to images
            if row['image_paths']:
                if isinstance(row['image_paths'], str):
                    row['images'] = json.loads(row['image_paths'])
                elif isinstance(row['image_paths'], list):
                    row['images'] = row['image_paths']
                else:
                    row['images'] = []
            else:
                row['images'] = []
            if row['metadata'] and isinstance(row['metadata'], str):
                row['metadata'] = json.loads(row['metadata'])
            
            # Remove the old field name
            del row['image_paths']
            
            return Collateral(**row)

    @staticmethod
    async def get_collaterals_by_user_id(user_id: str) -> List[Collateral]:
        """Get all collaterals for a user"""
        query = """
            SELECT id, user_id, status, loan_amount, loan_limit, interest, due_date,
                   image_paths, metadata, created_at, updated_at
            FROM collaterals 
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (user_id,))
            rows = await cursor.fetchall()
            
            collaterals = []
            for row in rows:
                # Parse JSON fields and map image_paths to images
                if row['image_paths']:
                    if isinstance(row['image_paths'], str):
                        row['images'] = json.loads(row['image_paths'])
                    elif isinstance(row['image_paths'], list):
                        row['images'] = row['image_paths']
                    else:
                        row['images'] = []
                else:
                    row['images'] = []
                if row['metadata'] and isinstance(row['metadata'], str):
                    row['metadata'] = json.loads(row['metadata'])
                
                # Remove the old field name
                del row['image_paths']
                
                collaterals.append(Collateral(**row))
            
            return collaterals

    @staticmethod
    async def update_collateral(collateral_id: str, collateral_data: CollateralUpdate) -> Optional[Collateral]:
        """Update a collateral"""
        # Process new images if provided
        processed_image_paths = None
        if collateral_data.images is not None:
            processed_image_paths = []
            for i, image_data in enumerate(collateral_data.images):
                try:
                    file_path = CollateralDB._save_image_to_files(image_data, collateral_id, i)
                    processed_image_paths.append(file_path)
                except Exception as e:
                    print(f"Warning: Failed to process image {i}: {e}")
        
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        
        for field, value in collateral_data.model_dump(exclude_unset=True).items():
            if value is not None:
                # Map 'images' field to 'image_paths' for database
                if field == 'images':
                    update_fields.append("image_paths = %s")
                    values.append(json.dumps(processed_image_paths))
                else:
                    update_fields.append(f"{field} = %s")
                    if isinstance(value, datetime):
                        values.append(value)
                    elif hasattr(value, 'value'):  # Enum
                        values.append(value.value)
                    elif field == 'metadata' and value is not None:
                        values.append(json.dumps(value))
                    else:
                        values.append(value)
        
        if not update_fields:
            # No fields to update
            return await CollateralDB.get_collateral_by_id(collateral_id)
        
        # Add updated_at field
        update_fields.append("updated_at = %s")
        values.append(datetime.utcnow())
        
        # Add collateral_id for WHERE clause
        values.append(collateral_id)
        
        query = f"""
            UPDATE collaterals 
            SET {', '.join(update_fields)}
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            await conn.execute(query, values)
            await conn.commit()
        
        # Fetch the updated collateral
        return await CollateralDB.get_collateral_by_id(collateral_id)

    @staticmethod
    async def update_loan_amount(collateral_id: str, new_loan_amount: float) -> Optional[Collateral]:
        """Update the loan amount for a collateral"""
        query = """
            UPDATE collaterals 
            SET loan_amount = %s, updated_at = %s
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            await conn.execute(query, (new_loan_amount, datetime.utcnow(), collateral_id))
            await conn.commit()
        
        # Fetch the updated collateral
        return await CollateralDB.get_collateral_by_id(collateral_id)

    @staticmethod
    async def list_collaterals(search_params: CollateralSearchParams) -> Dict[str, Any]:
        """List collaterals with filtering and pagination"""
        # Build WHERE clause
        where_conditions = []
        values = []
        
        if search_params.user_id:
            where_conditions.append("user_id = %s")
            values.append(search_params.user_id)
            
        if search_params.status:
            where_conditions.append("status = %s")
            values.append(search_params.status.value)
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        async with db_manager.get_connection() as conn:
            # Count query
            count_query = f"SELECT COUNT(*) FROM collaterals {where_clause}"
            cursor = await conn.execute(count_query, values)
            total_row = await cursor.fetchone()
            # Handle both dict and tuple results
            if isinstance(total_row, dict):
                total = total_row['count'] if total_row else 0
            else:
                total = total_row[0] if total_row else 0
            
            # Data query with pagination
            offset = (search_params.page - 1) * search_params.page_size
            data_query = f"""
                SELECT id, user_id, status, loan_amount, loan_limit, interest, due_date,
                       image_paths, metadata, created_at, updated_at
                FROM collaterals 
                {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            
            cursor = await conn.execute(data_query, values + [search_params.page_size, offset])
            rows = await cursor.fetchall()
            
            collaterals = []
            for row in rows:
                # Parse JSON fields and map image_paths to images
                if row['image_paths']:
                    if isinstance(row['image_paths'], str):
                        row['images'] = json.loads(row['image_paths'])
                    elif isinstance(row['image_paths'], list):
                        row['images'] = row['image_paths']
                    else:
                        row['images'] = []
                else:
                    row['images'] = []
                if row['metadata'] and isinstance(row['metadata'], str):
                    row['metadata'] = json.loads(row['metadata'])
                
                # Remove the old field name
                del row['image_paths']
                
                collaterals.append(Collateral(**row))
            
            return {
                "collaterals": collaterals,
                "total": total,
                "page": search_params.page,
                "page_size": search_params.page_size
            }
