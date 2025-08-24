import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  Alert,
  Platform,
  ActivityIndicator,
  RefreshControl
} from 'react-native';
import apiClient from '../api/apiClient';

const LoanCard = ({ loan, onPayNow }) => (
  <View style={styles.loanCard}>
    <View style={styles.loanHeader}>
      <Text style={styles.itemEmoji}>{loan.itemEmoji}</Text>
      <Text style={styles.itemName}>{loan.itemName}</Text>
    </View>
    <Text style={styles.borrowedAmount}>Borrowed: ${loan.loanAmount}</Text>
    {loan.status === 'active' && loan.dueDate && (
      <Text style={styles.dueDate}>Due: {loan.dueDate}</Text>
    )}
    {loan.status === 'active' && loan.daysRemaining !== undefined && (
      <Text style={[styles.daysRemaining, 
        loan.daysRemaining < 7 ? styles.urgentDays : styles.normalDays
      ]}>
        {loan.daysRemaining} days remaining
      </Text>
    )}
    <View style={styles.statusRow}>
      <Text style={[styles.status, 
        loan.status === 'active' ? styles.activeStatus : styles.paidStatus
      ]}>
        Status: {loan.status === 'active' ? 'Active' : loan.status}
      </Text>
      {loan.status === 'active' && (
        <TouchableOpacity 
          style={styles.payButton}
          onPress={() => onPayNow(loan.id)}
        >
          <Text style={styles.payButtonText}>Pay Now</Text>
        </TouchableOpacity>
      )}
    </View>
    {loan.closedDate && (
      <Text style={styles.closedDate}>Closed: {loan.closedDate}</Text>
    )}
  </View>
);

