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
import configparser

def config(file_path='kamera.conf'):
    config_path = os.path.expanduser(f'~/.config/{file_path}')
    config = configparser.RawConfigParser()
    
    if os.path.exists(config_path):
        config.read(config_path)
        print("Config file " + file_path + " found. Settings:" + str(config))
    else:
        print("Config file " + file_path + " NOT found")
    
    settings = {
        'cam1': config.get('Settings', 'cam1', fallback='/dev/video0'),
        'cam2': config.get('Settings', 'cam2', fallback='/dev/video2'),
        'rotation1': config.get('Settings', 'rotation1', fallback='90'),
        'rotation2': config.get('Settings', 'rotation2', fallback='90'),
        'delay1': config.get('Settings', 'delay1', fallback='2'),
        'delay2': config.get('Settings', 'delay2', fallback='4'),
        'height': config.get('Settings', 'height', fallback='100%'),
    }
    
    return settings

def main():
    kill_vlcs()
    settings = config()
    args = ["cvlc", "--no-video-title-show", "--extraintf", "rc", "--rc-host"]
    process1 = subprocess.Popen(args + ["localhost:8080", "--video-title", "kamera1", "v4l2://" + settings['cam1']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    args = ["cvlc", "--no-video-title-show", "--extraintf", "rc", "--rc-host"]
    process2 = subprocess.Popen(args + ["localhost:8081", "--video-title", "kamera2", "v4l2://" + settings['cam2']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(5)

    while True:
        window_id1 = check_window("kamera1")
        window_id2 = check_window("kamera2")
        if window_id1 and window_id2:
            print(f"Window '{window_id1}' and '{window_id2}' found ")
            break
        print("Waiting for VLC windows to be visible...")
        time.sleep(1)
    print("VLC windows are visible... pid1: " + str(process1.pid) + " , pid2: " + str(process2.pid))

    subprocess.run(["xdotool", "windowsize", window_id1, "100%", "50%"])
    subprocess.run(["xdotool", "windowmove", window_id1, "0", "0"])
    #subprocess.run(["xdotool", "windowsize", window_id1, "50%", settings['height']])

    time.sleep(1)
    subprocess.run(["xdotool", "windowsize", window_id2, "1050", "840"])
    subprocess.run(["xdotool", "windowmove", window_id2, "0", "840"])
    #subprocess.run(["xdotool", "windowsize", window_id2, "50%", settings['height']])

    time.sleep(3)

    delay_vlcs(float(settings['delay1']), float(settings['delay2']))

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

def delay_vlcs(delay1=4, delay2=4):
    netcat("localhost", 8080, "pause\n")
    netcat("localhost", 8081, "pause\n")
    time.sleep(min(delay1, delay2))
    netcat("localhost", 8080, "pause\n")
    time.sleep(abs(delay1 - delay2))
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

