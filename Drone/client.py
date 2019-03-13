from __future__ import print_function
import sys
import socket
import struct
import random
import time
import errno
import threading
import ConfigParser
from contextlib import closing

import rospy

from FlightLib.FlightLib import FlightLib
from FlightLib.FlightLib import LedLib

import play_animation

random.seed()

NTP_PACKET_FORMAT = "!12I"
NTP_DELTA = 2208988800L # 1970-01-01 00:00:00
NTP_QUERY = '\x1b' + 47 * '\0'  


def get_ntp_time(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
        s.sendto(NTP_QUERY, (host, port))
        msg, address = s.recvfrom(1024)
    unpacked = struct.unpack(NTP_PACKET_FORMAT, msg[0:struct.calcsize(NTP_PACKET_FORMAT)])
    return unpacked[10] + float(unpacked[11]) / 2**32 - NTP_DELTA


def reconnect(t=2):
    global clientSocket, host, port
    print("Trying to connect to", host, ":", port, "...")
    connected = False
    attempt_count = 0
    while not connected:
        print("Waiting for connection, attempt", attempt_count)
        try:
            clientSocket = socket.socket()
            # clientSocket.settimeout(3)
            clientSocket.connect((host, port))
            connected = True
            print("Connection successful")
        except socket.error as e:
            print("Waiting for connection:", e)
            time.sleep(t)
        attempt_count +=1
        if attempt_count >= 15:
            print("Too many attempts. Trying to get new server IP")
            broadcst_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            broadcst_client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            broadcst_client.bind(("", 8181))
            while True:
                data, addr = broadcst_client.recvfrom(1024)
                print("Recieved broadcast message %s from %s"%(data, addr))
                if parse_command(data.decode("UTF-8"))[0] == "server_ip":
                    print("Binding to new IP: ", addr)
                    host, port = addr
                    broadcst_client.close()
                    break


def send_all(msg):
        clientSocket.sendall(struct.pack('>I', len(msg)) + msg)


def recive_all(n):
    data = b''
    while len(data) < n:
        packet = clientSocket.recv(min(n - len(data), BUFFER_SIZE))
        if not packet:
            return None
        data += packet
    return data


def recive_message():
    raw_msglen = recive_all(4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    msg = recive_all(msglen)
    return msg


def form_command(command, args=()):
        return " ".join([command, args])


def parse_command(command_input):
    args = command_input.split()
    command = args.pop(0)
    return command, args


def recive_file(filename):
    print("Reciving file:", filename)
    with open(filename, 'wb') as file:  # TODO add directory
        while True:
            data = recive_message() #clientSocket.recv(BUFFER_SIZE)
            if data:
                print(data)
                if parse_command(data.decode("UTF-8"))[0] == "/endoffile":
                    print("File recived")
                    break
                file.write(data)


def write_to_config(section, option, value):
    config.set(section, option, value)
    with open(CONFIG_PATH, 'w') as file:
        config.write(file)


def animation_player(running_event, stop_event):
    print("Animation thread activated")
    frames = play_animation.read_animation_file()
    rate = rospy.Rate(1000 / 125)
    play_animation.takeoff()
    play_animation.animate_frame(frames[0]) #Reach first point at the same time with others
    rospy.sleep(5)
    for frame in frames:
        running_event.wait()
        if stop_event.is_set():
            running_animation_event.clear()
            break

        play_animation.animate_frame(frame)
        rate.sleep()
    else:
        play_animation.land()
        print("Animation ended")
    print("Animation thread closed")


stop_animation_event = threading.Event()
running_animation_event = threading.Event()


def start_animation(*args, **kwargs):
    animation_thread = threading.Thread(target=animation_player, args=(running_animation_event, stop_animation_event))
    print("Starting animation!")
    running_animation_event.set()
    stop_animation_event.clear()
    animation_thread.start()


def resume_animation():
    print("Resuming animation")
    running_animation_event.set()


def pause_animation():
    print("Pausing animation")
    running_animation_event.clear()


def stop_animation():
    stop_animation_event.set()
    print("Stopping animation")
#    animation_thread.join()



CONFIG_PATH = "client_config.ini"
config = ConfigParser.ConfigParser()
config.read(CONFIG_PATH)


port = int(config.get('SERVER', 'port'))
host = config.get('SERVER', 'host')
BUFFER_SIZE = int(config.get('SERVER', 'buffer_size'))
NTP_HOST = config.get('NTP', 'host')
NTP_PORT = int(config.get('NTP', 'port'))

files_directory = config.get('FILETRANSFER', 'files_directory')
animation_file = config.get('COPTER', 'animation_file')

COPTER_ID = config.get('COPTER', 'id')
if COPTER_ID == 'default':
    COPTER_ID = 'copter' + str(random.randrange(9999)).zfill(4)
    write_to_config('COPTER', 'id', COPTER_ID)

TAKEOFF_HEIGHT = float(config.get('COPTER', 'takeoff_height'))

USE_LEDS = config.getboolean('COPTER', 'use_leds')
play_animation.USE_LEDS = USE_LEDS

rospy.init_node('Swarm_client', anonymous=True)
if USE_LEDS:
    LedLib.init_led()

print("Client started on copter:", COPTER_ID)
print("NTP time:", time.ctime(get_ntp_time(NTP_HOST, NTP_PORT)))
print("System time", time.ctime(time.time()))

reconnect()

print("Connected to server")

try:
    while True:
        try:
            message = recive_message()
            if message:
                message = message.decode("UTF-8")
                command, args = parse_command(message)
                print("Command from server:", command, args)
                if command == "writefile":
                    recive_file(args[0])
                elif command == "starttime":
                    starttime = float(args[0])
                    print("Starting on:", time.ctime(starttime))
                    dt = starttime - get_ntp_time(NTP_HOST, NTP_PORT)
                    print("Until start:", dt)
                    rospy.Timer(rospy.Duration(dt), start_animation, oneshot=True)
                elif command == 'takeoff':
                    play_animation.takeoff()
                elif command == 'pause':
                    pause_animation()
                elif command == 'resume':
                    resume_animation()
                elif command == 'stop':
                    stop_animation()
                    #FlightLib.reach(5, 5, 2)
                elif command == 'land':
                    FlightLib.land1()  # TODO dont forget change back to land
                elif command == 'disarm':
                    FlightLib.arming(False)

                elif command == 'request':
                    request_target = args[0]
                    print("Got request for:", request_target)
                    response = ""
                    if request_target == 'test':
                        response = "test_succsess"
                    elif request_target == 'id':
                        response = COPTER_ID
                    send_all(bytes(form_command("response", response)))
                    print("Request responded with:",  response)
        except socket.error as e:
            if e.errno != errno.EINTR:
                print("Connection lost due error:", e)
                print("Reconnecting...")
                reconnect()
                print("Re-connection successful")
            else:
                print("Interrupted")
                raise KeyboardInterrupt
except KeyboardInterrupt:
    print("Shutdown on keyboard interrupt")
finally:
    clientSocket.close()

