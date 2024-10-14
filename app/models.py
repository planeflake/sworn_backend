from . import db

# Character Model
class Character(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, unique=False, nullable=False)
    level = db.Column(db.Integer, unique=False, nullable=False)
    energy = db.Column(db.Integer, nullable=False)
    xp = db.Column(db.Integer, nullable=False)
    skill_points = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(50), nullable=True, default='New Character')

    # Relationship to track the character's skills
    character_skills = db.relationship('CharacterSkill', backref='character_ref', lazy=True)

class CharacterSkill(db.Model):
    __tablename__ = 'character_skills'
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    level = db.Column(db.Integer, nullable=False)  # Skill level of the character

    # Use 'character_ref' to avoid conflict
    character = db.relationship('Character', backref='skills')
    skill = db.relationship('Skill', backref='character_skills')


class Resource(db.Model):
    __tablename__ = 'resources'  # Explicitly specifying plural table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Resource {self.name}>'

class CharacterResources(db.Model):
    __tablename__ = 'character_resources'  # Explicitly specifying plural table name
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)

class CharacterStat(db.Model):  # Changed to CharacterStat for naming consistency
    __tablename__ = 'character_stats'  # Plural table name
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    stat_id = db.Column(db.Integer, db.ForeignKey('stats.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False)

class Stat(db.Model):
    __tablename__ = 'stats'  # Explicitly specifying plural table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)

    skills = db.relationship('Skill', secondary='skill_stats', backref='stats')

class Skill(db.Model):
    __tablename__ = 'skills'  # Explicitly specifying plural table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    category = db.Column(db.String(50))

    # Parent Skill relationship
    parent_skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'))
    parent_skill = db.relationship('Skill', remote_side=[id], backref='sub_skills')

    def __repr__(self):
        return f'<Skill {self.name}>'

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
    # skill_bonus = db.Column(db.Integer, nullable=False)  # Commented out or removed

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
    
    def __repr__(self):
        return f'<Task {self.name}>'
