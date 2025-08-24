#!/usr/bin/env python3
"""
Script to initialize the system with default users and data
"""

import os
import asyncio
import psycopg
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def initialize_system():
    """Initialize the system with default users and data"""
    database_url = os.getenv('DATABASE_URL')
    print("🚀 Initializing system with default data...")
    
    conn = await psycopg.AsyncConnection.connect(database_url)
    try:
        # Clear existing data first
        print("🗑️  Clearing existing data...")
        tables = ['transactions', 'collaterals', 'accounts', 'app_users']
        for table in tables:
            await conn.execute(f"DELETE FROM {table}")
        await conn.commit()
        print("✅ Existing data cleared")
        
        # Create users
        print("👥 Creating users...")
        
        # Organization user (Kachra Seth)
        org_user_id = "organization"
        await conn.execute("""
            INSERT INTO app_users (
                id, email, username, first_name, last_name, phone, 
                address, city, state, country, postal_code, role, status, 
                kyc_verified, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            org_user_id,
            "kachra.seth@organization.com",
            "kachra_seth",
            "Kachra",
            "Seth", 
            "+1234567890",
            "123 Organization St",
            "Mumbai",
            "Maharashtra", 
            "India",
            "400001",
            "organization",
            "active",
            True,
            datetime.utcnow(),
            datetime.utcnow()
        ))
        print("✅ Created organization user: Kachra Seth")
        
        # Admin user
        admin_user_id = "admin_user_001"
        await conn.execute("""
            INSERT INTO app_users (
                id, email, username, first_name, last_name, phone, 
                address, city, state, country, postal_code, role, status, 
                kyc_verified, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            admin_user_id,
            "admin@celebralvalley.com",
            "admin",
            "System",
            "Administrator",
            "+1234567891", 
            "456 Admin Ave",
            "Mumbai",
            "Maharashtra",
            "India", 
            "400002",
            "admin",
            "active",
            True,
            datetime.utcnow(),
            datetime.utcnow()
        ))
        print("✅ Created admin user: System Administrator")
        
        # Regular users
        users_data = [
            {
                "id": "user_001",
                "email": "john.doe@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567892",
                "address": "789 User St",
                "city": "Mumbai",
                "state": "Maharashtra", 
                "country": "India",
                "postal_code": "400003"
            },
            {
                "id": "user_002", 
                "email": "jane.smith@example.com",
                "username": "janesmith",
                "first_name": "Jane",
                "last_name": "Smith",
                "phone": "+1234567893",
                "address": "321 User Ave",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India", 
                "postal_code": "400004"
            },
            {
                "id": "user_003",
                "email": "bob.wilson@example.com", 
                "username": "bobwilson",
                "first_name": "Bob",
                "last_name": "Wilson",
                "phone": "+1234567894",
                "address": "654 User Rd",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "postal_code": "400005"
            },
            {
                "id": "user_004",
                "email": "alice.brown@example.com",
                "username": "alicebrown", 
                "first_name": "Alice",
                "last_name": "Brown",
                "phone": "+1234567895",
                "address": "987 User Blvd",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "postal_code": "400006"
            }
        ]
        
        for user_data in users_data:
            await conn.execute("""
                INSERT INTO app_users (
                    id, email, username, first_name, last_name, phone, 
                    address, city, state, country, postal_code, role, status, 
                    kyc_verified, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_data["id"],
                user_data["email"],
                user_data["username"],
                user_data["first_name"],
                user_data["last_name"],
                user_data["phone"],
                user_data["address"],
                user_data["city"],
                user_data["state"],
                user_data["country"],
                user_data["postal_code"],
                "user",
                "active",
                True,
                datetime.utcnow(),
                datetime.utcnow()
            ))
            print(f"✅ Created user: {user_data['first_name']} {user_data['last_name']}")
        
        # Create accounts for all users
        print("🏦 Creating accounts...")
        
        # Organization account with initial fund
        await conn.execute("""
            INSERT INTO accounts (
                id, user_id, account_number, status, loan_balance, investment_balance, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            "org_account_001",
            org_user_id,
            "ORG001",
            "active",
            0.00,  # Organization never has loan balance
            100000.00,  # Initial fund
            datetime.utcnow(),
            datetime.utcnow()
        ))
        print("✅ Created organization account with ₹100,000 initial fund")
        
        # Admin account
        await conn.execute("""
            INSERT INTO accounts (
                id, user_id, account_number, status, loan_balance, investment_balance, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            "admin_account_001",
            admin_user_id,
            "ADMIN001",
            "active",
            0.00,
            0.00,
            datetime.utcnow(),
            datetime.utcnow()
        ))
        print("✅ Created admin account")
        
        # User accounts
        user_accounts = [
            ("user_account_001", "user_001", "ACC001"),
            ("user_account_002", "user_002", "ACC002"),
            ("user_account_003", "user_003", "ACC003"),
            ("user_account_004", "user_004", "ACC004")
        ]
        
        for account_id, user_id, account_number in user_accounts:
            await conn.execute("""
                INSERT INTO accounts (
                    id, user_id, account_number, status, loan_balance, investment_balance, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                account_id,
                user_id,
                account_number,
                "active",
                0.00,
                0.00,
                datetime.utcnow(),
                datetime.utcnow()
            ))
            print(f"✅ Created account: {account_number}")
        
        await conn.commit()
        print("✅ System initialization completed successfully!")
        print("\n📊 Summary:")
        print("- 1 Organization user (Kachra Seth) with ₹100,000 initial fund")
        print("- 1 Admin user (System Administrator)")
        print("- 4 Regular users (John Doe, Jane Smith, Bob Wilson, Alice Brown)")
        print("- 6 Accounts created (1 org, 1 admin, 4 users)")
        
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        await conn.rollback()
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(initialize_system())
