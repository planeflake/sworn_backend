from app import create_app, db
from app.models import Skill, Stat

app = create_app()

with app.app_context():
    # Create some stats
    strength = Stat(name='Strength')
    agility = Stat(name='Agility')
    intellect = Stat(name='Intellect')
    spirit = Stat(name='Spirit')
    stamina = Stat(name='Stamina')
    constitution = Stat(name='Constitution')

    # Create a skill and associate stats
    stealth = Skill(name='Stealth', stats=[agility, strength])
    athletics = Skill(name='Athletics', stats=[strength])
    gathering = Skill(name='Gathering', stats=[agility])
    fishing = Skill(name='Fishing', stats=[agility])
    cooking = Skill(name='Cooking', stats=[intellect])
    survival = Skill(name='Survival', stats=[constitution])
    herbalism = Skill(name='Herbalism', stats=[agility])
     


    # Add the objects to the session and commit them
    db.session.add_all([strength, agility, stealth, athletics])
    db.session.commit()

    print("Data populated successfully.")
