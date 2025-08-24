#!/usr/bin/env python3
"""
Simple Flask Frontend for Collateral Management System
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import requests
import json
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import subprocess
import tempfile
import shutil

app = Flask(__name__)

# Backend API configuration
BACKEND_URL = "http://localhost:8000"

# File upload configuration
UPLOAD_FOLDER = 'files/collaterals'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save uploaded file and return the path"""
    if file and allowed_file(file.filename):
        # Create unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Create user-specific directory
        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()))
        os.makedirs(user_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(user_dir, unique_filename)
        file.save(file_path)
        
        return file_path
    return None

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/collateral/create', methods=['GET', 'POST'])
def create_collateral():
    """Create new collateral page"""
    if request.method == 'POST':
        try:
            # Get form data
            user_id = request.form.get('user_id')
            name = request.form.get('name')
            description = request.form.get('description')
            
            # Handle file upload
            uploaded_files = []
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    file_path = save_uploaded_file(file)
                    if file_path:
                        uploaded_files.append(file_path)
            
            # Get AI analysis options
            enable_rag3 = request.form.get('enable_rag3') == 'on'
            enable_llm = request.form.get('enable_llm') == 'on'
            enable_loan_calc = request.form.get('enable_loan_calc') == 'on'
            
            if uploaded_files:
                # Create collateral using backend API
                collateral_data = {
                    "user_id": user_id,
                    "name": name,
                    "description": description,
                    "images": uploaded_files
                }
                
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/collaterals/",
                        json=collateral_data,
                        timeout=30
                    )
                    
                    if response.status_code == 201:
                        collateral = response.json()
                        return render_template('create_collateral.html', 
                                             message="Collateral created successfully!",
                                             user_id=user_id, 
                                             name=name, 
                                             description=description,
                                             collateral_id=collateral.get('id'),
                                             loan_limit=collateral.get('loan_limit'),
                                             estimated_value=collateral.get('metadata', {}).get('total_estimated_value'))
                    else:
                        error_msg = f"Backend API error: {response.status_code} - {response.text}"
                        return render_template('create_collateral.html', 
                                             error=error_msg,
                                             user_id=user_id, 
                                             name=name, 
                                             description=description)
                        
                except requests.exceptions.RequestException as e:
                    error_msg = f"Failed to connect to backend API: {str(e)}"
                    return render_template('create_collateral.html', 
                                         error=error_msg,
                                         user_id=user_id, 
                                         name=name, 
                                         description=description)
            else:
                # No file uploaded, just return form data
                return render_template('create_collateral.html', 
                                     message="Form submitted (no image uploaded)",
                                     user_id=user_id, 
                                     name=name, 
                                     description=description)
        
        except Exception as e:
            return render_template('create_collateral.html', 
                                 error=f"Error processing form: {str(e)}")
    
    return render_template('create_collateral.html')

@app.route('/collateral/list')
def list_collaterals():
    """List all collaterals"""
    # Mock data for now
    collaterals = [
        {
            'id': 'collateral_001',
            'name': 'Luxury Rolex Watch',
            'user_id': 'yashvika',
            'status': 'pending',
            'estimated_value': '$4,000 - $4,500',
            'created_at': '2024-01-20'
        }
    ]
    return render_template('list_collaterals.html', collaterals=collaterals)

@app.route('/collateral/<collateral_id>/approve', methods=['GET', 'POST'])
def approve_collateral(collateral_id):
    """Approve collateral page"""
    if request.method == 'POST':
        # Handle approval
        loan_amount = float(request.form.get('loan_amount', 4000))
        interest_rate = float(request.form.get('interest_rate', 12))
        loan_term = int(request.form.get('loan_term', 365))
        
        # Calculate loan details
        total_interest = loan_amount * (interest_rate/100) * (loan_term/365)
        total_amount = loan_amount + total_interest
        monthly_payment = total_amount / (loan_term/30)
        
        return render_template('approve_collateral.html',
                             collateral_id=collateral_id,
                             loan_amount=loan_amount,
                             interest_rate=interest_rate,
                             loan_term=loan_term,
                             total_interest=total_interest,
                             total_amount=total_amount,
                             monthly_payment=monthly_payment,
                             message="Collateral approved successfully!")
    
    return render_template('approve_collateral.html', collateral_id=collateral_id)

@app.route('/api/test-backend')
def test_backend():
    """Test backend connection"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return jsonify({
            'status': 'success',
            'backend_status': 'connected',
            'response': response.text
        })
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'backend_status': 'disconnected',
            'error': str(e)
        })

@app.route('/api/test-collateral-creation')
def test_collateral_creation():
    """Test collateral creation with rolex.jpeg"""
    try:
        # Test the integration script directly
        result = subprocess.run(['poetry', 'run', 'python', 'rag3_llampi_integration.py', '--example'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            return jsonify({
                'status': 'success',
                'message': 'Collateral creation test successful',
                'output': result.stdout[-500:]  # Last 500 chars
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Collateral creation test failed',
                'error': result.stderr
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Test execution failed',
            'error': str(e)
        })

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """API endpoint for image upload"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        file_path = save_uploaded_file(file)
        if not file_path:
            return jsonify({'error': 'Invalid file type'}), 400
        
        return jsonify({
            'status': 'success',
            'file_path': file_path,
            'filename': file.filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-collateral', methods=['POST'])
def create_collateral_api():
    """API endpoint for creating collateral"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['user_id', 'name', 'description', 'images']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Call backend API
        response = requests.post(
            f"{BACKEND_URL}/collaterals/",
            json=data,
            timeout=30
        )
        
        if response.status_code == 201:
            return jsonify(response.json()), 201
        else:
            return jsonify({
                'error': f'Backend API error: {response.status_code}',
                'details': response.text
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Backend connection failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print("🚀 Starting Flask Frontend...")
    print(f"📡 Backend URL: {BACKEND_URL}")
    print("🌐 Frontend will be available at: http://localhost:5001")
    print("📁 Make sure templates/ folder exists with HTML files")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
