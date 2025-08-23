"""
User database operations

This module handles all database operations related to users.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from dataModels.user import User, UserCreate, UserUpdate, UserSearchParams
from database import db_manager


class UserDB:
    """Database operations for users"""

    @staticmethod
    async def create_user(user_data: UserCreate) -> User:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        query = """
            INSERT INTO app_users (
                id, email, username, first_name, last_name, phone, date_of_birth, 
                address, city, state, country, postal_code, role, status, 
                kyc_verified, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            user_id,
            user_data.email,
            user_data.username,
            user_data.first_name,
            user_data.last_name,
            user_data.phone,
            user_data.date_of_birth,
            user_data.address,
            user_data.city,
            user_data.state,
            user_data.country,
            user_data.postal_code,
            user_data.role.value,
            "pending_verification",  # Default status
            False,  # Default kyc_verified
            now,
            now
        )

        async with db_manager.get_connection() as conn:
            await conn.execute(query, params)
            await conn.commit()
        
        # Fetch the created user
        created_user = await UserDB.get_user_by_id(user_id)
        if not created_user:
            raise Exception("Failed to create user")
        
        return created_user

    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        """Get a user by ID"""
        query = """
            SELECT id, email, username, first_name, last_name, phone, date_of_birth,
                   address, city, state, country, postal_code, role, status,
                   kyc_verified, created_at, updated_at
            FROM app_users 
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (user_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            
            return User(**row)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """Get a user by email"""
        query = """
            SELECT id, email, username, first_name, last_name, phone, date_of_birth,
                   address, city, state, country, postal_code, role, status,
                   kyc_verified, created_at, updated_at
            FROM app_users 
            WHERE email = %s
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (email,))
            row = await cursor.fetchone()
            if not row:
                return None
            
            return User(**row)

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[User]:
        """Get a user by username"""
        query = """
            SELECT id, email, username, first_name, last_name, phone, date_of_birth,
                   address, city, state, country, postal_code, role, status,
                   kyc_verified, created_at, updated_at
            FROM app_users 
            WHERE username = %s
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (username,))
            row = await cursor.fetchone()
            if not row:
                return None
            
            return User(**row)

    @staticmethod
    async def update_user(user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update a user"""
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        
        for field, value in user_data.model_dump(exclude_unset=True).items():
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
            return await UserDB.get_user_by_id(user_id)
        
        # Add updated_at field
        update_fields.append("updated_at = %s")
        values.append(datetime.utcnow())
        
        # Add user_id for WHERE clause
        values.append(user_id)
        
        query = f"""
            UPDATE app_users 
            SET {', '.join(update_fields)}
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            await conn.execute(query, values)
            await conn.commit()
        
        # Fetch the updated user
        return await UserDB.get_user_by_id(user_id)

    @staticmethod
    async def delete_user(user_id: str) -> bool:
        """Delete a user"""
        query = "DELETE FROM app_users WHERE id = %s"
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (user_id,))
            await conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    async def list_users(search_params: UserSearchParams) -> Dict[str, Any]:
        """List users with filtering and pagination"""
        # Build WHERE clause
        where_conditions = []
        values = []
        
        if search_params.email:
            where_conditions.append("email ILIKE %s")
            values.append(f"%{search_params.email}%")
            
        if search_params.username:
            where_conditions.append("username ILIKE %s")
            values.append(f"%{search_params.username}%")
            
        if search_params.status:
            where_conditions.append("status = %s")
            values.append(search_params.status.value)
            
        if search_params.role:
            where_conditions.append("role = %s")
            values.append(search_params.role.value)
            
        if search_params.kyc_verified is not None:
            where_conditions.append("kyc_verified = %s")
            values.append(search_params.kyc_verified)
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        async with db_manager.get_connection() as conn:
            # Count query
            count_query = f"SELECT COUNT(*) FROM app_users {where_clause}"
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
                SELECT id, email, username, first_name, last_name, phone, date_of_birth,
                       address, city, state, country, postal_code, role, status,
                       kyc_verified, created_at, updated_at
                FROM app_users 
                {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            
            cursor = await conn.execute(data_query, values + [search_params.page_size, offset])
            rows = await cursor.fetchall()
            users = [User(**row) for row in rows]
            
            return {
                "users": users,
                "total": total,
                "page": search_params.page,
                "page_size": search_params.page_size
            }

    @staticmethod
    async def user_exists(email: str = None, username: str = None, exclude_user_id: str = None) -> bool:
        """Check if a user exists by email or username"""
        conditions = []
        values = []
        
        if email:
            conditions.append("email = %s")
            values.append(email)
            
        if username:
            conditions.append("username = %s")
            values.append(username)
        
        if not conditions:
            return False
        
        query = f"SELECT COUNT(*) FROM app_users WHERE ({' OR '.join(conditions)})"
        
        if exclude_user_id:
            query += " AND id != %s"
            values.append(exclude_user_id)
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, values)
            result = await cursor.fetchone()
            # Handle both dict and tuple results
            if isinstance(result, dict):
                return result['count'] > 0
            else:
                return result[0] > 0 if result else False

    @staticmethod
    async def update_user_status(user_id: str, status: str) -> Optional[User]:
        """Update user status"""
        query = """
            UPDATE app_users 
            SET status = %s, updated_at = %s
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            await conn.execute(query, (status, datetime.utcnow(), user_id))
            await conn.commit()
        
        return await UserDB.get_user_by_id(user_id)

    @staticmethod
    async def update_kyc_status(user_id: str, kyc_verified: bool) -> Optional[User]:
        """Update user KYC verification status"""
        query = """
            UPDATE app_users 
            SET kyc_verified = %s, updated_at = %s
            WHERE id = %s
        """
        
        async with db_manager.get_connection() as conn:
            await conn.execute(query, (kyc_verified, datetime.utcnow(), user_id))
            await conn.commit()
        
        return await UserDB.get_user_by_id(user_id)

    @staticmethod
    async def get_users_by_role(role: str) -> List[User]:
        """Get all users by role"""
        query = """
            SELECT id, email, username, first_name, last_name, phone, date_of_birth,
                   address, city, state, country, postal_code, role, status,
                   kyc_verified, created_at, updated_at
            FROM app_users 
            WHERE role = %s
            ORDER BY created_at DESC
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (role,))
            rows = await cursor.fetchall()
            return [User(**row) for row in rows]

    @staticmethod
    async def get_users_by_status(status: str) -> List[User]:
        """Get all users by status"""
        query = """
            SELECT id, email, username, first_name, last_name, phone, date_of_birth,
                   address, city, state, country, postal_code, role, status,
                   kyc_verified, created_at, updated_at
            FROM app_users 
            WHERE status = %s
            ORDER BY created_at DESC
        """
        
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute(query, (status,))
            rows = await cursor.fetchall()
            return [User(**row) for row in rows]

