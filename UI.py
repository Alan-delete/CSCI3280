import os
import os.path as osp
import time
import tkinter
import tkinter as tk
from tkinter import filedialog
import threading
import pygame
import random
import datetime

import wave
import DataBase.mysql
from server import Mynode
from audio_decoder import AudioDecoder
# from p2p_audio import AudioSplitter
# from p2p_images import ImageSplitter

HOST = 'localhost'
USER = 'csci3280'
PASSWORD = 'csci3280'
DATABASE = 'project'

Attributes = None

class MyDialog(tkinter.simpledialog.Dialog):

    def body(self, master):

        self.entries = []
        self.result = {}
        self.attributes =Attributes
        self.success = False
        for idx, key in enumerate(self.attributes):
            tkinter.Label(master, text=key).grid(row=idx)
            e = tkinter.Entry(master)
            e.grid(row=idx, column=1)
            self.entries.append(e)

        return self.entries[0] # initial focus

    # override the method when ok button is clicked 
    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()
        self.success = True

        try:
            self.apply()
        finally:
            self.cancel()

    def apply(self):
        for idx, key in enumerate(self.attributes):
            val = self.entries[idx].get()
            if (val != ""):
                self.result[key] = val
        return 



class UI:
    def __init__(self, root, db):
        self.root = root
        self.db = db

        # folder to store the music 
        self.folder ='./'

        # res to store the list of music, in the dictionary form
        self.res = []

        # set up the node with connection to database 
        self.node = Mynode(host="", port=65432, file_port=65433, db = self.db)
        self.node.start()
        #self.node.connect_to("10.13.80.177", 65432)

        # current selected music idx
        self.cur_idx = 0

        # get attributes information
        cursor = self.db.conn.cursor()
        cursor.execute("DESC music")   
        attr_record = cursor.fetchall()
        
        self.ATTRIBUTES = {attr[0] :attr[1] for attr in attr_record}
        global Attributes
        Attributes = self.ATTRIBUTES
        # This is important to read the latest committed data
        cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
        self.db.conn.commit()
        cursor.close()        
       
        # The callback of closing 
        root.protocol('WM_DELETE_WINDOW', self.closeWindow)

        # # search settings
        # search_label = tkinter.Label(root, text="Search:")
        # self.search_box = tkinter.Entry(root)
        # search_button = tkinter.Button(root, text="Search", command=self.search_music)

        # Create a search bar with a search button
        search_frame = tk.Frame(root, borderwidth=2, relief="raised", padx=10, pady=10)
        search_frame.pack(fill="x")
        self.search_input = tk.Entry(search_frame, width=50)
        self.search_input.pack(side=tk.LEFT, padx=10)
        search_button = tk.Button(search_frame, text="Search", padx=10,command=self.search_music)
        search_button.pack(side=tk.LEFT)
       
        # Create a list of music
        # tkinter variable object that shows music list
        self.List_var = tkinter.StringVar()
        #lb = tkinter.Listbox(root,listvariable=self.List_var)
        #lb.bind('<<ListboxSelect>>', self.List_on_select)
        music_frame = tk.Frame(root, borderwidth=2, relief="raised", padx=10, pady=10)
        music_frame.pack(fill="both", expand=True)
        music_list = tk.Listbox(music_frame, listvariable=self.List_var,width=50)
        music_list.bind('<<ListboxSelect>>', self.List_on_select)
        music_list.pack(fill="both", expand=True)

        # Create player controls with play, stop, next, and prev buttons
        controls_frame = tk.Frame(root, borderwidth=2, relief="raised", pady=10)
        controls_frame.pack(fill="x")
        self.pause_resume = tkinter.StringVar(root, value='Play')
        play_button = tk.Button(controls_frame, padx=10,command=self.play_music,textvariable=self.pause_resume)
        play_button.pack(side=tk.LEFT)
        stop_button = tk.Button(controls_frame, text="Stop", padx=10,command=self.stop_music)
        stop_button.pack(side=tk.LEFT)
        prev_button = tk.Button(controls_frame, text="<<", padx=10,command=self.switch_pre)
        prev_button.pack(side=tk.LEFT)
        next_button = tk.Button(controls_frame, text=">>", padx=10,command=self.switch_nxt)
        next_button.pack(side=tk.LEFT)
        add_button = tk.Button(controls_frame, text="Add", padx=10,command=self.add_music)
        add_button.pack(side=tk.LEFT)
        delete_button = tk.Button(controls_frame, text="Delete", padx=10,command=self.delete_music)
        delete_button.pack(side=tk.LEFT)


        # Create a volume slider
        volume_frame = tk.Frame(root, borderwidth=2, relief="raised", pady=10)
        volume_frame.pack(fill="x")
        volume_label = tk.Label(volume_frame, text="Volume:")
        volume_label.pack(side=tk.LEFT, padx=10)
        volume_slider = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=200,command=self.control_voice)
        volume_slider.pack(side=tk.LEFT, padx=10)

        # Create a progress bar
        progress_frame = tk.Frame(root, borderwidth=2, relief="raised", padx=10, pady=10)
        progress_frame.pack(fill="x")
        progress_bar = tk.Canvas(progress_frame, width=400, height=20, bg='white')
        progress_bar.pack(fill="x")

        # Create a lyrics display box
        lyrics_frame = tk.Frame(root, borderwidth=2, relief="raised", padx=10, pady=10)
        lyrics_frame.pack(fill="both", expand=True)
        lyrics_label = tk.Label(lyrics_frame, text="Lyrics:")
        lyrics_label.pack()
        self.lyrics_box = tk.Text(lyrics_frame, width=50, height=10)
        self.lyrics_box.pack(fill="both", expand=True)

        # Label
        self.musicName = tkinter.StringVar(root, value='Current No music played')
        labelName = tkinter.Label(root, textvariable=self.musicName)
        labelName.place(x=10, y=30, width=260, height=20)




        self.query = ""
        show_list_thread = threading.Thread(target= self.fetch_show, daemon = True)
        show_list_thread.start()

        self.t = None 
        root.mainloop()

    def search_music(self):
        search_term = self.search_input.get()
        self.query = search_term



    def edit_music(self):
        if (0 <= self.cur_idx < len(self.res)):
            id = self.res[self.cur_idx]["id"]
            d = MyDialog(self.root)
            if (d.success):
                for key in d.result:
                    self.res[self.cur_idx][key] = d.result[key]
                # keep the id
                self.res[self.cur_idx]["id"] = id 
                self.db.insert_or_update(self.res[self.cur_idx])
        else:
            tkinter.messagebox.showerror(title=None, message="Please choose a song to edit!")

    def add_music(self):
        # Get the files
        files = tkinter.filedialog.askopenfilenames(title="Music files")
        
        # Get the names
        musics = [music for music in files
                    if music.endswith(('.mp3','.wav','.ogg'))]

        if len(musics) == 0:
            return

        for music in musics:
            head, tail = osp.split(music)
            name = tail[:tail.rfind('.')]

            # get the length of music 
            with wave.open(music,'rb') as f:
                time = f.getnframes()/f.getframerate()

            row = {"name": name, "time":str(datetime.timedelta(seconds=time))}
            d = MyDialog(self.root)

            if (d.success):
                for key in d.result:
                    row[key] = d.result[key]
                
                # ask if there is lyrics file, if yes, store it with the same name + ".txt"
                lyrics_file = tkinter.filedialog.askopenfile(title="Music lyrics")
                if (lyrics_file):
                    with open(osp.join(self.folder, row['name']+ ".txt" ), 'w+') as f:
                        f.write(lyrics_file.read())

                # create unique file name to store
                # row['location'] = osp.join(self.folder, str(random.randint(1,1e9)) +"_"+ row['name'] )
                row['location'] = osp.join(self.folder,  tail )
                
                # add the file to the target location 
                if (self.db.insert_or_update(row)):
                    try:
                        with open(row['location'], 'wb+') as tar_f:
                            with open(music, "rb") as ori_f:
                                tar_f.write(ori_f.read())
                    except:
                        tkinter.messagebox.showerror(title=None, message="Fail to add file!")
                        os.remove(row['location'])
                else:
                    print("Please check if the information are correct!")
                    tkinter.messagebox.showerror(title=None, message="Please check if the information are correct!")
                

    # get the res from other connected nodes given the self.query
    def get_nodes_res(self):
        #res = [{"name":"red", "time":"4:00", "author":"s"}]
        self.node.send_message({"type": "ask_inf"})
        filtered_remote_res = []

        for remote_song in self.node.remote_res:
            if any([self.query in remote_song[key] for key in remote_song]):
               filtered_remote_res.append(remote_song)

        return filtered_remote_res


    def List_on_select(self, evt):
        w = evt.widget
        self.pause_resume.set('Play')
        index = int(w.curselection()[0])
        print('You selected item %d' % (index))
        self.cur_idx = index


    # should be run on the thread
    def fetch_show(self):

        self.playing = True

        self.pause_resume.set('Play')

        while (True): 
            # should also gather information from other computers!
            # self.res = self.db.select()
            self.res = list(self.db.query_by_all(self.query))
            other_res = self.get_nodes_res()
            # merge the res
            all_names = set([i["name"] for i in self.res])
            for other_song in other_res:
                if (other_song["name"] not in all_names):
                    self.res.append(other_song)
                    all_names.add(other_song["name"])


            ret = [ "{:^15} {:^15} {:^15}".format(i["name"], i["author"] if i["author"] else "None",str(i["time"])) for i in self.res ]
            #ret.insert(0,"{:^15} {:^15} {:^15}".format("Name", "Author", "Time"))
            self.List_var.set(ret)
            time.sleep(0.5)


    def p2p_play(self):
        message = {"type": "ask_buffer",
                   
                   "data": self.res[self.cur_idx],

                   "ids": self.node.record[self.res[self.cur_idx]["name"]]
                   }
        self.node.interleave(self.res[self.cur_idx])
        #print(message)
        pass

    
    def play(self):

        if len(self.res):
            netxMusic = self.res[self.cur_idx]['location']
            


            if not osp.exists(netxMusic):
                # here download and play music from other compurers
                self.p2p_play()
            
            elif (netxMusic):
                self.musicName.set('playing "'+ self.res[self.cur_idx]['name'] + '"')
                self.decoder = AudioDecoder(netxMusic)
                self.decoder.decode_and_init()
                # PLAY
                self.decoder.play_music(start_position = self.current_position)
                
            else: 
                print("music not found")
                return 

    # delete the current selected song
    def delete_music(self):
        self.stop_music()

        self.db.delete(id = self.res[self.cur_idx]['id'])
        try:
            os.remove(self.res[self.cur_idx]['location'])
        except:
            print("File already deleted")
            

        if len(self.res) -1 == self.cur_idx:
            self.cur_idx = 0
        else:
            self.cur_idx += 1
        
    def lyrics_display(self,name): #display the lyrics
        try:
            with open(name+'txt', 'r', encoding='UTF-8') as file: 
                content = file.read()
                self.lyrics_box.insert(tk.END, content)
        except:
            self.lyrics_box.insert(tk.END, "No lyrics")


    def play_music(self):

        if self.pause_resume.get() == 'Play':
            
            if self.playing:
                self.stop_music()
            
            name = self.res[self.cur_idx]["name"]
            self.lyrics_box.delete(1.0, tk.END) 
            self.lyrics_display(name)

            self.pause_resume.set('Pause')
            self.playing = True
            self.current_position=0

            self.t = threading.Thread(target=self.play,daemon=True)
            self.t.start()

        elif self.pause_resume.get() == 'Pause':
            # pygame.mixer.init()

            if self.playing and self.t:
                self.current_position = self.decoder.pw.block_count
                self.decoder.stop_music()
            
            self.pause_resume.set('Continue')

        elif self.pause_resume.get() == 'Continue':
            # pygame.mixer.init()
            #if self.t:
            #    if self.decoder:
            #        self.decoder.play_music(start_position = self.current_position)
            
            self.t = threading.Thread(target=self.play,daemon=True)
            self.t.start()
            
            self.pause_resume.set('Pause')



    # stop music and set the start position to 0
    def stop_music(self):
        self.playing = False
        self.musicName.set("Current No music played")
        self.pause_resume.set('Play')
        try:
            if(self.decoder):
                self.decoder.stop_music()
        except:
            print("exception from decode stop")
        
        if (self.t): self.t.join()
        
        self.current_position=0


    def switch_nxt(self):

        self.stop_music()

        if len(self.res) -1 == self.cur_idx:
            self.cur_idx = 0
        else:
            self.cur_idx += 1

        self.playing = True
        self.pause_resume.set('Pause')

        
        self.t = threading.Thread(target=self.play,daemon=True)
        self.t.start()


    def closeWindow(self):
        self.stop_music()

        self.root.destroy()
        self.db.close()
        self.node.stop()


    def control_voice(self,value=0.5):
        pygame.mixer.music.set_volume(float(value))


    def switch_pre(self):

        # stop the current song 
        self.stop_music()

        if self.cur_idx == 0:
            self.cur_idx = len(self.res) - 2

        else:
            self.cur_idx -= 1


        self.playing = True
        self.pause_resume.set('Pause')
        self.t = threading.Thread(target=self.play,daemon=True)
        self.t.start()
        
if __name__ == "__main__":
    # connect to the local database 
    db = DataBase.mysql.my_Database(host = HOST,user= USER, password= PASSWORD, database= DATABASE)
    #db = None
    root = tkinter.Tk()
    root.title('Music Player')
    root.geometry('460x600+500+100')
    app = UI(root, db)
