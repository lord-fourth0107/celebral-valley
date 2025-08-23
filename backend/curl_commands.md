# API Endpoints - cURL Commands

Base URL: `http://localhost:8000`

## 🔐 Authentication
*Note: These endpoints don't require authentication for now*

---

## 👥 User Management

### 1. Create User
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role": "user"
  }'
```

### 2. Create Organization User
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "org@company.com",
    "username": "company_org",
    "first_name": "Company",
    "last_name": "Organization",
    "phone": "+1234567890",
    "role": "organization"
  }'
```

### 3. Get All Users (with pagination)
```bash
# Get all users (default: page 1, 20 per page)
curl -X GET "http://localhost:8000/users/"

# Get users with pagination
curl -X GET "http://localhost:8000/users/?page=1&page_size=10"

# Get users with filters
curl -X GET "http://localhost:8000/users/?email=john&status=active&kyc_verified=true"

# Get users by role
curl -X GET "http://localhost:8000/users/?role=organization"
```

### 4. Get User by ID
```bash
curl -X GET "http://localhost:8000/users/{user_id}"
```

### 5. Get User by Email
```bash
curl -X GET "http://localhost:8000/users/email/john.doe@example.com"
```

### 6. Get User by Username
```bash
curl -X GET "http://localhost:8000/users/username/johndoe"
```

### 7. Update User
```bash
curl -X PUT "http://localhost:8000/users/{user_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Johnny",
    "last_name": "Smith",
    "phone": "+0987654321",
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "postal_code": "10001"
  }'
```

### 8. Update User Status
```bash
curl -X PATCH "http://localhost:8000/users/{user_id}/status" \
  -H "Content-Type: application/json" \
  -d '"active"'
```

### 9. Update KYC Status
```bash
curl -X PATCH "http://localhost:8000/users/{user_id}/kyc" \
  -H "Content-Type: application/json" \
  -d 'true'
```

### 10. Delete User
```bash
curl -X DELETE "http://localhost:8000/users/{user_id}"
```

### 11. Check User Exists
```bash
curl -X GET "http://localhost:8000/users/{user_id}/exists"
```

---

## 🏦 Account Management

### 1. Create Account (One per User) - Auto-generated Account Number
```bash
curl -X POST "http://localhost:8000/accounts/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "{user_id}"
  }'
```

### 2. Get All Accounts
```bash
# Get all accounts
curl -X GET "http://localhost:8000/accounts/"

# Get accounts with pagination
curl -X GET "http://localhost:8000/accounts/?page=1&page_size=10"

# Get accounts by user ID
curl -X GET "http://localhost:8000/accounts/?user_id={user_id}"

# Get accounts by status
curl -X GET "http://localhost:8000/accounts/?status=active"

# Get accounts by account number (partial match)
curl -X GET "http://localhost:8000/accounts/?account_number=ACC123"
```

### 3. Get Account by ID
```bash
curl -X GET "http://localhost:8000/accounts/{account_id}"
```

### 4. Get Account by User ID
```bash
curl -X GET "http://localhost:8000/accounts/user/{user_id}"
```

### 5. Get Account by Account Number
```bash
curl -X GET "http://localhost:8000/accounts/number/ACC123456789"
```

### 6. Update Account
```bash
curl -X PUT "http://localhost:8000/accounts/{account_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "inactive"
  }'
```

### 7. Update Account Status
```bash
curl -X PATCH "http://localhost:8000/accounts/{account_id}/status" \
  -H "Content-Type: application/json" \
  -d '"suspended"'
```

### 8. Close Account
```bash
curl -X PATCH "http://localhost:8000/accounts/{account_id}/close"
```

### 9. Delete Account
```bash
curl -X DELETE "http://localhost:8000/accounts/{account_id}"
```

### 10. Check Account Exists
```bash
curl -X GET "http://localhost:8000/accounts/{account_id}/exists"
```

---

## 💰 Collateral Management

