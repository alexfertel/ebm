from flask import render_template, Blueprint

view = Blueprint('views', __name__)

@view.route('/')
def index():
    return render_template('index.html')