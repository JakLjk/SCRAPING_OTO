
from .webhook import init_server as __init_server

def start_server():
    serv = __init_server()
    serv.run(host="0.0.0.0", debug=True)