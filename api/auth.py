from flask import jsonify, request, current_app
from functools import wraps
import jwt
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to resolve imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import db from the parent package
from __init__ import db
# Import models from the parent package
from models import User
# Import the blueprint
from api import api

def generate_token(user_id):
    """Generate JWT token for user."""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),  # Token expires in 24 hours
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify JWT token and return user_id."""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def admin_required(f):
    """Decorator to require admin authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer TOKEN
            except IndexError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid authorization header format'
                }), 401
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Authentication token is missing'
            }), 401
        
        # Verify token
        user_id = verify_token(token)
        if user_id is None:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired token'
            }), 401
        
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 401
        
        # Add user to request context
        request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function

@api.route('/auth/login', methods=['POST'])
def login():
    """Admin login endpoint."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'status': 'error',
                'message': 'Username and password are required'
            }), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'status': 'error',
                'message': 'Invalid username or password'
            }), 401
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/auth/verify', methods=['GET'])
@admin_required
def verify_auth():
    """Verify if current token is valid."""
    try:
        user = request.current_user
        return jsonify({
            'status': 'success',
            'message': 'Token is valid',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/auth/logout', methods=['POST'])
@admin_required
def logout():
    """Logout endpoint (client-side token removal)."""
    return jsonify({
        'status': 'success',
        'message': 'Logout successful. Please remove token from client.'
    })

@api.route('/auth/create-admin', methods=['POST'])
def create_admin():
    """Create initial admin user (remove this endpoint after first use!)."""
    try:
        # Check if any users already exist
        existing_users = User.query.count()
        if existing_users > 0:
            return jsonify({
                'status': 'error',
                'message': 'Admin user already exists. This endpoint is disabled.'
            }), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create admin user
        admin_user = User(
            username=data['username'],
            email=data['email']
        )
        admin_user.set_password(data['password'])
        
        db.session.add(admin_user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Admin user created successfully',
            'user': {
                'id': admin_user.id,
                'username': admin_user.username,
                'email': admin_user.email
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/auth/change-password', methods=['PUT'])
@admin_required
def change_password():
    """Change user password."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({
                'status': 'error',
                'message': 'Current password and new password are required'
            }), 400
        
        user = request.current_user
        
        # Verify current password
        if not user.check_password(current_password):
            return jsonify({
                'status': 'error',
                'message': 'Current password is incorrect'
            }), 400
        
        # Set new password
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Password changed successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500