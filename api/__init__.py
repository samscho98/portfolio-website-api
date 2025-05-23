from flask import Blueprint

# Create the blueprint
api = Blueprint('api', __name__)

# Import routes AFTER creating the blueprint to avoid circular imports
# These imports must be at the bottom of the file
from . import health  # This imports the routes from health.py
from . import projects  # This imports the routes from projects.py
from . import contact  # This imports the routes from contact.py
from . import auth  # This imports the new admin auth routes

# Future routes for when you're ready to implement freelance features
# from . import clients
# from . import freelance_projects
# from . import time_logs
# from . import invoices