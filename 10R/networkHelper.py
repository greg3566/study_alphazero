from agent import Agent, AgentHuman
from socket import *
import pickle

class Server:
    def __init__(self):
        tempSock = socket(AF_INET, SOCK_STREAM)
        tempSock.connect(('gmail.com', 80))
        print(tempSock.getsockname())
        serverSock = socket(AF_INET, SOCK_STREAM)
        serverSock.bind(tempSock.getsockname())
        serverSock.listen(1)
        print(serverSock.getsockname())
        connectionSock, addr = serverSock.accept()
        print(connectionSock.getsockname())
        print(addr)

class Client:
    def __init__(self,name):
        clientSock = socket(AF_INET, SOCK_STREAM)
        clientSock.connect(name)
        print(clientSock.getsockname())