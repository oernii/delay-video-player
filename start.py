import tkinter as tk
from tkinter import ttk
import cv2
from threading import Thread
import time
import os
import importlib

class VideoCaptureWidget:
    def __init__(self, video_source, label):
        self.video_source = video_source
        self.label = label
        self.cap = cv2.VideoCapture(int(video_source[-1]))  # Extract the device number
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
    video_widget.cap = cv2.VideoCapture(int(device[-1]))  # Extract the device number
    video_widget.start()

def save_config_and_run(device1, device2, num1, num2):
    with open("config.txt", "w") as file:
        file.write(f"device1={device1}\n")
        file.write(f"device2={device2}\n")
        file.write(f"number1={num1}\n")
        file.write(f"number2={num2}\n")
    print("Configuration saved.")
    
    # Run another Python script within the same process
    run_another_script()

def run_another_script():
    try:
        import another_script  # Import the script
        importlib.reload(another_script)  # Reload in case it was already imported
    except ModuleNotFoundError:
        print("another_script.py not found.")
    except Exception as e:
        print(f"Error running another_script.py: {e}")

def load_config():
    config = {
        "device1": "/dev/video0",
        "device2": "/dev/video1",
        "number1": "0",
        "number2": "0"
    }
    if os.path.exists("config.txt"):
        with open("config.txt", "r") as file:
            for line in file:
                key, value = line.strip().split('=')
                config[key] = value
    return config

def create_gui():
    root = tk.Tk()
    root.title("Video Device Selector")

    config = load_config()

    # Device dropdowns
    device1_var = tk.StringVar(value=config["device1"])
    device2_var = tk.StringVar(value=config["device2"])
    devices = [f"/dev/video{i}" for i in range(5)]  # Assuming up to /dev/video4

    ttk.Label(root, text="Select Device 1:").grid(row=0, column=0, padx=5, pady=5)
    device1_menu = ttk.OptionMenu(root, device1_var, *devices)
    device1_menu.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(root, text="Select Device 2:").grid(row=1, column=0, padx=5, pady=5)
    device2_menu = ttk.OptionMenu(root, device2_var, *devices)
    device2_menu.grid(row=1, column=1, padx=5, pady=5)

    # Video preview labels
    label1 = tk.Label(root)
    label1.grid(row=2, column=0, padx=5, pady=5)

    label2 = tk.Label(root)
    label2.grid(row=2, column=1, padx=5, pady=5)

    # Number inputs
    ttk.Label(root, text="Enter Number 1:").grid(row=3, column=0, padx=5, pady=5)
    number1_entry = ttk.Entry(root)
    number1_entry.insert(0, config["number1"])
    number1_entry.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(root, text="Enter Number 2:").grid(row=4, column=0, padx=5, pady=5)
    number2_entry = ttk.Entry(root)
    number2_entry.insert(0, config["number2"])
    number2_entry.grid(row=4, column=1, padx=5, pady=5)

    # Video widgets
    video1 = VideoCaptureWidget(device1_var.get(), label1)
    video2 = VideoCaptureWidget(device2_var.get(), label2)

    # Start videos
    video1.start()
    video2.start()

    # Update video sources on selection change
    device1_var.trace("w", lambda *args: select_device(device1_var, video1))
    device2_var.trace("w", lambda *args: select_device(device2_var, video2))

    # Buttons
    ttk.Button(root, text="Save/Run", command=lambda: save_config_and_run(
        device1_var.get(), device2_var.get(), number1_entry.get(), number2_entry.get())
    ).grid(row=5, column=0, padx=5, pady=5)

    ttk.Button(root, text="Exit", command=lambda: (video1.stop(), video2.stop(), root.destroy())
    ).grid(row=5, column=1, padx=5, pady=5)

    root.protocol("WM_DELETE_WINDOW", lambda: (video1.stop(), video2.stop(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    create_gui()

