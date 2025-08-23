-- Create collaterals table
CREATE TABLE IF NOT EXISTS collaterals (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'released', 'defaulted')),
    loan_amount DECIMAL(15,2) NOT NULL,
    loan_limit DECIMAL(15,2) NOT NULL,
    interest DECIMAL(5,4) NOT NULL,
    due_date TIMESTAMP NOT NULL,
    image_paths JSON,
    metadata JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_due_date (due_date),
    INDEX idx_loan_amount (loan_amount),
    INDEX idx_loan_limit (loan_limit)
);
