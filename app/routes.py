from flask import Blueprint, request, jsonify, current_app
from app import db
from sqlalchemy.exc import SQLAlchemyError
from app.models import Character, Task, Skill, CharacterResources, CharacterSkill, StartingArea, Stat, Quest, CharacterTask,CharacterTask, Task, CharacterResources, db, WorldResources
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from datetime import datetime
import json

task_bp = Blueprint('tasks', __name__)
admin_bp = Blueprint('skills', __name__)
resource_bp = Blueprint('resources', __name__)

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

        def get_css_class(state, value):
            if state == 'available':
                return 'available'
            elif state in ['close_level', 'close_skill']:
                if 1 <= abs(value) <= 2:
                    return 'yellow'
                elif abs(value) >= 3:
                    return 'red'
            return 'locked'  # Default class for locked state

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

                print(f"Resource ID: {resource_id}")

                resource_name = WorldResources.query.filter_by(id=resource_id).first().resource_name
                required_qty = resource_data.get('amount')
                
                # Query the character's resources
                char_resource = CharacterResources.query.filter_by(character_id=character_id, resource_id=resource_id).first()
                
                # If the character doesn't have the resource or the quantity is insufficient
                if not char_resource or char_resource.quantity < required_qty:
                    resource_check = False
                
                # Append resource information
                resource_info.append({
                    'resource_id': resource_id,
                    'resource_name': resource_name,
                    'required_quantity': required_qty,
                    'character_quantity': char_resource.quantity if char_resource else 0
                })

            # Get skill level differences for the task
            skill_info = []
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

            # Calculate task state based on character level
            task_state = {"state": "available", "value": 0} if (task.level_required and character.level >= task.level_required) else {"state": "locked", "value": 0}
            level_difference = task.level_required - character.level if task.level_required else None

            if task.level_required:
                if character.level < task.level_required:
                    if character.level + 1 >= task.level_required:
                        task_state = {"state": "close_level", "value": level_difference}
                    else:
                        task_state = {"state": "locked", "value": level_difference}

            # Check skill requirements
            for skill in task.skills:
                char_skill_level = character_skills.get(skill.id, 0)
                skill_level_diff = task.skill_id_level_required - char_skill_level if task.skill_id_level_required else None

                if skill_level_diff is not None and char_skill_level < task.skill_id_level_required:
                    if char_skill_level + 1 >= task.skill_id_level_required:
                        if task_state["state"] != "close_level":
                            task_state = {"state": "close_skill", "value": skill_level_diff}
                    elif task_state["state"] not in ["close_level", "close_skill"]:
                        task_state = {"state": "locked", "value": skill_level_diff}

            # Append task information
            tasks_data.append({
                'id': task.id,
                'name': task.name,
                'description': task.description,
                'difficulty': task.difficulty,
                'xp': task.xp,
                'icon': task.icon,
                'resources': resource_info,
                'base_duration': task.base_duration,
                'base_energy': task.base_energy,
                'level_required': task.level_required,
                'level_difference': level_difference,
                'repeatable': task.repeatable,
                'skill_point_reward': task.skill_point_reward,
                'skills': skill_info,
                'has_energy': has_energy,
                'has_required_resources': resource_check,
                'state': task_state,
                'css_class': get_css_class(task_state['state'], task_state['value'])  # Add CSS class

            })
        
        # Define a sorting key function
        def task_sort_key(task):
            state = task['state']['state']
            value = task['state']['value']
            
            # Define the order of states
            state_order = {'available': 0, 'close_level': 1, 'close_skill': 2, 'locked': 3}
            
            # Return a tuple for sorting
            # Use value (not negative) to sort within each category
            return (state_order[state], value)

        # Sort the tasks using the custom sorting function
        sorted_tasks = sorted(tasks_data, key=task_sort_key)
        
        # Return the sorted task data as a JSON response
        return jsonify({"tasks": sorted_tasks}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/character/<int:character_id>', methods=['GET'])
def get_character_data(character_id):
    try:
        # Fetch the character by ID
        character = Character.query.get(character_id)

        print("Character:", character)

        if not character:
            return jsonify({"message": "Character not found."}), 404

        # Fetch character's resources
        resources = CharacterResources.query.filter_by(character_id=character_id).all()
        resource_data = [
            {
                "character_id": resource.character_id,
                "resource_id": resource.resource_id,
                "quantity": resource.quantity
            } for resource in resources
        ]

        # Fetch character's skills
        skills = CharacterSkill.query.filter_by(character_id=character_id).all()
        skill_data = [
            {
                "skill_id": skill.skill_id,
                "name": skill.skill.name,
                "description": skill.skill.description,
                "level": skill.level
            } for skill in skills
        ]

        # Fetch tasks that are available to the character
        tasks = Task.query.filter_by(starting_area_id=character.starting_area_id).all()
        task_data = [
            {
                "task_id": task.id,
                "name": task.name,
                "description": task.description,
                "level_required": task.level_required,
                "energy_required": task.base_energy,
                "xp_reward": task.xp,
                "repeatable": task.repeatable
            } for task in tasks
        ]

        # Return all character-related data
        character_data = {
            "id": character.id,
            "name": character.name,
            "level": character.level,
            "xp": character.xp,
            "energy": character.energy,
            "skill_points": character.skill_points,
            "resources": resource_data,
            "skills": skill_data,
            "tasks": task_data
        }

        return jsonify(character_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def check_skill_requirement(character_id, skill_requirements, db):
    # Example function to check if character meets skill requirements
    for skill, required_level in skill_requirements.items():
        skill_record = db.query(CharacterSkill).filter(
            CharacterSkill.character_id == character_id,
            CharacterSkill.skill_name == skill
        ).first()
        
        if not skill_record or skill_record.skill_level < required_level:
            return False
    return True

@admin_bp.route('/quest/<int:quest_id>', methods=['GET'])
def get_quest(quest_id):
    quest = db.query(Quest).filter(Quest.id == quest_id).first()

    if quest:
        return jsonify({
            "id": quest.id,
            "name": quest.name,
            "description": quest.description,
            "stages": quest.stages
        })
    return jsonify({"error": "Quest not found"}), 404

@admin_bp.route('/quest/<int:quest_id>/stage/<int:stage_id>/character/<int:character_id>', methods=['GET'])
def get_quest_stage(quest_id, stage_id, character_id):
    quest = db.query(Quest).filter(Quest.id == quest_id).first()

    if quest:
        stages = quest.stages
        stage = next((s for s in stages if s["stage_id"] == stage_id), None)

        if stage:
            choices = stage["choices"]
            for choice in choices:
                skill_req = choice.get("skill_requirement", {})
                if skill_req and not check_skill_requirement(character_id, skill_req, db):
                    choice["available"] = False
                else:
                    choice["available"] = True

            return jsonify({
                "stage_id": stage_id,
                "description": stage["description"],
                "choices": choices
            })

    return jsonify({"error": "Quest stage not found"}), 404

@task_bp.route('/complete_task', methods=['POST'])
def complete_task():
    try:
        data = request.json
        task_id = data.get('task_id')
        character_id = data.get('character_id')
        
        current_app.logger.info(f"Completing task {task_id} for character {character_id}")

        # Step 1: Check if CharacterTask exists; if not, create it
        character_task = CharacterTask.query.filter_by(task_id=task_id, character_id=character_id).first()
        if not character_task:
            character_task = CharacterTask(
                character_id=character_id,
                task_id=task_id,
                state='completed',
                last_updated=datetime.utcnow()
            )
            db.session.add(character_task)
            current_app.logger.info(f"Created new CharacterTask for task {task_id} and character {character_id}")
        else:
            character_task.state = 'completed'
            character_task.last_updated = datetime.utcnow()
            current_app.logger.info(f"Updated existing CharacterTask for task {task_id} and character {character_id}")

        # Step 2: Fetch the task details from the tasks table
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            current_app.logger.error(f"Task {task_id} not found")
            return jsonify({"error": "Task not found"}), 404

        current_app.logger.info(f"Task {task_id} details: {task}")
        current_app.logger.info(f"Task {task_id} resources: {task.resources}")

        # Step 3: Add resources to CharacterResources if they exist
        resources_granted = task.resources or []
        current_app.logger.info(f"Resources to be granted: {resources_granted}")

        for resource_data in resources_granted:
            resource_id = resource_data.get('id')
            quantity = resource_data.get('amount', 0)

            current_app.logger.info(f"Processing resource {resource_id} with quantity {quantity}")

            world_resource = WorldResources.query.filter_by(id=resource_id).first()
            if not world_resource:
                current_app.logger.warning(f"Resource with ID {resource_id} not found in WorldResources")
                continue

            character_resource = CharacterResources.query.filter_by(character_id=character_id, resource_id=world_resource.id).first()

            if character_resource:
                old_quantity = character_resource.quantity
                character_resource.quantity += quantity
                current_app.logger.info(f"Updated existing resource {resource_id} for character {character_id}. Old quantity: {old_quantity}, New quantity: {character_resource.quantity}")
            else:
                new_resource = CharacterResources(
                    character_id=character_id,
                    resource_id=world_resource.id,
                    quantity=quantity
                )
                db.session.add(new_resource)
                current_app.logger.info(f"Added new resource {resource_id} for character {character_id} with quantity {quantity}")

        # Commit all changes
        db.session.commit()
        current_app.logger.info("All changes committed successfully")

        return jsonify({"message": "Task completed and resources granted"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error in complete_task: {str(e)}", exc_info=True)
        return jsonify({"error": "A database error occurred"}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Unexpected error in complete_task: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500

@resource_bp.route('/<int:character_id>', methods=['GET'])
def get_resources(character_id):
    try:
        # Fetch character's resources by character_id
        resources = CharacterResources.query.filter_by(character_id=character_id).all()
        
        total_resources = []

        # Iterate over character's resources without reusing the 'resources' variable
        for character_resource in resources:
            # Fetch the world resource related to the character's resource
            resource = WorldResources.query.filter_by(id=character_resource.resource_id).first()
            total_resources.append({
                "resource_id": character_resource.resource_id,
                "name": resource.resource_name,
                "quantity": character_resource.quantity,
                "icon": resource.icon
            })            

        # Correctly use the total_resources to prepare the JSON response
        resource_data = [
            {
                "resource_id": r["resource_id"],
                "name": r["name"],
                "quantity": r["quantity"]
            } for r in total_resources
        ]

        return jsonify(resource_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/character/base/<int:character_id>', methods=['GET'])
def get_character_base_data(character_id):
    try:
        # Fetch the character by ID
        character = Character.query.get(character_id)

        print("Character:", character)

        if not character:
            return jsonify({"message": "Character not found."}), 404

        # Fetch character's resources
        resources = CharacterResources.query.filter_by(character_id=character_id).all()
        resource_data = [
            {
                "character_id": resource.character_id,
                "resource_id": resource.resource_id,
                "resource_name": WorldResources.query.filter_by(id=resource.resource_id).first().resource_name,
                "quantity": resource.quantity
            } for resource in resources
        ]

        # Fetch character's skills
        skills = CharacterSkill.query.filter_by(character_id=character_id).all()
        skill_data = [
            {
                "skill_id": skill.skill_id,
                "name": skill.skill.name,
                "description": skill.skill.description,
                "level": skill.level
            } for skill in skills
        ]

        # Return only basic character-related data (no tasks)
        character_data = {
            "id": character.id,
            "name": character.name,
            "level": character.level,
            "xp": character.xp,
            "energy": character.energy,
            "skill_points": character.skill_points,
            "resources": resource_data,
            "skills": skill_data
        }

        return jsonify(character_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/character/skills/increase', methods=['POST'])
def increase_character_skill():
    try:
        # Get the JSON data from the request
        data = request.get_json()

        character_id = data.get('character_id')
        skill_id = data.get('skill_id')
        points_to_add = data.get('points', 1)  # Default to adding 1 point if not provided

        if not character_id or not skill_id:
            return jsonify({"error": "Missing required fields"}), 400

        # Fetch the existing skill record for this character and skill
        character_skill = CharacterSkill.query.filter_by(character_id=character_id, skill_id=skill_id).first()

        if character_skill:
            # Update the skill level by adding the points
            character_skill.level += points_to_add
            character_skill.last_updated = datetime.utcnow()
        else:
            # Create a new record if the character doesn't have this skill yet
            character_skill = CharacterSkill(
                character_id=character_id,
                skill_id=skill_id,
                level=points_to_add,  # Set level to the points added
                last_updated=datetime.utcnow()
            )
            db.session.add(character_skill)

        # Commit changes to the database
        db.session.commit()

        return jsonify({
            "message": "Character skill updated successfully",
            "character_id": character_skill.character_id,
            "skill_id": character_skill.skill_id,
            "new_level": character_skill.level
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/')
def home():
    return "Hello, World!"
