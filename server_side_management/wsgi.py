from .webhook import init_server as __init_server

def start_server():
    serv = __init_server()
    serv.run()