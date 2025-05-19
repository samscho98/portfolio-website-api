from flask import jsonify
from sqlalchemy import text
import sys
import os

# Add parent directory to path to resolve imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import db from the parent package
from __init__ import db
# Import the blueprint
from api import api

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running and retrieve PostgreSQL version."""
    try:
        # Execute a query to get PostgreSQL version
        result = db.session.execute(text('SELECT version()')).scalar()
        
        # Extract the version number from the version string
        # The version string typically looks like:
        # "PostgreSQL 16.0 on x86_64-pc-linux-gnu, compiled by gcc..."
        version_info = result.split()[1] if result else "Unknown"
        
        return jsonify({
            'status': 'success',
            'message': 'API is running and database connection successful',
            'database_version': result,
            'postgres_version': version_info
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Database connection failed: {str(e)}'
        }), 500