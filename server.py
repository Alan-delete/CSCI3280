import socket

# DESKTOP-MHI4JFV
HOST = socket.gethostname()
HOSTIP = socket.gethostbyname(HOST)
PORT = 1600

def client_part():
    s = socket.socket()
    s.connect(((HOST, PORT)))
    print(s.recv(1024))
    s.close()


# new method using pythonp2p
from pythonp2p import Node

class Mynode(Node):
  # Maybe pass the reference of self.res and self.buffer as well 
  def __init__(self, host="", port=65432, file_port=65433, res = None):
      super().__init__(host, port, file_port)
      self.res = res
      

  def on_message(self, message, sender, private):
    # Gets called everytime there is a new message
    print("here is node", self.id)
    print("get information", message)

    if "type" not in message:
        return 

    if (message["type"] == "ask_inf"):
        # send the information to sender
        self.send_message({"type": "send_inf",
                           "data": self.res}, reciever=sender)
    
    elif(message["type"] == "send_inf"):
        # update the local res with the given data
        music_data = message["data"]

        local_music_names = set([ song["name"] for song in self.res])
        # update res or local database?
        # what if there are two songs with same name but different attributes?
        # So only "insert" but not update 
        for song in music_data:
            # without id information
            # only with unique name
            if (song["name"] not in local_music_names):
                del song["id"]
                self.res.append(song)

    elif(message["type"] == "ask_buffer"):
        music_name = message["name"]
        pass
    
    elif(message["type"] == "send_buffer"):
        # download and play the stream
        pass


    if (message["data"][1]==2):
        self.send_message({"data": [1,1,3]}, reciever=sender)
    
  
def test():

    fhash = ""
    #Empty string means '0.0.0.0' which means that program will bind to and receive requests from all NICs
    node0 = Mynode("", 65434)
    node1 = Mynode("", 65435)

    node0.start()
    node1.start()

    node0.connect_to("localhost", 65435)


    def test_node_connect():
        assert len(node0.nodes_connected) == 1
        assert len(node1.nodes_connected) == 1


    def test_node_message():
        node0.send_message({"data": [1,2,3]})
        #assert len(node1.msgs.keys()) == 1
        #assert len(node0.msgs.keys()) == 1


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
    test_node_message()
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