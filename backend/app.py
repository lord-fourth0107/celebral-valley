from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from routes import users, accounts, collaterals, transactions, auth

app = FastAPI(
    title="Celebral Valley API",
    description="A DeFi lending and borrowing platform API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(collaterals.router)
app.include_router(transactions.router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Celebral Valley API",
        "version": "1.0.0",
        "description": "A DeFi lending and borrowing platform",
        "endpoints": {
            "auth": "/auth",
            "users": "/users",
            "accounts": "/accounts", 
            "collaterals": "/collaterals",
            "transactions": "/transactions"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

# Database initialization and background tasks can be added here
# For example:
# @app.on_event("startup")
# async def startup_event():
#     # Initialize database connection
#     # Run migrations
#     pass

# @app.on_event("shutdown") 
# async def shutdown_event():
#     # Close database connections
#     # Cleanup resources
#     pass



