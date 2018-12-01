from flask import render_template, Blueprint, request, redirect
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER
import os

view = Blueprint('views', __name__)

@view.route('/', methods=['GET', 'POST'])
def index():
    print(request.form)
    # request._get_file_stream(total_content_length=, content_type=,)
    return render_template('index.html')

@view.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'data' not in request.files:
            print('iff')
            
            return redirect(request.url)
        file = request.files['data']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return redirect(request.url)
        # if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        return 'ok'
    return 'not ok'