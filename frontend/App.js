import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Image,
  Alert,
  SafeAreaView,
  ActivityIndicator
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import * as MediaLibrary from 'expo-media-library';

export default function App() {
  // State management
  const [facing, setFacing] = useState('back');
  const [permission, requestPermission] = useCameraPermissions();
  const [mediaPermission, requestMediaPermission] = MediaLibrary.usePermissions();
  const [capturedImage, setCapturedImage] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const cameraRef = useRef(null);

  // Check permissions on mount
  useEffect(() => {
    (async () => {
      await requestPermission();
      await requestMediaPermission();
    })();
  }, []);

  // Handle permission states
  if (!permission || !mediaPermission) {
    return (
      <View style={styles.container}>
        <Text>Loading permissions...</Text>
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>We need your permission to show the camera</Text>
        <TouchableOpacity style={styles.button} onPress={requestPermission}>
          <Text style={styles.buttonText}>Grant Camera Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // Toggle camera facing (front/back)
  const toggleCameraFacing = () => {
    setFacing(current => (current === 'back' ? 'front' : 'back'));
  };

  // Capture photo
  const takePicture = async () => {
    if (cameraRef.current) {
      try {
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.7,
          base64: true,
          exif: false
        });
        
        setCapturedImage(photo);
        
        // Save to device gallery if permission granted
        if (mediaPermission.granted) {
          await MediaLibrary.saveToLibraryAsync(photo.uri);
        }
      } catch (error) {
        Alert.alert('Error', 'Failed to take picture: ' + error.message);
      }
    }
  };

  // Upload image to backend
  const uploadImage = async () => {
    if (!capturedImage) return;

    setIsUploading(true);

    try {
      // Create form data
      const formData = new FormData();
      formData.append('image', {
        uri: capturedImage.uri,
        type: 'image/jpeg',
        name: 'photo.jpg',
      });

      // Replace with your backend URL
      const BACKEND_URL = 'http://localhost:3000/upload';
      
      const response = await fetch(BACKEND_URL, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const result = await response.json();
      
      if (response.ok) {
        Alert.alert('Success', 'Image uploaded successfully!');
        setCapturedImage(null); // Clear the image after successful upload
      } else {
        Alert.alert('Error', result.message || 'Upload failed');
      }
    } catch (error) {
      Alert.alert(
        'Upload Error', 
        'Failed to upload image. Make sure your backend is running.\n\nError: ' + error.message
      );
    } finally {
      setIsUploading(false);
    }
  };

  // Retake photo
  const retakePicture = () => {
    setCapturedImage(null);
  };

  // If we have a captured image, show preview screen
  if (capturedImage) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.previewContainer}>
          <Image source={{ uri: capturedImage.uri }} style={styles.preview} />
          
          <View style={styles.previewButtons}>
            <TouchableOpacity 
              style={[styles.button, styles.retakeButton]} 
              onPress={retakePicture}
            >
              <Text style={styles.buttonText}>Retake</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={[styles.button, styles.uploadButton, isUploading && styles.disabledButton]} 
              onPress={uploadImage}
              disabled={isUploading}
            >
              {isUploading ? (
                <ActivityIndicator color="white" />
              ) : (
                <Text style={styles.buttonText}>Upload</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </SafeAreaView>
    );
  }

  // Camera view
  return (
    <View style={styles.container}>
      <CameraView 
        style={styles.camera} 
        facing={facing}
        ref={cameraRef}
      >
        <View style={styles.buttonContainer}>
          <TouchableOpacity style={styles.flipButton} onPress={toggleCameraFacing}>
            <Text style={styles.flipText}>Flip</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.captureButton} onPress={takePicture}>
            <View style={styles.captureButtonInner} />
          </TouchableOpacity>
          
          <View style={{ width: 60 }} />
        </View>
      </CameraView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    backgroundColor: '#000',
  },
  message: {
    textAlign: 'center',
    paddingBottom: 10,
    color: 'white',
    fontSize: 16,
  },
  camera: {
    flex: 1,
  },
  buttonContainer: {
    position: 'absolute',
    bottom: 40,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '100%',
    paddingHorizontal: 30,
  },
  button: {
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: 'white',
  },
  captureButton: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: 'white',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureButtonInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#fff',
    borderWidth: 2,
    borderColor: '#000',
  },
  flipButton: {
    backgroundColor: 'rgba(255,255,255,0.3)',
    padding: 15,
    borderRadius: 8,
  },
  flipText: {
    fontSize: 16,
    color: 'white',
    fontWeight: 'bold',
  },
  previewContainer: {
    flex: 1,
    backgroundColor: '#000',
  },
  preview: {
    flex: 1,
    resizeMode: 'contain',
  },
  previewButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 20,
    paddingHorizontal: 30,
  },
  retakeButton: {
    backgroundColor: '#666',
    paddingHorizontal: 30,
  },
  uploadButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 30,
  },
  disabledButton: {
    opacity: 0.5,
  },
});
