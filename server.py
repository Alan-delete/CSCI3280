import socket

# DESKTOP-MHI4JFV
HOST = socket.gethostname()
HOSTIP = socket.gethostbyname(HOST)
print(HOSTIP)
print(socket.gethostbyname("localhost"))
PORT = 1600

def client_part():
    s = socket.socket()
    s.connect(((HOST, PORT)))
    print(s.recv(1024))
    s.close()


# if __name__ == '__main__':
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.bind((HOST, PORT))
#     # here 10 is the maximun number of clients  
#     server.listen(10)
#     print("start server")

#     while True:
#         client, addr = server.accept()
#         print( "connect to address:", addr)
#         client.send('test'.encode())
#         client.close()

# new method using pythonp2p
from pythonp2p import Node

class Mynode(Node):
  def on_message(message, sender, private):
    # Gets called everytime there is a new message
    pass
  
def test():

    fhash = ""
    #Empty string means '0.0.0.0' which means that program will bind to and receive requests from all NICs
    node0 = Node("", 65434)
    node1 = Node("", 65435)

    node0.start()
    node1.start()
    print(node0.ip)
    print(node1.ip)

    #node0.connect_to(HOST, 65435)


    def test_node_connect():
        assert len(node0.nodes_connected) == 1
        assert len(node1.nodes_connected) == 1


    def test_node_message():
        node0.send_message("node test")
        assert len(node1.msgs.keys()) == 1
        assert len(node0.msgs.keys()) == 1


    def test_node_private_message():
        node0.send_message("TEST MESSAGE", reciever=node1.id)


    def test_files_add():
        global fhash
        fhash = node1.addfile("LICENSE")


    def test_file_request():
        node0.requestFile(fhash)
        print(node0.file_manager.getallfiles())
        assert len(node0.requested) == 1
        assert len(node1.msgs.keys()) == 2

    #test_node_connect()
    node0.stop()
    node1.stop()


if __name__ == "__main__":
    test()
    # node = Mynode(HOST, PORT)  # start the node
    # node.start()
    # print(node.id)
    # ip = HOST
    # port = PORT
    # node.connect_to(ip, port)
    # print(node.node_connected)
    # data = {}
    # try:
    #     node.send_message(data, receiver=None)
    # except:
    #     print("Wrong")