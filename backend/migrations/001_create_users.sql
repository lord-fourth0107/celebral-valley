-- Create app_users table
CREATE TABLE IF NOT EXISTS app_users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    date_of_birth TIMESTAMP,
    address TEXT,
    city VARCHAR(255),
    state VARCHAR(255),
    country VARCHAR(255),
    postal_code VARCHAR(20),
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'admin', 'verifier')),
    status VARCHAR(50) NOT NULL DEFAULT 'pending_verification' CHECK (status IN ('active', 'inactive', 'pending_verification')),
    kyc_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_app_users_email ON app_users (email);
CREATE INDEX IF NOT EXISTS idx_app_users_username ON app_users (username);
CREATE INDEX IF NOT EXISTS idx_app_users_role ON app_users (role);
CREATE INDEX IF NOT EXISTS idx_app_users_status ON app_users (status);
CREATE INDEX IF NOT EXISTS idx_app_users_kyc_verified ON app_users (kyc_verified);

-- Create trigger function for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for app_users table
CREATE TRIGGER update_app_users_updated_at 
    BEFORE UPDATE ON app_users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
