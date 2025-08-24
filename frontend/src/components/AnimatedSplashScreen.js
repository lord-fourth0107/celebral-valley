import React, { useEffect, useRef } from 'react';
import { View, Animated, Image, StyleSheet, Dimensions } from 'react-native';

const { width, height } = Dimensions.get('window');

const AnimatedSplashScreen = ({ onAnimationComplete }) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.8)).current;

  useEffect(() => {
    const animateIn = () => {
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 800,
          useNativeDriver: true,
        }),
        Animated.timing(scaleAnim, {
          toValue: 1,
          duration: 800,
          useNativeDriver: true,
        }),
      ]).start(() => {
        setTimeout(() => {
          animateOut();
        }, 1500);
      });
    };

    const animateOut = () => {
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 0,
          duration: 500,
          useNativeDriver: true,
        }),
        Animated.timing(scaleAnim, {
          toValue: 1.1,
          duration: 500,
          useNativeDriver: true,
        }),
      ]).start(() => {
        if (onAnimationComplete) {
          onAnimationComplete();
        }
      });
    };

    animateIn();
  }, [fadeAnim, scaleAnim, onAnimationComplete]);

  return (
    <View style={styles.container}>
      <Animated.View 
        style={[
          styles.imageContainer,
          {
            opacity: fadeAnim,
            transform: [{ scale: scaleAnim }],
          },
        ]}
      >
        <Image
          source={require('../../assets/splash.png')}
          style={styles.image}
          resizeMode="contain"
        />
      </Animated.View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  imageContainer: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  image: {
    width: width,
    height: height * 0.4,
  },
});

export default AnimatedSplashScreen;