 #This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


#def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
 #   print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
 #   print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
# 导入
# 导入
import os
import os.path as osp
import time
import tkinter
import tkinter.filedialog
import threading
import pygame
import random

import DataBase.mysql


root = tkinter.Tk()
root.title('音乐播放器')
root.geometry('460x600+500+100')
root.resizable(False,False)  # 不能拉伸

# tkinter variable object that shows music list
List_var = None

# folder to store the music 
folder ='./'

# res to store the list of music
res = []

# current music idx
cur_idx = 0

now_music = ''


db = DataBase.mysql.my_Database()

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
    files = tkinter.filedialog.askopenfilenames()
    
    musics = [music for music in files
                if music.endswith(('.mp3','.wav','.ogg'))]

    if len(musics) == 0:
        return

    for music in musics:
        _, tail = osp.split(music)
        #new_window = tkinter().Tk()
        d = MyDialog(root)
        row = {"name": tail, "time":"4:00"}

        if (d.success):
            for key in d.result:
                row[key] = d.result[key]
            row['location'] = osp.join(folder, str(random.randint(1,1e9)) +"_"+ row['name'] )
            # add the file to the target location 
            try:
                with open(row['location'], 'wb+') as tar_f:
                    with open(music, "rb") as ori_f:
                        tar_f.write(ori_f.read())
            except:
                print("Fail to add file")
                os.remove(row['location'])

            #row['location'] = music
            db.insert_or_update(row)

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
    # 根据情况禁用和启用相应的按钮
    buttonPlay['state'] = 'normal'
    buttonStop['state'] = 'normal'
    # buttonPause['state'] = 'normal'
    pause_resume.set('播放')

    while (True):
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
    播放音乐
    :return:
    """
    if len(res):
        pygame.mixer.init()
        global cur_idx
        while playing:
            if not pygame.mixer.music.get_busy():
                netxMusic = res[cur_idx]['location']
                if (netxMusic):
                    pygame.mixer.music.load(netxMusic.encode())
                    # 播放
                    pygame.mixer.music.play(1)
                    #netxMusic = netxMusic.split('\\')[1:]
                    musicName.set('playing......'+ res[cur_idx]['name'] )
                else:
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
        pass

    if len(res) -1 == cur_idx:
        cur_idx = 0
    else:
        cur_idx = cur_idx + 1
    



def buttonPlayClick():
    """
    点击播放
    :return:
    """
    buttonNext['state'] = 'normal'

    buttonPrev['state'] = 'normal'
    # 选择要播放的音乐文件夹
    if pause_resume.get() == '播放':
        pause_resume.set('暂停')
        global folder

        if not folder:
            folder = tkinter.filedialog.askdirectory()

        if not folder:
            return

        global playing

        playing = True

        # 创建一个线程来播放音乐，当前主线程用来接收用户操作
        t = threading.Thread(target=play)
        t.start()

    elif pause_resume.get() == '暂停':
        # pygame.mixer.init()
        pygame.mixer.music.pause()

        pause_resume.set('继续')

    elif pause_resume.get() == '继续':
        # pygame.mixer.init()
        pygame.mixer.music.unpause()

        pause_resume.set('暂停')




def buttonStopClick():
    """
    停止播放
    :return:
    """
    global playing
    playing = False
    pygame.mixer.music.stop()


def buttonNextClick():
    """
    下一首
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
    # 创建线程播放音乐,主线程用来接收用户操作
    t = threading.Thread(target=play)
    t.start()


def closeWindow():
    """
    关闭窗口
    :return:
    """
    # 修改变量，结束线程中的循环

    global playing

    playing = False

    time.sleep(0.3)

    try:

        # 停止播放，如果已停止，

        # 再次停止时会抛出异常，所以放在异常处理结构中

        pygame.mixer.music.stop()

        pygame.mixer.quit()

    except:

        pass

    root.destroy()
    db.close()


def control_voice(value=0.5):
    """
    声音控制
    :param value: 0.0-1.0
    :return:
    """
    pygame.mixer.music.set_volume(float(value))


def buttonPrevClick():
    """
    上一首
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
    print(cur_idx)

    playing = True

    # 创建一个线程来播放音乐，当前主线程用来接收用户操作

    t = threading.Thread(target=play)
    t.start()


# 窗口关闭
root.protocol('WM_DELETE_WINDOW', closeWindow)

# 添加按钮
#buttonChoose = tkinter.Button(root,text='添加',command=buttonChooseClick)
buttonChoose = tkinter.Button(root,text='添加',command=buttonAddClick)
# 布局
buttonChoose.place(x=50,y=10,width=50,height=20)

# 播放按钮
pause_resume = tkinter.StringVar(root,value='播放')
buttonPlay = tkinter.Button(root,textvariable=pause_resume,command=buttonPlayClick)
buttonPlay.place(x=190,y=10,width=50,height=20)
buttonPlay['state'] = 'disabled'


# 停止按钮
buttonStop = tkinter.Button(root, text='停止',command=buttonStopClick)
buttonStop.place(x=120, y=10, width=50, height=20)
buttonStop['state'] = 'disabled'

# 下一首
buttonNext = tkinter.Button(root, text='下一首',command=buttonNextClick)
buttonNext.place(x=260, y=10, width=50, height=20)
buttonNext['state'] = 'disabled'
# 上一首
buttonPrev = tkinter.Button(root, text='上一首',command=buttonPrevClick)
buttonPrev.place(x=330, y=10, width=50, height=20)
buttonPrev['state'] = 'disabled'

# Delete
buttonDelete = tkinter.Button(root, text='Delete',command=buttonDeleteClick)
buttonDelete.place(x=390, y=10, width=50, height=20)
buttonDelete['state'] = 'disabled'


# 标签
musicName = tkinter.StringVar(root, value='暂时没有播放音乐...')
labelName = tkinter.Label(root, textvariable=musicName)
labelName.place(x=10, y=30, width=260, height=20)

# 音量控制
s = tkinter.Scale(root, label='音量', from_=0, to=1, orient=tkinter.HORIZONTAL,
                  length=240, showvalue=0, tickinterval=2, resolution=0.1,command=control_voice)
s.place(x=50, y=50, width=200)


show_list_thread = threading.Thread(target= Fetch_Show, daemon = True)
show_list_thread.start()

# 显示
root.mainloop()


