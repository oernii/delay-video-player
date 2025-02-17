import tkinter as tk
from tkinter import ttk
import cv2
from threading import Thread
import time
import os
import importlib
import configparser
import pprint

class VideoCaptureWidget:
    def __init__(self, video_source, label):
        self.video_source = video_source
        self.label = label
        self.cap = cv2.VideoCapture(video_source)
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            self.thread = Thread(target=self.update, daemon=True)
            self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            self.thread.join()
        self.cap.release()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                img = cv2.resize(img, (320, 240))
                self.photo = tk.PhotoImage(data=cv2.imencode('.png', img)[1].tobytes())
                self.label.config(image=self.photo)
            time.sleep(0.01)

def select_device(device_variable, video_widget):
    device = device_variable.get()
    video_widget.stop()
    video_widget.cap = cv2.VideoCapture(device)  # Support both video files and device IDs
    video_widget.start()

def run_another_script():
    try:
        import another_script  # Import the script
        importlib.reload(another_script)  # Reload in case it was already imported
    except ModuleNotFoundError:
        print("run.py not found.")
    except Exception as e:
        print(f"Error running run.py: {e}")

def save_config_and_run(cam1, cam2, num1, num2):
    config = configparser.ConfigParser()

    config['Settings'] = {
        'cam1': cam1,
        'cam2': cam2
    }

    config_dir = os.path.join(os.path.expanduser('~'), '.config')
    config_file_path = os.path.join(config_dir, 'kamera.conf')

    if os.path.exists(config_file_path):
        config.read(config_file_path)

    with open(config_file_path, 'w') as configfile:
        config.write(configfile)

    print("Configuration saved.")
    run_another_script()

def load_config():
    config = configparser.ConfigParser(interpolation=None)
    config['Settings'] = {
        "cam1": "/dev/video0",
        "cam2": "/dev/video2",
        "delay1": "10",
        "delay2": "10"
    }

    config_dir = os.path.join(os.path.expanduser('~'), '.config')
    config_file_path = os.path.join(config_dir, 'kamera.conf')

    if os.path.exists(config_file_path):
        config.read(config_file_path)
    return config

def create_gui():
    config = load_config()
    # print(config)
    # pprint.pprint(config)
    # pprint.pprint(dict(config))
    # for section in config.sections():
    #     print(f"[{section}]")
    #     for key, value in config.items(section):
    #         print(f"{key} = {value}")
    #     print()
    # exit(1)

    root = tk.Tk()
    root.title("Video Device Selector")

    # Device dropdowns or file paths
    cam1_var = tk.StringVar(value=config.get('Settings', 'cam1'))
    cam2_var = tk.StringVar(value=config.get('Settings', 'cam2'))
    devices = [f"/dev/video{i}" for i in [0,0,1,2,3,4,5,6,7]]
    #devices = [f"/dev/video{i}" for i in range(0,5) if os.path.exists(f"/dev/video{i}")]

    ttk.Label(root, text="Select Device 1 or File:").grid(row=0, column=0, padx=5, pady=5)
    cam1_menu = ttk.OptionMenu(root, cam1_var, *devices)
    cam1_menu.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(root, text="Select Device 2 or File:").grid(row=1, column=0, padx=5, pady=5)
    cam2_menu = ttk.OptionMenu(root, cam2_var, *devices)
    cam2_menu.grid(row=1, column=1, padx=5, pady=5)

    # Video preview labels
    label1 = tk.Label(root)
    label1.grid(row=2, column=0, padx=5, pady=5)

    label2 = tk.Label(root)
    label2.grid(row=2, column=1, padx=5, pady=5)

    # Number inputs
    ttk.Label(root, text="Enter DELAY 1:").grid(row=3, column=0, padx=5, pady=5)
    delay1_entry = ttk.Entry(root)
    delay1_entry.insert(0, config.get('Settings', 'delay1'))
    delay1_entry.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(root, text="Enter DELAY 2:").grid(row=4, column=0, padx=5, pady=5)
    delay2_entry = ttk.Entry(root)
    delay2_entry.insert(0, config.get('Settings', 'delay2'))
    delay2_entry.grid(row=4, column=1, padx=5, pady=5)

    # Video widgets
    video1 = VideoCaptureWidget(cam1_var.get(), label1)
    video2 = VideoCaptureWidget(cam2_var.get(), label2)

    # Start videos
    video1.start()
    video2.start()

    # Update video sources on selection change
    cam1_var.trace("w", lambda *args: select_device(cam1_var, video1))
    cam2_var.trace("w", lambda *args: select_device(cam2_var, video2))

    # Buttons
    ttk.Button(root, text="Save/Run", command=lambda: save_config_and_run(
        cam1_var.get(), cam2_var.get(), delay1_entry.get(), delay2_entry.get())
    ).grid(row=5, column=0, padx=5, pady=5)

    ttk.Button(root, text="Exit", command=lambda: (video1.stop(), video2.stop(), root.destroy())
    ).grid(row=5, column=1, padx=5, pady=5)

    root.protocol("WM_DELETE_WINDOW", lambda: (video1.stop(), video2.stop(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    create_gui()

