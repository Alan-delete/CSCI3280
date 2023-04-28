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
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pygame
import mysql.connector

class MusicPlayer:
    def __init__(self, window):
         self.window = window
         self.window.title("Music Player")
         # player setting
         self.play_button = ttk.Button(window, text="Play", command=self.play_music)
         self.pause_button = ttk.Button(window, text="Pause", command=self.pause_music)
         self.stop_button = ttk.Button(window, text="Stop", command=self.stop_music)
         self.volume_label = ttk.Label(window, text="Volume:")
         self.volume_slider = ttk.Scale(window, from_=0, to=100, orient="horizontal", command=self.change_volume)

         # create table
         menubar = tk.Menu(window)
         self.window.config(menu=menubar)

         file_menu = tk.Menu(menubar)
         menubar.add_cascade(label="File", menu=file_menu)
         file_menu.add_command(label="Open", command=self.open_music)

         edit_menu = tk.Menu(menubar)
         menubar.add_cascade(label="Edit", menu=edit_menu)
         edit_menu.add_command(label="Search", command=self.search_music)

         # player settings
         self.play_button.grid(row=0, column=0, padx=10, pady=10)
         self.pause_button.grid(row=0, column=1, padx=10, pady=10)
         self.stop_button.grid(row=0, column=2, padx=10, pady=10)
         self.volume_label.grid(row=1, column=0, padx=10, pady=10)
         self.volume_slider.grid(row=1, column=1, columnspan=2, padx=10, pady=10)

         # search settings
         search_label = ttk.Label(window, text="Search:")
         self.search_box = ttk.Entry(window)
         search_button = ttk.Button(window, text="Search", command=self.search_music)
         search_label.grid(row=2, column=0, padx=10, pady=10, sticky="W")
         self.search_box.grid(row=2, column=1, padx=10, pady=10)
         search_button.grid(row=2, column=2, padx=10, pady=10)

         # initialize
         pygame.mixer.init()
         self.cnx = mysql.connector.connect(user='your_username', password='your_password', host='your_host',
                                            database='your_database')
         self.cursor = self.cnx.cursor()
         self.music_file = None
    def open_music(self):
         self.music_file = filedialog.askopenfilename()
         pygame.mixer.music.load(self.music_file)
         # insert music file from database
         music_title = self.music_file.split("/")[-1]
         music_path = self.music_file.replace("'", "\\'")
         insert_query = f"INSERT INTO music (title, path) VALUES ('{music_title}', '{music_path}');"
         self.cursor.execute(insert_query)
         self.cnx.commit()

    def play_music(self):
         if self.music_file:
             pygame.mixer.music.play()

    def pause_music(self):
         if self.music_file:
             pygame.mixer.music.pause()

    def stop_music(self):
         if self.music_file:
             pygame.mixer.music.stop()

    def change_volume(self, event):
         pygame.mixer.music.set_volume(self.volume_slider.get() / 100)

    def search_music(self):
         search_term = self.search_box.get()
         # find music in the database and then play
         select_query = f"SELECT * FROM music WHERE title LIKE '%{search_term}%'"
         self.cursor.execute(select_query)
         result = self.cursor.fetchone()
         if result:
             music_title = result[1]
             music_path = result[2].replace("\\'", "'")
             self.music_file = music_path
             pygame.mixer.music.load(self.music_file)
             pygame.mixer.music.play()
         # this place to search
root = tk.Tk()
root.geometry("400x300")  # resize the window
app = MusicPlayer(root)
root.mainloop()



