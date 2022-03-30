import socket
import struct
import canmessage_pb2 as can_message

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            totallen = conn.recv(4)
            if not totallen:
                break
            totallenRecv = struct.unpack('>I', totallen)[0]
            messagelen = totallenRecv - 4
            message = conn.recv(messagelen)

            msg = can_message.CanMessage()
            msg.ParseFromString(message)
            print("Received message: ", msg)
