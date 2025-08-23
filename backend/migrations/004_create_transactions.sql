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
    processed_at TIMESTAMP,
    failed_at TIMESTAMP,
    failure_reason TEXT,
    
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (collateral_id) REFERENCES collaterals(id) ON DELETE SET NULL,
    
    INDEX idx_account_id (account_id),
    INDEX idx_user_id (user_id),
    INDEX idx_transaction_type (transaction_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_collateral_id (collateral_id),
    INDEX idx_reference_number (reference_number)
);
