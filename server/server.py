import socket
import select
import os

port = 12345
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

def start(port):
    print(f"Creating socket...")
    s = socket.socket()
    print(f"Binding to port {port}...")
    s.bind(('', port))
    print(f"Listening for connections...")
    s.listen(5)
    return s

def receive(socket, buffsize=1024, timeout=5):
    ready = select.select([socket], [], [], timeout)
    if ready[0]:
        return socket.recv(buffsize)
    else:
        return None

def handshake(socket, flag=False):
    print(f"Attempting handshake...")
    while True:
        # skip first SYN if already received (flag)
        if not flag:
            # listen for SYN
            print(f"Waiting for SYN...")
            r = receive(socket)
            if not r:
                print(f"Timed out. Retrying.")
                continue
            if not r == b'SYN':
                print(f"Unexpected response. Retrying.")
                continue
        flag = False
        
        # send ACK + SYN
        print(f"SYN received. Sending ACK + SYN...")
        socket.send(b'ACK')
        socket.send(b'SYN')
        
        # listen for ACK
        print(f"Waiting for ACK...")
        r = receive(socket)
        if not r:
            print(f"Timed out. Retrying.")
            continue
        if not r == b'ACK':
            print(f"Unexpected response. Retrying.")
            continue
        print(f"ACK received.")
        
        print(f"Handshake complete.")
        return

def handle(client, address):
    print(f'Got connection from {addr}.')
    # do handshake
    handshake(client)

    while True:
        # receive client's query
        r = receive(client, timeout=None)
        if r == b'SYN':
            print(f"SYN received. Initiating graceful disconnection...")
            handshake(client, True)
            client.close()
            print(f"Disconnected from {addr}.")
            break
        filename = r.decode("ascii")

        print(f"Searching for file: {filename}")
        # if file exists
        path = os.path.join(BASE_DIR, filename)
        if os.path.isfile(path):
            print(f"Found {filename}. Reading file...")
            # read file
            f = open(path, "rb")
            data = f.read()
            f.close()
            print(f"File read. Sending to client...")

            # send to client
            while True:
                # send data
                print(f"Sending {len(data)} bytes...")
                client.send((len(data)).to_bytes(4, 'big'))
                client.send(data)
                print(f"Sent. Waiting for ACK...")

                # get ACK
                r = receive(client)
                if not r:
                    print(f"Timed out. Retrying.")
                    continue
                elif not r == b'ACK':
                    print(f"Unexpected response. Retrying.")
                    continue
                
                break
        # file does not exist
        else:
            print(f"{filename} not found.")
            client.send((0).to_bytes(4, 'big'))


if __name__ == "__main__":
    # start server
    socket = start(port)

    while True:
        client, addr = socket.accept()
        handle(client, addr)
