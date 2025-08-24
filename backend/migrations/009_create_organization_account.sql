-- Create organization account
INSERT INTO accounts (
    id, user_id, account_number, status, wallet_id, loan_balance, investment_balance, created_at, updated_at
) VALUES (
    'org-account-001',
    'organization',
    'ORG001',
    'active',
    'org-wallet-001',
    0.00,
    0.00,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
) ON CONFLICT (id) DO NOTHING;
