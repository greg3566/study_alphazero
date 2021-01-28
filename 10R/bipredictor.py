from game import GameState
import random
from config import _V, _H, _A, _LM

class Bipredictor():
    def __init__(self):
        return None
    
    def predict(self,gameState):
        if gameState.isEnd==False:
            return (0,[1/_LM]*_A)
        else:
            return gameState.winner
        
    def saveImages(self,boardImages,otherImages,targets):
        return 0
    
    
class BipredictorWithGuide(Bipredictor):
    def __init__(self,guide):
        super().__init__()
        self.guide=guide
        
    def predict(self,tempGameState):
        return (self.guide.predict(tempGameState),[1/_LM]*_A )
    
class BipredictorRandom(Bipredictor):
    def __init__(self):
        super().__init__()
        
    def predict(self,tempGameState):
        v=random.uniform(-1,1)
        p=[]
        for i in range(_A):
            p.append(random.uniform(0,0.2))
        return (v,p)
    