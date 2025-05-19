import os
import sys

# Add the current directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import from local modules
from __init__ import create_app, db

# Create Flask application instance
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    """Configure Flask shell context."""
    # Import models here to avoid circular imports
    from models import User, Project, Tag, Contact, Client, FreelanceProject, TimeLog, Invoice
    
    return dict(
        db=db, 
        User=User, 
        Project=Project, 
        Tag=Tag, 
        Contact=Contact,
        Client=Client,
        FreelanceProject=FreelanceProject,
        TimeLog=TimeLog,
        Invoice=Invoice
    )

if __name__ == '__main__':
    app.run(debug=True)