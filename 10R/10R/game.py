### Rules and Data Structure of the Game
### Program can be applied to other games by changing this file

import numpy as np
import config

_V=config._V
_H=config._H
_HB=config._HB
_NPCM=config._NPCM

class Game:
    
    def __init__(self,agentBl,agentWh, printBoard=True):        
        self.boardPieces=np.zeros((_V,_H),dtype=np.int)
        # 0 when empty, NEGATIVE for BLACK(1st) player, POSITIVE for WHITE(2nd) player, 
        # +-1 for PING(slow circle piece) piece, +-2 for PONG(fast square piece) 
        
        for i in range(_V-2):
            for j in range(2):
                self.boardPieces[i+1,j+_HB]=1
                self.boardPieces[i+1,j+_H-_HB-2]=-1
        
        self.gameState=GameState(self.boardPieces)
        self.agentBl=agentBl
        self.agentBl.gameState=self.gameState
        self.agentWh=agentWh
        self.agentWh.gameState=self.gameState
        self.printBoard=printBoard
    
    def reset(self):
        self.boardPieces=np.zeros((_V,_H),dtype=np.int)
        for i in range(_V-2):
            for j in range(2):
                self.boardPieces[i+1,j+_HB]=1
                self.boardPieces[i+1,j+_H-_HB-2]=-1
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
        
        
class GameState:
    def __init__(self,boardPieces,original=None):
        if original==None:
            self.boardPieces=boardPieces

            self.currentPlayer=True
            # False for black(1st) player, True for white(2nd) player. True when initiate but change to False before 1st turn.
            self.noProgressCount=0
            # draw when self.noProgressCount become >=10
            self.possibleMoves={}
            # key is move-identifier tuple (v0,h0,d,c1), value is between-piece
            self.isActionEating=False
            self.isEnd=False
            self.winner=0

            # each move is identified with 
            #  v0,h0 :initial position of piece
            #  d :direction of move ('V' for vertical, 'H' for horizontal)
            #  c1 :destination of piece (changed component of position)

        else:
            self.boardPieces=original.boardPieces.copy()
            self.currentPlayer=original.currentPlayer
            self.noProgressCount=original.noProgressCount
            self.possibleMoves=original.possibleMoves.copy()
            self.isActionEating=original.isActionEating
            self.isEnd=original.isEnd
            self.winner=original.winner
            
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

        self.isActionEating=False   
        self.possibleMoves.clear()
        currentPlayerBool=self.bool2sign(self.currentPlayer)
        
        for i in range(_V):
            for j in range(_H):
                
                #ping
                if self.boardPieces[i,j]==currentPlayerBool:
                    if 0<=i+1<_V:
                        if self.isActionEating==False and self.boardPieces[i+1,j]==0:
                            self.possibleMoves[(i,j,'V',i+1)]=None
                        elif (0<=i+2<_V
                              and self.boardPieces[i+1,j]*currentPlayerBool<0 
                              and self.boardPieces[i+2,j]==0):
                            self.possibleMoves[(i,j,'V',i+2)]=(i+1,j)
                            self.isActionEating=True
                    if 0<=i-1<_V:
                        if self.isActionEating==False and self.boardPieces[i-1,j]==0:
                            self.possibleMoves[(i,j,'V',i-1)]=None
                        elif (0<=i-2<_V
                              and self.boardPieces[i-1,j]*currentPlayerBool<0 
                              and self.boardPieces[i-2,j]==0):
                            self.possibleMoves[(i,j,'V',i-2)]=(i-1,j)
                            self.isActionEating=True
                    if 0<=j+currentPlayerBool<_H:
                        if self.isActionEating==False and self.boardPieces[i,j+currentPlayerBool]==0:
                            self.possibleMoves[(i,j,'H',j+currentPlayerBool)]=None
                        elif (0<=j+2*currentPlayerBool<_H
                              and self.boardPieces[i,j+currentPlayerBool]*currentPlayerBool<0 
                              and self.boardPieces[i,j+2*currentPlayerBool]==0):
                            self.possibleMoves[(i,j,'H',j+2*currentPlayerBool)]=(i,j+currentPlayerBool)
                            self.isActionEating=True
                    if (0<=j-2*currentPlayerBool<_H
                        and self.boardPieces[i,j-currentPlayerBool]*currentPlayerBool<0 
                        and self.boardPieces[i,j-2*currentPlayerBool]==0):
                        self.possibleMoves[(i,j,'H',j-2*currentPlayerBool)]=(i,j-currentPlayerBool)
                        self.isActionEating=True

                #pong
                elif self.boardPieces[i,j]==2*currentPlayerBool:
                    #v+
                    ii=i+1
                    betweenPiece=None
                    while ii<_V:
                        if self.boardPieces[ii,j]==0:
                            self.possibleMoves[(i,j,'V',ii)]=betweenPiece
                            if betweenPiece!=None:
                                self.isActionEating=True
                        elif self.boardPieces[ii,j]*self.bool2sign(self.currentPlayer)<0:
                            if betweenPiece==None:
                                betweenPiece=(ii,j)
                            else:
                                break
                        else:
                            break
                        ii+=1
                    #v-
                    ii=i-1
                    betweenPiece=None
                    while ii>=0:
                        if self.boardPieces[ii,j]==0:
                            self.possibleMoves[(i,j,'V',ii)]=betweenPiece
                            if betweenPiece!=None:
                                self.isActionEating=True
                        elif self.boardPieces[ii,j]*self.bool2sign(self.currentPlayer)<0:
                            if betweenPiece==None:
                                betweenPiece=(ii,j)
                            else:
                                break
                        else:
                            break
                        ii-=1
                    #h+
                    jj=j+1
                    betweenPiece=None
                    while jj<_H:
                        if self.boardPieces[i,jj]==0:
                            self.possibleMoves[(i,j,'H',jj)]=betweenPiece
                            if betweenPiece!=None:
                                self.isActionEating=True
                        elif self.boardPieces[i,jj]*self.bool2sign(self.currentPlayer)<0:
                            if betweenPiece==None:
                                betweenPiece=(i,jj)
                            else:
                                break
                        else:
                            break
                        jj+=1
                    #h-
                    jj=j-1
                    betweenPiece=None
                    while jj>=0:
                        if self.boardPieces[i,jj]==0:
                            self.possibleMoves[(i,j,'H',jj)]=betweenPiece
                            if betweenPiece!=None:
                                self.isActionEating=True
                        elif self.boardPieces[i,jj]*self.bool2sign(self.currentPlayer)<0:
                            if betweenPiece==None:
                                betweenPiece=(i,jj)
                            else:
                                break
                        else:
                            break
                        jj-=1
                            
        if self.isActionEating==True :
            for tempMove in self.possibleMoves.copy().items():
                if tempMove[1]==None:
                    del self.possibleMoves[tempMove[0]]


    def checkEnd(self):
        #global self.isEnd
        #global self.winner

        if self.noProgressCount>=_NPCM:
            self.isEnd=True
            self.winner=0
        if len(self.possibleMoves)==0:
            self.isEnd=True
            self.winner=self.bool2sign(not self.currentPlayer)
        elif np.count_nonzero(self.boardPieces==2*self.bool2sign(self.currentPlayer))>1:
            self.isEnd=True
            self.winner=self.bool2sign(self.currentPlayer)
        elif np.count_nonzero(self.boardPieces==2*self.bool2sign(not self.currentPlayer))>1:
            self.isEnd=True
            self.winner=self.bool2sign(not self.currentPlayer)
       
            
    def initiateTurn(self):
        #global self.currentPlayer
        if self.isActionEating==True:
            self.makePossibleMoves()
            if self.isActionEating==False:
                self.currentPlayer=not self.currentPlayer
                self.makePossibleMoves()
        else:
            self.currentPlayer=not self.currentPlayer
            self.makePossibleMoves()    
        self.checkEnd()

    ### Prepare Turn
    def promotion(self):
        for i in range(_V):
            if self.boardPieces[i,0]==-1:
                self.boardPieces[i,0]=-2
            elif self.boardPieces[i,_H-1]==1:
                self.boardPieces[i,_H-1]=2

    def doMove(self,v0,h0,d,c1):
        # change position of pieces, eliminate pieces,
        #  renew self.noProgressCount, promote unit
        #  due to rules
        #global self.boardPieces
        #global self.noProgressCount

        if ((v0,h0,d,c1) in self.possibleMoves):
            self.noProgressCount+=1
            if d=='V':
                self.boardPieces[c1,h0]=self.boardPieces[v0,h0]
            elif d=='H':
                if abs(self.boardPieces[v0,h0])==1:
                    #self.noProgressCount=max(0,self.noProgressCount-4)
                    self.noProgressCount=0
                self.boardPieces[v0,c1]=self.boardPieces[v0,h0]
            self.boardPieces[v0,h0]=0
            betweenPiece=self.possibleMoves.get((v0,h0,d,c1))
            if betweenPiece!=None:
                self.boardPieces[betweenPiece[0],betweenPiece[1]]=0
                #self.noProgressCount=max(0,self.noProgressCount-4)
                self.noProgressCount=0
            self.promotion()

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
        print("no progress for "+str(self.noProgressCount)+" turn")
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
        if len(moveStr)==3:
                h0=self.c2I(moveStr[0])[1]
                v0=self.c2I(moveStr[1])[1]
                i1=self.c2I(moveStr[2])
                return (v0,h0,i1[0],i1[1])
        else:
            return (-1,-1,-1,-1)

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
        v0,h0,d,c1=currentMove
        self.doMove(v0,h0,d,c1)
        
    def board2Binary(self):
        binaryBoard=np.zeros((4,_V,_H),dtype=np.int)
        binaryBoard[0,self.boardPieces==self.bool2sign(self.currentPlayer)] = 1
        binaryBoard[1,self.boardPieces==2*self.bool2sign(self.currentPlayer)] = 1
        binaryBoard[2,self.boardPieces==self.bool2sign(not self.currentPlayer)] = 1
        binaryBoard[3,self.boardPieces==2*self.bool2sign(not self.currentPlayer)] = 1
        
        if self.currentPlayer==False:
            binaryBoard=np.flip(binaryBoard,axis=2)
        return binaryBoard
        
    def other2Binary(self):
        #binaryBoard=np.zeros((2,_V,_H),dtype=np.int)
        #binaryBoard[0,:,:] = self.bool2sign(self.currentPlayer)
        #binaryBoard[1,:,:] = self.noProgressCount
        binaryBoard=np.zeros((1,_V,_H),dtype=np.int)
        binaryBoard[0,:,:] = self.noProgressCount
        return binaryBoard
    