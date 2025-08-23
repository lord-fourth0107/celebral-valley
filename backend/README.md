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
   poetry install
   ```

2. **Run the application**:
   ```bash
   poetry run python run.py
   ```
   
   Or using uvicorn directly:
   ```bash
   poetry run uvicorn app:app --reload --host 0.0.0.0 --port 8000
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

The application uses PostgreSQL as the database backend with psycopg3 for high-performance async database operations. The database connection is managed through the `database.py` module.

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# PostgreSQL Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# Application Configuration
ENVIRONMENT=development
DEBUG=true
```

### Database Features

The `database.py` module provides:
- **Connection Pooling**: Efficient connection management with configurable pool size (5-20 connections)
- **Async Support**: Full async/await support for all database operations using psycopg3
- **Health Checks**: Built-in database health monitoring with connection pool status
- **Raw SQL Support**: Direct PostgreSQL queries with parameterized statements
- **Transaction Support**: Full transaction support with context managers

### Usage Examples

```python
from database import fetch_rows, fetch_row, execute_query, fetch_value

# Fetch multiple rows
users = await fetch_rows("SELECT * FROM users WHERE active = $1", True)

# Fetch single row
user = await fetch_row("SELECT * FROM users WHERE id = $1", user_id)

# Execute query (INSERT, UPDATE, DELETE)
result = await execute_query("INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id", "John", "john@example.com")

# Fetch single value
count = await fetch_value("SELECT COUNT(*) FROM users")

# Using connection context manager for transactions
from database import get_db_connection

async with get_db_connection() as conn:
    await conn.execute("BEGIN")
    try:
        await conn.execute("INSERT INTO users (name) VALUES ($1)", "John")
        await conn.execute("INSERT INTO profiles (user_id) VALUES ($1)", user_id)
        await conn.execute("COMMIT")
    except:
        await conn.execute("ROLLBACK")
        raise
```

### Database Setup

1. Ensure PostgreSQL is installed and running
2. Create your database
3. Set the `DATABASE_URL` in your `.env` file
4. Run migrations using Alembic:
   ```bash
   cd backend
   alembic upgrade head
   ```

## Security Considerations

- Use environment variables for sensitive configuration
- Implement proper password hashing (bcrypt)
- Add rate limiting
- Configure CORS properly for production
- Use HTTPS in production
- Implement proper input validation
- Add audit logging
