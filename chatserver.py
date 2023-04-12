# Paul Schmitz, Star ID fl1809jp, 11/13/2022
# This program creates a chat server on a TCP connection. It receives
# client connections and handles each on a separate thread. It handles three
# operations which are PM (public message), DM (direct message), and EX (exit).
# PM is broadcast to all active clients. DM will display a list of active
# clients, prompt user to pick one, and send the message to that user. EX logs
# off the user. Each incoming user is validated with a password stored in the
# server's local files. The command-line argument is the port.

# dictionary https://www.geeksforgeeks.org/python-dictionary/?ref=lbp
# string split https://www.w3schools.com/python/ref_string_split.asp

# imports
from socket import *
import sys
from threading import Thread

# track active users in a map
# key = username, value = socket
activeClients = {}

# track all threads
activeThreads = []

# this function handles the login process and validates the password
def loginRoutine(socket, username):
    # ask user for password
    socket.send("** Enter password:\r\n".encode())
    password = socket.recv(2048).decode()
    
    # read user data file
    file = open("userdata.txt")
    filedata = file.readlines()
    file.close()

    # search data for existing username and password
    for entry in filedata:
        usernameData, passwordData = entry.split(" ", 1)
        # remove the newline character from the password
        passwordData = passwordData[:-1]
        
        # case when it is existing username
        if usernameData == username:
            if passwordData == password:

                # track client and return true
                activeClients[username] = socket
                socket.send("** Password correct, welcome back\r\n".encode())
                return True
            else:

                # send error message to client
                socket.send("** Wrong password, please reconnect\r\n".encode())
                return False
            
    # if reaching end of file, then it is a new user
    # store credentials in file
    file = open("userdata.txt", "a")
    file.write(username + " " + password + "\n")
    file.close()

    # track client and return true
    activeClients[username] = socket
    socket.send("** Registered new user with password\r\n".encode())
    return True

# this function handles the public message operation
def operationPm(socket):
    
    # get the message from client
    socket.send("** Enter the message to be sent:\r\n".encode())
    message = socket.recv(2048).decode()

    # append end of line characters for nice formatting
    message += "\r\n"
    
    # send message to all active clients
    for otherSocket in activeClients.values():
        if socket != otherSocket:
            otherSocket.send(message.encode())
    
    # send confirmation to client
    socket.send("** Your message was sent\r\n".encode())

# this function handles the direct message operation
def operationDm(socket):
    
    # ask client to send desired username and message
    # and also send a list of all active users
    message = "** Enter the username followed by the message to be sent:\r\n"
    for username in activeClients.keys():
        message += "   " + username + "\r\n"
    socket.send(message.encode())
        
    # get the target username and message from client
    try:
        username, message = socket.recv(2048).decode().split(" ", 1)
    except ValueError:
        message = ""
    message += "\r\n"
    
    # check if the username exists and send message
    try:
        dmSocket = activeClients[username]
        dmSocket.send(message.encode())
        socket.send("** Your message was sent\r\n".encode())
        
    # handling for when the username does not exist
    except KeyError:
        socket.send("** Your message was not sent \r\n".encode())

# this function handles the exit operation
def operationEx(username):
    
    # remove user from active clients list.
    # note: the client is responsible for closing the connection
    activeClients.pop(username)

# this function is run by a new thread whenever a connection is made
def handleConnection(socket):
    # setup a try block in case connection is broken
    try:
        # get username from client, then run login routine to validate
        username = socket.recv(2048).decode()
        loginValid = loginRoutine(socket, username)
        
        # server waits for commands
        while loginValid:
            
            # receive command
            command = socket.recv(2048).decode()
            if (command == "PM"):
                operationPm(socket)
            elif (command == "DM"):
                operationDm(socket)
            elif (command == "EX"):
                operationEx(username)
                loginValid = False
            else:
                socket.send("** Invalid command, enter PM, DM, or EX\r\n".encode())
            
    # if connection is broken, run EX operation  
    except BrokenPipeError:
        operationEx(username)

    # stop thread
    return

# read CLI as port
try:
    serverPort = int(sys.argv[1])
except:
    print("Invalid arguments, please provide <port>")
    sys.exit()

# fields
serverName = "localhost"
serverSocket = socket(AF_INET, SOCK_STREAM)

# bind and listen on socket
serverSocket.bind((serverName, serverPort))
serverSocket.listen(10)
print("The server is waiting for connections")

# main program loop
while True:
    
    # get connection, then start new thread to handle it
    connectionSocket, addr = serverSocket.accept()
    t = Thread(target=handleConnection, args=[connectionSocket])
    t.start()
    activeThreads.append(t)

# close socket
serverSocket.shutdown(SHUT_RDWR)
serverSocket.close()

# close all threads
for thread in activeThreads:
    thread.join()

# exit program
sys.exit()
