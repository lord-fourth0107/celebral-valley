import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import BorrowLoansScreen from '../screens/BorrowLoansScreen';
import NewLoanFormScreen from '../screens/NewLoanFormScreen';

const Stack = createStackNavigator();

export default function BorrowStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="BorrowLoans" component={BorrowLoansScreen} />
      <Stack.Screen name="NewLoanForm" component={NewLoanFormScreen} />
    </Stack.Navigator>
  );
}