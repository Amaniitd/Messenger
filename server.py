import socket
import threading

PORT = 5050
# SERVER = socket.gethostbyname(socket.gethostname())
SERVER = "localhost"
# print(SERVER)
# SERVER = "103.27.8.110"
ADDR = (SERVER, PORT)
HEADER = 64
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDR)

dict = {}
max_length = 1024


def send(msg, client):
    message = msg.encode("utf-8")
    client.send(message)


def receive(client, connected):
    msg = ""
    try:
        msg = client.recv(max_length).decode("utf-8")
        while(msg == None or msg == ""):
            msg = client.recv(max_length).decode("utf-8")
            return msg
    except:
        connected[0] = False
    return msg


def handle_client(conn, addr, noOfConf, boolRecv):
    toSend = False
    toRecv = False
    Username = ""
    connected = [True]
    while connected[0]:
        s = receive(conn, connected)
        if (connected[0] == False):
            if (Username != ""):
                del dict[Username]
                boolRecv.pop()
                print("[CONNECTION] Total active connections are:", len(dict))

            break
        if (len(s) == 0):
            continue
        if (s[0:8] == "REGISTER"):
            if (s[9:15] == "TOSEND"):
                if (toSend == False):
                    i = 16
                    while(i < len(s) and s[i] != '\n'):
                        i += 1
                    if (s[i] != '\n' or s[i+1] != '\n'):
                        send("ERROR 100 Malformed username\n\n", conn)
                    else:
                        Username = s[16:i]
                        if (Username.isalnum() == False):
                            send("ERROR 100 Malformed username\n\n", conn)
                        elif Username in dict:
                            send("ERROR 100 Malformed username\n\n", conn)
                        else:
                            toSend = True
                            send("REGISTERED TOSEND " +
                                 Username + "\n\n", conn)
                else:
                    send("ERROR: Invalid message\n", conn)
            elif (s[9:15] == "TORECV"):
                if (toRecv == False):
                    i = 16
                    while(i < len(s) and s[i] != '\n'):
                        i += 1
                    if (s[i] != '\n' or s[i+1] != '\n'):
                        send("ERROR 100 Malformed username\n\n", conn)
                    else:
                        Username = s[16:i]
                        if (Username.isalnum() == False):
                            send("ERROR 100 Malformed username\n\n", conn)
                        elif Username in dict:
                            send("ERROR 100 Malformed username\n\n", conn)
                        else:
                            toRecv = True
                            send("REGISTERED TORECV " +
                                 Username + "\n\n", conn)
                            dict[Username] = [conn, None]
                            print(
                                "[CONNECTION] Total active connections are:", len(dict))

                else:
                    send("ERROR: Invalid message\n", conn)
            else:
                send("ERROR: Invalid message\n", conn)
        elif (s[0:4] == "SEND"):
            if (toSend):
                i = 5
                while(s[i] != '\n'):
                    i += 1
                receiver = s[5:i-1]
                k = i
                i += 1
                c = s[i:i + 15]
                if (c != "Content-length:"):
                    send("ERROR 103 Header Incomplete\n\n", conn)
                    connected[0] = False
                    if (Username != ""):
                        del dict[Username]
                        boolRecv.pop()
                        print(
                            "[CONNECTION] Total active connections are:", len(dict))
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
                        send("ERROR 103 Header Incomplete\n\n", conn)
                        connected[0] = False
                        if (Username != ""):
                            del dict[Username]
                            boolRecv.pop()
                            print(
                                "[CONNECTION] Total active connections are:", len(dict))
                        break
                    else:
                        if receiver in dict:
                            send("FORWARD " + Username +
                                 s[k: len(s)], dict[receiver][0])
                            dict[receiver][1] = dict[Username][0]
                        elif receiver == "ALL":
                            noOfConf[0] = 1
                            boolRecv[0] = True
                            for g in range(1, len(boolRecv)):
                                boolRecv[g] = False
                            for r in dict:
                                if (r == Username):
                                    continue
                                send("FORWARD " + Username +
                                     s[k: len(s)], dict[r][0])
                                dict[r][1] = dict[Username][0]
                        else:
                            send("ERROR 102 Unable to send\n\n", conn)
            else:
                send("ERROR 101 No user registered\n\n", conn)
        elif (s[0:8] == "RECEIVED"):
            if (toSend):
                if (noOfConf[0] < len(boolRecv)):
                    boolRecv[noOfConf[0]] = True
                    noOfConf[0] += 1
                    if (noOfConf[0] == len(boolRecv)):
                        noOfConf[0] = 10000
                        z = True
                        for x in range(len(boolRecv)):
                            if (boolRecv[x] == False):
                                z = False
                        if (z):
                            send("SENT ALL\n", dict[Username][1])
                        else:
                            send("ERROR 102 Unable to send\n",
                                 dict[Username][1])

                else:
                    send("SENT " + Username + "\n", dict[Username][1])
            else:
                send("ERROR 101 No user registered\n\n", conn)
        elif (s[0:9] == "ERROR 103"):
            if (noOfConf[0] < len(boolRecv)):
                boolRecv[noOfConf[0]] = False
                noOfConf[0] += 1
                if (noOfConf[0] == len(boolRecv)):
                    noOfConf[0] = 10000
                    if (z):
                        send("ERROR 102 Unable to send\n", dict[Username][1])
            else:
                send(s, dict[Username][1])


def start():
    server.listen()
    print("[LISTENING] server is listening on:", SERVER)
    noOfConf = [10000]
    boolRecv = []
    while True:
        conn, addr = server.accept()
        boolRecv.append(False)
        thread = threading.Thread(
            target=handle_client, args=(conn, addr, noOfConf, boolRecv))
        thread.start()


print("[STARTING] server is starting...")
start()
