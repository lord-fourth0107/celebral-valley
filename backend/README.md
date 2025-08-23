# Celebral Valley Backend API

A FastAPI-based backend for the Celebral Valley DeFi lending and borrowing platform.

## Project Structure

```
backend/
├── app.py                 # Main FastAPI application
├── run.py                 # Application runner script
├── requirements.txt       # Python dependencies
├── dataModels/           # Pydantic data models
│   ├── user.py
│   ├── account.py
│   ├── collateral.py
│   └── transaction.py
├── routes/               # API route modules
│   ├── auth.py          # Authentication endpoints
│   ├── users.py         # User management endpoints
│   ├── accounts.py      # Account management endpoints
│   ├── collaterals.py   # Collateral management endpoints
│   └── transactions.py  # Transaction management endpoints
└── migrations/          # Database migrations
```

## Features

- **Authentication**: JWT-based authentication (TODO: implement endpoints)
- **User Management**: CRUD operations for users (TODO: implement endpoints)
- **Account Management**: Account creation and management (TODO: implement endpoints)
- **Collateral Management**: Collateral submission, approval, and management (TODO: implement endpoints)
- **Transaction Management**: Complete transaction lifecycle management (TODO: implement endpoints)
- **Transaction Ledger**: Complete transaction history for accounts

## API Endpoints

All route modules are set up with proper prefixes and tags, but endpoints are not yet implemented.

### Route Structure
- `/auth` - Authentication endpoints (TODO: implement)
- `/users` - User management endpoints (TODO: implement)
- `/accounts` - Account management endpoints (TODO: implement)
- `/collaterals` - Collateral management endpoints (TODO: implement)
- `/transactions` - Transaction management endpoints (TODO: implement)



## Installation and Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python run.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API**:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - ReDoc docs: http://localhost:8000/redoc

## Development Notes

- Currently uses in-memory storage for demo purposes
- Replace with proper database integration (PostgreSQL recommended)
- Add proper password hashing for production
- Configure proper CORS settings for production
- Add proper JWT secret key management
- Implement proper error handling and logging
- Add rate limiting and security measures

## Database Integration

The application is designed to work with PostgreSQL. To integrate with a database:

1. Set up PostgreSQL database
2. Configure database connection in environment variables
3. Run migrations using Alembic
4. Replace in-memory storage with database operations

## Security Considerations

- Use environment variables for sensitive configuration
- Implement proper password hashing (bcrypt)
- Add rate limiting
- Configure CORS properly for production
- Use HTTPS in production
- Implement proper input validation
- Add audit logging
