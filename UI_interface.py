import os
import os.path as osp
import time
import tkinter
import tkinter.filedialog
import threading
import pygame
import random

import DataBase.mysql

HOST = 'localhost'
USER = 'csci3280'
PASSWORD = 'csci3280'
DATABASE = 'project'

root = tkinter.Tk()
root.title('Music Player')
root.geometry('460x600+500+100')
root.resizable(False,False) 

# tkinter variable object that shows music list
List_var = None

# folder to store the music 
folder ='./'

# res to store the list of music, in the dictionary form
res = []

# current selected music idx
cur_idx = 0

now_music = ''

# Connect to the local database
db = DataBase.mysql.my_Database(host = HOST,user= USER, password= PASSWORD, database= DATABASE)

# get attributes information
cursor = db.conn.cursor()
cursor.execute("DESC music")   
attr_record = cursor.fetchall()
ATTRIBUTES = {attr[0] :attr[1] for attr in attr_record}
# This is important to read the latest committed data
cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
db.conn.commit()
cursor.close()



class MyDialog(tkinter.simpledialog.Dialog):

    def body(self, master):

        self.entries = []
        self.result = {}
        self.success = False
        for idx, key in enumerate(ATTRIBUTES):
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
        for idx, key in enumerate(ATTRIBUTES):
            val = self.entries[idx].get()
            if (val != ""):
                self.result[key] = val
        return 


def buttonAddClick():
    """
    Add music 
    :return:
    """

    # Get the files
    files = tkinter.filedialog.askopenfilenames()
    
    # Get the names
    musics = [music for music in files
                if music.endswith(('.mp3','.wav','.ogg'))]

    if len(musics) == 0:
        return

    for music in musics:
        _, tail = osp.split(music)

        row = {"name": tail, "time":"4:00"}
        d = MyDialog(root)

        if (d.success):
            for key in d.result:
                row[key] = d.result[key]
            # create unique file name to store
            row['location'] = osp.join(folder, str(random.randint(1,1e9)) +"_"+ row['name'] )
            if (not row['location'].endswith(".wav") ): row['location'] += ".wav"
            # add the file to the target location 
            
            if (db.insert_or_update(row)):
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
            

            

def List_on_select(evt):
    global cur_idx
    w = evt.widget
    index = int(w.curselection()[0])
    print('You selected item %d' % (index))
    cur_idx = index
    buttonDelete['state'] = 'normal'

# should be run on the thread
def Fetch_Show():

    global res
    global List_var

    global playing
    playing = True
    # Enable buttons
    buttonPlay['state'] = 'normal'
    buttonStop['state'] = 'normal'
    # buttonPause['state'] = 'normal'
    pause_resume.set('PLAY')

    while (True): 
        # should also gather information from other computers!
        res = db.select()
        ret = [i["name"] for i in res]

        if (List_var):
            List_var.set(ret)
        else:
            List_var = tkinter.StringVar()
            List_var.set(ret)
            lb = tkinter.Listbox(root,listvariable=List_var)
            lb.place(x=50,y=150,width=260,height=300)
            lb.bind('<<ListboxSelect>>', List_on_select)
        time.sleep(1)


def play():
    """
    PLAY音乐
    :return:
    """ 
    global cur_idx
    if len(res):
        pygame.mixer.init()
        while playing:
            if not pygame.mixer.music.get_busy():
                netxMusic = res[cur_idx]['location']
                if (netxMusic):
                    pygame.mixer.music.load(netxMusic.encode())
                    # PLAY
                    pygame.mixer.music.play(1)
                    #netxMusic = netxMusic.split('\\')[1:]
                    musicName.set('playing......'+ res[cur_idx]['name'] )
                else:
                    # here download and play music from other compurers 

                    print("music not found")
                
            else:
                time.sleep(0.1)

# delete the current selected song
def buttonDeleteClick():
    global cur_idx
    global res
    global playing
    playing = False


    time.sleep(0.5)
    try:
        os.remove(res[cur_idx]['location'])
        db.delete(id = res[cur_idx]['id'])
    except:
        print("Fail to delete")
        

    if len(res) -1 == cur_idx:
        cur_idx = 0
    else:
        cur_idx = cur_idx + 1
    



