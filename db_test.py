import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a direct connection to test the database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'postgresql://postgres:password@localhost:5432/portfolio'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define minimal versions of the models for testing
class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    slug = db.Column(db.String(100))
    description = db.Column(db.Text)
    
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

# Test the connection
with app.app_context():
    try:
        # Try to query all projects
        projects = Project.query.all()
        print(f"Database connection successful! Found {len(projects)} projects.")
        
        # Try to query all tags
        tags = Tag.query.all()
        print(f"Found {len(tags)} tags.")
        
        # Print first project details if any exists
        if projects:
            print(f"First project: {projects[0].title}")
            
    except Exception as e:
        print(f"Error connecting to the database: {e}")