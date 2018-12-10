import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'src/uploads')
RECEIVED_FOLDER = os.path.join(BASE_DIR, 'sender-app/static/received')


MESSAGE_LENGTH = 1000000
SYS_MSG = 0
DATA_MSG = 1
MAX_BITS = 160
SIZE = 1 << MAX_BITS
PORT = 18861
SUCC_COUNT = 2
STABILIZATION_DELAY = 3
FIX_FINGERS_DELAY = 5
REPLICATION_DELAY = 7
CHECK_REPLICAS_DELAY = 8
UPDATE_SUCCESSORS_DELAY = 4
RETRY_ON_FAILURE_TIMES = 3
RETRY_ON_FAILURE_DELAY = 1

PROTOCOLS = {
    'PUB/SUB': 1,
    'CONFIG': 2,
    'RPC': 3,
    'DATA': 4
}
TOPICS = {
    'REGISTER': 1,
    'LOGIN': 2,
    'PUBLICATION': 3,
    'SUBSCRIPTION': 4,
    'UNSUBSCRIPTION': 5,
    'CMD': 6,
    'ANSWER': 7,
    'CREATE': 8
}
