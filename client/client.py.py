import socket
import select

# server address
port = 12345
host = '127.0.0.1'

def connect(host, port):
    print(f"Creating socket...")
    s = socket.socket()
    print(f"Connecting to server...")
    s.connect((host, port))
    print(f"Connected.")

    return s

def receive(socket, buffsize=1024, timeout=5):
    ready = select.select([socket], [], [], timeout)
    if ready[0]:
        return socket.recv(buffsize)
    else:
        return None

def handshake(socket):
    print(f"Attempting handshake...")
    while True:
        # send SYN
        print(f"Sending SYN...")
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
        print(f"ACK received. Waiting for SYN...")
        
        # listen for SYN
        r = receive(socket)
        if not r:
            print(f"Timed out. Retrying.")
            continue
        if not r == b'SYN':
            print(f"Unexpected response. Retrying.")
            continue
        print(f"SYN received. Sending ACK...")
        
        # send ACK to complete handshake
        socket.send(b'ACK')
        print(f"Handshake complete.")
        return

if __name__ == "__main__":
    # connect to server
    socket = connect(host, port)
    
    # do handshake
    handshake(socket)

    while True:
        # ask user for file to query
        filename = input("Enter filename to query(or hit return to terminate): ")

        # graceful exit
        if len(filename) == 0:
            handshake(socket)
            break
        
        # ask server for file
        print(f"Sending request...")
        socket.send(filename.encode('ascii'))

        # receive filesize
        r = receive(socket, 4, None)
        if r is None:
            print(f"Timed out.")
            continue
        filesize = int.from_bytes(r, 'big')
        if not filesize > 0:
            print(f"File not available.")
            continue
            
        while True:
           # recieve file
            print(f"Receiving {filesize} bytes...")
            data = receive(socket, filesize, None)
            
            if not len(data) == filesize:
                print(f"Failed to receive complete file. Waiting for server to resend...")
                continue
            
            print(f"Received. Sending ACK...")
            socket.send(b'ACK')
            print(f"ACK sent...")
            break
        

        print(f"Writing to {filename}...")
        f = open(filename, "wb")
        f.write(data)
        f.close()
        print(f"Done.")

    print(f"Terminating...")
    socket.close()
