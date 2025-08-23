#!/usr/bin/env python3
import os
import asyncio
import psycopg
from dotenv import load_dotenv

load_dotenv()

async def run_migration():
    """Run the organization role migration"""
    database_url = os.getenv('DATABASE_URL')
    print("🚀 Running organization role migration...")
    
    conn = await psycopg.AsyncConnection.connect(database_url)
    try:
        # Read and execute the migration
        with open('migrations/005_add_organization_role.sql', 'r') as f:
            sql_content = f.read()
        
        print("📝 Executing migration...")
        await conn.execute(sql_content)
        await conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        await conn.rollback()
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