def buttonPlayClick():
    """
    点击PLAY
    :return:
    """
    global playing
    buttonNext['state'] = 'normal'

    buttonPrev['state'] = 'normal'

    if pause_resume.get() == 'PLAY':
        pause_resume.set('STOP')
        playing = True

        t = threading.Thread(target=play)
        t.start()

    elif pause_resume.get() == 'STOP':
        # pygame.mixer.init()
        pygame.mixer.music.pause()

        pause_resume.set('CONTINUE')

    elif pause_resume.get() == 'CONTINUE':
        # pygame.mixer.init()
        pygame.mixer.music.unpause()

        pause_resume.set('STOP')




def buttonStopClick():
    """
    STOPPLAY
    :return:
    """
    global playing
    playing = False
    pygame.mixer.music.stop()


def buttonNextClick():
    """
    NEXT
    :return:
    """
    global playing
    playing = False
    pygame.mixer.music.stop()
    global cur_idx
    if len(res) -1 == cur_idx:
        cur_idx = 0
    else:
        cur_idx = cur_idx + 1

    playing = True

    t = threading.Thread(target=play)
    t.start()


def closeWindow():
    """
    关闭窗口
    :return:
    """

    global playing

    playing = False

    time.sleep(0.3)

    try:

        pygame.mixer.music.stop()

        pygame.mixer.quit()

    except:

        pass

    root.destroy()
    db.close()


def control_voice(value=0.5):
    """
    :param value: 0.0-1.0
    :return:
    """
    pygame.mixer.music.set_volume(float(value))


def buttonPrevClick():
    """
    PREV
    :return:
    """
    global playing

    playing = False

    pygame.mixer.music.stop()
    #
    # pygame.mixer.quit()
    global cur_idx
    # cur_idx += 1
    # cur_idx -= 1
    if cur_idx == 0:
        cur_idx = len(res) - 2
        # cur_idx -= 1
    elif cur_idx == len(res) - 1:
        cur_idx -= 2
    else:
        cur_idx -= 2
        # cur_idx -= 1


    playing = True
    t = threading.Thread(target=play)
    t.start()

if __name__ == "__main__":

    # The callback of closing 
    root.protocol('WM_DELETE_WINDOW', closeWindow)

    # Add
    buttonChoose = tkinter.Button(root,text='ADD',command=buttonAddClick)
    
    # Layout
    buttonChoose.place(x=50,y=10,width=50,height=20)

    # PLAY
    pause_resume = tkinter.StringVar(root,value='PLAY')
    buttonPlay = tkinter.Button(root,textvariable=pause_resume,command=buttonPlayClick)
    buttonPlay.place(x=190,y=10,width=50,height=20)
    buttonPlay['state'] = 'disabled'


    # END
    buttonStop = tkinter.Button(root, text='STOP',command=buttonStopClick)
    buttonStop.place(x=120, y=10, width=50, height=20)
    buttonStop['state'] = 'disabled'

    # NEXT
    buttonNext = tkinter.Button(root, text='NEXT',command=buttonNextClick)
    buttonNext.place(x=260, y=10, width=50, height=20)
    buttonNext['state'] = 'disabled'
    
    # PREV
    buttonPrev = tkinter.Button(root, text='PREV',command=buttonPrevClick)
    buttonPrev.place(x=330, y=10, width=50, height=20)
    buttonPrev['state'] = 'disabled'

    # DELETE
    buttonDelete = tkinter.Button(root, text='DELETE',command=buttonDeleteClick)
    buttonDelete.place(x=390, y=10, width=50, height=20)
    buttonDelete['state'] = 'disabled'


    # Label
    musicName = tkinter.StringVar(root, value='Current No music played')
    labelName = tkinter.Label(root, textvariable=musicName)
    labelName.place(x=10, y=30, width=260, height=20)

    # Volume control
    s = tkinter.Scale(root, label='Volume', from_=0, to=1, orient=tkinter.HORIZONTAL,
                    length=240, showvalue=1, tickinterval=2, resolution=0.1,command=control_voice)
    s.place(x=50, y=50, width=200)


    show_list_thread = threading.Thread(target= Fetch_Show, daemon = True)
    show_list_thread.start()

    # 显示
    root.mainloop()


