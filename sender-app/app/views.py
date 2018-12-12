from flask import render_template, Blueprint, request, redirect
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, TOKEN, RECEIVED_FOLDER
# from . import utils
import os
import time
from datetime import date

from .src.client import EBMC

# from src.client import EBMC

view: Blueprint = Blueprint('views', __name__)

ebmc = ''


@view.route('/init')
def init():
    global ebmc
    print('Creo ebmc en init')
    ebmc = EBMC('s.martin@estudiantes.matcom.uh.cu', 'a.fertel@estudiantes.matcom.uh.cu',
                'correo.estudiantes.matcom.uh.cu', '#1S1m0l5enet')
    return redirect('/')


@view.route('/', methods=['GET', 'POST'])
def index(error=''):
    file_info = get_files()
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

        send_file(file_location, request.form['target'], request.form['radio'])

        return redirect('/')
    return 'not ok'


@view.route('/login', methods=['POST'])
def login():
    ebmc.login(request.form['email'], request.form['pass'])
    # token = ebm.login(request.form['email'],request.form['pass'])
    start = time.time()
    while True:
        if ebmc.token:
            TOKEN = ebmc.token
            return redirect('/')
        if time.time() - start > 40:
            break

    # TODO: ebm.login debe retornar el token de  usuario que se acaba de logear, 
    # de lo contrario 0, o algo por el estilo
    return index('Bad Credentials')


@view.route('/sing-up', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ebmc.register(request.form['email'], request.form['pwd'])
        return redirect('/')
    return render_template('register.html')


@view.route('/subscribe', methods=['POST'])
def subscribe():
    # ebm.subscribe(request.form['event'], TOKEN)
    ebmc.subscribe(request.form['event'])
    # hay q hacer un unsubscribe
    return redirect('/')


@view.route('/create-event', methods=['POST'])
def create_event():
    # TODO: ver si implementar esto,
    ebmc.create_event(request.form['event'])

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


def get_files():
    files = os.listdir(RECEIVED_FOLDER)
    file_info = [
        (file,
         date.fromtimestamp(os.path.getmtime(os.path.join(RECEIVED_FOLDER, file))),
         os.path.getsize(os.path.join(RECEIVED_FOLDER, file)) / 1000000.0
         ) for file in files
    ]
    return file_info


def send_file(file_location, target, type):
    with open(file_location, 'rb') as file:

        # file = open(file_location)
        size = os.path.getsize(file_location)

        # TODO: cambia 1000 por el tamanno maximo permitido
        for target in range(int(size / 1000)):
            # TODO: mandar correro con esta info
            # (self, user: str, data: str, name: str)
            ebmc.send('sandor', file.read(1000), file.name)

        if size % 1000:
            ebmc.send('sandor', file.read(size % 1000), file.name)

        # mandar correro con esta info
    os.remove(file_location)
    # persistan en el cliente una vez q se mandaron
