from config import RECIVED_FOLDER
from datetime import date
import os

def get_files():
    files = os.listdir(RECIVED_FOLDER)
    file_info = [ 
        (file, 
        date.fromtimestamp(os.path.getmtime(os.path.join(RECIVED_FOLDER,file))),
        os.path.getsize(os.path.join(RECIVED_FOLDER,file))/1000000.0
         ) for file in files
        ]
    return file_info