import { createLoan, LoanStatus } from '../types/Loan';

// Hardcoded loan data - easily extensible to API calls
export const mockLoans = [
  createLoan({
    id: '1',
    itemName: 'iPhone 13 Pro',
    itemEmoji: '📱',
    borrowedAmount: 450,
    dueDate: 'Dec 15, 2025',
    status: LoanStatus.ACTIVE
  }),
  createLoan({
    id: '2',
    itemName: 'Nike Air Max',
    itemEmoji: '👟',
    borrowedAmount: 120,
    dueDate: 'Jan 10, 2026',
    status: LoanStatus.ACTIVE
  }),
  createLoan({
    id: '3',
    itemName: 'Sony Headphones',
    itemEmoji: '🎧',
    borrowedAmount: 80,
    dueDate: 'Nov 20, 2024',
    status: LoanStatus.PAID_OFF
  })
];

// API-ready functions for future backend integration
export const fetchActiveLoans = async () => {
  // Future: replace with actual API call
  return mockLoans.filter(loan => loan.status === LoanStatus.ACTIVE);
};

export const fetchPastLoans = async () => {
  // Future: replace with actual API call
  return mockLoans.filter(loan => loan.status === LoanStatus.PAID_OFF);
};

export const payLoan = async (loanId) => {
  // Future: replace with actual API call
  console.log('Paying loan:', loanId);
  // Mock payment logic here
};