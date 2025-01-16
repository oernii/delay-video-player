import tkinter as tk
from tkinter import ttk
import cv2
from threading import Thread
import time

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
    video_widget.cap = cv2.VideoCapture(device)
    video_widget.start()

def create_gui():
    root = tk.Tk()
    root.title("Video Device Selector")

    # Device dropdowns
    device1_var = tk.StringVar(value="/dev/video0")
    device2_var = tk.StringVar(value="/dev/video1")
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

    # Video widgets
    video1 = VideoCaptureWidget(device1_var.get(), label1)
    video2 = VideoCaptureWidget(device2_var.get(), label2)

    # Start videos
    video1.start()
    video2.start()

    # Update video sources on selection change
    device1_var.trace("w", lambda *args: select_device(device1_var, video1))
    device2_var.trace("w", lambda *args: select_device(device2_var, video2))

    root.protocol("WM_DELETE_WINDOW", lambda: (video1.stop(), video2.stop(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    create_gui()

