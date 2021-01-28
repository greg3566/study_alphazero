from bipredictor import Bipredictor
import config

_V=config._V
_H=config._H


class BipredictorTictactoe(Bipredictor):
    def predict(self,gameState):
        result=0
        result+=gameState.boardPieces[1,1]*0.4
        result+=gameState.boardPieces[0,0]*0.1
        result+=gameState.boardPieces[0,2]*0.1
        result+=gameState.boardPieces[2,0]*0.1
        result+=gameState.boardPieces[2,2]*0.1
        return (result,[0.1]*(_V*_H*(_V+_H)))
        
    def saveImages(self,boardImages,otherImages,targets):
        return 0