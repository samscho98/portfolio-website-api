from flask import jsonify, request
import sys
import os
from datetime import datetime

# Add parent directory to path to resolve imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import db from the parent package
from __init__ import db
# Import models from the parent package
from models import Contact
# Import the blueprint
from api import api

@api.route('/contact', methods=['POST'])
def submit_contact():
    """Submit a contact form."""
    try:
        # Get form data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create new contact
        new_contact = Contact(
            name=data['name'],
            email=data['email'],
            message=data['message'],
            created_at=datetime.utcnow(),
            read=False
        )
        
        # Save to database
        db.session.add(new_contact)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Contact form submitted successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500