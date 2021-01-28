from bipredictorWithModel import BipredictorWithModel
import numpy as np
from config import _V, _H, _A, _GL, _CB, _CO

memorySize=_GL*32

class BipredictorWithModelAndGuide(BipredictorWithModel):
    def __init__(
                 self,filters=64, conv_kernel_size=3, 
                 res_kernel_size=3,res_block_size=8, 
                 c_reg=0.0001,momentum=0.9, lr=0.001,
                 epochs=1, batch_size=None, fname='latest_weight.h5',
                 guide=None, guideRatio=0.33
                ):
        super().__init__(
                         filters, conv_kernel_size, 
                         res_kernel_size, res_block_size,
                         c_reg, momentum, lr,
                         epochs, batch_size, fname
                        )
        self.guide=guide
        self.guideRatio=guideRatio
        
    def predict(self,tempGameState):
        boardImages=np.expand_dims(tempGameState.board2Binary(), axis=0)
        otherImages=np.expand_dims(tempGameState.other2Binary(), axis=0)
        v,p=self.model.predict(
                               np.append(boardImages, otherImages, axis=1)
                              )
        if v[0]<-1 or v[0]>1:
            print("value is out of range",v[0])
        
        v_guide=self.guide.predict(tempGameState)
        v_mean=(v[0]*tempGameState.bool2sign(tempGameState.currentPlayer)+v_guide*self.guideRatio)/(1+self.guideRatio)
        return (v_mean,p[0])