import os
import asyncio
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    """Database connection manager for PostgreSQL"""
    
    def __init__(self):
        self.database_url: Optional[str] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize database connections"""
        if self._initialized:
            return
            
        # Get environment variables
        self.database_url = os.getenv("DATABASE_URL")
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        # Test connection
        conn = await psycopg.AsyncConnection.connect(self.database_url)
        await conn.execute("SELECT 1")
        await conn.close()
        
        self._initialized = True
        print("Database connections initialized successfully")
    
    async def close(self) -> None:
        """Close all database connections"""
        self._initialized = False
        print("Database connections closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection"""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        connection = await psycopg.AsyncConnection.connect(self.database_url)
        connection.row_factory = dict_row
        try:
            yield connection
        finally:
            await connection.close()
    
    async def execute(self, query: str, *args) -> str:
        """Execute a query and return the result"""
        async with self.get_connection() as conn:
            if args:
                result = await conn.execute(query, args)
            else:
                result = await conn.execute(query)
            await conn.commit()
            return result.statusmessage
    
    async def fetch(self, query: str, *args) -> List[Dict[str, Any]]:
        """Fetch rows from a query"""
        async with self.get_connection() as conn:
            if args:
                cursor = await conn.execute(query, args)
            else:
                cursor = await conn.execute(query)
            return await cursor.fetchall()
    
    async def fetchrow(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Fetch a single row from a query"""
        async with self.get_connection() as conn:
            if args:
                cursor = await conn.execute(query, args)
            else:
                cursor = await conn.execute(query)
            return await cursor.fetchone()
    
    async def fetchval(self, query: str, *args) -> Any:
        """Fetch a single value from a query"""
        async with self.get_connection() as conn:
            if args:
                cursor = await conn.execute(query, args)
            else:
                cursor = await conn.execute(query)
            row = await cursor.fetchone()
            if row:
                # Return the first value from the dict
                return list(row.values())[0]
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            async with self.get_connection() as conn:
                # Test with a simple query
                cursor = await conn.execute("SELECT 1 as test")
                result = await cursor.fetchone()
                
                # Get version info
                cursor = await conn.execute("SELECT version()")
                version = await cursor.fetchone()
                version_str = version['version'] if version else "unknown"
                
                return {
                    "status": "healthy",
                    "database": "postgresql",
                    "version": version_str.split()[1] if version_str else "unknown",
                    "connection": "direct",
                    "test_query": "successful",
                    "test_result": result
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
                "error_details": repr(e)
            }

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions for easy access
async def get_db_connection():
    """Get a database connection"""
    return db_manager.get_connection()

async def execute_query(query: str, *args) -> str:
    """Execute a query"""
    return await db_manager.execute(query, *args)

async def fetch_rows(query: str, *args) -> List[Dict[str, Any]]:
    """Fetch rows from a query"""
    return await db_manager.fetch(query, *args)

async def fetch_row(query: str, *args) -> Optional[Dict[str, Any]]:
    """Fetch a single row from a query"""
    return await db_manager.fetchrow(query, *args)

async def fetch_value(query: str, *args) -> Any:
    """Fetch a single value from a query"""
    return await db_manager.fetchval(query, *args)

async def check_db_health() -> Dict[str, Any]:
    """Check database health"""
    return await db_manager.health_check()
