from flask import render_template, Blueprint, request, redirect
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, RECIVED_FOLDER
from datetime import date
import os
# from src.client import EBMC

view = Blueprint('views', __name__)
# ebmc = EBMC()

def get_files():
    files = os.listdir(RECIVED_FOLDER)
    file_info = [ 
        (file, 
        date.fromtimestamp(os.path.getmtime(os.path.join(RECIVED_FOLDER,file))),
        os.path.getsize(os.path.join(RECIVED_FOLDER,file))/1000000.0
         ) for file in files
        ]
    return file_info

@view.route('/', methods=['GET', 'POST'])
def index(error = ''):
    file_info = get_files()
    return render_template('index.html', files = file_info, error = error )

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
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        return redirect('/')
    return 'not ok'

@view.route('/login', methods=['POST'])
def login():
    # if ebm.login(request.form['email'],request.form['pass']):
    #     return redirect('/')
    return index('Bad Credentials')
    
@view.route('/register', methods=['POST'])
def register():
    pass

@view.route('/subscribe', methods=['POST'])
def subscribe():
    pass