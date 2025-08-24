-- Add balance columns to accounts table
ALTER TABLE accounts 
ADD COLUMN loan_balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
ADD COLUMN investment_balance DECIMAL(15,2) NOT NULL DEFAULT 0.00;

-- Create index on balances for efficient queries
CREATE INDEX IF NOT EXISTS idx_accounts_loan_balance ON accounts (loan_balance);
CREATE INDEX IF NOT EXISTS idx_accounts_investment_balance ON accounts (investment_balance);
