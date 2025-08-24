import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  Alert
} from 'react-native';
import { fetchActiveLoans, fetchPastLoans, payLoan } from '../data/mockData';
import { LoanStatus } from '../types/Loan';

const LoanCard = ({ loan, onPayNow }) => (
  <View style={styles.loanCard}>
    <View style={styles.loanHeader}>
      <Text style={styles.itemEmoji}>{loan.itemEmoji}</Text>
      <Text style={styles.itemName}>{loan.itemName}</Text>
    </View>
    <Text style={styles.borrowedAmount}>Borrowed: ${loan.borrowedAmount}</Text>
    {loan.status === LoanStatus.ACTIVE && (
      <Text style={styles.dueDate}>Due: {loan.dueDate}</Text>
    )}
    <View style={styles.statusRow}>
      <Text style={[styles.status, 
        loan.status === LoanStatus.ACTIVE ? styles.activeStatus : styles.paidStatus
      ]}>
        Status: {loan.status}
      </Text>
      {loan.status === LoanStatus.ACTIVE && (
        <TouchableOpacity 
          style={styles.payButton}
          onPress={() => onPayNow(loan.id)}
        >
          <Text style={styles.payButtonText}>Pay Now</Text>
        </TouchableOpacity>
      )}
    </View>
  </View>
);

export default function BorrowLoansScreen({ navigation }) {
  const [activeLoans, setActiveLoans] = useState([]);
  const [pastLoans, setPastLoans] = useState([]);

  useEffect(() => {
    loadLoans();
  }, []);

  const loadLoans = async () => {
    try {
      const [active, past] = await Promise.all([
        fetchActiveLoans(),
        fetchPastLoans()
      ]);
      setActiveLoans(active);
      setPastLoans(past);
    } catch (error) {
      Alert.alert('Error', 'Failed to load loans');
    }
  };

  const handleNewLoan = () => {
    navigation.navigate('NewLoanForm');
  };

  const handlePayNow = async (loanId) => {
    try {
      await payLoan(loanId);
      Alert.alert('Payment', 'Payment processed successfully');
      // Reload loans after payment
      loadLoans();
    } catch (error) {
      Alert.alert('Error', 'Payment failed');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>My Loans</Text>
      </View>
      
      <ScrollView style={styles.content}>
        <TouchableOpacity style={styles.newLoanButton} onPress={handleNewLoan}>
          <Text style={styles.newLoanButtonText}> Get a new loan </Text>
        </TouchableOpacity>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Active Loans:</Text>
          {activeLoans.map((loan) => (
            <LoanCard 
              key={loan.id} 
              loan={loan} 
              onPayNow={handlePayNow}
            />
          ))}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Past Loans:</Text>
          {pastLoans.map((loan) => (
            <LoanCard 
              key={loan.id} 
              loan={loan} 
              onPayNow={handlePayNow}
            />
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    paddingVertical: 15,
    alignItems: 'center',
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
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 15,
    color: '#333',
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
  },
  borrowedAmount: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  dueDate: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
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