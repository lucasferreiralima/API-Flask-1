from flask import Blueprint

setelan = Blueprint('setelan', __name__, template_folder='../templates/setelan')

from app.setelan import routes