### 1. Create Collateral
```bash
curl -X POST "http://localhost:8000/collaterals/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "{user_id}",
    "loan_amount": 10000.00,
    "loan_limit": 15000.00,
    "interest": 5.5,
    "due_date": "2024-12-31T23:59:59Z",
    "image_paths": ["/path/to/image1.jpg", "/path/to/image2.jpg"],
    "metadata": {
      "collateral_type": "jewelry",
      "description": "Gold necklace"
    }
  }'
```

### 2. Get All Collaterals
```bash
curl -X GET "http://localhost:8000/collaterals/"
```

### 3. Get Collateral by ID
```bash
curl -X GET "http://localhost:8000/collaterals/{collateral_id}"
```

### 4. Update Collateral
```bash
curl -X PUT "http://localhost:8000/collaterals/{collateral_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "loan_amount": 12000.00
  }'
```

### 5. Delete Collateral
```bash
curl -X DELETE "http://localhost:8000/collaterals/{collateral_id}"
```

---

## 💰 Transaction Management

### 1. Invest Money
```bash
curl -X POST "http://localhost:8000/transactions/invest" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "{account_id}",
    "user_id": "{user_id}",
    "amount": 5000.00,
    "description": "Investment in platform"
  }'
```

### 2. Withdraw Money
```bash
curl -X POST "http://localhost:8000/transactions/withdraw" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "{account_id}",
    "user_id": "{user_id}",
    "amount": 1000.00,
    "description": "Withdrawal to bank account"
  }'
```

### 3. Pay Loan
```bash
curl -X POST "http://localhost:8000/transactions/pay-loan" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "{account_id}",
    "user_id": "{user_id}",
    "amount": 500.00,
    "collateral_id": "{collateral_id}",
    "description": "Monthly loan payment"
  }'
```

### 4. Extend Loan
```bash
curl -X POST "http://localhost:8000/transactions/extend-loan" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "{account_id}",
    "user_id": "{user_id}",
    "collateral_id": "{collateral_id}",
    "extension_days": 30,
    "fee": 50.00,
    "description": "Loan extension request"
  }'
```

### 5. Get All Transactions
```bash
# Get all transactions
curl -X GET "http://localhost:8000/transactions/"

# Get transactions with pagination
curl -X GET "http://localhost:8000/transactions/?page=1&page_size=10"

# Get transactions by account
curl -X GET "http://localhost:8000/transactions/?account_id={account_id}"

# Get transactions by user
curl -X GET "http://localhost:8000/transactions/?user_id={user_id}"

# Get transactions by type
curl -X GET "http://localhost:8000/transactions/?transaction_type=invest"

# Get transactions by status
curl -X GET "http://localhost:8000/transactions/?status=completed"
```

### 6. Get Transaction by ID
```bash
curl -X GET "http://localhost:8000/transactions/{transaction_id}"
```

### 7. Get Transactions by Account
```bash
curl -X GET "http://localhost:8000/transactions/account/{account_id}"
```

### 8. Get Transactions by User
```bash
curl -X GET "http://localhost:8000/transactions/user/{user_id}"
```

### 9. Get Transactions by Type
```bash
curl -X GET "http://localhost:8000/transactions/type/invest"
curl -X GET "http://localhost:8000/transactions/type/withdraw"
curl -X GET "http://localhost:8000/transactions/type/pay_loan"
curl -X GET "http://localhost:8000/transactions/type/extend_loan"
```

### 10. Get User Transaction Summary
```bash
curl -X GET "http://localhost:8000/transactions/user/{user_id}/summary"
```

---

## 🔍 System Endpoints

### 1. Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

### 2. API Root
```bash
curl -X GET "http://localhost:8000/"
```

---

## 📝 Example Usage Scenarios

