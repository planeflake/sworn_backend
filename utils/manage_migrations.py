import os

def run_migration():
    # Set the FLASK_APP environment variable
    os.environ['FLASK_APP'] = 'app.py'  # Adjust this if needed

    # Change the working directory to the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(project_root)

    # Prompt for a migration message
    message = input("Enter a migration message: ")

    # Run flask db migrate
    os.system(f"flask db migrate -m \"{message}\"")

    # Run flask db upgrade
    os.system("flask db upgrade")

if __name__ == "__main__":
    run_migration()
