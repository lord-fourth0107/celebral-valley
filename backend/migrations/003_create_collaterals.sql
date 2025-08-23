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
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_collaterals_user_id ON collaterals (user_id);
CREATE INDEX IF NOT EXISTS idx_collaterals_status ON collaterals (status);
CREATE INDEX IF NOT EXISTS idx_collaterals_due_date ON collaterals (due_date);
CREATE INDEX IF NOT EXISTS idx_collaterals_loan_amount ON collaterals (loan_amount);
CREATE INDEX IF NOT EXISTS idx_collaterals_loan_limit ON collaterals (loan_limit);

-- Create trigger for collaterals table
CREATE TRIGGER update_collaterals_updated_at 
    BEFORE UPDATE ON collaterals 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
