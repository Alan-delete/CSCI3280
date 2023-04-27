import socket

HOST = socket.gethostname()
PORT = 1600

def client_part():
    s = socket.socket()
    s.connect(((HOST, PORT)))
    print(s.recv(1024))
    s.close()


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    # here 10 is the maximun number of clients  
    server.listen(10)
    print("start server")

    while True:
        client, addr = server.accept()
        print( "connect to address:", addr)
        client.send('test'.encode())
        client.close()