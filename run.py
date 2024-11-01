#!/bin/python3
# vim: set expandtab tabstop=4 shiftwidth=4:
# Author: Ernest Beinrohr <Ernest@Beinrohr.sk> 2024
# License: GPL v2

import subprocess
import signal
import time
import os
import psutil
import socket


def main():
    kill_vlcs()
    args = ["cvlc", "--no-video-title-show", "--extraintf", "rc", "--video-filter=transform{type=\"90\"}", "--rc-host"]
    process1 = subprocess.Popen(args + ["localhost:8080", "--video-title", "video0", "v4l2:///dev/video0"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process2 = subprocess.Popen(args + ["localhost:8081", "--video-title", "video2","v4l2:///dev/video2"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(5)

    while True:
        window_id1 = check_window("video0")
        window_id2 = check_window("video2")
        if window_id1 and window_id2:
            print(f"Window '{window_id1}' and '{window_id2}' found ")
            break
        print("Waiting for VLC windows to be visible...")
        time.sleep(1)
    print("VLC windows are visible... pid1: " + str(process1.pid) + " , pid2: " + str(process2.pid))

    subprocess.run(["xdotool", "windowmove", window_id1, "0", "0"])
    subprocess.run(["xdotool", "windowsize", window_id1, "50%", "50%"])

    subprocess.run(["xdotool", "windowmove", window_id2, "50%", "0"])
    subprocess.run(["xdotool", "windowsize", window_id2, "50%", "50%"])


    delay_vlcs()

    try:
        while True:
            print(f"Process 1 running: {is_running(process1)}")
            print(f"Process 2 running: {is_running(process2)}")

            if not is_running(process1) and not is_running(process2):
                print("Both processes have ended.")
                break

            time.sleep(5)

    except KeyboardInterrupt:
        print("Interrupted by user. Cleaning up...")

        if is_running(process1):
            terminate_process_and_children(process1)
            #terminate_process(process1)
        if is_running(process2):
            terminate_process_and_children(process2)
            #terminate_process(process2)
        kill_vlcs()

def netcat(host, port, message):
    try:
        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            response = sock.recv(1024)
            print(f"Received from server: {response.decode('utf-8')}")
            time.sleep(1)
            sock.sendall(message.encode('utf-8'))
            response = sock.recv(1024)
            print(f"Received from server: {response.decode('utf-8')}")
    except Exception as e:
        print(f"An error occurred: {e}")

def delay_vlcs():
    netcat("localhost", 8080, "pause\n")
    netcat("localhost", 8081, "pause\n")
    time.sleep(4)
    netcat("localhost", 8080, "pause\n")
    netcat("localhost", 8081, "pause\n")

def kill_vlcs():
    subprocess.Popen(["pkill", "-9", "lvc"])

def check_window(window_name):
    try:
        output = subprocess.check_output(
            ["wmctrl", "-l"], text=True
        )
        for line in output.splitlines():
            if window_name in line:
                return line.split()[0]
    except subprocess.CalledProcessError:
        return False
    return False

def is_running(process):
    return process.poll() is None

# Function to terminate a process
def terminate_process(process):
    if is_running(process):
        process.terminate()
        print(f"Process {process.pid} terminated.")

def terminate_process_and_children(pid):
    """Terminate the specified process and all its child processes by PID."""
    try:
        # Get the process object for the given PID
        process = psutil.Process(pid)
        print(f"Terminating process with PID: {pid} and name: {process.name()}")
        
        # Terminate child processes recursively
        for child in process.children(recursive=True):
            print(f"Terminating child process with PID: {child.pid} and name: {child.name()}")
            child.terminate()  # You can use child.kill() for a forceful termination
            
        # Terminate the parent process
        process.terminate()  # You can use process.kill() for a forceful termination
        print(f"Process with PID: {pid} terminated successfully.")
        return True
    except psutil.NoSuchProcess:
        print(f"No process found with PID: {pid}.")
    except psutil.AccessDenied:
        print(f"Access denied to terminate process with PID: {pid}.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return False

main();

