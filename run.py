"""
Simple runner script for the Flask backend.
This lets us keep the backend code separate while avoiding import issues.
"""
import os
import sys

# Add the project path to sys.path
project_path = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_path)

# Import the app from backend
from backend.app import app

if __name__ == '__main__':
    app.run(debug=True)