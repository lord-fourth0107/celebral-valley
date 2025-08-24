// Loan data structure for type safety and API extensibility
export const LoanStatus = {
  ACTIVE: 'Active',
  PAID_OFF: 'Paid Off',
  OVERDUE: 'Overdue'
};

export const createLoan = ({
  id,
  itemName,
  itemEmoji,
  borrowedAmount,
  dueDate,
  status = LoanStatus.ACTIVE,
  createdAt = new Date().toISOString()
}) => ({
  id,
  itemName,
  itemEmoji,
  borrowedAmount,
  dueDate,
  status,
  createdAt
});