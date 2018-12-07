from config import RECIVED_FOLDER
from datetime import date
import os


def get_files():
    files = os.listdir(RECIVED_FOLDER)
    file_info = [
        (file,
         date.fromtimestamp(os.path.getmtime(os.path.join(RECIVED_FOLDER, file))),
         os.path.getsize(os.path.join(RECIVED_FOLDER, file)) / 1000000.0
         ) for file in files
    ]
    return file_info


def send_file(file_location, target, type):
    file = open(file_location)
    size = os.path.getsize(file_location)

    # TODO: cambia 1000 por el tamanno maximo permitido
    for target in range(int(size / 1000)):

        # TODO: mandar correro con esta info
        # (self, user: str, data: str, name: str)
        ebmc.send('sandor', file.read(1000), file.name)

    if size % 1000:
        ebmc.send('sandor', file.read(size % 1000), file.name)

        # mandar correro con esta info
    file.close()
    os.remove(file_location)
    # TODO: buscar como borrar los archivos, ya que no es necsarios q 
    # persistan en el cliente una vez q se mandaron
