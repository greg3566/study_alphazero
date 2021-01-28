import numpy as np
import random
from collections import deque
from agent import Agent
from config import _V, _H, _A, _LM, _GL, key2pindex, pindex2key
#import time

class MCTLeaf:
    def __init__(self,gameState):
        self.gameState=gameState
        self.childs=[]
        self.NWQP=[]
        self.totalN=0
        self.moves=[]

memorySize=_GL*2
        
class AgentMCTS(Agent):
    
    def __init__(self,bipredictor,depth, c_puct=1, temperature=0.1, noise=0.3, saveImage=False, printValue=True):
        super().__init__()
        self.bipredictor=bipredictor
        self.depth=depth
        self.c_puct=c_puct
        self.temperature=temperature
        self.noise=noise
        self.saveImage=saveImage
        if saveImage==True:
            self.boardImages=deque(maxlen=memorySize)
            self.otherImages=deque(maxlen=memorySize)
            self.players=deque(maxlen=memorySize)
            self.policys=deque(maxlen=memorySize)
        self.printValue=printValue
        self.root=None
        #self.t=[0,0,0,0,0,0]
        
    def selectMove(self):
        if self.printValue==True:
            vv,pp=self.bipredictor.predict(self.gameState)
            print(vv)
            
        if self.root==None:
            self.root=MCTLeaf(self.gameState)
        
        for i in range(self.depth):
            
            #choose
            iterLeaf=self.root
            route=[]
            while iterLeaf.childs and not iterLeaf.gameState.isEnd:
                maxWeight=-2
                maxNo=0
                for childNo in range(len(iterLeaf.childs)):
                    signedQ=iterLeaf.NWQP[childNo][2]* iterLeaf.gameState.bool2sign(iterLeaf.gameState.currentPlayer)
                    U=self.c_puct*iterLeaf.NWQP[childNo][3]*(0.01+iterLeaf.totalN**0.5)/(1+iterLeaf.NWQP[childNo][0])
                    cWeight=signedQ+U
                    if cWeight>maxWeight:
                        maxWeight=cWeight
                        maxNo=childNo
                route.append(maxNo)
                iterLeaf=iterLeaf.childs[maxNo]
            
            #expand
            iterGameState=iterLeaf.gameState
            if iterGameState.isEnd:
                v=iterGameState.winner
            else:
                v,p=self.bipredictor.predict(iterGameState) #Consumes 70% of time
#                 p=p.clip(0)
#                 pSum=np.add.reduce(p)
#                 if pSum>0:
#                     p/=pSum
#                 else:
#                     p=np.full_like(p,1/len(p))
#                     print("no positive p error from agentMCTS selectMove")
                iterGameState.makePossibleMoves()
                for tempMove in iterGameState.possibleMoves.keys():
                    childGameState=iterGameState.copy()
                    #v0,h0,d,c1=tempMove
                    childGameState.doMove(*tempMove)
                    childGameState.initiateTurn() #Consumes 20% of time
                    childLeaf=MCTLeaf(childGameState)
                    iterLeaf.childs.append(childLeaf)
                    iterLeaf.NWQP.append((0,0,0,p[key2pindex(tempMove,iterGameState.currentPlayer)]))
                    iterLeaf.moves.append(tempMove)
            
            #backup
            iterLeaf=self.root
            for childNo in route:
                N,W,Q,P=iterLeaf.NWQP[childNo]
                N+=1
                W+=v
                Q=W/N
                iterLeaf.NWQP[childNo]=(N,W,Q,P)
                iterLeaf.totalN+=1
                iterLeaf=iterLeaf.childs[childNo]
        Ns=list(zip(*self.root.NWQP))[0]
        maxNs=max(Ns)
        weight=list(map(lambda x: (x/maxNs)**(1/self.temperature),Ns))
        if self.saveImage==True:
            self.recordImage(self.root.moves.copy(),weight.copy())
        lweight=len(weight)
        if lweight>0:
            weight+=np.random.dirichlet([1/_LM]*lweight)*np.sum(weight)*self.noise/(1-self.noise)
        currentNo=random.choices(range(len(self.root.childs)),weight)[0]
        currentMove=self.root.moves[currentNo]
        self.root=self.root.childs[currentNo]
        return currentMove
    
    def fetch(self,currentMove):
        if self.root!=None:
            if self.root.childs:
                currentNo=self.root.moves.index(currentMove)
                self.root=self.root.childs[currentNo]
            else:
                self.root=None
       
            
        
    def recordImage(self,moves,weight):
        self.boardImages.append(self.gameState.board2Binary())
        self.otherImages.append(self.gameState.other2Binary())
        self.players.append(self.gameState.bool2sign(self.gameState.currentPlayer))
        
        policy=np.zeros(_A,dtype=np.float)
        
        sumw=0
        while weight:
            move=key2pindex(moves.pop(),self.gameState.currentPlayer)
            w=weight.pop()
            sumw+=w
            policy[move]=w
        policy/=sumw
        self.policys.append(policy)
            
    def end(self):
        if self.saveImage==True:
            zs=map(lambda x: x*self.gameState.winner, self.players)
            self.bipredictor.saveImages(self.boardImages,self.otherImages,zs,self.policys)
            self.boardImages.clear()
            self.otherImages.clear()
            self.players.clear()
            self.policys.clear()
        self.root=None
            