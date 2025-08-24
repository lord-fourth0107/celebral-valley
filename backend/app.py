from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import database manager
from database import db_manager

# Import routers
from routes import users, accounts, transactions, collaterals

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
app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(collaterals.router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Kachra Seth API",
        "version": "1.0.0",
        "description": "A DeFi lending and borrowing platform",
        "endpoints": {
            "users": "/users",
            "accounts": "/accounts", 
            "transactions": "/transactions",
            "collaterals": "/collaterals"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from database import check_db_health
    
    db_health = await check_db_health()
    
    return {
        "status": "healthy" if db_health["status"] == "healthy" else "unhealthy",
        "message": "API is running",
        "database": db_health
    }

@app.on_event("startup")
async def startup_event():
    """Initialize database connections on startup"""
    ...
    # await db_manager.initialize()

@app.on_event("shutdown") 
async def shutdown_event():
    """Close database connections on shutdown"""
    await db_manager.close()



