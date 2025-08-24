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
  Modal
} from 'react-native';

export default function InvestScreen() {
  const [investmentData, setInvestmentData] = useState({
    totalInvested: 1250,
    expectedReturn: 1406,
    roi: 12.48,
    averageAPR: 12.48
  });
  const [showInvestModal, setShowInvestModal] = useState(false);
  const [investmentAmount, setInvestmentAmount] = useState('');

  useEffect(() => {
    loadInvestmentData();
  }, []);

  const loadInvestmentData = () => {
    // Placeholder data - future: load from API
    setInvestmentData({
      totalInvested: 1250,
      expectedReturn: 1406,
      roi: 12.48,
      averageAPR: 12.48
    });
  };

  const handleInvestMore = () => {
    setInvestmentAmount('');
    setShowInvestModal(true);
  };

  const processInvestment = (amount) => {
    // Update investment data
    setInvestmentData(prevData => {
      const newTotalInvested = prevData.totalInvested + amount;
      const newExpectedReturn = Math.round(newTotalInvested * (1 + prevData.roi / 100));
      
      return {
        ...prevData,
        totalInvested: newTotalInvested,
        expectedReturn: newExpectedReturn
      };
    });
    
    setShowInvestModal(false);
    Alert.alert('Investment Added', `Successfully added $${amount} to your investment pool!`);
    // Future: API call to process investment
  };

  const handleInvestSubmit = () => {
    const amount = parseFloat(investmentAmount);
    if (amount && amount > 0) {
      processInvestment(amount);
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
        </View>

        <ScrollView style={styles.content}>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Your Investment:</Text>
            
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
              <TouchableOpacity style={styles.cancelButton} onPress={closeModal}>
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.investButton} onPress={handleInvestSubmit}>
                <Text style={styles.investButtonText}>Invest</Text>
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
});