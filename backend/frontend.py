#!/usr/bin/env python3
"""
Simple Flask Frontend for Collateral Management System
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# Backend API configuration
BACKEND_URL = "http://localhost:8000"

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/collateral/create', methods=['GET', 'POST'])
def create_collateral():
    """Create new collateral page"""
    if request.method == 'POST':
        # Handle form submission
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        description = request.form.get('description')
        
        # For now, just return success message
        return render_template('create_collateral.html', 
                             message="Collateral creation form submitted!",
                             user_id=user_id, name=name, description=description)
    
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
        import subprocess
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

if __name__ == '__main__':
    print("🚀 Starting Flask Frontend...")
    print(f"📡 Backend URL: {BACKEND_URL}")
    print("🌐 Frontend will be available at: http://localhost:5001")
    print("📁 Make sure templates/ folder exists with HTML files")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
