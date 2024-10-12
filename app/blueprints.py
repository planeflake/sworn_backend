from flask import Blueprint

api = Blueprint('api', __name__)

@api.route('/characters')
def example():
    return "This is an example route."
