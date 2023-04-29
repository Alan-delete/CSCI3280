import os
import os.path as osp
import time
import tkinter
import tkinter as tk
from tkinter import filedialog
import threading
import pygame
import random

import DataBase.mysql

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



class MusicPlayer:
    def __init__(self, root):
        self.root = root

        # tkinter variable object that shows music list
        self.List_var = tkinter.StringVar()
        lb = tkinter.Listbox(root,listvariable=self.List_var)
        lb.bind('<<ListboxSelect>>', self.List_on_select)

        # folder to store the music 
        self.folder ='./'

        # res to store the list of music, in the dictionary form
        self.res = []

        # current selected music idx
        self.cur_idx = 0


        # Connect to the local database
        self.db = DataBase.mysql.my_Database(host = HOST,user= USER, password= PASSWORD, database= DATABASE)

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

        # Add
        buttonChoose = tkinter.Button(root,text='ADD',command=self.add_music)

        # PLAY
        self.pause_resume = tkinter.StringVar(root,value='PLAY')
        buttonPlay = tkinter.Button(root,textvariable=self.pause_resume,command=self.play_music)
        buttonPlay['state'] = 'normal'
        

        # END
        buttonStop = tkinter.Button(root, text='STOP',command=self.stop_music)
        buttonStop['state'] = 'normal'

        # NEXT
        buttonNext = tkinter.Button(root, text='NEXT',command=self.switch_nxt)
        buttonNext['state'] = 'normal'
        
        # PREV
        buttonPrev = tkinter.Button(root, text='PREV',command=self.switch_pre)
        buttonPrev['state'] = 'normal'

        # DELETE
        buttonDelete = tkinter.Button(root, text='DELETE',command=self.delete_music)
        buttonDelete['state'] = 'normal'


        # Label
        self.musicName = tkinter.StringVar(root, value='Current No music played')
        labelName = tkinter.Label(root, textvariable=self.musicName)
        labelName.place(x=10, y=30, width=260, height=20)

        # Volume control
        s = tkinter.Scale(root, label='Volume', from_=0, to=1, orient=tkinter.HORIZONTAL,
                        length=240, showvalue=1, tickinterval=2, resolution=0.1,command=self.control_voice)
        

        # search settings
        search_label = tkinter.Label(root, text="Search:")
        self.search_box = tkinter.Entry(root)
        search_button = tkinter.Button(root, text="Search", command=self.search_music)


        buttonChoose.place(x=50,y=10,width=50,height=20)
        buttonPlay.place(x=190,y=10,width=50,height=20)        
        buttonStop.place(x=120, y=10, width=50, height=20)  
        buttonNext.place(x=260, y=10, width=50, height=20)
        buttonPrev.place(x=330, y=10, width=50, height=20)        
        buttonDelete.place(x=390, y=10, width=50, height=20)
        s.place(x=50, y=50, width=200)
        lb.place(x=50,y=200,width=260,height=300)
        search_label.place(x=50, y=150, width=50)
        self.search_box.place(x=100, y=150, width=200)
        search_button.place(x=320, y=140, width=50)

        # search_label.grid(row=5, column=0, padx=10, pady=10, sticky="W")
        # self.search_box.grid(row=5, column=1, padx=10, pady=10)
        # search_button.grid(row=5, column=2, padx=10, pady=10)




        # buttonChoose.grid(row=0, column=0, padx=5, pady=5)
        # buttonPlay.grid(row=0, column=1, padx=5, pady=5)
        # buttonStop.grid(row=0, column=2, padx=5, pady=5)
        # buttonNext.grid(row=1, column=0, padx=10, pady=10)
        # buttonPrev.grid(row=1, column=1, columnspan=2, padx=10, pady=10)
        # buttonDelete.grid(row=1, column=2, padx=10, pady=10)
        # labelName.grid(row=2, column=0, padx=10, pady=10)
        # s.grid(row=3, column=0, padx=10, pady=10)
        # lb.grid(row=4, column=0, padx=100, pady=100)

        show_list_thread = threading.Thread(target= self.fetch_show, daemon = True)
        show_list_thread.start()

        self.t = None 
        root.mainloop()

    def search_music(self):
        search_term = self.search_box.get()
        # find music in the database and then play
        # select_query = f"SELECT * FROM music WHERE title LIKE '%{search_term}%'"
        # self.cursor.execute(select_query)
        # result = self.cursor.fetchone()
        # if result:
        #     music_title = result[1]
        #     music_path = result[2].replace("\\'", "'")
        #     self.music_file = music_path
        #     pygame.mixer.music.load(self.music_file)
        #     pygame.mixer.music.play()
        # this place to search
    
    def open_music(self):
         self.music_file = filedialog.askopenfilename()
         pygame.mixer.music.load(self.music_file)
         # insert music file from database
         music_title = self.music_file.split("/")[-1]
         music_path = self.music_file.replace("'", "\\'")
         insert_query = f"INSERT INTO music (title, path) VALUES ('{music_title}', '{music_path}');"
        #  self.cursor.execute(insert_query)
        #  self.cnx.commit()




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
            name = tail.replace(".wav", "")

            row = {"name": name, "time":"4:00"}
            d = MyDialog(self.root, self.ATTRIBUTES)

            if (d.success):
                for key in d.result:
                    row[key] = d.result[key]
                
                # ask if there is lyrics file, if yes, store it with the same name + ".txt"
                lyrics_file = tkinter.filedialog.askopenfile(title="Music lyrics")
                if (lyrics_file):
                    with open(osp.join(self.folder, row['name']+ ".txt" ), 'w+') as f:
                        f.write(lyrics_file.read())

                # create unique file name to store
                row['location'] = osp.join(self.folder, str(random.randint(1,1e9)) +"_"+ row['name'] )
                if (not row['location'].endswith(".wav") ): row['location'] += ".wav"
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
                

                

    def List_on_select(self, evt):
        w = evt.widget
        self.pause_resume.set('PLAY')
        index = int(w.curselection()[0])
        print('You selected item %d' % (index))
        self.cur_idx = index


    # should be run on the thread
    def fetch_show(self):

        self.playing = True

        self.pause_resume.set('PLAY')

        while (True): 
            # should also gather information from other computers!
            self.res = self.db.select()

            ret = [i["name"] for i in self.res]
            self.List_var.set(ret)
            time.sleep(1)


    def play(self):

        if len(self.res):
            pygame.mixer.init()
            if not pygame.mixer.music.get_busy():
                netxMusic = self.res[self.cur_idx]['location']
                if (netxMusic):
                    pygame.mixer.music.load(netxMusic.encode())
                    # PLAY
                    pygame.mixer.music.play(1)
                    #netxMusic = netxMusic.split('\\')[1:]
                    self.musicName.set('playing "'+ self.res[self.cur_idx]['name'] + '"')
                else:
                    # here download and play music from other compurers 
                    print("music not found")
                    return 

            while self.playing:
                time.sleep(0.1)
            pygame.mixer.music.stop()

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
        



    def play_music(self):

        if self.pause_resume.get() == 'PLAY':
            self.pause_resume.set('PAUSE')
            self.playing = True
            self.t = threading.Thread(target=self.play)
            self.t.start()

        elif self.pause_resume.get() == 'PAUSE':
            # pygame.mixer.init()
            pygame.mixer.music.pause()

            self.pause_resume.set('CONTINUE')

        elif self.pause_resume.get() == 'CONTINUE':
            # pygame.mixer.init()
            pygame.mixer.music.unpause()

            self.pause_resume.set('PAUSE')




    def stop_music(self):
        self.playing = False
        self.musicName.set("Current No music played")
        self.pause_resume.set('PLAY')
        if (self.t):
            self.t.join()
            self.t = None


    def switch_nxt(self):

        self.stop_music()

        if len(self.res) -1 == self.cur_idx:
            self.cur_idx = 0
        else:
            self.cur_idx += 1

        self.playing = True
        self.pause_resume.set('PAUSE')
        self.t = threading.Thread(target=self.play)
        self.t.start()


    def closeWindow(self):
        self.stop_music()

        try:
            pygame.mixer.quit()
        except:
            pass

        self.root.destroy()
        self.db.close()


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
        self.pause_resume.set('PAUSE')
        self.t = threading.Thread(target=self.play)
        self.t.start()
        
if __name__ == "__main__":
    #root = tk.Tk()
    #root.geometry("400x300")  # resize the window
    root = tkinter.Tk()
    root.title('Music Player')
    root.geometry('460x600+500+100')
    #root.geometry("400x300")
    #root.resizable(False,False) 

    app = MusicPlayer(root)

