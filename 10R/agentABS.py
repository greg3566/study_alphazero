import numpy as np
from game import GameState
import random
from agent import Agent

class AgentABS(Agent):
    
    def __init__(self,predictor,depth,epsilon0=0, decay=1, cor=0, saveImage=False, printValue=True):
        super().__init__()
        self.bestMove=None
        self.predictor=predictor
        self.depth=depth
        self.epsilon0=epsilon0
        self.epsilon=epsilon0
        self.decay=decay
        self.cor=cor
        self.saveImage=saveImage
        if saveImage==True:
            self.boardImages=np.empty((0,4,7,11),dtype=np.int)
            self.otherImages=np.empty((0,2,7,11),dtype=np.int)
            self.players=np.empty(0,dtype=np.float)
            self.values=np.empty(0,dtype=np.float)
            self.isPredicteds=np.empty(0,dtype=np.bool)
        self.printValue=printValue
        
    def selectMove(self):
        if self.epsilon!=0 and random.random()<self.epsilon:
            if self.printValue==True:
                print("epsiloned!")
            if self.saveImage==True:
                self.recordImage(0,False)
            self.epsilon*=self.decay
            return random.choice(list(self.gameState.possibleMoves.keys()))
        else:
            if self.printValue==True:
                print(self.predictor.predict(self.gameState),end=' -> ')
            value=self.simulate(self.gameState,-2,2,self.depth)##
            if self.printValue==True:
                print(value)##
            if self.saveImage==True:
                #value is + when White is good NOT currentplayer ##
                #value is + when currentplayer is good
                self.recordImage(self.gameState.bool2sign(self.gameState.currentPlayer)*value,True)
            self.epsilon*=self.decay
            return self.bestMove
    
    def simulate(self,prevGameState,alpha,beta,remain):
        if remain>0:
            if prevGameState.isEnd==True:
                return prevGameState.winner
            remain-=1
            prevPlayer=prevGameState.currentPlayer
            tempBestMove=None
            if prevPlayer==True:
                result=-2
            else:
                result=2
                
            for tempMove in prevGameState.possibleMoves.keys():
                size=len(prevGameState.possibleMoves)
                newGameState=GameState(None,original=prevGameState)
                
                v0,h0,d,c1=tempMove
                newGameState.doMove(v0,h0,d,c1)
                newGameState.initiateTurn()
                tempVal=self.simulate(newGameState,alpha,beta,remain)
                if prevPlayer==True:
                    tempVal-=self.cor*(size-1)/(size+1)
                    if tempVal>result:
                        result=tempVal
                        if tempVal>alpha:
                            alpha=tempVal
                            if beta<=alpha:
                                break
                        tempBestMove=tempMove
                else:
                    tempVal+=self.cor*(size-1)/(size+1)
                    if tempVal<result:
                        result=tempVal
                        if tempVal<beta:
                            beta=tempVal
                            if beta<=alpha:
                                break
                        tempBestMove=tempMove
                        
            self.bestMove=tempBestMove
        else:
            result= self.predictor.predict(prevGameState)
            remain=-1
        
        return result
    
    def recordImage(self,value,isPredicted):
        self.boardImages=np.append(self.boardImages, 
                                   np.expand_dims(self.gameState.board2Binary(), axis=0), 
                                   axis=0
                                  )
        self.otherImages=np.append(self.otherImages, 
                                   np.expand_dims(self.gameState.other2Binary(), axis=0), 
                                   axis=0
                                  )
        if isPredicted==True:
            self.values=np.append(self.values,value)
        else:
            self.values=np.append(self.values,0)
        self.isPredicteds=np.append(self.isPredicteds,isPredicted)
        self.players=np.append(self.players,self.gameState.bool2sign(self.gameState.currentPlayer))
        
    def end(self):
        self.epsilon=self.epsilon0
        if self.saveImage==True:
            zs=self.players*self.gameState.winner
            zs+=self.values
            zs[self.isPredicteds==True]/=2
            self.predictor.saveImages(self.boardImages, self.otherImages, zs)
            
            self.boardImages=np.empty((0,4,7,11),dtype=np.int)
            self.otherImages=np.empty((0,2,7,11),dtype=np.int)
            self.players=np.empty(0,dtype=np.float)
            self.values=np.empty(0,dtype=np.float)
            self.isPredicteds=np.empty(0,dtype=np.bool)