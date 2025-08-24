# Database Management Scripts

This directory contains scripts for managing the database data.

## Scripts

### 1. `clear_all_data.py`
**Purpose**: Delete all rows from all tables in the database
**Usage**: `python clear_all_data.py`
**What it does**: 
- Clears all data from `transactions`, `collaterals`, `accounts`, and `app_users` tables
- Respects foreign key constraints by deleting in the correct order

### 2. `initialize_system.py`
**Purpose**: Initialize the system with default users and data
**Usage**: `python initialize_system.py`
**What it does**:
- Clears existing data first
- Creates 1 organization user (Kachra Seth) with ₹100,000 initial fund
- Creates 1 admin user (System Administrator)
- Creates 4 regular users (John Doe, Jane Smith, Bob Wilson, Alice Brown)
- Creates accounts for all users
- Sets up the organization account with initial funding

## User Details

### Organization User
- **Name**: Kachra Seth
- **Email**: kachra.seth@organization.com
- **Username**: kachra_seth
- **Role**: organization
- **Initial Fund**: ₹100,000

### Admin User
- **Name**: System Administrator
- **Email**: admin@celebralvalley.com
- **Username**: admin
- **Role**: admin

### Regular Users
1. **John Doe** (john.doe@example.com, johndoe)
2. **Jane Smith** (jane.smith@example.com, janesmith)
3. **Bob Wilson** (bob.wilson@example.com, bobwilson)
4. **Alice Brown** (alice.brown@example.com, alicebrown)

## Account Details

All users get accounts with the following structure:
- **Organization**: ORG001 (₹100,000 investment balance)
- **Admin**: ADMIN001 (₹0 balance)
- **Users**: ACC001, ACC002, ACC003, ACC004 (₹0 balance each)

## Prerequisites

- PostgreSQL database running
- `DATABASE_URL` environment variable set
- Required Python packages installed (`psycopg`, `python-dotenv`)

## Usage Examples

```bash
# Clear all data
python clear_all_data.py

# Initialize system with default data
python initialize_system.py

# Delete all rows (alternative to clear_all_data.py)
python delete_all_rows.py
```
