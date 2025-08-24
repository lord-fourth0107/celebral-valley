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
  TextInput,
  Modal,
  ActivityIndicator
} from 'react-native';
import * as apiClient from '../api/apiClient';

export default function InvestScreen() {
  const [investmentData, setInvestmentData] = useState({
    totalInvested: 0,
    expectedReturn: 0,
    roi: 12.48,
    averageAPR: 12.48
  });
  const [showInvestModal, setShowInvestModal] = useState(false);
  const [investmentAmount, setInvestmentAmount] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [useMockData] = useState(false);
  const [accountData, setAccountData] = useState(null);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    loadInvestmentData();
  }, []);

  const loadInvestmentData = async () => {
    try {
      setLoading(true);
      
      // Fetch account data for hardcoded demo user
      const getAccountFunction = useMockData ? apiClient.getAccountByUserIdMock : apiClient.getAccountByUserId;
      const account = await getAccountFunction('yashvika');
      
      setAccountData(account);
      
      // Calculate investment data from account balance
      const totalInvested = account.investment_balance || 0;
      const roi = 12.48; // Fixed ROI percentage
      const expectedReturn = Math.round(totalInvested * (1 + roi / 100));
      
      setInvestmentData({
        totalInvested: totalInvested,
        expectedReturn: expectedReturn,
        roi: roi,
        averageAPR: roi
      });
      
      console.log('Investment data loaded:', {
        account_id: account.id,
        investment_balance: account.investment_balance,
        loan_balance: account.loan_balance
      });
      
    } catch (error) {
      console.error('Failed to load investment data:', error);
      Alert.alert(
        'Loading Error',
        `Unable to load investment data: ${error.message}`,
        [{ text: 'Retry', onPress: loadInvestmentData }]
      );
      
      // Fallback to default data
      setInvestmentData({
        totalInvested: 1250,
        expectedReturn: 1406,
        roi: 12.48,
        averageAPR: 12.48
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleInvestMore = () => {
    setInvestmentAmount('');
    setShowInvestModal(true);
  };

  const processInvestment = async (amount) => {
    try {
      const depositData = {
        account_id: accountData?.id || 'yashvika_account',
        user_id: 'yashvika',
        amount: amount,
        description: `Investment deposit of $${amount}`,
        reference_number: `INV_${Date.now()}`,
        metadata: {
          transaction_purpose: 'investment_deposit',
          investment_amount: amount.toString()
        }
      };

      const createDepositFunction = useMockData ? apiClient.createDepositMock : apiClient.createDeposit;
      const depositResult = await createDepositFunction(depositData);
      
      console.log('Deposit created successfully:', depositResult);
      
      // Update investment data locally
      setInvestmentData(prevData => {
        const newTotalInvested = prevData.totalInvested + amount;
        const newExpectedReturn = Math.round(newTotalInvested * (1 + prevData.roi / 100));
        
        return {
          ...prevData,
          totalInvested: newTotalInvested,
          expectedReturn: newExpectedReturn
        };
      });
      
      // Update account data locally
      if (accountData) {
        setAccountData(prev => ({
          ...prev,
          investment_balance: prev.investment_balance + amount
        }));
      }
      
      setShowInvestModal(false);
      Alert.alert(
        'Investment Added', 
        `Successfully added $${amount} to your investment pool!\n\nTransaction ID: ${depositResult.id}`,
        [{ text: 'OK' }]
      );
      
    } catch (error) {
      console.error('Investment deposit failed:', error);
      Alert.alert(
        'Investment Failed',
        `Unable to process your investment: ${error.message}\n\nPlease try again.`,
        [{ text: 'OK' }]
      );
    }
  };
  
  const handleRefresh = () => {
    setRefreshing(true);
    loadInvestmentData();
  };

  const handleInvestSubmit = async () => {
    const amount = parseFloat(investmentAmount);
    if (amount && amount > 0) {
      setProcessing(true);
      await processInvestment(amount);
      setProcessing(false);
    } else {
      Alert.alert('Invalid Amount', 'Please enter a valid amount');
    }
  };

  const closeModal = () => {
    setShowInvestModal(false);
    setInvestmentAmount('');
  };

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <Text style={styles.title}>Investment Pool</Text>
          <TouchableOpacity 
            style={styles.refreshButton} 
            onPress={handleRefresh}
            disabled={loading || refreshing}
          >
            {refreshing ? (
              <ActivityIndicator size="small" color="#007AFF" />
            ) : (
              <Text style={styles.refreshButtonText}>↻</Text>
            )}
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.content}>
          {loading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#007AFF" />
              <Text style={styles.loadingText}>Loading investment data...</Text>
            </View>
          ) : (
            <>
          {accountData && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Account Overview:</Text>
              <View style={styles.accountCard}>
                <View style={styles.accountRow}>
                  <Text style={styles.accountLabel}>Account:</Text>
                  <Text style={styles.accountValue}>{accountData.account_number}</Text>
                </View>
                <View style={styles.accountRow}>
                  <Text style={styles.accountLabel}>Investment Balance:</Text>
                  <Text style={styles.accountValue}>${accountData.investment_balance?.toLocaleString() || '0'}</Text>
                </View>
                <View style={styles.accountRow}>
                  <Text style={styles.accountLabel}>Loan Balance:</Text>
                  <Text style={styles.loanValue}>${accountData.loan_balance?.toLocaleString() || '0'}</Text>
                </View>
              </View>
            </View>
          )}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Investment Performance:</Text>
            
            <View style={styles.investmentCard}>
              <View style={styles.metricRow}>
                <Text style={styles.metricEmoji}>💰</Text>
                <View style={styles.metricContent}>
                  <Text style={styles.metricLabel}>Total Invested</Text>
                  <Text style={styles.metricValue}>${investmentData.totalInvested.toLocaleString()}</Text>
                </View>
              </View>

              <View style={styles.metricRow}>
                <Text style={styles.metricEmoji}>📈</Text>
                <View style={styles.metricContent}>
                  <Text style={styles.metricLabel}>Expected Return</Text>
                  <Text style={styles.metricValue}>${investmentData.expectedReturn.toLocaleString()}</Text>
                </View>
              </View>

              <View style={styles.metricRow}>
                <Text style={styles.metricEmoji}>🎯</Text>
                <View style={styles.metricContent}>
                  <Text style={styles.metricLabel}>ROI</Text>
                  <Text style={styles.roiValue}>{investmentData.roi.toFixed(2)}%</Text>
                </View>
              </View>
            </View>

            <TouchableOpacity style={styles.investMoreButton} onPress={handleInvestMore}>
              <Text style={styles.investMoreButtonText}> Invest More</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Pool Information:</Text>
            
            <View style={styles.infoList}>
              <View style={styles.infoItem}>
                <Text style={styles.bullet}>•</Text>
                <Text style={styles.infoText}>Funds are pooled across all active loans</Text>
              </View>
              
              <View style={styles.infoItem}>
                <Text style={styles.bullet}>•</Text>
                <Text style={styles.infoText}>Average APR: {investmentData.averageAPR.toFixed(2)}%</Text>
              </View>
              
              <View style={styles.infoItem}>
                <Text style={styles.bullet}>•</Text>
                <Text style={styles.infoText}>Risk-adjusted returns</Text>
              </View>
              
              <View style={styles.infoItem}>
                <Text style={styles.bullet}>•</Text>
                <Text style={styles.infoText}>Automatic diversification</Text>
              </View>
            </View>
          </View>
            </>
          )}
        </ScrollView>
      </SafeAreaView>

      {/* Investment Modal */}
      <Modal
        visible={showInvestModal}
        transparent={true}
        animationType="slide"
        onRequestClose={closeModal}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Invest More</Text>
            <Text style={styles.modalSubtitle}>Enter the amount you want to invest:</Text>
            
            <View style={styles.inputContainer}>
              <Text style={styles.dollarSign}>$</Text>
              <TextInput
                style={styles.amountInput}
                value={investmentAmount}
                onChangeText={setInvestmentAmount}
                keyboardType="numeric"
                placeholder="0.00"
                placeholderTextColor="#999"
                autoFocus={true}
              />
            </View>

            <View style={styles.modalButtons}>
              <TouchableOpacity style={styles.cancelButton} onPress={closeModal} disabled={processing}>
                <Text style={[styles.cancelButtonText, processing && styles.disabledText]}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={[styles.investButton, processing && styles.disabledButton]} 
                onPress={handleInvestSubmit}
                disabled={processing}
              >
                {processing ? (
                  <View style={styles.processingContainer}>
                    <ActivityIndicator size="small" color="white" style={styles.processingSpinner} />
                    <Text style={styles.investButtonText}>Processing...</Text>
                  </View>
                ) : (
                  <Text style={styles.investButtonText}>Invest</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
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
    paddingHorizontal: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: Platform.OS === 'ios' ? 10 : 0,
  },
  refreshButton: {
    padding: 5,
  },
  refreshButtonText: {
    fontSize: 20,
    color: '#007AFF',
    fontWeight: 'bold',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 100,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
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
  section: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 15,
    color: '#333',
  },
  investmentCard: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  metricRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
  },
  metricEmoji: {
    fontSize: 24,
    marginRight: 15,
  },
  metricContent: {
    flex: 1,
  },
  metricLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  roiValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  investMoreButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 15,
    alignItems: 'center',
    marginBottom: 20,
  },
  investMoreButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  accountCard: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  accountRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  accountLabel: {
    fontSize: 14,
    color: '#666',
  },
  accountValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  loanValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ff6b35',
  },
  infoList: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  bullet: {
    fontSize: 16,
    color: '#333',
    marginRight: 8,
    marginTop: 2,
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    flex: 1,
    lineHeight: 20,
  },
  // Modal styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 24,
    margin: 20,
    width: '80%',
    maxWidth: 300,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
    color: '#333',
  },
  modalSubtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 24,
    color: '#666',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    paddingHorizontal: 12,
    marginBottom: 24,
    backgroundColor: '#f9f9f9',
  },
  dollarSign: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginRight: 8,
  },
  amountInput: {
    flex: 1,
    fontSize: 18,
    paddingVertical: 12,
    color: '#333',
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
  },
  cancelButton: {
    flex: 1,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
  },
  cancelButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
  },
  investButton: {
    flex: 1,
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
  },
  investButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: 'white',
  },
  disabledButton: {
    backgroundColor: '#ccc',
    opacity: 0.7,
  },
  disabledText: {
    color: '#999',
  },
  processingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  processingSpinner: {
    marginRight: 8,
  },
});