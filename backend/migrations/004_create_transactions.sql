-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id VARCHAR(255) PRIMARY KEY,
    account_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('deposit', 'withdrawal', 'interest', 'loan_disbursement', 'payment', 'fee')),
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'cancelled', 'reversed')),
    amount DECIMAL(15,2) NOT NULL,
    fee DECIMAL(15,2),
    description TEXT,
    reference_number VARCHAR(255),
    collateral_id VARCHAR(255),
    loan_balance_before DECIMAL(15,2),
    loan_balance_after DECIMAL(15,2),
    invested_balance_before DECIMAL(15,2),
    invested_balance_after DECIMAL(15,2),
    metadata JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    failed_at TIMESTAMP,
    failure_reason TEXT,
    
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE CASCADE,
    FOREIGN KEY (collateral_id) REFERENCES collaterals(id) ON DELETE SET NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions (account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions (user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_transaction_type ON transactions (transaction_type);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions (status);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions (created_at);
CREATE INDEX IF NOT EXISTS idx_transactions_collateral_id ON transactions (collateral_id);
CREATE INDEX IF NOT EXISTS idx_transactions_reference_number ON transactions (reference_number);

-- Create trigger for transactions table
CREATE TRIGGER update_transactions_updated_at 
    BEFORE UPDATE ON transactions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
