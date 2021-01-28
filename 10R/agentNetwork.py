from agent import Agent, AgentHuman
from socket import *
import pickle

connectionSock=None
clientSock=None


class AgentFromNetworkBl(Agent):
    def __init__(self,ip=''):
        super().__init__()
        global connectionSock
        serverSock = socket(AF_INET, SOCK_STREAM)
        serverSock.bind((ip,50010))
        serverSock.listen(1)
        connectionSock, addr = serverSock.accept()
        serverSock.close()
        
    def selectMove(self):
        pickledResult= connectionSock.recv(32)
        return pickle.loads(pickledResult)

        
class AgentHumanForNetworkWh(AgentHuman):
    def __init__(self):
        super().__init__()
        
    def selectMove(self):
        result=super().selectMove()
        pickledResult=pickle.dumps(result)
        connectionSock.send(pickledResult)
        return result
        
    
class AgentFromNetworkWh(Agent):
    def __init__(self, serverip='59.15.88.89'):
        super().__init__()
        global clientSock
        clientSock = socket(AF_INET, SOCK_STREAM)
        clientSock.connect((serverip,50010))

    def selectMove(self):
        pickledResult= clientSock.recv(32)
        return pickle.loads(pickledResult)
        
class AgentHumanForNetworkBl(AgentHuman):
    def __init__(self):
        super().__init__()
        
    def selectMove(self):
        result=super().selectMove()
        pickledResult=pickle.dumps(result)
        clientSock.send(pickledResult)
        return result
