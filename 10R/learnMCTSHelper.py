from game import Game, GameState
from agentMCTS import AgentMCTS
import time
from shutil import copyfile

def checkBest(bipredictor,bipredictorBest,depth):
    
    try:
        open(bipredictorBest.fname,'rb').close()
    except:
        print('make predictorBest')
        copyfile(bipredictor.fname, bipredictorBest.fname)
        return None
    
    agent=AgentMCTS(bipredictor=bipredictor, depth=depth, temperature=0.001, noise=0, saveImage=False, printValue=False)
    agentBest=AgentMCTS(bipredictor=bipredictorBest, depth=depth, temperature=0.001, noise=0, saveImage=False, printValue=False)
    winCount=0
    for ii in range(2):
        game=Game(agent,agentBest,printBoard=False)
        i=0
        t=time.time()
        while not game.gameState.isEnd:
            print(i,end=' ')
            #print("th turn : ")
            game.step()
            i+=1
            #print(time.time()-t)
        print("end")
        print(game.gameState.winner)
        winCount+=-game.gameState.winner
        game.reset()

        game=Game(agentBest,agent,printBoard=False)
        i=0
        t=time.time()
        while not game.gameState.isEnd:
            print(i,end=' ')
            #print("th turn : ")
            game.step()
            i+=1
            #print(time.time()-t)
        print("end")
        print(game.gameState.winner)
        winCount+=game.gameState.winner
        game.reset()
        agent.depth*=2
        agentBest.depth*=2
    if winCount>0:
        print("good")
        copyfile(bipredictor.fname, bipredictorBest.fname)
        bipredictorBest.model.load_weights(bipredictorBest.fname)
    elif winCount==0:
        print("soso****")
    else:
        print("not good")
        copyfile(bipredictorBest.fname, bipredictor.fname)
        bipredictor.model.load_weights(bipredictor.fname)