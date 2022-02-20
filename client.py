import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
max_length = 1024


def send(msg):
    message = msg.encode("utf-8")
    client.send(message)


def receive():
    msg = ""
    try:
        msg = client.recv(max_length).decode("utf-8")
        while(msg == None or msg == ""):
            msg = client.recv(max_length).decode("utf-8")
    except:
        connected = False
    return msg


HEADER = 64
PORT = 5050
connected = False
# SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = "localhost"
# SERVER = "103.27.8.110"
while True:
    SERVER = input("Enter server's IP address: ")
    ADDR = (SERVER, PORT)
    try:
        client.connect(ADDR)
        break
    except:
        pass
    print("\nFailed to connect to given server's address\n")

print("[CONNECTED]: successfully connected to the server\n")

print("\nUsername Format:")
print("Only alphanumeric characters are allowed")
print("Username \"ALL\"is not allowed\n")

while True:
    USRNME = input("Enter you Username: ")
    try:
        if (USRNME != "ALL" and USRNME.isalnum()):
            print("\n[REGISTRATION] ....Registering Username...\n")
            send("REGISTER TOSEND " + USRNME + "\n\n")
            msg = receive()
            if (msg == ""):
                continue
            if (msg[0] == 'E'):
                print(
                    "[ERROR 100] Failed to register: Malformed Username or username already taken")
            else:
                send("REGISTER TORECV " + USRNME + "\n\n")
                msg = receive()
                if (msg == ""):
                    continue
                if (msg[0] == 'E'):
                    print(
                        "[ERROR 100] Failed to register: Malformed Username or username already taken")
                else:
                    print("[REGISTRATION] Registration successful\n")
                    connected = True
                    break
    except:
        print("\nInvalid Username\n")


def handle_send():
    while connected:
        s = input()
        if (len(s) == 0):
            continue
        if (s[0] != '@'):
            print(
                "[ERROR] invalid message format: should start with \'@\' followed by receiver's username")
        else:
            i = 1
            while (i < len(s)):
                if (s[i] != " "):
                    i = i + 1
                else:
                    break
            receiver = s[1: i + 1]
            msg = s[i+1:len(s)]
            send("SEND " + receiver + "\n" +
                 "Content-length: " + str(len(msg)) + "\n\n" + msg)


def handle_receive():
    while connected:
        s = receive()
        if (s == ""):
            continue
        if (s[0] == 'S'):
            receiver = s[5:len(s) - 1]
            print("[MESSAGE SENT] to " + receiver + '\n')
        elif (s[0:9] == "ERROR 102"):
            print("[ERROR 102] Unable to send\n")
        elif(s[0:9] == 'ERROR 100'):
            print("[ERROR 100] No user registered\n")
        elif(s[0:7] == "FORWARD"):
            i = 8
            while(s[i] != '\n'):
                i += 1
            sender = s[8:i]
            i += 1
            c = s[i:i + 15]
            if (c != "Content-length:"):
                send("ERROR 103 Header Incomplete\n\n")
                break
            else:
                i += 16
                j = i
                while(s[i] != '\n'):
                    i += 1
                contentLength = int(s[j:i + 1])
                i += 2
                msg = s[i:len(s)]
                if (contentLength != len(msg)):
                    send("ERROR 103 Header Incomplete\n\n")
                    break
                else:
                    print("[" + sender + "] " + msg)
                    send("RECEIVED " + sender + "\n\n")
        else:
            print("[ERROR 103] Header incomplete\n")
            break
    print("[CONNECTION] connection lost...\n")


thread1 = threading.Thread(target=handle_send)
thread2 = threading.Thread(target=handle_receive)
thread1.start()
thread2.start()
