import * as FileSystem from 'expo-file-system';
import { Platform } from 'react-native';

// API Configuration
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000'  // Development server
  : 'https://api.celebralvalley.com';  // Production server

// Optional: Add your API key here if needed
const API_KEY = process.env.EXPO_PUBLIC_API_KEY || '';

// We'll use axios directly instead of the generated client to avoid React Native compatibility issues

/**
 * Convert a local file URI to a Blob for upload
 * @param {string} uri - Local file URI
 * @returns {Promise<Blob>} - File as Blob
 */
const uriToBlob = async (uri) => {
  try {
    const fileBase64 = await FileSystem.readAsStringAsync(uri, {
      encoding: FileSystem.EncodingType.Base64,
    });
    
    const binary = atob(fileBase64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    
    return new Blob([bytes], { type: 'image/jpeg' });
  } catch (error) {
    console.error('Error converting URI to Blob:', error);
    throw error;
  }
};

/**
 * Submit item for valuation
 * @param {Object} params - Valuation parameters
 * @param {string} params.itemTitle - Item title
 * @param {string} params.description - Item description
 * @param {Array} params.photos - Array of photo objects with uri property
 * @param {Object} params.metadata - Optional metadata
 * @returns {Promise<Object>} - Valuation response
 */
export const submitValuation = async ({ itemTitle, description, photos, metadata }) => {
  try {
    // Create FormData
    const formData = new FormData();
    
    // Add text fields
    formData.append('itemTitle', itemTitle);
    formData.append('description', description);
    
    // Convert photos to blobs and add to FormData
    for (let i = 0; i < photos.length; i++) {
      const photo = photos[i];
      if (photo && photo.uri) {
        // For React Native, we can append the file directly
        formData.append('photos', {
          uri: photo.uri,
          type: 'image/jpeg',
          name: `photo_${i}.jpg`,
        });
      }
    }
    
    // Add metadata if provided
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    } else {
      // Default metadata
      formData.append('metadata', JSON.stringify({
        totalPhotos: photos.filter(p => p !== null).length,
        submittedAt: new Date().toISOString(),
        platform: Platform.OS
      }));
    }
    
    // Make the API call using axios directly for multipart/form-data
    const axios = require('axios').default;
    
    const response = await axios.post(
      `${API_BASE_URL}/collaterals/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
          ...(API_KEY ? { 'X-API-Key': API_KEY } : {})
        },
        timeout: 30000, // 30 second timeout
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('API Error submitting valuation:', error);
    
    // Handle different error types
    if (error.response) {
      // Server responded with error
      const errorData = error.response.data;
      throw new Error(errorData.message || 'Server error occurred');
    } else if (error.request) {
      // Request made but no response
      throw new Error('Network error - please check your connection');
    } else {
      // Other errors
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
};

/**
 * Mock function for testing - returns hardcoded valuation result
 * @param {Object} params - Same as submitValuation
 * @returns {Promise<Object>} - Mock valuation response
 */
export const submitValuationMock = async ({ itemTitle, description, photos }) => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  // Determine if approved based on item title
  const isApproved = !itemTitle?.toLowerCase().includes('teddy') && 
                    !itemTitle?.toLowerCase().includes('toy');
  
  if (isApproved) {
    return {
      success: true,
      valuationId: `val_${Date.now()}`,
      estimatedValue: 750,
      loanAmount: 450,
      confidence: 0.92,
      item: {
        title: itemTitle,
        category: 'Electronics',
        brand: 'Apple',
        condition: 'Excellent'
      },
      photos: photos.filter(p => p !== null).map((photo, index) => ({
        photoId: `photo_${index}`,
        url: photo.uri,
        analysis: {
          features: ['screen_condition', 'body_condition', 'accessories'],
          scores: {
            overall: 0.95,
            screen: 0.98,
            body: 0.92
          }
        }
      })),
      metadata: {
        processedAt: new Date().toISOString(),
        processingTimeMs: 2340,
        aiModel: 'valuation-v2.1'
      }
    };
  } else {
    return {
      success: false,
      valuationId: `val_${Date.now()}`,
      estimatedValue: 10,
      loanAmount: 0,
      confidence: 0.3,
      item: {
        title: itemTitle,
        category: 'Other',
        condition: 'Poor'
      },
      photos: [],
      metadata: {
        processedAt: new Date().toISOString(),
        processingTimeMs: 1200,
        aiModel: 'valuation-v2.1'
      }
    };
  }
};

/**
 * Fetch user's collaterals (loans)
 * @param {Object} params - Query parameters
 * @param {string} params.status - Filter by status (active, past, all)
 * @param {number} params.limit - Maximum number of items
 * @param {number} params.offset - Number of items to skip
 * @returns {Promise<Object>} - Collaterals list response
 */
export const listCollaterals = async (params = {}) => {
  try {
    // Bypass generated client and use axios directly for React Native compatibility
    const axios = require('axios').default;
    
    const queryParams = new URLSearchParams();
    if (params.status && params.status !== 'all') {
      queryParams.append('status', params.status);
    }
    const page = Math.floor((params.offset || 0) / (params.limit || 20)) + 1;
    queryParams.append('page', page.toString());
    queryParams.append('page_size', (params.limit || 20).toString());
    
    const url = `${API_BASE_URL}/collaterals/?${queryParams.toString()}`;
    
    const response = await axios.get(url, {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        ...(API_KEY ? { 'X-API-Key': API_KEY } : {})
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('API Error fetching collaterals:', error);
    throw error;
  }
};

/**
 * Mock function for testing - returns hardcoded collaterals list
 * @param {Object} params - Same as listCollaterals
 * @returns {Promise<Object>} - Mock collaterals response
 */
export const listCollateralsMock = async (params = {}) => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  const mockCollaterals = [
    {
      id: '1',
      item_name: 'iPhone 13 Pro',
      item_emoji: '📱',
      status: 'active',
      loan_amount: 450.00,
      due_date: '2025-02-15',
      days_remaining: 22,
      interest_rate: 12,
      estimated_value: 750.00,
      created_at: '2025-01-15T10:00:00Z'
    },
    {
      id: '2',
      item_name: 'MacBook Pro M1',
      item_emoji: '💻',
      status: 'active',
      loan_amount: 1200.00,
      due_date: '2025-02-20',
      days_remaining: 27,
      interest_rate: 10,
      estimated_value: 2000.00,
      created_at: '2025-01-10T14:30:00Z'
    },
    {
      id: '3',
      item_name: 'Gold Watch',
      item_emoji: '⌚',
      status: 'past',
      loan_amount: 300.00,
      due_date: '2024-12-30',
      days_remaining: 0,
      interest_rate: 15,
      estimated_value: 500.00,
      created_at: '2024-11-30T09:15:00Z',
      closed_at: '2024-12-28T16:45:00Z'
    },
    {
      id: '4',
      item_name: 'Diamond Ring',
      item_emoji: '💍',
      status: 'past',
      loan_amount: 800.00,
      due_date: '2024-11-15',
      days_remaining: 0,
      interest_rate: 8,
      estimated_value: 1500.00,
      created_at: '2024-10-15T11:20:00Z',
      closed_at: '2024-11-14T13:30:00Z'
    }
  ];
  
  // Filter by status if provided
  let filteredCollaterals = mockCollaterals;
  if (params.status && params.status !== 'all') {
    filteredCollaterals = mockCollaterals.filter(c => c.status === params.status);
  }
  
  // Apply pagination
  const offset = params.offset || 0;
  const limit = params.limit || 20;
  const paginatedCollaterals = filteredCollaterals.slice(offset, offset + limit);
  
  return {
    collaterals: paginatedCollaterals,
    total: filteredCollaterals.length,
    limit: limit,
    offset: offset,
    has_more: offset + limit < filteredCollaterals.length
  };
};

// Export the API client for other uses
export default {
  // Methods
  submitValuation,
  submitValuationMock,
  listCollaterals,
  listCollateralsMock,
  
  // Configuration
  API_BASE_URL,
  API_KEY
};