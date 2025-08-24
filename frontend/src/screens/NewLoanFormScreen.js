import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  TextInput,
  Alert,
  Image,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { CameraView, useCameraPermissions } from 'expo-camera';
import * as MediaLibrary from 'expo-media-library';
import * as FileSystem from 'expo-file-system';
import apiClient from '../api/apiClient';

const PhotoSlot = ({ photo, onPress, onLongPress, index }) => (
  <TouchableOpacity 
    style={styles.photoSlot} 
    onPress={() => onPress(index)}
    onLongPress={() => onLongPress && onLongPress(index)}
  >
    {photo ? (
      <Image source={{ uri: photo.uri }} style={styles.photoImage} />
    ) : (
      <>
        <MaterialIcons name="camera-alt" size={32} color="#666" />
        <Text style={styles.photoSlotText}>Add Photo</Text>
      </>
    )}
  </TouchableOpacity>
);

export default function NewLoanFormScreen({ navigation }) {
  const [photos, setPhotos] = useState([null, null, null, null]);
  const [uploadedImagePaths, setUploadedImagePaths] = useState([null, null, null, null]);
  const [itemTitle, setItemTitle] = useState('');
  const [description, setDescription] = useState('');
  const [showCamera, setShowCamera] = useState(false);
  const [activePhotoIndex, setActivePhotoIndex] = useState(0);
  const [permission, requestPermission] = useCameraPermissions();
  const [mediaPermission, requestMediaPermission] = MediaLibrary.usePermissions();
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [useMockData] = useState(false); // Toggle this to use real API

  // Create data directory if it doesn't exist
  const ensureDataDirectory = async () => {
    const dataDir = `${FileSystem.documentDirectory}data/`;
    const dirInfo = await FileSystem.getInfoAsync(dataDir);
    if (!dirInfo.exists) {
      await FileSystem.makeDirectoryAsync(dataDir, { intermediates: true });
    }
    return dataDir;
  };

  // Save photo to data directory
  const savePhotoToDataDirectory = async (photoUri) => {
    try {
      const dataDir = await ensureDataDirectory();
      const timestamp = new Date().getTime();
      const filename = `photo_${timestamp}.jpg`;
      const destinationUri = `${dataDir}${filename}`;
      
      await FileSystem.copyAsync({
        from: photoUri,
        to: destinationUri,
      });
      
      console.log(`Photo saved to: ${destinationUri}`);
      return destinationUri;
    } catch (error) {
      console.error('Error saving photo:', error);
      throw error;
    }
  };

  const handlePhotoSlotPress = async (index) => {
    if (!permission?.granted) {
      await requestPermission();
    }
    if (!mediaPermission?.granted) {
      await requestMediaPermission();
    }
    
    if (permission?.granted && mediaPermission?.granted) {
      setActivePhotoIndex(index);
      setShowCamera(true);
    } else {
      Alert.alert('Permission Required', 'Camera and media library permissions are needed to add photos.');
    }
  };

  const handlePhotoLongPress = (index) => {
    if (photos[index]) {
      Alert.alert(
        'Delete Photo',
        'Are you sure you want to delete this photo?',
        [
          {
            text: 'Cancel',
            style: 'cancel',
          },
          {
            text: 'Delete',
            style: 'destructive',
            onPress: () => {
              const newPhotos = [...photos];
              const newUploadedPaths = [...uploadedImagePaths];
              newPhotos[index] = null;
              newUploadedPaths[index] = null;
              setPhotos(newPhotos);
              setUploadedImagePaths(newUploadedPaths);
            },
          },
        ]
      );
    }
  };

  const takePicture = async (cameraRef) => {
    if (cameraRef.current) {
      try {
        setUploading(true);
        
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.7,
          base64: false,
          exif: false
        });
        
        // Save photo to data directory
        const savedPhotoPath = await savePhotoToDataDirectory(photo.uri);
        
        // Update photo with saved path
        const photoWithSavedPath = {
          ...photo,
          savedPath: savedPhotoPath
        };
        
        // Update photos array
        const newPhotos = [...photos];
        newPhotos[activePhotoIndex] = photoWithSavedPath;
        setPhotos(newPhotos);
        
        // Upload image to backend immediately
        try {
          const uploadFunction = useMockData ? 
            apiClient.uploadImageMock : 
            apiClient.uploadImage;
          
          const filename = `photo_${Date.now()}_${activePhotoIndex}.jpg`;
          const uploadResult = await uploadFunction(photo.uri, filename);
          
          console.log('Image uploaded successfully:', uploadResult);
          
          // Store the backend file path
          const newUploadedPaths = [...uploadedImagePaths];
          newUploadedPaths[activePhotoIndex] = uploadResult.file_path;
          setUploadedImagePaths(newUploadedPaths);
          
          // Show success feedback briefly
          Alert.alert('Success', 'Photo uploaded successfully!', [{ text: 'OK' }], { duration: 1000 });
          
        } catch (uploadError) {
          console.error('Image upload failed:', uploadError);
          Alert.alert('Upload Failed', 'Failed to upload image. Please try again.');
          
          // Remove the photo from UI since upload failed
          const newPhotos = [...photos];
          newPhotos[activePhotoIndex] = null;
          setPhotos(newPhotos);
        }
        
        if (mediaPermission.granted) {
          await MediaLibrary.saveToLibraryAsync(photo.uri);
        }
        
        setShowCamera(false);
      } catch (error) {
        Alert.alert('Error', 'Failed to take picture: ' + error.message);
      } finally {
        setUploading(false);
      }
    }
  };

  const handleGetValuation = async () => {
    if (!itemTitle.trim()) {
      Alert.alert('Required Field', 'Please enter an item title');
      return;
    }
    
    if (!description.trim()) {
      Alert.alert('Required Field', 'Please enter a description');
      return;
    }
    
    if (photos.every(photo => photo === null)) {
      Alert.alert('Required Field', 'Please add at least one photo');
      return;
    }

    // Check that all photos have been uploaded
    const validPhotos = photos.filter(photo => photo !== null);
    const validUploadedPaths = uploadedImagePaths.filter(path => path !== null);
    
    if (validPhotos.length !== validUploadedPaths.length) {
      Alert.alert('Upload Error', 'Some images are still uploading. Please wait for all uploads to complete.');
      return;
    }

    try {
      setProcessing(true);
      
      // Use temporary user ID for demo - in real app this would come from authentication
      const user_id = 'demo_user_123';
      
      // Prepare collateral creation data
      const collateralData = {
        user_id: user_id,
        name: itemTitle.trim(),
        description: description.trim(),
        images: validUploadedPaths // Use the backend file paths
      };
      
      console.log('Creating collateral with data:', collateralData);
      
      // Call create collateral API
      const createFunction = useMockData ? 
        apiClient.createCollateralMock : 
        apiClient.createCollateral;
      
      const collateralResult = await createFunction(collateralData);
      
      console.log('Collateral created successfully:', collateralResult);
      
      // Navigate to valuation result screen with the collateral response
      navigation.navigate('ValuationResult', {
        itemTitle: itemTitle.trim(),
        description: description.trim(),
        photos: validPhotos,
        collateral: collateralResult,
        success: true
      });
      
    } catch (error) {
      console.error('Error creating collateral:', error);
      Alert.alert('Error', `Failed to create collateral: ${error.message}`);
    } finally {
      setProcessing(false);
    }
  };

  if (showCamera) {
    return <CameraScreen onTakePicture={takePicture} onClose={() => setShowCamera(false)} />;
  }

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
        <Text style={styles.title}>New Loan</Text>
        <View style={styles.headerSpacer} />
      </View>

      <KeyboardAvoidingView 
        style={styles.keyboardAvoidingView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
      >
        <ScrollView 
          style={styles.content}
          contentContainerStyle={styles.contentContainer}
          keyboardShouldPersistTaps="handled"
        >
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Item Title:</Text>
          <TextInput
            style={styles.titleInput}
            placeholder="Enter item name..."
            value={itemTitle}
            onChangeText={setItemTitle}
            placeholderTextColor="#999"
          />
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Description:</Text>
          <TextInput
            style={styles.descriptionInput}
            placeholder="Describe condition, brand, model, age, any damages..."
            value={description}
            onChangeText={setDescription}
            placeholderTextColor="#999"
            multiline
            numberOfLines={5}
            textAlignVertical="top"
          />
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Item Photos:</Text>
          <View style={styles.photoGrid}>
            <View style={styles.photoRow}>
              <PhotoSlot photo={photos[0]} onPress={handlePhotoSlotPress} onLongPress={handlePhotoLongPress} index={0} />
              <PhotoSlot photo={photos[1]} onPress={handlePhotoSlotPress} onLongPress={handlePhotoLongPress} index={1} />
            </View>
            <View style={styles.photoRow}>
              <PhotoSlot photo={photos[2]} onPress={handlePhotoSlotPress} onLongPress={handlePhotoLongPress} index={2} />
              <PhotoSlot photo={photos[3]} onPress={handlePhotoSlotPress} onLongPress={handlePhotoLongPress} index={3} />
            </View>
          </View>
        </View>

          <TouchableOpacity 
            style={[styles.valuationButton, (processing || uploading) && styles.valuationButtonDisabled]} 
            onPress={handleGetValuation}
            disabled={processing || uploading}
          >
            {processing ? (
              <View style={styles.buttonContent}>
                <ActivityIndicator size="small" color="white" />
                <Text style={styles.valuationButtonText}> Analyzing... </Text>
              </View>
            ) : uploading ? (
              <View style={styles.buttonContent}>
                <ActivityIndicator size="small" color="white" />
                <Text style={styles.valuationButtonText}> Uploading... </Text>
              </View>
            ) : (
              <Text style={styles.valuationButtonText}> Get Valuation </Text>
            )}
          </TouchableOpacity>
        </ScrollView>
      </KeyboardAvoidingView>
      </SafeAreaView>
    </View>
  );
}

