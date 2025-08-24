import * as FileSystem from 'expo-file-system';
import { Platform } from 'react-native';

// API Configuration
const API_BASE_URL = __DEV__ 
  ? 'https://0878bdf69d9c.ngrok-free.app'  // Development server
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
 * Upload an image file to the backend
 * @param {string} fileUri - Local file URI
 * @param {string} fileName - Original filename
 * @returns {Promise<Object>} - Upload response with file path
 */
export const uploadImage = async (fileUri, fileName) => {
  try {
    const axios = require('axios').default;
    
    // Create FormData
    const formData = new FormData();
    formData.append('file', {
      uri: fileUri,
      type: 'image/jpeg',
      name: fileName || 'image.jpg',
    });
    
    const response = await axios.post(
      `${API_BASE_URL}/collaterals/upload-image`,
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
    console.error('API Error uploading image:', error);
    
    // Handle different error types
    if (error.response) {
      // Server responded with error
      const errorData = error.response.data;
      throw new Error(errorData.detail || 'Server error occurred');
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
 * Create a new collateral with uploaded images
 * @param {Object} params - Collateral parameters
 * @param {string} params.user_id - User ID
 * @param {string} params.name - Item name
 * @param {string} params.description - Item description
 * @param {Array} params.images - Array of uploaded image paths
 * @returns {Promise<Object>} - Collateral creation response
 */
export const createCollateral = async ({ user_id, name, description, images }) => {
  try {
    const axios = require('axios').default;
    
    const requestData = {
      user_id: user_id,
      name: name,
      description: description,
      images: images || []
    };
    
    const response = await axios.post(
      `${API_BASE_URL}/collaterals/`,
      requestData,
      {
        headers: {
          'Content-Type': 'application/json',
          ...(API_KEY ? { 'X-API-Key': API_KEY } : {})
        },
        timeout: 60000, // 60 second timeout for analysis
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('API Error creating collateral:', error);
    
    // Handle different error types
    if (error.response) {
      // Server responded with error
      const errorData = error.response.data;
      throw new Error(errorData.detail || 'Server error occurred');
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
 * Mock function for image upload testing
 * @param {string} fileUri - Local file URI
 * @param {string} fileName - Original filename
 * @returns {Promise<Object>} - Mock upload response
 */
export const uploadImageMock = async (fileUri, fileName) => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  return {
    success: true,
    message: "Image uploaded successfully",
    file_path: `data/mock_${Date.now()}_${fileName}`,
    original_filename: fileName,
    size: 123456
  };
};

/**
 * Create a loan against a collateral
 * @param {Object} params - Loan parameters
 * @param {string} params.account_id - Account ID receiving the loan
 * @param {string} params.user_id - User ID receiving the loan
 * @param {string} params.collateral_id - Collateral ID to loan against
 * @param {number} params.loan_amount - Amount to loan
 * @param {string} params.description - Optional loan description
 * @param {string} params.reference_number - Optional external reference
 * @param {Object} params.metadata - Optional additional metadata
 * @returns {Promise<Object>} - Loan creation response
 */
export const createLoan = async ({ account_id, user_id, collateral_id, loan_amount, description, reference_number, metadata }) => {
  try {
    const axios = require('axios').default;
    
    const requestData = {
      account_id: account_id,
      user_id: user_id,
      collateral_id: collateral_id,
      loan_amount: loan_amount,
      description: description,
      reference_number: reference_number,
      metadata: metadata || {}
    };
    
    const response = await axios.post(
      `${API_BASE_URL}/transactions/create-loan`,
      requestData,
      {
        headers: {
          'Content-Type': 'application/json',
          ...(API_KEY ? { 'X-API-Key': API_KEY } : {})
        },
        timeout: 60000, // 60 second timeout
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('API Error creating loan:', error);
    
    // Handle different error types
    if (error.response) {
      // Server responded with error
      const errorData = error.response.data;
      throw new Error(errorData.detail || 'Server error occurred');
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
 * Get account details by user ID
 * @param {string} user_id - User ID to get account for
 * @returns {Promise<Object>} - Account details response
 */
export const getAccountByUserId = async (user_id) => {
  try {
    const axios = require('axios').default;
    
    const response = await axios.get(
      `${API_BASE_URL}/accounts/user/${user_id}`,
      {
        headers: {
          'Content-Type': 'application/json',
          ...(API_KEY ? { 'X-API-Key': API_KEY } : {})
        },
        timeout: 10000, // 10 second timeout
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('API Error fetching account:', error);
    
    // Handle different error types
    if (error.response) {
      // Server responded with error
      const errorData = error.response.data;
      throw new Error(errorData.detail || 'Server error occurred');
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
 * Create a deposit transaction
 * @param {Object} params - Deposit parameters
 * @param {string} params.account_id - Account ID to deposit to
 * @param {string} params.user_id - User ID making the deposit
 * @param {number} params.amount - Amount to deposit
 * @param {string} params.description - Optional deposit description
 * @param {string} params.reference_number - Optional external reference
 * @param {Object} params.metadata - Optional additional metadata
 * @returns {Promise<Object>} - Deposit transaction response
 */
export const createDeposit = async ({ account_id, user_id, amount, description, reference_number, metadata }) => {
  try {
    const axios = require('axios').default;
    
    const requestData = {
      account_id: account_id,
      user_id: user_id,
      amount: amount,
      description: description,
      reference_number: reference_number,
      metadata: metadata || {}
    };
    
    const response = await axios.post(
      `${API_BASE_URL}/transactions/deposit`,
      requestData,
      {
        headers: {
          'Content-Type': 'application/json',
          ...(API_KEY ? { 'X-API-Key': API_KEY } : {})
        },
        timeout: 60000,
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('API Error creating deposit:', error);
    
    if (error.response) {
      const errorData = error.response.data;
      throw new Error(errorData.detail || 'Server error occurred');
    } else if (error.request) {
      throw new Error('Network error - please check your connection');
    } else {
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
};

/**
 * Mock function for deposit creation testing
 * @param {Object} params - Same as createDeposit
 * @returns {Promise<Object>} - Mock deposit response
 */
export const createDepositMock = async ({ account_id, user_id, amount, description }) => {
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  return {
    id: `txn_${Date.now()}`,
    account_id: account_id,
    user_id: user_id,
    transaction_type: "DEPOSIT",
    amount: amount,
    description: description || `Investment deposit of $${amount}`,
    status: "completed",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    metadata: {
      deposit_amount: amount.toString(),
      transaction_purpose: "investment_deposit"
    }
  };
};

/**
 * Mock function for account details testing
 * @param {string} user_id - User ID to get account for
 * @returns {Promise<Object>} - Mock account response
 */
export const getAccountByUserIdMock = async (user_id) => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  return {
    id: 'acc_demo_123',
    user_id: user_id,
    account_number: 'ACC17241234ABCD5678',
    status: 'active',
    loan_balance: 450.00,
    investment_balance: 1250.00,
    wallet_id: 'wallet_demo_123',
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2025-01-24T15:30:00Z',
    closed_at: null
  };
};

/**
 * Mock function for loan creation testing
 * @param {Object} params - Same as createLoan
 * @returns {Promise<Object>} - Mock loan response
 */
export const createLoanMock = async ({ account_id, user_id, collateral_id, loan_amount, description }) => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  return {
    id: `txn_${Date.now()}`,
    account_id: account_id,
    user_id: user_id,
    transaction_type: "LOAN_DISBURSEMENT",
    amount: loan_amount,
    description: description || `Loan disbursement for collateral ${collateral_id}`,
    status: "completed",
    collateral_id: collateral_id,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    metadata: {
      loan_amount: loan_amount.toString(),
      transaction_purpose: "loan_creation"
    }
  };
};

/**
 * Mock function for collateral creation testing
 * @param {Object} params - Same as createCollateral
 * @returns {Promise<Object>} - Mock collateral response
 */
export const createCollateralMock = async ({ user_id, name, description, images }) => {
  // Simulate network delay for analysis
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // Determine if approved based on item name
  const isApproved = !name?.toLowerCase().includes('teddy') && 
                    !name?.toLowerCase().includes('toy');
  
  if (isApproved) {
    return {
      id: `coll_${Date.now()}`,
      user_id: user_id,
      status: "pending",
      loan_limit: 750.00,
      interest: 0.12,
      due_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
      metadata: {
        name: name,
        description: description,
        original_images: images,
        total_estimated_value: 1200.00,
        overall_loan_limit: 750.00,
        interest_rate: 0.12,
        analysis_timestamp: new Date().toISOString(),
        rag3_integration: false // Mock doesn't use real analysis
      },
      images: images,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
  } else {
    return {
      id: `coll_${Date.now()}`,
      user_id: user_id,
      status: "rejected",
      loan_limit: 0.00,
      interest: 0.15,
      due_date: null,
      metadata: {
        name: name,
        description: description,
        original_images: images,
        total_estimated_value: 50.00,
        overall_loan_limit: 0.00,
        interest_rate: 0.15,
        analysis_timestamp: new Date().toISOString(),
        rejection_reason: "Item does not meet collateral requirements",
        rag3_integration: false
      },
      images: images,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
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
      metadata: {
        name: 'Luxury Rolex Watch',
        total_estimated_value: 12500.0
      },
      status: 'approved',
      loan_amount: '7000.00',
      due_date: '2026-08-24T01:20:42.116648',
      interest: '0.1200',
      created_at: '2025-08-24T05:20:42.116820'
    },
    {
      id: '2',
      metadata: {
        name: 'Diamond Ring',
        total_estimated_value: 1500.0
      },
      status: 'approved',
      loan_amount: '1.00',
      due_date: '2025-11-22T04:40:56.748478',
      interest: '0.0550',
      created_at: '2025-08-24T04:40:56.748478'
    },
    {
      id: '3',
      metadata: {
        name: 'Silver Ring',
        total_estimated_value: 800.0
      },
      status: 'approved',
      loan_amount: '2.00',
      due_date: '2025-11-22T03:16:38.901050',
      interest: '0.0550',
      created_at: '2025-08-24T03:16:38.901050'
    },
    {
      id: '4',
      metadata: {
        name: 'Gold Necklace',
        total_estimated_value: 1200.0
      },
      status: 'approved',
      loan_amount: '2.00',
      due_date: '2025-11-22T03:04:46.514633',
      interest: '0.0550',
      created_at: '2025-08-24T03:04:46.514633'
    },
    {
      id: '5',
      metadata: {
        name: 'Headphones',
        total_estimated_value: 150.0
      },
      status: 'pending',
      loan_amount: '5000.00',
      due_date: '2026-08-24T08:40:37.745885',
      interest: '0.1200',
      created_at: '2025-08-24T12:40:37.746257'
    },
    {
      id: '6',
      metadata: {
        name: 'Broken Phone',
        total_estimated_value: 50.0
      },
      status: 'rejected',
      loan_amount: '0.00',
      due_date: null,
      interest: '0.0000',
      created_at: '2025-08-24T10:00:00.000000'
    }
  ];
  
  // Filter by status if provided
  let filteredCollaterals = mockCollaterals;
  if (params.status && params.status !== 'all') {
    // Map frontend status to backend status
    let backendStatus = params.status;
    if (params.status === 'active') {
      backendStatus = 'approved';
    } else if (params.status === 'past') {
      backendStatus = 'repaid';
    }
    filteredCollaterals = mockCollaterals.filter(c => c.status === backendStatus);
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
  uploadImage,
  uploadImageMock,
  createCollateral,
  createCollateralMock,
  createLoan,
  createLoanMock,
  createDeposit,
  createDepositMock,
  getAccountByUserId,
  getAccountByUserIdMock,
  listCollaterals,
  listCollateralsMock,
  
  // Configuration
  API_BASE_URL,
  API_KEY
};