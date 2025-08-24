-- Create yashvika user
INSERT INTO app_users (
    id, email, username, first_name, last_name, role, status, kyc_verified
) VALUES (
    'yashvika',
    'yashvika@example.com',
    'yashvika',
    'Yashvika',
    'User',
    'user',
    'active',
    TRUE
) ON CONFLICT (id) DO NOTHING;

-- Create yashvika account
INSERT INTO accounts (
    id, user_id, account_number, status, wallet_id, loan_balance, investment_balance, created_at, updated_at
) VALUES (
    'yashvika',
    'yashvika',
    'YASH001',
    'active',
    'yashvika-wallet-001',
    0.00,
    0.00,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
) ON CONFLICT (id) DO NOTHING;
