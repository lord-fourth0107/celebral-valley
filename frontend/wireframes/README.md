# PawnLoan App Wireframes

This directory contains ASCII wireframes for the PawnLoan mobile application - a peer-to-peer lending platform where users can get loans using their physical items as collateral, and invest in other users' loans.

## User Flow Overview

### Borrowing Flow
1. **Main Navigation** (`01-main-tabs.txt`) - Bottom tab navigation
2. **My Loans** (`02-borrow-loans.txt`) - View existing loans, create new ones
3. **New Loan Form** (`03-new-loan-form.txt`) - Item details and description
4. **Camera Screen** (`04-camera-screen.txt`) - Take photos of item
5. **Valuation Result** (`05-valuation-result.txt`) - AI valuation and loan offer
6. **Loan Details** (`07-loan-details.txt`) - Manage active loans

### Investing Flow
1. **Investment Hub** (`06-invest-tab.txt`) - Browse available loans to fund
2. **Investment Details** (`08-investment-details.txt`) - Loan evaluation and funding

## Key Features

### For Borrowers
- **Item Photography**: Multiple photos with camera integration
- **AI Valuation**: Automated item assessment and loan offers
- **Flexible Terms**: 30-day standard loans with extension options
- **Payment Options**: Full payment, partial payment, or loan extension
- **Status Tracking**: Clear visibility of loan status and due dates

### For Investors
- **Portfolio Dashboard**: Track investments and returns
- **Risk Assessment**: Star rating system for loan risk
- **Borrower Profiles**: Credit scores and payment history
- **ROI Calculations**: Clear profit and return percentages
- **Market Data**: Item values and demand indicators

## Technical Integration

These wireframes are designed to work with the existing camera upload functionality:
- Reuse the camera component from the current React Native app
- Extend the backend to handle loan valuation APIs
- Add new endpoints for borrowing and investing features

## Screen Dimensions

All wireframes are designed for mobile screens with:
- Portrait orientation
- Bottom tab navigation
- Standard mobile interaction patterns
- Touch-friendly button sizes

## Next Steps

1. Convert wireframes to React Native components
2. Integrate with existing camera functionality
3. Build loan valuation backend API
4. Add user authentication and profile management
5. Implement payment processing
6. Add push notifications for loan reminders