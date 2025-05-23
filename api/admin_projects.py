from flask import jsonify, request
from datetime import datetime
import sys
import os

# Add parent directory to path to resolve imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import db from the parent package
from __init__ import db
# Import models from the parent package
from models import Project, Tag
# Import the blueprint
from api import api
# Import authentication decorator
from .auth import admin_required

# Helper function to create slug from title
def create_slug(title):
    """Create a URL-friendly slug from title."""
    import re
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)  # Remove special characters
    slug = re.sub(r'\s+', '-', slug)  # Replace spaces with hyphens
    slug = slug.strip('-')  # Remove leading/trailing hyphens
    return slug

# Helper function to get or create tags
def get_or_create_tags(tag_names):
    """Get existing tags or create new ones."""
    tags = []
    for tag_name in tag_names:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        tags.append(tag)
    return tags

@api.route('/admin/projects', methods=['POST'])
@admin_required
def create_project():
    """Create a new project."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['title', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create slug from title if not provided
        slug = data.get('slug') or create_slug(data['title'])
        
        # Check if slug already exists
        existing_project = Project.query.filter_by(slug=slug).first()
        if existing_project:
            return jsonify({
                'status': 'error',
                'message': 'A project with this slug already exists'
            }), 400
        
        # Create new project
        new_project = Project(
            title=data['title'],
            slug=slug,
            description=data['description'],
            github=data.get('github'),
            private=data.get('private', False),
            featured=data.get('featured', False),
            content=data.get('content'),
            image_url=data.get('image_url'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Handle tags
        if 'tags' in data and data['tags']:
            tag_objects = get_or_create_tags(data['tags'])
            new_project.tags = tag_objects
        
        # Save to database
        db.session.add(new_project)
        db.session.commit()
        
        # Return created project
        project_data = {
            'id': new_project.id,
            'title': new_project.title,
            'slug': new_project.slug,
            'description': new_project.description,
            'github': new_project.github,
            'private': new_project.private,
            'featured': new_project.featured,
            'content': new_project.content,
            'image_url': new_project.image_url,
            'tags': [tag.name for tag in new_project.tags],
            'created_at': new_project.created_at.isoformat(),
            'updated_at': new_project.updated_at.isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'message': 'Project created successfully',
            'project': project_data
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/admin/projects/<int:project_id>', methods=['PUT'])
@admin_required
def update_project(project_id):
    """Update an existing project."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        # Find project
        project = Project.query.get(project_id)
        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
        
        # Update fields if provided
        if 'title' in data:
            project.title = data['title']
            # Update slug if title changed and no custom slug provided
            if 'slug' not in data:
                new_slug = create_slug(data['title'])
                # Check if new slug conflicts with existing projects (excluding current)
                existing = Project.query.filter(Project.slug == new_slug, Project.id != project_id).first()
                if not existing:
                    project.slug = new_slug
        
        if 'slug' in data:
            # Check if slug conflicts with existing projects (excluding current)
            existing = Project.query.filter(Project.slug == data['slug'], Project.id != project_id).first()
            if existing:
                return jsonify({
                    'status': 'error',
                    'message': 'A project with this slug already exists'
                }), 400
            project.slug = data['slug']
        
        if 'description' in data:
            project.description = data['description']
        if 'github' in data:
            project.github = data['github']
        if 'private' in data:
            project.private = data['private']
        if 'featured' in data:
            project.featured = data['featured']
        if 'content' in data:
            project.content = data['content']
        if 'image_url' in data:
            project.image_url = data['image_url']
        
        # Handle tags
        if 'tags' in data:
            if data['tags']:
                tag_objects = get_or_create_tags(data['tags'])
                project.tags = tag_objects
            else:
                project.tags = []
        
        # Update timestamp
        project.updated_at = datetime.utcnow()
        
        # Save changes
        db.session.commit()
        
        # Return updated project
        project_data = {
            'id': project.id,
            'title': project.title,
            'slug': project.slug,
            'description': project.description,
            'github': project.github,
            'private': project.private,
            'featured': project.featured,
            'content': project.content,
            'image_url': project.image_url,
            'tags': [tag.name for tag in project.tags],
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'message': 'Project updated successfully',
            'project': project_data
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/admin/projects/<int:project_id>', methods=['DELETE'])
@admin_required
def delete_project(project_id):
    """Delete a project."""
    try:
        # Find project
        project = Project.query.get(project_id)
        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
        
        # Store project title for response
        project_title = project.title
        
        # Delete project
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Project "{project_title}" deleted successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/admin/projects', methods=['GET'])
@admin_required
def get_all_projects_admin():
    """Get all projects for admin (including private ones)."""
    try:
        projects = Project.query.order_by(Project.updated_at.desc()).all()
        
        result = []
        for project in projects:
            project_data = {
                'id': project.id,
                'title': project.title,
                'slug': project.slug,
                'description': project.description,
                'github': project.github,
                'private': project.private,
                'featured': project.featured,
                'content': project.content,
                'image_url': project.image_url,
                'tags': [tag.name for tag in project.tags],
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat()
            }
            result.append(project_data)
        
        return jsonify({
            'status': 'success',
            'projects': result,
            'count': len(result)
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/admin/projects/<int:project_id>', methods=['GET'])
@admin_required
def get_project_admin(project_id):
    """Get a specific project for admin."""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
        
        project_data = {
            'id': project.id,
            'title': project.title,
            'slug': project.slug,
            'description': project.description,
            'github': project.github,
            'private': project.private,
            'featured': project.featured,
            'content': project.content,
            'image_url': project.image_url,
            'tags': [tag.name for tag in project.tags],
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'project': project_data
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/admin/tags', methods=['GET'])
@admin_required
def get_all_tags():
    """Get all available tags."""
    try:
        tags = Tag.query.order_by(Tag.name).all()
        
        result = []
        for tag in tags:
            tag_data = {
                'id': tag.id,
                'name': tag.name,
                'project_count': len(tag.projects)
            }
            result.append(tag_data)
        
        return jsonify({
            'status': 'success',
            'tags': result,
            'count': len(result)
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/admin/tags/<int:tag_id>', methods=['DELETE'])
@admin_required
def delete_tag(tag_id):
    """Delete a tag (only if not used by any projects)."""
    try:
        tag = Tag.query.get(tag_id)
        if not tag:
            return jsonify({
                'status': 'error',
                'message': 'Tag not found'
            }), 404
        
        # Check if tag is used by any projects
        if tag.projects:
            return jsonify({
                'status': 'error',
                'message': f'Cannot delete tag "{tag.name}" - it is used by {len(tag.projects)} project(s)'
            }), 400
        
        tag_name = tag.name
        db.session.delete(tag)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Tag "{tag_name}" deleted successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500