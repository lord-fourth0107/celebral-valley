import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  Image,
  TextInput,
  Alert,
  Platform
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

export default function ValuationResultScreen({ navigation, route }) {
  // Get data from navigation params (from NewLoanForm)
  const { itemTitle, description, photos } = route.params || {};
  
  // Hardcoded valuation result - simulate API response
  const [valuationResult] = useState(() => {
    // Simulate approval/rejection based on item title
    const isApproved = !itemTitle?.toLowerCase().includes('teddy') && 
                      !itemTitle?.toLowerCase().includes('toy');
    
    if (isApproved) {
      return {
        approved: true,
        itemName: itemTitle || 'iPhone 13 Pro Max 256GB',
        estimatedValue: 750,
        maxLoanAmount: 450,
        interestRate: 12,
        loanTerm: '30 days',
        dueDate: 'Jan 15, 2026',
        extendFee: 25
      };
    } else {
      return {
        approved: false,
        itemName: itemTitle || 'Used Teddy Bear',
        reasons: [
          'Low estimated value',
          'Difficult to resell',
          'Condition concerns'
        ]
      };
    }
  });

  const [requestedAmount, setRequestedAmount] = useState('');

  const handleProceedWithLoan = () => {
    const amount = parseFloat(requestedAmount);
    if (!amount || amount <= 0) {
      Alert.alert('Invalid Amount', 'Please enter a valid loan amount');
      return;
    }
    if (amount > valuationResult.maxLoanAmount) {
      Alert.alert('Amount Too High', `Maximum approved amount is $${valuationResult.maxLoanAmount}`);
      return;
    }

    Alert.alert(
      'Loan Confirmed',
      `Your loan of $${amount} has been approved and will be processed shortly.`,
      [
        {
          text: 'OK',
          onPress: () => navigation.navigate('BorrowLoans')
        }
      ]
    );
  };

  const handleDecline = () => {
    Alert.alert(
      'Decline Loan',
      'Are you sure you want to decline this loan offer?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Yes, Decline',
          style: 'destructive',
          onPress: () => navigation.navigate('BorrowLoans')
        }
      ]
    );
  };

  const handleTryAnother = () => {
    navigation.navigate('NewLoanForm');
  };

  const handleContactSupport = () => {
    Alert.alert('Contact Support', 'Support contact functionality would be implemented here.');
  };

  const renderPhotoThumbnails = () => {
    if (!photos || photos.length === 0) {
      return (
        <View style={styles.photoThumbnails}>
          <Text style={styles.photoPlaceholder}>📷 📷 📷 📷</Text>
        </View>
      );
    }

    return (
      <View style={styles.photoThumbnails}>
        {photos.filter(photo => photo !== null).map((photo, index) => (
          <Image
            key={index}
            source={{ uri: photo.uri }}
            style={styles.thumbnail}
          />
        ))}
        {/* Fill remaining slots with placeholders if needed */}
        {Array.from({ length: Math.max(0, 4 - photos.filter(photo => photo !== null).length) }).map((_, index) => (
          <View key={`placeholder-${index}`} style={styles.thumbnailPlaceholder}>
            <Text style={styles.placeholderText}>📷</Text>
          </View>
        ))}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity 
            style={styles.backButton} 
            onPress={() => navigation.goBack()}
          >
            <MaterialIcons name="arrow-back" size={24} color="#000" />
            <Text style={styles.backText}>Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Loan Valuation</Text>
          <View style={styles.headerSpacer} />
        </View>

        <ScrollView style={styles.content}>
          {/* Approval/Rejection Status */}
          <View style={styles.statusSection}>
            <Text style={[
              styles.statusText,
              valuationResult.approved ? styles.approvedStatus : styles.rejectedStatus
            ]}>
              {valuationResult.approved ? '✅ APPROVED!' : '❌ NOT APPROVED'}
            </Text>
          </View>

          {/* Item Summary */}
          <View style={styles.itemCard}>
            <Text style={styles.itemName}>{valuationResult.itemName}</Text>
            {renderPhotoThumbnails()}
          </View>

          <View style={styles.divider} />

          {valuationResult.approved ? (
            // Approved Loan Content
            <>
              <View style={styles.loanOfferSection}>
                <Text style={styles.sectionTitle}>LOAN OFFER</Text>
                
                <View style={styles.loanDetails}>
                  <View style={styles.loanDetailRow}>
                    <Text style={styles.detailLabel}>Maximum Approved:</Text>
                    <Text style={styles.detailValue}>💰 ${valuationResult.maxLoanAmount}.00</Text>
                  </View>
                  <View style={styles.loanDetailRow}>
                    <Text style={styles.detailLabel}>Interest Rate:</Text>
                    <Text style={styles.detailValue}>📈 {valuationResult.interestRate}% APR</Text>
                  </View>
                  <View style={styles.loanDetailRow}>
                    <Text style={styles.detailLabel}>Loan Term:</Text>
                    <Text style={styles.detailValue}>📅 {valuationResult.loanTerm}</Text>
                  </View>
                  <View style={styles.loanDetailRow}>
                    <Text style={styles.detailLabel}>Estimated Item Value:</Text>
                    <Text style={styles.detailValue}>${valuationResult.estimatedValue}</Text>
                  </View>
                </View>
              </View>

              <View style={styles.divider} />

              {/* Loan Amount Input */}
              <View style={styles.amountSection}>
                <Text style={styles.amountLabel}>
                  Enter loan amount (max ${valuationResult.maxLoanAmount}):
                </Text>
                <View style={styles.amountInputContainer}>
                  <Text style={styles.dollarSign}>$</Text>
                  <TextInput
                    style={styles.amountInput}
                    value={requestedAmount}
                    onChangeText={setRequestedAmount}
                    keyboardType="numeric"
                    placeholder="0.00"
                    placeholderTextColor="#999"
                  />
                </View>
              </View>

              {/* Terms Warning */}
              <View style={styles.warningSection}>
                <Text style={styles.warningTitle}>If not repaid by {valuationResult.dueDate}:</Text>
                <Text style={styles.warningText}>• Item will be sold</Text>
                <Text style={styles.warningText}>• You can extend for ${valuationResult.extendFee} fee</Text>
              </View>

              {/* Action Buttons */}
              <TouchableOpacity style={styles.proceedButton} onPress={handleProceedWithLoan}>
                <Text style={styles.proceedButtonText}>Proceed with Loan</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.declineButton} onPress={handleDecline}>
                <Text style={styles.declineButtonText}>Decline</Text>
              </TouchableOpacity>
            </>
          ) : (
            // Rejected Loan Content
            <>
              <View style={styles.rejectionSection}>
                <Text style={styles.rejectionMessage}>
                  Unfortunately, we cannot offer a loan for this item.
                </Text>
                
                <Text style={styles.reasonsTitle}>Reasons:</Text>
                {valuationResult.reasons.map((reason, index) => (
                  <Text key={index} style={styles.reasonText}>• {reason}</Text>
                ))}
              </View>

              <TouchableOpacity style={styles.tryAnotherButton} onPress={handleTryAnother}>
                <Text style={styles.tryAnotherButtonText}>Try Another Item</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.supportButton} onPress={handleContactSupport}>
                <Text style={styles.supportButtonText}>Contact Support</Text>
              </TouchableOpacity>
            </>
          )}
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
    paddingHorizontal: 20,
    paddingVertical: 15,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: Platform.OS === 'ios' ? 10 : 0,
  },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  backText: {
    fontSize: 16,
    marginLeft: 5,
    color: '#000',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    flex: 2,
    textAlign: 'center',
  },
  headerSpacer: {
    flex: 1,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  statusSection: {
    alignItems: 'center',
    marginBottom: 30,
  },
  statusText: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  approvedStatus: {
    color: '#4CAF50',
  },
  rejectedStatus: {
    color: '#f44336',
  },
  itemCard: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 16,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  itemName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  photoThumbnails: {
    flexDirection: 'row',
    gap: 8,
  },
  thumbnail: {
    width: 60,
    height: 60,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
  },
  thumbnailPlaceholder: {
    width: 60,
    height: 60,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
    justifyContent: 'center',
  },
  placeholderText: {
    fontSize: 20,
  },
  photoPlaceholder: {
    fontSize: 20,
    color: '#666',
  },
  divider: {
    height: 1,
    backgroundColor: '#e0e0e0',
    marginVertical: 20,
  },
  loanOfferSection: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
  },
  loanDetails: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  loanDetailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  detailLabel: {
    fontSize: 16,
    color: '#666',
  },
  detailValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  amountSection: {
    marginBottom: 20,
  },
  amountLabel: {
    fontSize: 16,
    color: '#333',
    marginBottom: 10,
  },
  amountInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: 8,
    paddingHorizontal: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  dollarSign: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginRight: 8,
  },
  amountInput: {
    flex: 1,
    fontSize: 16,
    paddingVertical: 15,
    color: '#333',
  },
  warningSection: {
    marginBottom: 30,
  },
  warningTitle: {
    fontSize: 16,
    color: '#333',
    marginBottom: 8,
  },
  warningText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  proceedButton: {
    backgroundColor: '#4CAF50',
    borderRadius: 8,
    paddingVertical: 15,
    alignItems: 'center',
    marginBottom: 15,
  },
  proceedButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  declineButton: {
    backgroundColor: '#f44336',
    borderRadius: 8,
    paddingVertical: 15,
    alignItems: 'center',
    marginBottom: 30,
  },
  declineButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  rejectionSection: {
    marginBottom: 30,
  },
  rejectionMessage: {
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 24,
  },
  reasonsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 10,
  },
  reasonText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 6,
  },
  tryAnotherButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 15,
    alignItems: 'center',
    marginBottom: 15,
  },
  tryAnotherButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  supportButton: {
    backgroundColor: '#FF9800',
    borderRadius: 8,
    paddingVertical: 15,
    alignItems: 'center',
    marginBottom: 30,
  },
  supportButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});