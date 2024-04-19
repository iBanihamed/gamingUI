import os
import tkinter as tk
import subprocess
from tkinter import filedialog
from PIL import Image, ImageTk
from pygame import mixer

class GameLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Launcher")
        self.root.geometry("400x300")

        self.game_folder = ""
        self.games = []
        self.selected_game_index = None

        self.create_widgets()

        # Load up games to select from 
        self.game_folder = "./assets/cover_art"
        self.load_games()

    def create_widgets(self):
        # # Button to select game folder
        # self.select_folder_btn = tk.Button(self.root, text="Select Game Folder", command=self.select_folder)
        # self.select_folder_btn.pack(pady=10)

        # Frame to display game images
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(pady=10)

        # Button to launch selected game
        self.launch_btn = tk.Button(self.root, text="Launch Game", command=self.launch_game, state=tk.DISABLED)
        self.launch_btn.pack(pady=10)

    def select_folder(self):
        #self.game_folder = filedialog.askdirectory(title="Select Game Folder")
        self.game_folder = "./assets"
        self.load_games()
    
    def mount_dmg(self, dmg_path):
        try:
            # Mount the .dmg file
            mount_output = subprocess.check_output(['hdiutil', 'attach', '-mountpoint', '/Volumes/dmg_mount', dmg_path]).decode().strip()
            mountPoint = mount_output.split()[-1]
            print(f"Mounting successful! Mounted to {mountPoint}")
            return mountPoint  # Return the mount point
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

    def run_file_inside_dmg(self, application_path, file_path):
        try:
            print(f"Running game {file_path.split('/')[-1].split('.')[0]}")
            subprocess.run(["sudo" , "open", "-a", application_path, file_path])
            # Execute the file if it's an executable
            if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
                #subprocess.run([file_path], check=True)
                pass

            else:
                print("File is not executable.")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

    def load_games(self):
        self.games = []
        for filename in os.listdir(self.game_folder):
            if filename.endswith(".png") or filename.endswith(".jpg"):
                self.games.append(os.path.join(self.game_folder, filename))

        self.selected_game_index = None  # Reset selected game index
        self.display_games()

    def display_games(self):
        for widget in self.image_frame.winfo_children():
            widget.destroy()

        for index, game_path in enumerate(self.games):
            img = Image.open(game_path)
            img = img.resize((100, 100))
            img = ImageTk.PhotoImage(img)

            label = tk.Label(self.image_frame, image=img)
            label.image = img
            label.bind("<Button-1>", lambda event, idx=index: self.select_game(idx))
            label.pack(side=tk.LEFT, padx=10)

            # Highlight selected game with blue border
            if index == self.selected_game_index:
                label.config(borderwidth=3, relief="solid", highlightbackground="blue")
            else:
                label.config(borderwidth=0)

        if self.games:
            self.launch_btn.config(state=tk.NORMAL)
        else:
            self.launch_btn.config(state=tk.DISABLED)

    def select_game(self, index):
        self.selected_game_index = index
        self.display_games()
        selected_game = self.games[self.selected_game_index].split('/')[-1].split('.')[0]
        sound_byte = f'./assets/sounds/{selected_game}.mp3'
        self.play_sound(sound_byte)

    def play_sound(self, sound):
        # Load the sound file
        mixer.init()
        mixer.music.load(sound)
        mixer.music.play()


    def launch_game(self):
        if self.selected_game_index is not None:
            mixer.music.stop()
            gamePath = self.games[self.selected_game_index]
            gameName = gamePath.split('/')[-1].split('.')[0]
            print("Launching game: ", gameName)
            dmg_file = "./dolphin-emu.dmg"  # Replace with your .dmg file path

            # Mount the .dmg file
            mount_point = self.mount_dmg(dmg_file)

            # Path to the file inside the mounted disk image
            file_inside_dmg = os.path.join(mount_point, "Dolphin.app")

            # Run the file inside the mounted disk image
            self.run_file_inside_dmg(file_inside_dmg, f"./games/{gameName}.ciso")
        else:
            print("No game selected.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameLauncherApp(root)
    root.mainloop()
