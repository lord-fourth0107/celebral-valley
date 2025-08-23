-- Add organization role to app_users table
-- First drop the existing constraint
ALTER TABLE app_users DROP CONSTRAINT IF EXISTS app_users_role_check;

-- Add the new constraint with organization role
ALTER TABLE app_users ADD CONSTRAINT app_users_role_check 
    CHECK (role IN ('user', 'admin', 'verifier', 'organization'));
