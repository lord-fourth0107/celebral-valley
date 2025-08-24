import React from 'react';
import { View, Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MaterialIcons, FontAwesome5 } from '@expo/vector-icons';
import BorrowStack from './src/navigation/BorrowStack';
import InvestScreen from './src/screens/InvestScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarIcon: ({ focused, color, size }) => {
            let iconName;
            let IconComponent;
            
            if (route.name === 'Borrow') {
              IconComponent = MaterialIcons;
              iconName = 'account-balance-wallet';
            } else if (route.name === 'Invest') {
              IconComponent = FontAwesome5;
              iconName = 'chart-line';
            }
            
            return (
              <IconComponent 
                name={iconName} 
                size={24} 
                color={focused ? '#007AFF' : '#999'} 
              />
            );
          },
          tabBarActiveTintColor: '#007AFF',
          tabBarInactiveTintColor: '#999',
          tabBarStyle: {
            paddingBottom: 8,
            paddingTop: 8,
            height: 70,
            backgroundColor: '#fff',
            borderTopWidth: 1,
            borderTopColor: '#e0e0e0',
          },
          tabBarLabelStyle: {
            fontSize: 12,
            fontWeight: '600',
            marginTop: -3,
          },
          tabBarItemStyle: {
            paddingTop: 8,
          },
        })}
      >
        <Tab.Screen 
          name="Borrow" 
          component={BorrowStack}
        />
        <Tab.Screen 
          name="Invest" 
          component={InvestScreen}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

