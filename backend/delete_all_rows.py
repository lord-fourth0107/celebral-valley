#!/usr/bin/env python3
"""
Script to delete all rows from all tables in the database
"""

import os
import asyncio
import psycopg
from dotenv import load_dotenv

load_dotenv()

async def delete_all_rows():
    """Delete all rows from all tables"""
    database_url = os.getenv('DATABASE_URL')
    print("🗑️  Deleting all rows from database...")
    
    conn = await psycopg.AsyncConnection.connect(database_url)
    try:
        # List of tables to clear (in order to respect foreign key constraints)
        tables = [
            'transactions',
            'collaterals', 
            'accounts',
            'app_users'
        ]
        
        for table in tables:
            print(f"🗑️  Deleting all rows from: {table}")
            result = await conn.execute(f"DELETE FROM {table}")
            print(f"✅ Deleted rows from {table}")
        
        await conn.commit()
        print("✅ All rows deleted successfully!")
        
    except Exception as e:
        print(f"❌ Failed to delete rows: {e}")
        await conn.rollback()
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(delete_all_rows())
