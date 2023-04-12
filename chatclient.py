# Paul Schmitz, Star ID fl1809jp, 11/13/2022
# This program creates a chat client on a TCP connection. It contacts a server
# which must be running separately. The client can send commands and data. The
# commands are PM (public message), DM (direct message), and EX (exit). The
# server will response with prompts when necessary. The first command-line
# argument is the server name. The second command-line argument is the port.
# The third command-line argument is the username. Password will be asked by
# the server during the connection.

# imports
from socket import *
import sys
from threading import Thread

# setup fields from CLI
try:
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
    username = sys.argv[3]
except:
    print("Invalid arguments, please provide <servername> <port> <username>")
    sys.exit()

# create socket
clientSocket = socket(AF_INET, SOCK_STREAM)

# this function receives and displays incoming messages
def handleMessages():
    while True:
        message = clientSocket.recv(2048).decode()
        
        # this condition triggers when the socket is closed
        if not message: break

        # display the message
        print(message, end="")

# connect to server, start thread to receive messages
clientSocket.connect((serverName, serverPort))
t = Thread(target=handleMessages)
t.start()

# send username
clientSocket.send(username.encode())

# send commands
while True:
    message = input()
    clientSocket.send(message.encode())

    # close program when user enters "EX"
    if message == "EX":
        break

# close socket
clientSocket.shutdown(SHUT_RDWR)
clientSocket.close()

# close thread
t.join()

# exit program
sys.exit()
