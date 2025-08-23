"""
Collateral database operations

This module handles all database operations related to collaterals.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json

from dataModels.collateral import Collateral, CollateralCreate, CollateralUpdate, CollateralSearchParams
from database import db_manager


class CollateralDB:
    """Database operations for collaterals"""

    @staticmethod
    async def create_collateral(collateral_data: CollateralCreate) -> Collateral:
        """Create a new collateral"""
        collateral_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
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
            json.dumps(collateral_data.image_paths) if collateral_data.image_paths else None,
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
            
            # Parse JSON fields
            if row['image_paths'] and isinstance(row['image_paths'], str):
                row['image_paths'] = json.loads(row['image_paths'])
            if row['metadata'] and isinstance(row['metadata'], str):
                row['metadata'] = json.loads(row['metadata'])
            
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
                # Parse JSON fields
                if row['image_paths'] and isinstance(row['image_paths'], str):
                    row['image_paths'] = json.loads(row['image_paths'])
                if row['metadata'] and isinstance(row['metadata'], str):
                    row['metadata'] = json.loads(row['metadata'])
                collaterals.append(Collateral(**row))
            
            return collaterals

    @staticmethod
    async def update_collateral(collateral_id: str, collateral_data: CollateralUpdate) -> Optional[Collateral]:
        """Update a collateral"""
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        
        for field, value in collateral_data.model_dump(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = %s")
                if isinstance(value, datetime):
                    values.append(value)
                elif hasattr(value, 'value'):  # Enum
                    values.append(value.value)
                elif field in ['image_paths', 'metadata'] and value is not None:
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
                # Parse JSON fields
                if row['image_paths'] and isinstance(row['image_paths'], str):
                    row['image_paths'] = json.loads(row['image_paths'])
                if row['metadata'] and isinstance(row['metadata'], str):
                    row['metadata'] = json.loads(row['metadata'])
                collaterals.append(Collateral(**row))
            
            return {
                "collaterals": collaterals,
                "total": total,
                "page": search_params.page,
                "page_size": search_params.page_size
            }
