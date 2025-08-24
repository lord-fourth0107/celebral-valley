"""
Account database operations

This module handles all database operations related to accounts.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import time

from dataModels.account import Account, AccountCreate, AccountUpdate, AccountSearchParams
from database import db_manager


class AccountDB:
    """Database operations for accounts"""

    @staticmethod
    def _generate_account_number() -> str:
        """Generate a unique account number"""
        # Format: ACC + timestamp + random suffix
        timestamp = int(time.time())
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"ACC{timestamp}{random_suffix}"

    @staticmethod
    async def create_account(account_data: AccountCreate) -> Account:
        """Create a new account (one per user)"""
        # Check if user already has an account
        existing_account = await AccountDB.get_account_by_user_id(account_data.user_id)
        if existing_account:
            raise Exception("User already has an account")
        
        account_id = str(uuid.uuid4())
        account_number = AccountDB._generate_account_number()
        now = datetime.utcnow()
        
        # Ensure account number is unique
        while await AccountDB.account_exists(account_number=account_number):
            account_number = AccountDB._generate_account_number()
        
        query = """
            INSERT INTO accounts (
                id, user_id, account_number, status, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (
            account_id,
            account_data.user_id,
            account_number,
            "active",  # Default status
            now,
            now
        )

        async with db_manager.get_connection() as conn:
            await conn.execute(query, params)
            await conn.commit()
        
        # Fetch the created account
        created_account = await AccountDB.get_account_by_id(account_id)
        if not created_account:
            raise Exception("Failed to create account")
        
        return created_account

    @staticmethod
    async def get_account_by_id(account_id: str) -> Optional[Account]:
        """Get an account by ID"""
        query = """
            SELECT id, user_id, account_number, status, wallet_id, loan_balance, investment_balance, created_at, updated_at, closed_at
            FROM accounts 
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (account_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            
            return Account(**row)

    @staticmethod
    async def get_account_by_user_id(user_id: str) -> Optional[Account]:
        """Get an account by user ID (one account per user)"""
        query = """
            SELECT id, user_id, account_number, status, wallet_id, loan_balance, investment_balance, created_at, updated_at, closed_at
            FROM accounts 
            WHERE user_id = %s
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (user_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            
            return Account(**row)

    @staticmethod
    async def get_account_by_account_number(account_number: str) -> Optional[Account]:
        """Get an account by account number"""
        query = """
            SELECT id, user_id, account_number, status, wallet_id, loan_balance, investment_balance, created_at, updated_at, closed_at
            FROM accounts 
            WHERE account_number = %s
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (account_number,))
            row = await cursor.fetchone()
            if not row:
                return None
            
            return Account(**row)

    @staticmethod
    async def update_account(account_id: str, account_data: AccountUpdate) -> Optional[Account]:
        """Update an account"""
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        
        for field, value in account_data.model_dump(exclude_unset=True).items():
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
            return await AccountDB.get_account_by_id(account_id)
        
        # Add updated_at field
        update_fields.append("updated_at = %s")
        values.append(datetime.utcnow())
        
        # Add account_id for WHERE clause
        values.append(account_id)
        
        query = f"""
            UPDATE accounts 
            SET {', '.join(update_fields)}
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            await conn.execute(query, values)
            await conn.commit()
        
        # Fetch the updated account
        return await AccountDB.get_account_by_id(account_id)

    @staticmethod
    async def delete_account(account_id: str) -> bool:
        """Delete an account"""
        query = "DELETE FROM accounts WHERE id = %s"
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (account_id,))
            await conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    async def list_accounts(search_params: AccountSearchParams) -> Dict[str, Any]:
        """List accounts with filtering and pagination"""
        # Build WHERE clause
        where_conditions = []
        values = []
        
        if search_params.user_id:
            where_conditions.append("user_id = %s")
            values.append(search_params.user_id)
            
        if search_params.account_number:
            where_conditions.append("account_number ILIKE %s")
            values.append(f"%{search_params.account_number}%")
            
        if search_params.status:
            where_conditions.append("status = %s")
            values.append(search_params.status.value)
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        async with db_manager.get_connection() as conn:
            # Count query
            count_query = f"SELECT COUNT(*) FROM accounts {where_clause}"
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
                SELECT id, user_id, account_number, status, wallet_id, loan_balance, investment_balance, created_at, updated_at, closed_at
                FROM accounts 
                {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            
            cursor = await conn.execute(data_query, values + [search_params.page_size, offset])
            rows = await cursor.fetchall()
            accounts = [Account(**row) for row in rows]
            
            return {
                "accounts": accounts,
                "total": total,
                "page": search_params.page,
                "page_size": search_params.page_size
            }

    @staticmethod
    async def account_exists(user_id: str = None, account_number: str = None) -> bool:
        """Check if an account exists by user_id or account_number"""
        conditions = []
        values = []
        
        if user_id:
            conditions.append("user_id = %s")
            values.append(user_id)
            
        if account_number:
            conditions.append("account_number = %s")
            values.append(account_number)
        
        if not conditions:
            return False
        
        query = f"SELECT COUNT(*) FROM accounts WHERE ({' OR '.join(conditions)})"
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, values)
            result = await cursor.fetchone()
            # Handle both dict and tuple results
            if isinstance(result, dict):
                return result['count'] > 0
            else:
                return result[0] > 0 if result else False

    @staticmethod
    async def update_account_status(account_id: str, status: str) -> Optional[Account]:
        """Update account status"""
        query = """
            UPDATE accounts 
            SET status = %s, updated_at = %s
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            await conn.execute(query, (status, datetime.utcnow(), account_id))
            await conn.commit()
        
        return await AccountDB.get_account_by_id(account_id)

    @staticmethod
    async def close_account(account_id: str) -> Optional[Account]:
        """Close an account"""
        query = """
            UPDATE accounts 
            SET status = %s, closed_at = %s, updated_at = %s
            WHERE id = %s
        """
        
        now = datetime.utcnow()
        
        async with db_manager.get_connection() as conn:
            await conn.execute(query, ("closed", now, now, account_id))
            await conn.commit()
        
        return await AccountDB.get_account_by_id(account_id)

    @staticmethod
    async def update_account_balances(account_id: str, loan_balance: float = None, investment_balance: float = None) -> Optional[Account]:
        """Update account balances"""
        update_fields = []
        values = []
        
        if loan_balance is not None:
            update_fields.append("loan_balance = %s")
            values.append(loan_balance)
            
        if investment_balance is not None:
            update_fields.append("investment_balance = %s")
            values.append(investment_balance)
        
        if not update_fields:
            return await AccountDB.get_account_by_id(account_id)
        
        # Add updated_at field
        update_fields.append("updated_at = %s")
        values.append(datetime.utcnow())
        
        # Add account_id for WHERE clause
        values.append(account_id)
        
        query = f"""
            UPDATE accounts 
            SET {', '.join(update_fields)}
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            await conn.execute(query, values)
            await conn.commit()
        
        return await AccountDB.get_account_by_id(account_id)

    @staticmethod
    async def get_organization_account() -> Optional[Account]:
        """Get the organization account (assumes there's only one)"""
        query = """
            SELECT id, user_id, account_number, status, wallet_id, loan_balance, investment_balance, created_at, updated_at, closed_at
            FROM accounts 
            WHERE user_id = 'organization' OR account_number LIKE 'ORG%'
            LIMIT 1
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query)
            row = await cursor.fetchone()
            if not row:
                return None
            
            return Account(**row)
