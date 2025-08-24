-- Add wallet_id column to accounts table
ALTER TABLE accounts 
ADD COLUMN wallet_id VARCHAR(255);

-- Create index on wallet_id for efficient queries
CREATE INDEX IF NOT EXISTS idx_accounts_wallet_id ON accounts (wallet_id);
