# 🏦 Collateral Management Frontend

A simple Flask-based frontend for the Collateral Management System with AI-powered image analysis.

## 🚀 Quick Start

### Option 1: Using the startup script (Recommended)
```bash
./start_frontend.sh
```

### Option 2: Manual installation
```bash
# Install Flask dependencies
pip install -r frontend_requirements.txt

# Start the frontend
python frontend.py
```

## 🌐 Access URLs

- **Dashboard:** http://localhost:5001
- **Create Collateral:** http://localhost:5001/collateral/create
- **View Collaterals:** http://localhost:5001/collateral/list
- **Approve Collateral:** http://localhost:5001/collateral/{id}/approve

## 📁 File Structure

```
├── frontend.py                 # Main Flask application
├── templates/                  # HTML templates
│   ├── index.html             # Dashboard page
│   ├── create_collateral.html # Create collateral form
│   ├── list_collaterals.html  # View all collaterals
│   └── approve_collateral.html # Approve collateral page
├── frontend_requirements.txt   # Python dependencies
├── start_frontend.sh          # Startup script
└── FRONTEND_README.md         # This file
```

## 🎯 Features

### 1. **Dashboard** (`/`)
- Overview of collateral statistics
- Quick action buttons
- Recent collaterals list
- Backend connection status

### 2. **Create Collateral** (`/collateral/create`)
- Form for new collateral creation
- Image upload interface
- AI analysis options selection
- Quick test with existing rolex.jpeg

### 3. **View Collaterals** (`/collateral/list`)
- List all collateral assets
- Status indicators (pending/approved)
- Quick action buttons
- AI analysis summary

### 4. **Approve Collateral** (`/collateral/{id}/approve`)
- Review collateral details
- AI analysis results display
- Loan parameter configuration
- Risk assessment information

## 🔧 Configuration

### Backend URL
The frontend connects to your backend at `http://localhost:8000`. You can change this in `frontend.py`:

```python
BACKEND_URL = "http://localhost:8000"
```

### Port Configuration
The frontend runs on port 5001 by default. Change this in `frontend.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 🧪 Testing

### Test Backend Connection
Click the "🔗 Test Backend" button on the dashboard to verify backend connectivity.

### Test Collateral Creation
Use the "🧪 Test with rolex.jpeg" button on the create collateral page to test the AI workflow.

### API Endpoints
- `GET /api/test-backend` - Test backend connection
- `GET /api/test-collateral-creation` - Test collateral creation workflow

## 🎨 UI Features

- **Responsive Design:** Works on desktop and mobile
- **Modern UI:** Built with Tailwind CSS
- **Interactive Elements:** Hover effects and smooth transitions
- **Status Indicators:** Color-coded status badges
- **Real-time Updates:** Dynamic content loading

## 🔒 Security Notes

- This is a basic frontend for development/testing
- No authentication implemented
- No input validation on frontend
- Backend handles all business logic

## 🚨 Troubleshooting

### Frontend won't start
```bash
# Check Python version
python --version

# Install dependencies manually
pip install Flask requests

# Check port availability
lsof -i :5000
```

### Backend connection failed
```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify backend port
lsof -i :8000
```

### Template errors
```bash
# Ensure templates folder exists
ls -la templates/

# Check file permissions
chmod 644 templates/*.html
```

## 🔄 Development

### Adding New Pages
1. Create HTML template in `templates/`
2. Add route in `frontend.py`
3. Update navigation links

### Modifying Styles
- Edit HTML files directly
- Tailwind CSS classes are used for styling
- Custom CSS can be added in `<style>` tags

### Adding JavaScript
- JavaScript functions are embedded in HTML files
- Can be moved to separate `.js` files for larger applications

## 📱 Mobile Support

The frontend is fully responsive and works on:
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Tablet devices

## 🎉 Success!

Your frontend is now ready! Open http://localhost:5001 to start using the Collateral Management System.

---

**Note:** This frontend integrates with your existing backend APIs. Make sure your backend is running and accessible at the configured URL.
