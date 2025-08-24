"""
Balance calculation service

This module handles balance calculations and updates for transactions.
"""

from decimal import Decimal
from typing import Tuple

from dataModels.transaction import TransactionType, TransactionCreate
from db.account import AccountDB
from db.transaction import TransactionDB


class BalanceService:
    """Service for handling balance calculations and updates"""

    @staticmethod
    async def calculate_balances_for_transaction(
        account_id: str, 
        transaction_type: TransactionType, 
        amount: Decimal,
        user_id: str = None
    ) -> Tuple[Decimal, Decimal, Decimal, Decimal]:
        """
        Calculate balance before and after for a transaction
        
        Returns:
            Tuple of (loan_balance_before, loan_balance_after, invested_balance_before, invested_balance_after)
        """
        # Get current account balances
        account = await AccountDB.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        loan_balance_before = account.loan_balance
        invested_balance_before = account.investment_balance
        
        # Calculate new balances based on transaction type
        loan_balance_after = loan_balance_before
        invested_balance_after = invested_balance_before
        
        if transaction_type == TransactionType.DEPOSIT:
            # Deposit increases investment balance
            invested_balance_after = invested_balance_before + amount
            if user_id == "organization":
                loan_balance_after = Decimal('0.00')  # Organization never has loan balance
            
        elif transaction_type == TransactionType.WITHDRAWAL:
            # Withdrawal decreases investment balance
            if invested_balance_before < amount:
                raise ValueError(f"Insufficient investment balance. Available: {invested_balance_before}, Required: {amount}")
            invested_balance_after = invested_balance_before - amount
            if user_id == "organization":
                loan_balance_after = Decimal('0.00')  # Organization never has loan balance
            
        elif transaction_type == TransactionType.LOAN_DISBURSEMENT:
            # Loan disbursement increases loan balance for users, but organization never gets loan balance
            if user_id == "organization":
                # Organization disbursement should not happen (they don't take loans)
                raise ValueError("Organization cannot receive loan disbursements")
            else:
                loan_balance_after = loan_balance_before + amount
            
        elif transaction_type == TransactionType.PAYMENT:
            # Payment decreases loan balance for users, but investment balance for organization
            if user_id == "organization":
                # Organization payment decreases investment balance (paying from investment funds)
                if invested_balance_before < amount:
                    raise ValueError(f"Insufficient investment balance. Available: {invested_balance_before}, Required: {amount}")
                invested_balance_after = invested_balance_before - amount
                loan_balance_after = Decimal('0.00')  # Organization never has loan balance
            else:
                # User payment decreases loan balance
                if loan_balance_before < amount:
                    raise ValueError(f"Insufficient loan balance. Available: {loan_balance_before}, Required: {amount}")
                loan_balance_after = loan_balance_before - amount
                invested_balance_after = invested_balance_before
            
        elif transaction_type == TransactionType.FEE:
            # Fee decreases investment balance (or loan balance depending on context)
            # For now, we'll deduct from investment balance
            if invested_balance_before < amount:
                raise ValueError(f"Insufficient investment balance for fee. Available: {invested_balance_before}, Required: {amount}")
            invested_balance_after = invested_balance_before - amount
            if user_id == "organization":
                loan_balance_after = Decimal('0.00')  # Organization never has loan balance
            
        elif transaction_type == TransactionType.INTEREST:
            # Interest increases investment balance
            invested_balance_after = invested_balance_before + amount
            if user_id == "organization":
                loan_balance_after = Decimal('0.00')  # Organization never has loan balance
            
        return loan_balance_before, loan_balance_after, invested_balance_before, invested_balance_after

    @staticmethod
    async def update_account_balances(account_id: str, loan_balance: Decimal, investment_balance: Decimal):
        """Update account balances"""
        await AccountDB.update_account_balances(
            account_id=account_id,
            loan_balance=float(loan_balance),
            investment_balance=float(investment_balance)
        )

    @staticmethod
    async def process_transaction_balances(transaction_id: str):
        """Process and update balances for a transaction"""
        # Get the transaction
        transaction = await TransactionDB.get_transaction_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        # Calculate balances
        loan_balance_before, loan_balance_after, invested_balance_before, invested_balance_after = \
            await BalanceService.calculate_balances_for_transaction(
                transaction.account_id,
                transaction.transaction_type,
                transaction.amount,
                transaction.user_id
            )
        
        # Update transaction with balance information
        await TransactionDB.update_transaction_balances(
            transaction_id=transaction_id,
            loan_balance_before=float(loan_balance_before),
            loan_balance_after=float(loan_balance_after),
            invested_balance_before=float(invested_balance_before),
            invested_balance_after=float(invested_balance_after)
        )
        
        # Update account balances
        await BalanceService.update_account_balances(
            account_id=transaction.account_id,
            loan_balance=loan_balance_after,
            investment_balance=invested_balance_after
        )
        
        # Mark transaction as completed
        await TransactionDB.mark_transaction_completed(transaction_id)
        
        # Create opposite transaction for organization account for specific transaction types
        # Only create opposite transactions for user transactions, not organization transactions
        if (transaction.transaction_type in [
            TransactionType.DEPOSIT, 
            TransactionType.WITHDRAWAL, 
            TransactionType.LOAN_DISBURSEMENT, 
            TransactionType.PAYMENT,
            TransactionType.FEE
        ] and transaction.user_id != "organization"):
            try:
                await BalanceService.create_opposite_organization_transaction(
                    user_transaction_id=transaction_id,
                    user_account_id=transaction.account_id,
                    user_id=transaction.user_id,
                    transaction_type=transaction.transaction_type,
                    amount=transaction.amount,
                    description=f"Opposite transaction for {transaction.description}",
                    collateral_id=transaction.collateral_id
                )
            except Exception as e:
                # Log the error but don't fail the user transaction
                print(f"Failed to create opposite organization transaction: {e}")
        
        return {
            "loan_balance_before": loan_balance_before,
            "loan_balance_after": loan_balance_after,
            "invested_balance_before": invested_balance_before,
            "invested_balance_after": invested_balance_after
        }

    @staticmethod
    async def create_opposite_organization_transaction(
        user_transaction_id: str,
        user_account_id: str,
        user_id: str,
        transaction_type: TransactionType,
        amount: Decimal,
        description: str = None,
        collateral_id: str = None
    ):
        """Create an opposite transaction for the organization account"""
        # Get organization account
        org_account = await AccountDB.get_organization_account()
        if not org_account:
            raise ValueError("Organization account not found")
        
        # Determine opposite transaction type
        opposite_type = BalanceService._get_opposite_transaction_type(transaction_type)
        
        # Create opposite transaction data
        opposite_transaction_data = TransactionCreate(
            account_id=org_account.id,
            user_id="organization",  # Organization user ID
            transaction_type=opposite_type,
            amount=amount,
            description=description or f"Opposite transaction for {transaction_type.value}",
            reference_number=user_transaction_id,  # Reference to original transaction
            collateral_id=collateral_id,
            metadata={
                "opposite_to": user_transaction_id,
                "user_account_id": user_account_id,
                "user_id": user_id,
                "original_transaction_type": transaction_type.value
            }
        )
        
        # Create the opposite transaction
        opposite_transaction = await TransactionDB.create_transaction(opposite_transaction_data)
        
        # Process balances for the opposite transaction
        try:
            await BalanceService.process_transaction_balances(opposite_transaction.id)
        except ValueError as e:
            # If balance processing fails, mark transaction as failed
            await TransactionDB.mark_transaction_failed(opposite_transaction.id, str(e))
            raise e
        
        return opposite_transaction

    @staticmethod
    def _get_opposite_transaction_type(transaction_type: TransactionType) -> TransactionType:
        """Get the opposite transaction type for organization account"""
        opposite_map = {
            TransactionType.DEPOSIT: TransactionType.DEPOSIT,  # User deposits, org also deposits (same)
            TransactionType.WITHDRAWAL: TransactionType.WITHDRAWAL,  # User withdraws, org also withdraws (same)
            TransactionType.LOAN_DISBURSEMENT: TransactionType.WITHDRAWAL,  # User gets loan, org withdraws (opposite)
            TransactionType.PAYMENT: TransactionType.DEPOSIT,  # User pays, org deposits (opposite)
            TransactionType.FEE: TransactionType.INTEREST,  # User pays fee, org gets interest
            TransactionType.INTEREST: TransactionType.FEE,  # User gets interest, org pays fee
        }
        
        return opposite_map.get(transaction_type, transaction_type)

    @staticmethod
    async def revert_transaction_balances(transaction_id: str):
        """Revert balance changes for a transaction (used when Crossmint fails)"""
        # Get the transaction
        transaction = await TransactionDB.get_transaction_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        # Get the balance information from the transaction
        if (transaction.loan_balance_before is None or 
            transaction.invested_balance_before is None):
            raise ValueError(f"Transaction {transaction_id} does not have balance information to revert")
        
        # Revert account balances to the before state
        await BalanceService.update_account_balances(
            account_id=transaction.account_id,
            loan_balance=Decimal(str(transaction.loan_balance_before)),
            investment_balance=Decimal(str(transaction.invested_balance_before))
        )
        
        # Mark transaction as failed
        await TransactionDB.mark_transaction_failed(transaction_id, "Reverted due to Crossmint failure")
        
        return {
            "reverted_loan_balance": transaction.loan_balance_before,
            "reverted_invested_balance": transaction.invested_balance_before
        }