export default function BorrowLoansScreen({ navigation }) {
  const [showPastLoans, setShowPastLoans] = useState(false);
  const [activeLoans, setActiveLoans] = useState([]);
  const [pastLoans, setPastLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [useMockData] = useState(true); // Toggle this to use real API

  // Format date to readable format
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };

  // Calculate days remaining
  const calculateDaysRemaining = (dueDate) => {
    const due = new Date(dueDate);
    const now = new Date();
    const diffTime = due - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  };

  // Transform API response to screen format
  const transformCollateral = (collateral) => {
    const base = {
      id: collateral.id,
      itemEmoji: collateral.item_emoji || '📦',
      itemName: collateral.item_name,
      loanAmount: collateral.loan_amount,
      status: collateral.status
    };

    if (collateral.status === 'active') {
      return {
        ...base,
        dueDate: formatDate(collateral.due_date),
        daysRemaining: collateral.days_remaining || calculateDaysRemaining(collateral.due_date)
      };
    } else {
      return {
        ...base,
        closedDate: formatDate(collateral.closed_at || collateral.due_date),
        status: 'Repaid'
      };
    }
  };

  // Fetch collaterals from API
  const fetchCollaterals = async () => {
    try {
      setError(null);
      
      // Use mock or real API based on toggle
      const fetchFunction = useMockData ? 
        apiClient.listCollateralsMock : 
        apiClient.listCollaterals;
      
      const response = await fetchFunction({ status: 'all' });
      
      // Separate active and past loans
      const active = [];
      const past = [];
      
      response.collaterals.forEach(collateral => {
        const transformed = transformCollateral(collateral);
        if (collateral.status === 'active') {
          active.push(transformed);
        } else {
          past.push(transformed);
        }
      });
      
      setActiveLoans(active);
      setPastLoans(past);
    } catch (err) {
      console.error('Error fetching collaterals:', err);
      setError('Failed to load loans. Please try again.');
      
      // Set default data on error
      setActiveLoans([]);
      setPastLoans([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchCollaterals();
  }, []);

  // Pull to refresh
  const onRefresh = () => {
    setRefreshing(true);
    fetchCollaterals();
  };

  const handleNewLoan = () => {
    navigation.navigate('NewLoanForm');
  };

  const handlePayNow = async (loanId) => {
    Alert.alert(
      'Pay Loan',
      'This will redirect you to payment processing.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Continue',
          onPress: () => {
            // TODO: Implement payment flow
            Alert.alert('Payment', 'Payment processing would be implemented here.');
          }
        }
      ]
    );
  };

  const toggleLoansView = () => {
    setShowPastLoans(!showPastLoans);
  };

  // Loading state
  if (loading) {
    return (
      <View style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <View style={styles.header}>
            <Text style={styles.title}>Your Loans</Text>
          </View>
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#007AFF" />
            <Text style={styles.loadingText}>Loading your loans...</Text>
          </View>
        </SafeAreaView>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <Text style={styles.title}>Your Loans</Text>
        </View>

        <ScrollView 
          style={styles.content}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor="#007AFF"
            />
          }
        >
          {error && (
            <View style={styles.errorContainer}>
              <Text style={styles.errorText}>{error}</Text>
              <TouchableOpacity style={styles.retryButton} onPress={fetchCollaterals}>
                <Text style={styles.retryButtonText}>Retry</Text>
              </TouchableOpacity>
            </View>
          )}

          <TouchableOpacity style={styles.newLoanButton} onPress={handleNewLoan}>
            <Text style={styles.newLoanButtonText}> Get a new loan </Text>
          </TouchableOpacity>

          {/* Active Loans Section */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Active Loans ({activeLoans.length}):</Text>
            {activeLoans.length === 0 ? (
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyText}>No active loans</Text>
                <Text style={styles.emptySubtext}>Get started by requesting a new loan above</Text>
              </View>
            ) : (
              activeLoans.map((loan) => (
                <LoanCard 
                  key={loan.id} 
                  loan={loan} 
                  onPayNow={handlePayNow}
                />
              ))
            )}
          </View>

          {/* Past Loans Section */}
          <View style={styles.section}>
            <TouchableOpacity onPress={toggleLoansView} style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Past Loans ({pastLoans.length}):</Text>
              <Text style={styles.toggleText}>
                {showPastLoans ? 'Hide' : 'Show'}
              </Text>
            </TouchableOpacity>
            
            {showPastLoans && (
              <>
                {pastLoans.length === 0 ? (
                  <View style={styles.emptyContainer}>
                    <Text style={styles.emptyText}>No past loans</Text>
                  </View>
                ) : (
                  pastLoans.map((loan) => (
                    <LoanCard 
                      key={loan.id} 
                      loan={loan} 
                      onPayNow={handlePayNow}
                    />
                  ))
                )}
              </>
            )}
          </View>
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  safeArea: {
    flex: 1,
  },
  header: {
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    paddingVertical: 15,
    alignItems: 'center',
    marginTop: Platform.OS === 'ios' ? 10 : 0,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  errorContainer: {
    backgroundColor: '#fff5f5',
    borderRadius: 8,
    padding: 16,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#ffcccc',
  },
  errorText: {
    color: '#cc0000',
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 12,
  },
  retryButton: {
    backgroundColor: '#007AFF',
    borderRadius: 6,
    paddingVertical: 8,
    paddingHorizontal: 16,
    alignSelf: 'center',
  },
  retryButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  newLoanButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 15,
    alignItems: 'center',
    marginBottom: 30,
  },
  newLoanButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  section: {
    marginBottom: 30,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  toggleText: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '500',
  },
  emptyContainer: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
  loanCard: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  loanHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  itemEmoji: {
    fontSize: 24,
    marginRight: 10,
  },
  itemName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  borrowedAmount: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  dueDate: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  daysRemaining: {
    fontSize: 12,
    fontWeight: '500',
    marginBottom: 10,
  },
  urgentDays: {
    color: '#ff6b35',
  },
  normalDays: {
    color: '#007AFF',
  },
  closedDate: {
    fontSize: 12,
    color: '#999',
    marginTop: 5,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  status: {
    fontSize: 14,
    fontWeight: '500',
  },
  activeStatus: {
    color: '#ff6b35',
  },
  paidStatus: {
    color: '#4CAF50',
  },
  payButton: {
    backgroundColor: '#007AFF',
    borderRadius: 6,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  payButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '500',
  },
});