import socket
import os
import os.path as osp
import time 
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
    def __init__(self, host="", port=65432, file_port=65433, db = None):
        super().__init__(host, port, file_port)
        self.db = db 
        self._remote_res = []
        # {"music_name": [node that has that song]}
        self.record = {}
    
    @property
    def remote_res(self):
        return self._remote_res

    def clear_cache(self):
        self.record = {}

    def interleave(self, song, bound):
        ids = self.record[song["name"]]
        for idx, id in enumerate(ids):
            self.send_message({ "type": "ask_buffer",
                                "idx" : idx,
                                "total_idx": len(ids),
                                "bound" : bound,
                                "data": song }, 
                                reciever=id)

    def encryption_handler(self, dta):
        # if dta["rnid"] == self.id:
        #     dta["data"] = cf.decrypt(dta["data"], self.private_key)
        #     return dta
        # elif dta["rnid"] is None:
        #     return dta
        # else:
        #     return False
        return dta
    
    def send_message(self, data, reciever=None):
        # time that the message was sent
        #if reciever:
        #    data = cf.encrypt(data, cf.load_key(reciever))
        self.message("msg", data, {"rnid": reciever})



    def on_message(self, message, sender, private):
        # Gets called everytime there is a new message

        if "type" not in message:
            return 

        if (message["type"] == "ask_inf"):
            # send the information to sender
            local_music = self.db.select()
            self.send_message({"type": "send_inf",
                            "data": local_music} ) #, reciever=sender)
        
        elif (message["type"] == "send_inf"):

            # update the local res with the given data
            music_data = message["data"]
            local_music = self.db.select()
            local_music_names = set([ song["name"] for song in local_music])
            # update res or local database?
            # what if there are two songs with same name but different attributes?
            # So only "insert" but not update 
            for song in music_data:
                # without id information
                # only with unique name
                if (song["name"] not in local_music_names and song["name"] not in self.record):
                    song["id"] = -1
                    self.remote_res.append(song)
                
                # also record the node id of that song
                if (song["name"] not in self.record):
                    self.record[song["name"]] = set([sender])
                else:
                    self.record[song["name"]].add(sender)


        
        elif (message["type"] == "ask_buffer"):
            song = message["data"]
            idx = message["idx"]
            total_idx = message["total_idx"]
            low, high = message["bound"]
            with open(song["location"],"rb") as f:
                buffer = [ byte for i, byte in enumerate(f.read()[low:high]) if i%total_idx == idx]
            self.send_message({ "type": "send_buffer",
                                "buffer" : buffer,
                                "idx" : idx,
                                "total_idx": len(total_idx),
                                "data": song}) 
                               # reciever=sender)
            
        
        elif (message["type"] == "send_buffer"):
            # download and play the stream
            song = message["data"]
            idx = message["idx"]
            total_idx = message["total_idx"]
            buffer = message["buffer"]

            



        #if (message["data"][1]==2):
        #    self.send_message({"data": [1,1,3]}, reciever=sender)
        
  


class Demonode(Node):
    # Maybe pass the reference of self.res and self.buffer as well 
    def __init__(self, host="", port=65432, file_port=65433, db = None, res = None):
        super().__init__(host, port, file_port)
        self.db = db 
        self.res = res
        # {"music_name": [node that has that song]}
        self.record = {}

    def clear_cache(self):
        self.record = {}

    def interleave(self, song, bound):
        ids = self.record[song["name"]]
        for idx, id in enumerate(ids):
            self.send_message({ "type": "ask_buffer",
                                "idx" : idx,
                                "total_idx": len(ids),
                                "bound" : bound,
                                "data": song }, 
                                reciever=id)


    def on_message(self, message, sender, private):
        # Gets called everytime there is a new message


        if "type" not in message:
            return 

        if (message["type"] == "ask_inf"):
            # send the information to sender
            local_music = [{"id": 0, "name":"remote", "time":"4;00", "author":"someboady"}]
            self.send_message({"type": "send_inf",
                            "data": local_music})#, reciever=sender)
        
        elif (message["type"] == "send_inf"):
            # update the local res with the given data
            music_data = message["data"]
            local_music = self.db.select()
            local_music_names = set([ song["name"] for song in local_music])
            # update res or local database?
            # what if there are two songs with same name but different attributes?
            # So only "insert" but not update 
            for song in music_data:
                # without id information
                # only with unique name
                if (song["name"] not in local_music_names):
                    song["id"] = -1
                    self.res.append(song)
                
                # also record the node id of that song
                if (song["name"] not in self.record):
                    self.record[song["name"]] = set([sender])
                else:
                    self.record[song["name"]].add(sender)

        
        elif (message["type"] == "ask_buffer"):
            song = message["data"]
            idx = message["idx"]
            total_idx = message["total_idx"]
            low, high = message["bound"]
            with open(song["location"],"rb") as f:
                buffer = [ byte for i, byte in enumerate(f.read()[low:high]) if i%total_idx == idx]
            self.send_message({ "type": "send_buffer",
                                "buffer" : buffer,
                                "idx" : idx,
                                "total_idx": len(total_idx),
                                "data": song}, 
                                reciever=sender)
            pass
        
        elif (message["type"] == "send_buffer"):
            # download and play the stream
            song = message["data"]
            idx = message["idx"]
            total_idx = message["total_idx"]
            buffer = message["buffer"]

            pass



        #if (message["data"][1]==2):
        #    self.send_message({"data": [1,1,3]}, reciever=sender)


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
    # test()
    node0 = Demonode("", 65434)
    #node1 = Demonode("", 65435)


    node0.start()

    node0.connect_to("localhost", 65432)
    
    #node0.send_message({"type": "ask_inf"})
    time.sleep(20)
    node0.stop()
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