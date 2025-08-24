#!/usr/bin/env python3
"""
End-to-End Test Script for Yashvika's Collateral Flow

This script tests the complete collateral lifecycle:
1. Create a collateral with image analysis
2. Approve the collateral and create a loan
3. Extend the loan with a fee
4. Pay back the loan

Prerequisites:
- Backend server running on http://localhost:8000
- Crossmint API key set in environment
- Test image available (rolex.jpeg)
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = "rolex.jpeg"  # Relative to backend directory

# You can modify these to use existing user/account IDs
# If None, the script will try to find the first available user/account
EXISTING_USER_ID = "yashvika"  # Using Yashvika's user ID
EXISTING_ACCOUNT_ID = "yashvika_account"  # Using Yashvika's account ID

class E2ETestFlow:
    def __init__(self):
        self.session = None
        self.user_id = None
        self.account_id = None
        self.collateral_id = None
        self.loan_transaction_id = None
        self.extension_transaction_id = None
        self.payment_transaction_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def log_step(self, step_name, data=None):
        """Log a test step with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] 🔄 {step_name}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")
    
    async def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request and handle response"""
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    result = await response.json()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    result = await response.json()
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data) as response:
                    result = await response.json()
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status != expected_status:
                print(f"❌ Expected status {expected_status}, got {response.status}")
                print(f"   Response: {result}")
                return None
                
            return result
            
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    async def step_1_get_user(self):
        """Step 1: Get existing user"""
        await self.log_step("Step 1: Getting existing user")
        
        if EXISTING_USER_ID:
            # Use specific user ID if provided
            result = await self.make_request("GET", f"/users/{EXISTING_USER_ID}")
            if result:
                self.user_id = EXISTING_USER_ID
                print(f"✅ Using specified user: {self.user_id}")
                print(f"   Name: {result['first_name']} {result['last_name']}")
                print(f"   Email: {result['email']}")
                return True
            else:
                print(f"❌ Specified user ID not found: {EXISTING_USER_ID}")
                return False
        else:
            # Get the first available user
            result = await self.make_request("GET", "/users/")
            if result and result['users']:
                self.user_id = result['users'][0]['id']
                user = result['users'][0]
                print(f"✅ Using first available user: {self.user_id}")
                print(f"   Name: {user['first_name']} {user['last_name']}")
                print(f"   Email: {user['email']}")
                return True
            else:
                print("❌ No users found in the system")
                return False
    
    async def step_2_get_account(self):
        """Step 2: Get existing account for user"""
        await self.log_step("Step 2: Getting existing account for user")
        
        if EXISTING_ACCOUNT_ID:
            # Use specific account ID if provided
            result = await self.make_request("GET", f"/accounts/{EXISTING_ACCOUNT_ID}")
            if result:
                self.account_id = EXISTING_ACCOUNT_ID
                print(f"✅ Using specified account: {self.account_id}")
                print(f"   Account number: {result['account_number']}")
                print(f"   Balance: ${result['investment_balance']}")
                return True
            else:
                print(f"❌ Specified account ID not found: {EXISTING_ACCOUNT_ID}")
                return False
        else:
            # Get account for the user
            result = await self.make_request("GET", f"/accounts/user/{self.user_id}")
            if result:
                self.account_id = result["id"]
                print(f"✅ Using user's account: {self.account_id}")
                print(f"   Account number: {result['account_number']}")
                print(f"   Investment balance: ${result['investment_balance']}")
                print(f"   Loan balance: ${result['loan_balance']}")
                return True
            else:
                print("❌ No account found for user")
                return False
    
    async def step_3_deposit_money(self):
        """Step 3: Deposit money for testing"""
        await self.log_step("Step 3: Depositing money for testing")
        
        deposit_data = {
            "account_id": self.account_id,
            "user_id": self.user_id,
            "amount": "10000.00",  # $10,000 deposit
            "description": "Test deposit for collateral flow",
            "reference_number": f"TEST_DEP_{int(time.time())}",
            "metadata": {
                "test_deposit": True,
                "purpose": "collateral_flow_testing"
            }
        }
        
        result = await self.make_request("POST", "/transactions/deposit", deposit_data, expected_status=201)
        
        if result:
            print(f"✅ Deposited ${deposit_data['amount']}")
            print(f"   Transaction ID: {result['id']}")
            return True
        else:
            print("❌ Failed to deposit money")
            return False
    
    async def step_4_create_collateral(self):
        """Step 4: Create collateral with image analysis"""
        await self.log_step("Step 4: Creating collateral with image analysis")
        
        # Check if test image exists
        if not os.path.exists(TEST_IMAGE_PATH):
            print(f"❌ Test image not found: {TEST_IMAGE_PATH}")
            return False
        
        collateral_data = {
            "user_id": self.user_id,
            "name": "Luxury Rolex Watch",
            "description": "A high-end Rolex watch for collateral testing",
            "images": [TEST_IMAGE_PATH]
        }
        
        result = await self.make_request("POST", "/collaterals/", collateral_data, expected_status=201)
        
        if result:
            self.collateral_id = result["id"]
            print(f"✅ Created collateral: {self.collateral_id}")
            print(f"   Loan limit: ${result['loan_limit']}")
            print(f"   Interest rate: {float(result['interest']) * 100}%")
            print(f"   Due date: {result['due_date']}")
            return True
        else:
            print("❌ Failed to create collateral")
            return False
    
    async def step_5_approve_collateral(self):
        """Step 5: Approve collateral and create loan"""
        await self.log_step("Step 5: Approving collateral and creating loan")
        
        # Get collateral details to know loan limit
        collateral = await self.make_request("GET", f"/collaterals/{self.collateral_id}")
        if not collateral:
            print("❌ Failed to get collateral details")
            return False
        
        loan_amount = float(collateral["loan_limit"]) * 0.8  # 80% of loan limit
        
        approve_data = {
            "loan_amount": str(loan_amount)
        }
        
        result = await self.make_request("POST", f"/collaterals/{self.collateral_id}/approve", approve_data)
        
        if result:
            print(f"✅ Approved collateral with loan amount: ${loan_amount}")
            print(f"   New status: {result['status']}")
            return True
        else:
            print("❌ Failed to approve collateral")
            return False
    
    async def step_6_create_loan(self):
        """Step 6: Create loan disbursement"""
        await self.log_step("Step 6: Creating loan disbursement")
        
        # Get collateral details
        collateral = await self.make_request("GET", f"/collaterals/{self.collateral_id}")
        if not collateral:
            print("❌ Failed to get collateral details")
            return False
        
        loan_amount = float(collateral["loan_amount"])
        
        loan_data = {
            "account_id": self.account_id,
            "user_id": self.user_id,
            "collateral_id": self.collateral_id,
            "loan_amount": str(loan_amount),
            "description": f"Loan disbursement for {collateral['metadata']['name']}",
            "reference_number": f"LOAN_{int(time.time())}",
            "metadata": {
                "test_loan": True,
                "collateral_name": collateral['metadata']['name']
            }
        }
        
        result = await self.make_request("POST", "/transactions/create-loan", loan_data, expected_status=201)
        
        if result:
            self.loan_transaction_id = result["id"]
            print(f"✅ Created loan disbursement: ${loan_amount}")
            print(f"   Transaction ID: {self.loan_transaction_id}")
            return True
        else:
            print("❌ Failed to create loan")
            return False
    
    async def step_7_extend_loan(self):
        """Step 7: Extend loan with fee"""
        await self.log_step("Step 7: Extending loan with fee")
        
        extension_data = {
            "account_id": self.account_id,
            "user_id": self.user_id,
            "collateral_id": self.collateral_id,
            "extension_days": 30,
            "fee": "500.00",  # $500 extension fee
            "description": "30-day loan extension",
            "reference_number": f"EXT_{int(time.time())}",
            "metadata": {
                "test_extension": True,
                "extension_days": 30
            }
        }
        
        result = await self.make_request("POST", f"/collaterals/{self.collateral_id}/extend-loan", extension_data, expected_status=201)
        
        if result:
            self.extension_transaction_id = result["id"]
            print(f"✅ Extended loan for 30 days with fee: ${extension_data['fee']}")
            print(f"   Transaction ID: {self.extension_transaction_id}")
            return True
        else:
            print("❌ Failed to extend loan")
            return False
    
    async def step_8_pay_loan(self):
        """Step 8: Pay back the loan"""
        await self.log_step("Step 8: Paying back the loan")
        
        # Get current account balances to determine payment amount
        account = await self.make_request("GET", f"/accounts/{self.account_id}")
        if not account:
            print("❌ Failed to get account details")
            return False
        
        loan_balance = float(account["loan_balance"])
        payment_amount = loan_balance * 0.5  # Pay 50% of loan balance
        
        payment_data = {
            "account_id": self.account_id,
            "user_id": self.user_id,
            "amount": str(payment_amount),
            "collateral_id": self.collateral_id,
            "description": f"Partial loan payment of ${payment_amount}",
            "reference_number": f"PAY_{int(time.time())}",
            "metadata": {
                "test_payment": True,
                "payment_type": "partial"
            }
        }
        
        result = await self.make_request("POST", "/transactions/payment", payment_data, expected_status=201)
        
        if result:
            self.payment_transaction_id = result["id"]
            print(f"✅ Paid ${payment_amount} towards loan")
            print(f"   Transaction ID: {self.payment_transaction_id}")
            return True
        else:
            print("❌ Failed to pay loan")
            return False
    
    async def step_9_verify_final_state(self):
        """Step 9: Verify final state of all entities"""
        await self.log_step("Step 9: Verifying final state")
        
        # Get final account state
        account = await self.make_request("GET", f"/accounts/{self.account_id}")
        if account:
            print(f"✅ Final account state:")
            print(f"   Investment balance: ${account['investment_balance']}")
            print(f"   Loan balance: ${account['loan_balance']}")
        
        # Get final collateral state
        collateral = await self.make_request("GET", f"/collaterals/{self.collateral_id}")
        if collateral:
            print(f"✅ Final collateral state:")
            print(f"   Status: {collateral['status']}")
            print(f"   Loan amount: ${collateral['loan_amount']}")
            print(f"   Due date: {collateral['due_date']}")
        
        # Get all transactions for this account
        transactions = await self.make_request("GET", f"/transactions/?account_id={self.account_id}")
        if transactions:
            print(f"✅ Total transactions: {transactions['total']}")
            for tx in transactions['transactions']:
                print(f"   - {tx['transaction_type']}: ${tx['amount']} ({tx['status']})")
        
        return True
    
    async def run_full_flow(self):
        """Run the complete end-to-end test flow"""
        print("🚀 Starting Yashvika's End-to-End Collateral Flow Test")
        print("=" * 60)
        
        steps = [
            ("Get User", self.step_1_get_user),
            ("Get Account", self.step_2_get_account),
            ("Deposit Money", self.step_3_deposit_money),
            ("Create Collateral", self.step_4_create_collateral),
            ("Approve Collateral", self.step_5_approve_collateral),
            ("Create Loan", self.step_6_create_loan),
            ("Extend Loan", self.step_7_extend_loan),
            ("Pay Loan", self.step_8_pay_loan),
            ("Verify Final State", self.step_9_verify_final_state)
        ]
        
        for step_name, step_func in steps:
            try:
                success = await step_func()
                if not success:
                    print(f"❌ Step '{step_name}' failed. Stopping test.")
                    return False
                print(f"✅ Step '{step_name}' completed successfully")
                await asyncio.sleep(1)  # Small delay between steps
            except Exception as e:
                print(f"❌ Step '{step_name}' failed with exception: {e}")
                return False
        
        print("\n🎉 All steps completed successfully!")
        print("=" * 60)
        print("📊 Test Summary:")
        print(f"   User ID: {self.user_id}")
        print(f"   Account ID: {self.account_id}")
        print(f"   Collateral ID: {self.collateral_id}")
        print(f"   Loan Transaction ID: {self.loan_transaction_id}")
        print(f"   Extension Transaction ID: {self.extension_transaction_id}")
        print(f"   Payment Transaction ID: {self.payment_transaction_id}")
        
        return True

async def main():
    """Main function to run the test"""
    print("🔧 Checking prerequisites...")
    
    # Check if backend is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    print("✅ Backend server is running")
                else:
                    print("❌ Backend server is not responding properly")
                    return
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        print(f"   Make sure the server is running on {BASE_URL}")
        return
    
    # Check if test image exists
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ Test image not found: {TEST_IMAGE_PATH}")
        print("   Please ensure the test image is available")
        return
    
    # Check if users exist in the system
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/users/") as response:
                if response.status == 200:
                    users_data = await response.json()
                    if not users_data.get('users'):
                        print("❌ No users found in the system")
                        print("   Please create at least one user before running the test")
                        return
                    print(f"✅ Found {len(users_data['users'])} users in the system")
                else:
                    print("❌ Cannot fetch users from the system")
                    return
    except Exception as e:
        print(f"❌ Cannot check users: {e}")
        return
    
    print("✅ All prerequisites met")
    
    # Run the test flow
    async with E2ETestFlow() as test_flow:
        success = await test_flow.run_full_flow()
        
        if success:
            print("\n🎯 End-to-End Test PASSED!")
            sys.exit(0)
        else:
            print("\n💥 End-to-End Test FAILED!")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
