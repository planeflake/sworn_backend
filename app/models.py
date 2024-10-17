from datetime import datetime
from . import db

class Character(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, unique=False, nullable=False)
    level = db.Column(db.Integer, unique=False, nullable=False)
    energy = db.Column(db.Integer, nullable=False)
    xp = db.Column(db.Integer, nullable=False)
    skill_points = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(50), nullable=True, default='New Character')
    max_health = db.Column(db.Integer, nullable=False, default=10)
    health = db.Column(db.Integer, nullable=False, default=10)
    max_energy = db.Column(db.Integer, nullable=False, default=10)
    starting_area_id = db.Column(db.Integer, db.ForeignKey('starting_areas.id'), nullable=False)

    character_tasks = db.relationship('CharacterTask', back_populates='character', lazy=True)
    character_skills = db.relationship('CharacterSkill', back_populates='character', lazy=True)
    resources = db.relationship('CharacterResources', back_populates='character', lazy=True)

class experienceForLevel(db.Model):
    __tablename__ = 'experience_for_level'
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False)
    experience = db.Column(db.Integer, nullable=False)

class CharacterTask(db.Model):
    __tablename__ = 'character_tasks'
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    
    # Task state: available, completed, failed, in_progress, etc.
    state = db.Column(db.String(50), nullable=False, default='in_progress')
    
    # Timestamp of the last state change
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Update the relationship with Character
    character = db.relationship('Character', back_populates='character_tasks')

    # Task relationship
    task = db.relationship('Task', back_populates='character_tasks')

class CharacterResources(db.Model):
    __tablename__ = 'character_resources'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('world_resources.id'), nullable=False)

    character = db.relationship('Character', back_populates='resources')
    world_resource = db.relationship('WorldResources', back_populates='character_resources')

class Stat(db.Model):
    __tablename__ = 'stats'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)

    skills = db.relationship('Skill', secondary='skill_stats', backref='stats')

class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    category = db.Column(db.String(50))

    # Parent Skill relationship
    parent_skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'))
    parent_skill = db.relationship('Skill', remote_side=[id], backref='sub_skills')

    # Relationship with CharacterSkill
    character_skills = db.relationship('CharacterSkill', back_populates='skill')

    def __repr__(self):
        return f'<Skill {self.name}>'

class CharacterSkill(db.Model):
    __tablename__ = 'character_skills'
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    level = db.Column(db.Integer, nullable=False)

    character = db.relationship('Character', back_populates='character_skills')
    skill = db.relationship('Skill', back_populates='character_skills')
skill_stats = db.Table('skill_stats',
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id'), primary_key=True),
    db.Column('stat_id', db.Integer, db.ForeignKey('stats.id'), primary_key=True)
)

starting_area_skills = db.Table('starting_area_skills',
db.Column('starting_area_id', db.Integer, db.ForeignKey('starting_areas.id'), primary_key=True),
db.Column('skill_id', db.Integer, db.ForeignKey('skills.id'), primary_key=True)
)

class StartingArea(db.Model):
    __tablename__ = 'starting_areas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))

    # Define the many-to-many relationship between StartingArea and Skill
    skills = db.relationship('Skill', secondary=starting_area_skills, backref='starting_areas')

task_skills = db.Table('task_skills',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id'), primary_key=True)
)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    difficulty = db.Column(db.Integer, nullable=False)
    xp = db.Column(db.Integer, nullable=False)
    icon = db.Column(db.String(255), nullable=True)
    resources = db.Column(db.JSON)  # Use JSONB in PostgreSQL if possible
    starting_area_id = db.Column(db.Integer, db.ForeignKey('starting_areas.id'))
    base_duration = db.Column(db.Integer, nullable=False)
    base_energy = db.Column(db.Integer, nullable=False)
    level_required = db.Column(db.Integer, nullable=True)
    repeatable = db.Column(db.Boolean, nullable=False, default=False)
    unlocks_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    skill_id_level_required = db.Column(db.Integer, nullable=True)
    skill_point_reward = db.Column(db.Integer, nullable=True)
    
    # Use the many-to-many relationship with skills
    skills = db.relationship('Skill', secondary=task_skills, backref='tasks')
    
    # Add the relationship with CharacterTask
    character_tasks = db.relationship('CharacterTask', back_populates='task')

    def __repr__(self):
        return f'<Task {self.name}>'

class Quest(db.Model):
    __tablename__ = 'quests'

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, index=True)
    description = db.Column(db.String)
    stages = db.Column(db.JSON)  # Stores the quest stages, each stage containing choices and outcomes

class WorldResources(db.Model):
    __tablename__ = 'world_resources'
    id = db.Column(db.Integer, primary_key=True)
    resource_name = db.Column(db.String, nullable=False)
    resource_description = db.Column(db.String, nullable=False)
    resource_type = db.Column(db.String, nullable=False)
    region = db.Column(db.String, nullable=True)
    icon = db.Column(db.String, nullable=True)
    rarity = db.Column(db.String, nullable=True)

    character_resources = db.relationship('CharacterResources', back_populates='world_resource', lazy=True)
