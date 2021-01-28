### Rules and Data Structure of the Game
### Program can be applied to other games by changing this file

import numpy as np
from config import _V, _H, _N, _Gravity

class Game():
    
    def __init__(self,agentBl,agentWh, printBoard=True):        
        self.boardPieces=np.zeros((_V,_H),dtype=np.int)
        
        self.gameState=GameState(self.boardPieces)
        self.agentBl=agentBl
        self.agentBl.gameState=self.gameState
        self.agentWh=agentWh
        self.agentWh.gameState=self.gameState
        self.printBoard=printBoard
    
    def reset(self):
        self.boardPieces=np.zeros((_V,_H),dtype=np.int)
        self.gameState=GameState(self.boardPieces)
        self.agentBl.gameState=self.gameState
        self.agentWh.gameState=self.gameState
        
    def step(self):
        self.gameState.initiateTurn()
        if self.printBoard==True:
            self.gameState.printBoard()
        if self.gameState.isEnd==True:
            self.agentBl.end()
            self.agentWh.end()
        else:
            self.gameState.getMove(self.agentBl,self.agentWh)
        
        
class GameState():
    def __init__(self,boardPieces,original=None):
        if original==None:
            self.boardPieces=boardPieces

            self.currentPlayer=True
            self.possibleMoves={}
            self.isEnd=False
            self.winner=0

        else:
            self.boardPieces=original.boardPieces.copy()
            self.currentPlayer=original.currentPlayer
            self.possibleMoves=original.possibleMoves.copy()
            self.isEnd=original.isEnd
            self.winner=original.winner
            
        self.lastMove=None
    
    def copy(self):
        return GameState(None,self)
    
    ### Basic Tools

    def bool2sign(self,b):
        # return 1 for True, -1 for False
        if b:
            return 1
        else:
            return -1

    

    ### Prepare Turn

    def makePossibleMoves(self):
        # clear and add elements in posibleMoves
        self.possibleMoves.clear()
        for j in range(_H):
            for i in reversed(range(_V)):
                if self.boardPieces[i,j]==0:
                    self.possibleMoves[i,j]=None
                    if _Gravity==True:
                        break

    def checkEnd(self):
        #global self.isEnd
        #global self.winner

        if self.lastMove!=None:
            v0,h0=self.lastMove
            ds=((0,1),(1,-1),(1,0),(1,1))
            for dv,dh in ds:
                v,h=v0,h0
                count=-1
                while 0<=v<_V and 0<=h<_H:
                    if self.boardPieces[v,h]==self.bool2sign(not self.currentPlayer):
                        count+=1
                        v+=dv
                        h+=dh
                    else:
                        break
                v,h=v0,h0
                while 0<=v<_V and 0<=h<_H:
                    if self.boardPieces[v,h]==self.bool2sign(not self.currentPlayer):
                        count+=1
                        v-=dv
                        h-=dh
                    else:
                        break
                if count>=_N:
                    self.isEnd=True
                    self.winner=self.bool2sign(not self.currentPlayer)
                    return None
        
        if len(self.possibleMoves)==0:
            self.isEnd=True
            self.winner=0

    def initiateTurn(self):
        #global self.currentPlayer
        self.currentPlayer=not self.currentPlayer
        self.makePossibleMoves()
        self.checkEnd()
        

    ### Prepare Turn
    def doMove(self,v0,h0):
        # change position of pieces, eliminate pieces,
        #  renew self.noProgressCount, promote unit
        #  due to rules
        #global self.boardPieces
        #global self.noProgressCount

        if ((v0,h0) in self.possibleMoves):
            self.boardPieces[v0,h0]=self.bool2sign(self.currentPlayer)
            self.lastMove=(v0,h0)

    ### For Human Player

    def printBoard(self):
        print('　',end='')
        for j in range(_H):
            print(chr(ord('Ａ')+j),end='')
        print('')
        for i in range(_V):
            print(chr(ord('０')+i),end='')
            for j in range(_H):
                boardPiece=self.boardPieces[i,j]
                if boardPiece==-1:
                    print('●',end='')
                elif boardPiece==-2:
                    print('■',end='')
                elif boardPiece==1:
                    print('○',end='')
                elif boardPiece==2:
                    print('□',end='')
                else:
                    print('┼',end='')
            print('')
        if self.currentPlayer==False:
            print('Black',end='')
        else:
            print('White',end='')
        print("'s turn")
        if self.isEnd==True:
            if self.winner==0:
                print("draw")
            elif self.winner==-1:
                print("Black Win")
            elif self.winner==1:
                print("White Win")

    def c2I(self,c):
        i=[0 for _ in range(2)]
        i[1]=ord(c);
        if( i[1]>=ord('0') and i[1]<ord('0')+_V ):
            i[1]-=ord('0')
            i[0]='V'
        elif( i[1]>=ord('A') and i[1]<ord('A')+_H ):
            i[1]-=ord('A')
            i[0]='H'
        elif( i[1]>=ord('a') and i[1]<ord('a')+_H ):
            i[1]-=ord('a')
            i[0]='H'
        else:
            i[0]='E'
        return i
    
    def cs2Is(self,moveStr):
        if len(moveStr)==2:
            h0=self.c2I(moveStr[0])[1]
            v0=self.c2I(moveStr[1])[1]
            return (v0,h0)       

    def getMove(self,agentBl,agentWh):
        while True:
            if self.currentPlayer==False:
                currentMove=agentBl.selectMove()
                agentWh.fetch(currentMove)
            else:
                currentMove=agentWh.selectMove()
                agentBl.fetch(currentMove)
            if currentMove in self.possibleMoves:
                break
            else:
                print("Ilegal move",currentMove)
        v0,h0=currentMove
        self.doMove(v0,h0)
        
    def board2Binary(self):
        binaryBoard=np.zeros((2,_V,_H),dtype=np.int)
        binaryBoard[0,self.boardPieces==self.bool2sign(self.currentPlayer)] = 1
        binaryBoard[1,self.boardPieces==self.bool2sign(not self.currentPlayer)] = 1
        
        if self.currentPlayer==False:
            binaryBoard=np.flip(binaryBoard,axis=2)
        return binaryBoard
        
    def other2Binary(self):
        #binaryBoard=np.zeros((2,_V,_H),dtype=np.int)
        #binaryBoard[0,:,:] = self.bool2sign(self.currentPlayer)
        #binaryBoard[1,:,:] = self.noProgressCount
        binaryBoard=np.zeros((0,_V,_H),dtype=np.int)
        return binaryBoard

