from flask import Blueprint, request, jsonify
from app import db
from app.models import Skill, Stat

# Define a Blueprint for skills
admin_bp = Blueprint('skills', __name__)

@admin_bp.route('/skills', methods=['GET', 'POST'])
def manage_skills():
    if request.method == 'GET':
        # Handle GET request: Retrieve all skills
        skills = Skill.query.all()
        return jsonify([{
            'id': skill.id,
            'name': skill.name,
            'description': skill.description,
            'category': skill.category,
            'parent_skill_id': skill.parent_skill_id  # Include parent skill info
        } for skill in skills])

    elif request.method == 'POST':
        # Handle POST request: Insert a new skill with optional parent_skill_id
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        category = data.get('category')
        parent_skill_id = data.get('parent_skill_id')  # Get parent_skill_id from request

        if not name:
            return jsonify({'error': 'Name is required'}), 400

        # Create the new skill
        new_skill = Skill(name=name, description=description, category=category)

        # If parent_skill_id is provided, set the parent_skill relationship
        if parent_skill_id:
            parent_skill = Skill.query.get(parent_skill_id)
            if parent_skill:
                new_skill.parent_skill = parent_skill
            else:
                return jsonify({'error': 'Parent skill not found'}), 404

        # Add the skill to the database
        db.session.add(new_skill)
        db.session.commit()

        return jsonify({
            'message': 'Skill created successfully',
            'skill': {
                'id': new_skill.id,
                'name': new_skill.name,
                'description': new_skill.description,
                'category': new_skill.category,
                'parent_skill_id': new_skill.parent_skill_id
            }
        }), 201

# Route to handle both GET and POST for stats
@admin_bp.route('/stats', methods=['GET', 'POST'])
def manage_stats():
    if request.method == 'GET':
        # Handle GET request: Retrieve all stats
        stats = Stat.query.all()
        return jsonify([{
            'id': stat.id,
            'name': stat.name,
            'description': stat.description,
            'type': stat.type
        } for stat in stats])

    elif request.method == 'POST':
        # Handle POST request: Insert a new stat
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        stat_type = data.get('type')

        if not name or not stat_type:
            return jsonify({'error': 'Name and type are required'}), 400

        new_stat = Stat(name=name, description=description, type=stat_type)
        db.session.add(new_stat)
        db.session.commit()

        return jsonify({
            'message': 'Stat created successfully',
            'stat': {
                'id': new_stat.id,
                'name': new_stat.name,
                'description': new_stat.description,
                'type': new_stat.type
            }
        }), 201

@admin_bp.route('/')
def home():
    return "Hello, World!"
