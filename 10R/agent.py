import numpy as np
from game import GameState
import random

class Agent():
    def __init__(self):
        self.gameState=None
        
    def selectMove(self):
        print("wrong agent")
        
    def end(self):
        return 0
    
    def fetch(self,currentMove):
        return 0

class AgentHuman(Agent):
    def selectMove(self):
        return self.gameState.cs2Is(input())
    
class AgentRandom(Agent):
    def selectMove(self):
        return random.choice(list(self.gameState.possibleMoves.keys()))