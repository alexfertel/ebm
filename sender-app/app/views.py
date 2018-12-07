from flask import render_template, Blueprint, request, redirect
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, TOKEN
from . import utils
import os

# from src.client import EBMC

view: Blueprint = Blueprint('views', __name__)


@view.route('/', methods=['GET', 'POST'])
def index(error=''):
    file_info = utils.get_files()
    return render_template('index.html', files=file_info, error=error)


@view.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'data' not in request.files:
            return 'Please select one file'
        file = request.files['data']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return 'Please select one file'
        # if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        file_location = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_location)

        utils.send_file(file_location, request.form['target'], request.form['radio'])

        return redirect('/')
    return 'not ok'


@view.route('/login', methods=['POST'])
def login():
    # token = ebm.login(request.form['email'],request.form['pass'])
    # if token:
    #     TOKEN = token
    #     return redirect('/')

    # TODO: ebm.login debe retornar el token de  usuario que se acaba de logear, 
    # de lo contrario 0, o algo por el estilo
    return index('Bad Credentials')


@view.route('/sing-up', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # ebm.login(request.form['email'],request.form['pass'])
        return redirect('/')
    return render_template('register.html')


@view.route('/subscribe', methods=['POST'])
def subscribe():
    # ebm.subscribe(request.form['event'], TOKEN)
    # TODO: ver bien que retorna este metodo, si no hace nada, entonce se queda asi
    # hay q hacer un unsubscribe
    return redirect('/')


@view.route('/create-event', methods=['POST'])
def create_event():
    # TODO: ver si implementar esto, 
    return redirect('/')


@view.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # TODO: aqui crear la instancia de ebm con los parametros del form
        # request.form['email_server']
        # request.form['user']
        # request.form['pwd']
        # request.form['email']
        # ebmc = EBMC()
        return redirect('/')
    return render_template('settings.html')