### Complete User Registration & Account Creation Flow
```bash
# 1. Create user
USER_RESPONSE=$(curl -s -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "username": "alice",
    "first_name": "Alice",
    "last_name": "Johnson",
    "phone": "+1234567890",
    "role": "user"
  }')

# Extract user ID from response
USER_ID=$(echo $USER_RESPONSE | jq -r '.id')

# 2. Create account for user (account number auto-generated)
ACCOUNT_RESPONSE=$(curl -s -X POST "http://localhost:8000/accounts/" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\"
  }")

# Extract account ID and account number from response
ACCOUNT_ID=$(echo $ACCOUNT_RESPONSE | jq -r '.id')
ACCOUNT_NUMBER=$(echo $ACCOUNT_RESPONSE | jq -r '.account_number')

echo "Created account: $ACCOUNT_NUMBER"

# 3. Update user status to active
curl -X PATCH "http://localhost:8000/users/$USER_ID/status" \
  -H "Content-Type: application/json" \
  -d '"active"'

# 4. Update KYC status
curl -X PATCH "http://localhost:8000/users/$USER_ID/kyc" \
  -H "Content-Type: application/json" \
  -d 'true'

# 5. Verify account was created
curl -X GET "http://localhost:8000/accounts/user/$USER_ID"
```

### Organization User & Account Setup
```bash
# 1. Create organization user
ORG_RESPONSE=$(curl -s -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "org@company.com",
    "username": "company_org",
    "first_name": "Company",
    "last_name": "Organization",
    "phone": "+1234567890",
    "role": "organization"
  }')

ORG_USER_ID=$(echo $ORG_RESPONSE | jq -r '.id')

# 2. Create account for organization (account number auto-generated)
curl -X POST "http://localhost:8000/accounts/" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$ORG_USER_ID\"
  }"

# 3. Activate organization account
curl -X PATCH "http://localhost:8000/users/$ORG_USER_ID/status" \
  -H "Content-Type: application/json" \
  -d '"active"'
```

### Account Management Operations
```bash
# 1. Get user's account
ACCOUNT=$(curl -s -X GET "http://localhost:8000/accounts/user/$USER_ID")
ACCOUNT_ID=$(echo $ACCOUNT | jq -r '.id')

# 2. Update account status
curl -X PATCH "http://localhost:8000/accounts/$ACCOUNT_ID/status" \
  -H "Content-Type: application/json" \
  -d '"suspended"'

# 3. Reactivate account
curl -X PATCH "http://localhost:8000/accounts/$ACCOUNT_ID/status" \
  -H "Content-Type: application/json" \
  -d '"active"'

# 4. Close account
curl -X PATCH "http://localhost:8000/accounts/$ACCOUNT_ID/close"
```

---

## 🚀 Running the API

1. **Start the server:**
```bash
cd backend
source .venv/bin/activate
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

2. **Access API documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

3. **Test endpoints:**
```bash
# Test health check
curl http://localhost:8000/health

# Test root endpoint
curl http://localhost:8000/
```

---

## 📋 Notes

- Replace `{user_id}`, `{account_id}`, `{collateral_id}`, `{transaction_id}` with actual IDs
- All timestamps should be in ISO 8601 format
- The API uses JSON for request/response bodies
- Error responses include detailed error messages
- Pagination is available for list endpoints
- Filtering is available for user, account, and transaction endpoints
- **One account per user** - attempting to create a second account for the same user will fail
- **Organization role** - users can have role "organization" for organizational accounts
- **Auto-generated account numbers** - account numbers are automatically generated in format `ACC{timestamp}{random_suffix}` and are guaranteed to be unique
- **Transaction types** - supported types: `invest`, `withdraw`, `pay_loan`, `extend_loan`, `interest`, `loan_disbursement`, `fee`
- **Transaction statuses** - supported statuses: `pending`, `completed`, `failed`, `cancelled`, `reversed`
- **Immutable transactions** - transactions cannot be updated, modified, or deleted as they are ledger entries
- **Business logic placeholders** - transaction endpoints include TODO comments where business logic will be implemented later
