# Camera Upload App

A basic React Native Expo application that uses the camera to capture photos and upload them to a backend service.

## Features

- 📸 Camera integration with front/back camera toggle
- 🖼️ Photo preview before upload
- 📤 Image upload to backend server
- 💾 Automatic save to device gallery
- 🔒 Permission handling for camera and media library

## Project Structure

```
camera-upload-app/
├── App.js                 # Main React Native app
├── package.json          # Frontend dependencies
├── Justfile              # Development commands
├── server/               # Backend directory
│   ├── server.js         # Express server
│   ├── package.json      # Backend dependencies
│   └── uploads/          # (created automatically) Image uploads
└── README.md             # This file
```

## Quick Start with Just

We use [Just](https://github.com/casey/just) for command management. Install it first:

```bash
# macOS
brew install just

# or download from releases: https://github.com/casey/just/releases
```

Then run:

```bash
# Setup everything
just setup

# Start development (both frontend and backend)
just dev-backend &   # Start backend in background
just dev-frontend    # Start frontend (interactive)
```

## Manual Setup (without Just)

### 1. Install Dependencies

Frontend:
```bash
npm install
```

Backend:
```bash
cd server && npm install
```

### 2. Start Services

Backend:
```bash
cd server && npm start
```

Frontend (new terminal):
```bash
npx expo start
```

## Available Just Commands

```bash
just --list              # Show all commands
just setup               # Install all dependencies  
just dev-backend         # Start backend server
just dev-frontend        # Start frontend Expo server
just test-backend        # Test backend health
just clean               # Clean all build artifacts
just info                # Show app information
```

## How It Works

### Frontend (React Native)

1. **Permissions**: App requests camera and media library permissions on startup
2. **Camera View**: Uses `expo-camera` to display camera feed with controls
3. **Photo Capture**: Takes picture using `takePictureAsync()` with quality optimization
4. **Preview**: Shows captured image with retake/upload options
5. **Upload**: Sends image to backend using FormData and fetch API

### Backend (Node.js/Express)

1. **File Handling**: Uses `multer` for multipart form data processing
2. **Storage**: Saves images with unique timestamps in `/uploads` directory
3. **Validation**: Checks file type and size (10MB limit)
4. **API Endpoints**:
   - `POST /upload` - Upload image
   - `GET /images` - List all uploaded images
   - `GET /images/:filename` - View specific image

## Key Code Concepts

### Camera Integration

```javascript
// Camera permissions
const [permission, requestPermission] = useCameraPermissions();

// Take picture
const photo = await cameraRef.current.takePictureAsync({
  quality: 0.7,
  base64: true,
  exif: false
});
```

### Image Upload

```javascript
// Create form data
const formData = new FormData();
formData.append('image', {
  uri: capturedImage.uri,
  type: 'image/jpeg',
  name: 'photo.jpg',
});

// Upload to server
const response = await fetch('http://localhost:3000/upload', {
  method: 'POST',
  body: formData,
  headers: { 'Content-Type': 'multipart/form-data' },
});
```

### Backend File Processing

```javascript
// Multer configuration
const storage = multer.diskStorage({
  destination: 'uploads/',
  filename: (req, file, cb) => {
    const uniqueName = `${Date.now()}-${Math.round(Math.random() * 1E9)}${path.extname(file.originalname)}`;
    cb(null, uniqueName);
  }
});

const upload = multer({ storage, limits: { fileSize: 10 * 1024 * 1024 } });
```

## Testing

### With Just commands:
```bash
just dev-backend &        # Start backend
just dev-frontend         # Start frontend
just test-backend         # Test backend health
just list-uploads         # View uploaded images
```

### Manual testing:
1. Start the backend: `cd server && npm start`
2. Start frontend: `npx expo start`
3. Grant camera permissions on your device
4. Take and upload a photo
5. Check `server/uploads/` directory for saved images
6. Visit http://localhost:3000/images to see all uploads

## Extending the App

This basic structure is designed to be extensible:

- **Authentication**: Add user auth to associate uploads with users
- **Cloud Storage**: Replace local storage with AWS S3, Cloudinary, etc.
- **Image Processing**: Add filters, compression, or resizing
- **Database**: Store metadata in PostgreSQL, MongoDB, etc.
- **Real-time**: Add WebSocket support for live updates
- **Offline Support**: Cache images locally when network is unavailable

## Troubleshooting

- **Camera not working**: Check device permissions in Settings
- **Upload fails**: Ensure backend server is running on correct port
- **CORS errors**: Backend includes CORS middleware for cross-origin requests
- **File size errors**: Images are limited to 10MB, adjust in server.js if needed

## Dependencies

### Frontend
- `expo-camera` - Camera functionality
- `expo-media-library` - Save to device gallery

### Backend
- `express` - Web server framework
- `multer` - File upload handling
- `cors` - Cross-origin resource sharing