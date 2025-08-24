# Celebral Valley

A comprehensive DeFi lending and borrowing platform built for hackathon implementation, featuring AI-powered collateral valuation, blockchain integration, and modern mobile-first user experience.

## 🚀 Project Overview

BrokeNoMore is a decentralized finance platform that enables users to borrow against physical assets (collateral) using AI-powered valuation. The platform combines traditional lending with modern DeFi principles, offering secure, transparent, and efficient lending services.

## 🏗️ Architecture

The project follows a modern microservices architecture with:

- **Backend**: FastAPI-based REST API with PostgreSQL database
- **Frontend**: React Native mobile application with Expo
- **AI Services**: Computer vision and LLM integration for asset valuation
- **Blockchain**: CrossMint integration for NFT and wallet management
- **Database**: PostgreSQL with async operations and connection pooling

## ✨ Key Features

### 💰 Financial Services
- **Lending**: Borrow against physical assets
- **Collateral Management**: AI-powered asset valuation
- **Transaction Ledger**: Complete financial history tracking
- **Balance Tracking**: Real-time balance updates

### 🤖 AI-Powered Valuation
- Computer vision analysis of collateral images
- LLM integration for detailed asset assessment
- Automated valuation scoring
- Risk assessment algorithms

### 📱 Mobile-First Experience
- React Native mobile application
- Camera integration for asset documentation
- Intuitive loan application flow
- Real-time status updates

### ⛓️ Finance
- CrossMint wallet integration
- NFT creation for collateral
- Smart contract integration
- Decentralized identity management

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with psycopg3
- **Authentication**: JWT with python-jose
- **AI/ML**: PyTorch, CLIP, Qdrant, Anthropic
- **Dependencies**: Poetry for package management
- **Testing**: pytest with async support

### Frontend
- **Framework**: React Native with Expo
- **Navigation**: React Navigation v7
- **State Management**: React Hooks
- **HTTP Client**: Axios
- **Camera**: Expo Camera
- **File System**: Expo File System

### Infrastructure
- **Database Migrations**: Alembic
- **Connection Pooling**: psycopg-pool
- **Environment Management**: python-dotenv
- **Code Quality**: Black, Flake8

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- Poetry (Python package manager)
- Expo CLI

### Backend Setup

1. **Clone and navigate to backend**:
   ```bash
   cd backend
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Environment configuration**:
   Create a `.env` file:
   ```env
   DATABASE_URL=postgresql://username:password@host:port/database_name
   ENVIRONMENT=development
   DEBUG=true
   ```

4. **Database setup**:
   ```bash
   # Run migrations
   poetry run python run_migration.py
   
   # Or using Alembic
   poetry run alembic upgrade head
   ```

5. **Start the backend**:
   ```bash
   poetry run python run.py
   # Or
   poetry run uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   # Or
   expo start
   ```

4. **Run on device/simulator**:
   ```bash
   npm run ios      # iOS Simulator
   npm run android  # Android Emulator
   npm run web      # Web Browser
   ```

## 📚 API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Core Endpoints

- **Users**: `/users` - User management and authentication
- **Accounts**: `/accounts` - Financial account operations
- **Collaterals**: `/collaterals` - Asset collateral management
- **Transactions**: `/transactions` - Financial transaction tracking

## 🗄️ Database Schema

The application uses a comprehensive database schema with the following core entities:

- **Users**: User profiles and authentication
- **Accounts**: Financial accounts with balances
- **Collaterals**: Asset collateral with valuations
- **Transactions**: Complete transaction history
- **Organizations**: Multi-tenant organization support

## 🔧 Development

### Code Quality
```bash
# Format code
poetry run black .

# Lint code
poetry run flake8

# Run tests
poetry run pytest
```

### Database Operations
```bash
# Clear all data (development only)
python clear_all_data.py

# Run specific migrations
python run_migration.py

# Initialize system
python initialize_system.py
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run specific test files
poetry run pytest test_core_logic.py
poetry run pytest test_integration.py
```




## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project was created for hackathon purposes. Please check with the team for licensing information.

## 👥 Team
Shubham Rastogi

Uttam Singh

Rohan Mishra

Yashavika Singh

---

**Built with ❤️ for the hackathon community** 