const CameraScreen = ({ onTakePicture, onClose }) => {
  const cameraRef = React.useRef(null);
  const [facing, setFacing] = useState('back');

  return (
    <View style={styles.cameraContainer}>
      <CameraView 
        style={styles.camera} 
        facing={facing}
        ref={cameraRef}
      >
        <View style={styles.cameraHeader}>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <MaterialIcons name="close" size={28} color="white" />
          </TouchableOpacity>
        </View>
        
        <View style={styles.cameraControls}>
          <TouchableOpacity 
            style={styles.flipButton} 
            onPress={() => setFacing(current => (current === 'back' ? 'front' : 'back'))}
          >
            <MaterialIcons name="flip-camera-ios" size={24} color="white" />
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.captureButton} 
            onPress={() => onTakePicture(cameraRef)}
          >
            <View style={styles.captureButtonInner} />
          </TouchableOpacity>
          
          <View style={{ width: 60 }} />
        </View>
      </CameraView>
    </View>
  );
};

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
  keyboardAvoidingView: {
    flex: 1,
  },
  content: {
    flexGrow: 1,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  contentContainer: {
    paddingBottom: 30,
  },
  section: {
    marginBottom: 25,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 10,
    color: '#333',
  },
  photoGrid: {
    gap: 15,
  },
  photoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  photoSlot: {
    width: '47%',
    aspectRatio: 1,
    backgroundColor: '#fff',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  photoImage: {
    width: '100%',
    height: '100%',
    borderRadius: 8,
    resizeMode: 'cover',
  },
  photoSlotText: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  titleInput: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    fontSize: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  descriptionInput: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    fontSize: 16,
    height: 120,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  valuationButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 18,
    alignItems: 'center',
    marginBottom: 30,
  },
  valuationButtonDisabled: {
    backgroundColor: '#ccc',
    opacity: 0.7,
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  valuationButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  cameraContainer: {
    flex: 1,
    backgroundColor: '#000',
  },
  camera: {
    flex: 1,
  },
  cameraHeader: {
    position: 'absolute',
    top: 50,
    left: 20,
    zIndex: 1,
  },
  closeButton: {
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 20,
    padding: 8,
  },
  cameraControls: {
    position: 'absolute',
    bottom: 40,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '100%',
    paddingHorizontal: 30,
  },
  flipButton: {
    backgroundColor: 'rgba(255,255,255,0.3)',
    padding: 15,
    borderRadius: 25,
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
});