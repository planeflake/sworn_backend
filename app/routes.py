from flask import Blueprint, request, jsonify
from app import db
from app.models import Skill, Stat, StartingArea, Task, Character, CharacterResources, Resource

admin_bp = Blueprint('skills', __name__)

@admin_bp.route('/skills', methods=['GET', 'POST'])
def manage_skills():
    if request.method == 'GET':
        # Handle GET request: Retrieve all skills, including parent skill name
        skills = Skill.query.all()
        return jsonify([{
            'id': skill.id,
            'name': skill.name,
            'description': skill.description,
            'category': skill.category,
            'parent_skill_id': skill.parent_skill_id,
            'parent_skill_name': skill.parent_skill.name if skill.parent_skill else None  # Include parent skill name
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
                'parent_skill_id': new_skill.parent_skill_id,
                'parent_skill_name': new_skill.parent_skill.name if new_skill.parent_skill else None
            }
        }), 201

@admin_bp.route('/starting_areas', methods=['GET'])
def get_starting_areas():
    # Query all StartingArea objects from the database, including their associated skills
    starting_areas = StartingArea.query.all()

    # Convert the list of StartingArea objects into a list of dictionaries (JSON serializable)
    starting_areas_data = [
        {
            'id': area.id,
            'name': area.name,
            'description': area.description,
            # Include associated skills as a list of dictionaries
            'skills': [
                {'id': skill.id, 'name': skill.name, 'description': skill.description} 
                for skill in area.skills
            ]
        }
        for area in starting_areas
    ]
    
    # Return the data as JSON
    return jsonify(starting_areas_data)

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

@admin_bp.route('/tasks/<int:starting_area_id>/character/<int:character_id>', methods=['GET'])
def get_tasks_by_starting_area(starting_area_id, character_id):
    try:
        # Query the Task table for tasks associated with the given starting area ID
        tasks = Task.query.filter_by(starting_area_id=starting_area_id).all()
        character = Character.query.filter_by(id=character_id).first()

        # If the character or tasks are not found, return 404
        if not character:
            return jsonify({"message": "Character not found."}), 404
        if not tasks:
            return jsonify({"message": "No tasks found for this starting area.", "tasks": []}), 404

        # Get character's skill levels
        character_skills = {cs.skill_id: cs.level for cs in character.character_skills}

        # Convert tasks to a list of dictionaries with additional checks
        tasks_data = []
        for task in tasks:
            # Check if character has enough energy to perform the task
            has_energy = character.energy >= task.base_energy

            # Parse the required resources from the task's resources JSON field
            required_resources = task.resources  # Assuming it's stored as JSON
            resource_check = True
            resource_info = []
            for resource_data in required_resources:
                resource_id = resource_data.get('id')
                required_qty = resource_data.get('amount')
                
                # Query the character's resources
                char_resource = CharacterResources.query.filter_by(character_id=character_id).filter_by(resource_id=resource_id).first()
                
                # If the character doesn't have the resource or the quantity is insufficient
                if not char_resource or char_resource.quantity < required_qty:
                    resource_check = False
                
                # Append resource information
                resource_info.append({
                    'resource_id': resource_id,
                    'required_quantity': required_qty,
                    'character_quantity': char_resource.quantity if char_resource else 0
                })

            # Get skill level differences for the task
            skill_info = []
            skill_state = "available"
            skill_difference = None
            for skill in task.skills:
                char_skill_level = character_skills.get(skill.id, 0)  # Default to 0 if the character doesn't have the skill
                skill_level_diff = task.skill_id_level_required - char_skill_level if task.skill_id_level_required else None

                skill_info.append({
                    'id': skill.id,
                    'name': skill.name,
                    'character_skill_level': char_skill_level,
                    'required_skill_level': task.skill_id_level_required,
                    'skill_level_difference': skill_level_diff
                })

                # Check if the character is close to skill level requirement
                if skill_level_diff is not None:
                    if char_skill_level < task.skill_id_level_required:
                        if char_skill_level + 1 >= task.skill_id_level_required:
                            skill_state = {"close_skill": skill_level_diff}
                        else:
                            skill_state = "locked"

            # Calculate task state based on character level
            task_state = "available" if (task.level_required and character.level >= task.level_required) else skill_state
            level_difference = task.level_required - character.level if task.level_required else None

            if task.level_required and (character.level + 1 >= task.level_required):
                if task_state == "available":
                    task_state = {"close_level": level_difference}
                else:
                    task_state.update({"close_level": level_difference})

            # If still locked, set as locked
            if task_state == "locked":
                task_state = "locked"

            # Append task information
            tasks_data.append({
                'id': task.id,
                'name': task.name,
                'description': task.description,
                'difficulty': task.difficulty,
                'xp': task.xp,
                'icon': task.icon,
                'resources': resource_info,  # Now including resource details
                'base_duration': task.base_duration,
                'base_energy': task.base_energy,
                'level_required': task.level_required,
                'level_difference': level_difference,
                'repeatable': task.repeatable,
                'skill_point_reward': task.skill_point_reward,
                'skills': skill_info,  # Skills info including level differences
                'has_energy': has_energy,
                'has_required_resources': resource_check,  # True if character has all required resources
                'state': task_state  # Task state as JSON (available, locked, close_skill, close_level)
            })
        
        # Return the task data as a JSON response
        return jsonify({"tasks": tasks_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/')
def home():
    return "Hello, World!"
