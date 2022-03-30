import logging
import struct
import pandas as pd
import canmessage_pb2 as can_message
import socket
import time


HOST = "127.0.0.1"
PORT = 65432


def get_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s


# acceleration = delta kph / delta hours
def get_acceleration(old_speed, new_speed, delta_seconds):
    delta_velocity = abs(new_speed - old_speed)
    delta_time = delta_seconds / 3600
    return delta_velocity/delta_time


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Read test data from 1 lap
    df = pd.read_csv('OneLapTest.csv')

    last_time = 0.0
    last_speed = 0.0

    try:
        socket_conn = get_socket()

        for index, row in df.iterrows():
            # relative time from start of CAN bus
            rel_time = row["Time (rel)"]
            # speed of vehicle in kph
            speed = row["IprVehSpdKph"]
            # duration is how long vehicle has been traveling at this speed
            duration = rel_time - last_time
            last_time = rel_time
            # calculate acceleration
            acceleration = get_acceleration(last_speed, speed, duration)
            # Create protobuf message to send
            message = can_message.CanMessage()
            message.duration = duration
            message.speed = speed
            message.acceleration = acceleration
            # Setup message to send over socket
            data = message.SerializeToString()
            length = 4 + len(data)
            pack = struct.pack('>I', length)  # the first part of the message is length
            socket_conn.sendall(pack + data)
            print("sent message", message)
            # sleep for duration to simulate time delay of real CAN message
            time.sleep(duration)
    except Exception:
        logging.exception("Unexpected exception: ")
    finally:
        if socket_conn:
            socket_conn.close()
