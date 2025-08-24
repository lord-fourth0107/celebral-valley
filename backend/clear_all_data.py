#!/usr/bin/env python3
"""
Script to clear all data from all tables in the database
"""

import os
import asyncio
import psycopg
from dotenv import load_dotenv

load_dotenv()

async def clear_all_data():
    """Delete all rows from all tables"""
    database_url = os.getenv('DATABASE_URL')
    print("🗑️  Clearing all data from database...")
    
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
            print(f"🗑️  Clearing table: {table}")
            await conn.execute(f"DELETE FROM {table}")
            print(f"✅ Cleared {table}")
        
        await conn.commit()
        print("✅ All data cleared successfully!")
        
    except Exception as e:
        print(f"❌ Failed to clear data: {e}")
        await conn.rollback()
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(clear_all_data())
