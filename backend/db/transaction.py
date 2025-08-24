"""
Transaction database operations

This module handles all database operations related to transactions.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json

from dataModels.transaction import (
    Transaction, TransactionCreate, TransactionUpdate, TransactionSearchParams,
    TransactionType, TransactionStatus
)
from database import db_manager


class TransactionDB:
    """Database operations for transactions"""

    @staticmethod
    async def create_transaction(transaction_data: TransactionCreate) -> Transaction:
        """Create a new transaction"""
        transaction_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        query = """
            INSERT INTO transactions (
                id, account_id, user_id, transaction_type, status, amount, 
                description, reference_number, collateral_id, metadata,
                loan_balance_before, loan_balance_after, invested_balance_before, invested_balance_after,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            transaction_id,
            transaction_data.account_id,
            transaction_data.user_id,
            transaction_data.transaction_type.value,
            "pending",  # Default status
            transaction_data.amount,
            transaction_data.description,
            transaction_data.reference_number,
            transaction_data.collateral_id,
            json.dumps(transaction_data.metadata) if transaction_data.metadata else None,
            transaction_data.loan_balance_before,
            transaction_data.loan_balance_after,
            transaction_data.invested_balance_before,
            transaction_data.invested_balance_after,
            now,
            now
        )

        async with db_manager.get_connection() as conn:
            await conn.execute(query, params)
            await conn.commit()
        
        # Fetch the created transaction
        created_transaction = await TransactionDB.get_transaction_by_id(transaction_id)
        if not created_transaction:
            raise Exception("Failed to create transaction")
        
        return created_transaction

    @staticmethod
    async def get_transaction_by_id(transaction_id: str) -> Optional[Transaction]:
        """Get a transaction by ID"""
        query = """
            SELECT id, account_id, user_id, transaction_type, status, amount,
                   description, reference_number, collateral_id, metadata,
                   loan_balance_before, loan_balance_after, invested_balance_before, 
                   invested_balance_after, created_at, updated_at, processed_at, 
                   failed_at, failure_reason
            FROM transactions 
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (transaction_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            
            # Parse JSON fields
            if row['metadata'] and isinstance(row['metadata'], str):
                row['metadata'] = json.loads(row['metadata'])
            
            return Transaction(**row)

    @staticmethod
    async def get_transactions_by_account_id(account_id: str) -> List[Transaction]:
        """Get all transactions for an account"""
        query = """
            SELECT id, account_id, user_id, transaction_type, status, amount,
                   description, reference_number, collateral_id, metadata,
                   loan_balance_before, loan_balance_after, invested_balance_before, 
                   invested_balance_after, created_at, updated_at, processed_at, 
                   failed_at, failure_reason
            FROM transactions 
            WHERE account_id = %s
            ORDER BY created_at DESC
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (account_id,))
            rows = await cursor.fetchall()
            
            transactions = []
            for row in rows:
                # Parse JSON fields
                if row['metadata'] and isinstance(row['metadata'], str):
                    row['metadata'] = json.loads(row['metadata'])
                transactions.append(Transaction(**row))
            
            return transactions

    @staticmethod
    async def get_transactions_by_user_id(user_id: str) -> List[Transaction]:
        """Get all transactions for a user"""
        query = """
            SELECT id, account_id, user_id, transaction_type, status, amount,
                   description, reference_number, collateral_id, metadata,
                   loan_balance_before, loan_balance_after, invested_balance_before, 
                   invested_balance_after, created_at, updated_at, processed_at, 
                   failed_at, failure_reason
            FROM transactions 
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (user_id,))
            rows = await cursor.fetchall()
            
            transactions = []
            for row in rows:
                # Parse JSON fields
                if row['metadata'] and isinstance(row['metadata'], str):
                    row['metadata'] = json.loads(row['metadata'])
                transactions.append(Transaction(**row))
            
            return transactions

    @staticmethod
    async def get_transactions_by_type(transaction_type: TransactionType) -> List[Transaction]:
        """Get all transactions by type"""
        query = """
            SELECT id, account_id, user_id, transaction_type, status, amount,
                   description, reference_number, collateral_id, metadata,
                   loan_balance_before, loan_balance_after, invested_balance_before, 
                   invested_balance_after, created_at, updated_at, processed_at, 
                   failed_at, failure_reason
            FROM transactions 
            WHERE transaction_type = %s
            ORDER BY created_at DESC
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (transaction_type.value,))
            rows = await cursor.fetchall()
            
            transactions = []
            for row in rows:
                # Parse JSON fields
                if row['metadata'] and isinstance(row['metadata'], str):
                    row['metadata'] = json.loads(row['metadata'])
                transactions.append(Transaction(**row))
            
            return transactions

    @staticmethod
    async def update_transaction(transaction_id: str, transaction_data: TransactionUpdate) -> Optional[Transaction]:
        """Update a transaction"""
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        
        for field, value in transaction_data.model_dump(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = %s")
                if isinstance(value, datetime):
                    values.append(value)
                elif hasattr(value, 'value'):  # Enum
                    values.append(value.value)
                else:
                    values.append(value)
        
        if not update_fields:
            # No fields to update
            return await TransactionDB.get_transaction_by_id(transaction_id)
        
        # Add updated_at field
        update_fields.append("updated_at = %s")
        values.append(datetime.utcnow())
        
        # Add transaction_id for WHERE clause
        values.append(transaction_id)
        
        query = f"""
            UPDATE transactions 
            SET {', '.join(update_fields)}
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            await conn.execute(query, values)
            await conn.commit()
        
        # Fetch the updated transaction
        return await TransactionDB.get_transaction_by_id(transaction_id)

    @staticmethod
    async def delete_transaction(transaction_id: str) -> bool:
        """Delete a transaction"""
        query = "DELETE FROM transactions WHERE id = %s"
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (transaction_id,))
            await conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    async def list_transactions(search_params: TransactionSearchParams) -> Dict[str, Any]:
        """List transactions with filtering and pagination"""
        # Build WHERE clause
        where_conditions = []
        values = []
        
        if search_params.account_id:
            where_conditions.append("account_id = %s")
            values.append(search_params.account_id)
            
        if search_params.user_id:
            where_conditions.append("user_id = %s")
            values.append(search_params.user_id)
            
        if search_params.transaction_type:
            where_conditions.append("transaction_type = %s")
            values.append(search_params.transaction_type.value)
            
        if search_params.status:
            where_conditions.append("status = %s")
            values.append(search_params.status.value)
            
        if search_params.reference_number:
            where_conditions.append("reference_number ILIKE %s")
            values.append(f"%{search_params.reference_number}%")
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        async with db_manager.get_connection() as conn:
            # Count query
            count_query = f"SELECT COUNT(*) FROM transactions {where_clause}"
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
                SELECT id, account_id, user_id, transaction_type, status, amount,
                       description, reference_number, collateral_id, metadata,
                       loan_balance_before, loan_balance_after, invested_balance_before, 
                       invested_balance_after, created_at, updated_at, processed_at, 
                       failed_at, failure_reason
                FROM transactions 
                {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            
            cursor = await conn.execute(data_query, values + [search_params.page_size, offset])
            rows = await cursor.fetchall()
            
            transactions = []
            for row in rows:
                # Parse JSON fields
                if row['metadata'] and isinstance(row['metadata'], str):
                    row['metadata'] = json.loads(row['metadata'])
                transactions.append(Transaction(**row))
            
            return {
                "transactions": transactions,
                "total": total,
                "page": search_params.page,
                "page_size": search_params.page_size
            }

    @staticmethod
    async def update_transaction_status(transaction_id: str, status: TransactionStatus) -> Optional[Transaction]:
        """Update transaction status"""
        query = """
            UPDATE transactions 
            SET status = %s, updated_at = %s
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            await conn.execute(query, (status.value, datetime.utcnow(), transaction_id))
            await conn.commit()
        
        return await TransactionDB.get_transaction_by_id(transaction_id)

    @staticmethod
    async def mark_transaction_completed(transaction_id: str) -> Optional[Transaction]:
        """Mark a transaction as completed"""
        query = """
            UPDATE transactions 
            SET status = %s, processed_at = %s, updated_at = %s
            WHERE id = %s
        """
        
        now = datetime.utcnow()
        
        async with db_manager.get_connection() as conn:
            await conn.execute(query, ("completed", now, now, transaction_id))
            await conn.commit()
        
        return await TransactionDB.get_transaction_by_id(transaction_id)

    @staticmethod
    async def mark_transaction_failed(transaction_id: str, failure_reason: str) -> Optional[Transaction]:
        """Mark a transaction as failed"""
        query = """
            UPDATE transactions 
            SET status = %s, failed_at = %s, failure_reason = %s, updated_at = %s
            WHERE id = %s
        """
        
        now = datetime.utcnow()
        
        async with db_manager.get_connection() as conn:
            await conn.execute(query, ("failed", now, failure_reason, now, transaction_id))
            await conn.commit()
        
        return await TransactionDB.get_transaction_by_id(transaction_id)

    @staticmethod
    async def get_transaction_summary_by_user(user_id: str) -> Dict[str, Any]:
        """Get transaction summary for a user"""
        query = """
            SELECT 
                transaction_type,
                status,
                COUNT(*) as count,
                SUM(amount) as total_amount
            FROM transactions 
            WHERE user_id = %s
            GROUP BY transaction_type, status
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (user_id,))
            rows = await cursor.fetchall()
            
            summary = {
                "total_transactions": 0,
                "total_amount": 0,
                "by_type": {},
                "by_status": {}
            }
            
            for row in rows:
                transaction_type = row['transaction_type']
                status = row['status']
                count = row['count']
                amount = row['total_amount'] or 0
                
                summary["total_transactions"] += count
                summary["total_amount"] += amount
                
                if transaction_type not in summary["by_type"]:
                    summary["by_type"][transaction_type] = {"count": 0, "amount": 0}
                summary["by_type"][transaction_type]["count"] += count
                summary["by_type"][transaction_type]["amount"] += amount
                
                if status not in summary["by_status"]:
                    summary["by_status"][status] = {"count": 0, "amount": 0}
                summary["by_status"][status]["count"] += count
                summary["by_status"][status]["amount"] += amount
            
            return summary

    @staticmethod
    async def update_transaction_balances(
        transaction_id: str, 
        loan_balance_before: float = None, 
        loan_balance_after: float = None,
        invested_balance_before: float = None, 
        invested_balance_after: float = None
    ) -> Optional[Transaction]:
        """Update transaction balance fields"""
        update_fields = []
        values = []
        
        if loan_balance_before is not None:
            update_fields.append("loan_balance_before = %s")
            values.append(loan_balance_before)
            
        if loan_balance_after is not None:
            update_fields.append("loan_balance_after = %s")
            values.append(loan_balance_after)
            
        if invested_balance_before is not None:
            update_fields.append("invested_balance_before = %s")
            values.append(invested_balance_before)
            
        if invested_balance_after is not None:
            update_fields.append("invested_balance_after = %s")
            values.append(invested_balance_after)
        
        if not update_fields:
            return await TransactionDB.get_transaction_by_id(transaction_id)
        
        # Add updated_at field
        update_fields.append("updated_at = %s")
        values.append(datetime.utcnow())
        
        # Add transaction_id for WHERE clause
        values.append(transaction_id)
        
        query = f"""
            UPDATE transactions 
            SET {', '.join(update_fields)}
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            await conn.execute(query, values)
            await conn.commit()
        
        return await TransactionDB.get_transaction_by_id(transaction_id)
