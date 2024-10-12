from . import db

# Character Model
class Character(db.Model):
    __tablename__ = 'characters'  # Explicitly specifying plural table name
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, unique=False, nullable=False)
    level = db.Column(db.Integer, unique=False, nullable=False)
    

# Character_Stat Model (can be CharacterStat for better naming convention)
class CharacterStat(db.Model):  # Changed to CharacterStat for naming consistency
    __tablename__ = 'character_stats'  # Plural table name
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    stat_id = db.Column(db.Integer, db.ForeignKey('stats.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False)

# Stat Model
class Stat(db.Model):
    __tablename__ = 'stats'  # Explicitly specifying plural table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)

    skills = db.relationship('Skill', secondary='skill_stats', backref='stats')


# Skill Model
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

# Association Table for Many-to-Many between Skills and Stats
skill_stats = db.Table('skill_stats',
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id'), primary_key=True),
    db.Column('stat_id', db.Integer, db.ForeignKey('stats.id'), primary_key=True)
)