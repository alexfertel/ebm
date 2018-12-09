import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'sender-app/uploads')
RECEIVED_FOLDER = os.path.join(BASE_DIR, 'sender-app/static/received')
TOKEN = ''
