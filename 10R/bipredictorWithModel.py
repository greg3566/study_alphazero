import numpy as np
import tensorflow as tf
import random
from collections import deque
from bipredictor import Bipredictor
from config import _V, _H, _A, _GL, _CB, _CO

memorySize=_GL*64

class BipredictorWithModel(Bipredictor):
    def __init__(
                 self,filters=64, conv_kernel_size=3, 
                 res_kernel_size=3,res_block_size=8, 
                 c_reg=0.0001,momentum=0.9, lr=0.001,
                 epochs=1, batch_size=None, fname='latest_weight.h5'
                ):
        super().__init__()
        self.epochs=epochs
        self.batch_size=batch_size
        self.fname=fname
        
        self.bm=Residual_CNN(
                             filters=filters,
                             conv_kernel_size=conv_kernel_size,
                             res_kernel_size=res_kernel_size,
                             res_block_size=res_block_size,
                             c_reg=c_reg, momentum=momentum,
                             lr=lr
                            )
        
        self.model=self.bm.build_model()
        
        try:
            self.model.load_weights(self.fname)
        except (OSError, IOError) as e:
            print(e)
        except Exception as e:
            print(e)
        
        self.images=deque(maxlen=memorySize)
        self.zs=deque(maxlen=memorySize)
        self.policys=deque(maxlen=memorySize)
        
#         a=np.array(range(_A))
#         r=np.reshape(a,(_V,_H,_V+_H))
#         rv=np.flip(r,0)
#         iv=np.argsort(list(range(_V-1,-1,-1))+list(range(_V,_V+_H)))
#         rv=rv[:,:,iv]
#         self.argflip_v=np.argsort(np.reshape(rv,_A))
#         rh=np.flip(r,1)
#         ih=np.argsort(list(range(_V))+list(range(_V+_H-1,_V-1,-1)))
#         rh=rh[:,:,ih]
#         self.argflip_h=np.argsort(np.reshape(rh,_A))
        
        
    def predict(self,tempGameState):
        boardImages=np.expand_dims(tempGameState.board2Binary(), axis=0)
        otherImages=np.expand_dims(tempGameState.other2Binary(), axis=0)
        v,p=self.model.predict(
                               np.append(boardImages, otherImages, axis=1)
                              )
        if v[0]<-1 or v[0]>1:
            print("value is out of range",v[0])
        return (v[0]*tempGameState.bool2sign(tempGameState.currentPlayer),p[0])
    
    def saveImages(self, boardImages, otherImages, zs, policys):
        self.images.extend(
                           map(
                               lambda x:np.append(x[0],x[1],axis=0),
                               zip(boardImages,otherImages)
                              )
                          )
        self.zs.extend(zs)
        self.policys.extend(policys)
#         if len(self.zs)>=memorySize:
#             self.learnImage()
    
    def learnImage(self,onlyOnce=False):
        l=len(self.zs)
        print(l)
        batch_size=32 if self.batch_size==None else self.batch_size
        if l>=batch_size:
            arg=np.random.choice(l,max(l//8,batch_size),replace=False)
            images=np.array(self.images)[arg]
            zs=np.array(self.zs)[arg]
            policys=np.array(self.policys)[arg]
            print(len(zs))
#             images=np.append(images,np.flip(images,2),axis=0)
#             zs=np.append(zs,zs)
#             policys=np.append(policys,policys[:,self.argflip_v],axis=0)
            
            if onlyOnce==True:
                self.model.fit(images, [zs,policys], batch_size=len(arg), epochs=1)
            else:
                self.model.fit(images, [zs,policys], batch_size=len(arg), epochs=self.epochs)
            
            self.model.save_weights(self.fname)
            
#         self.images.clear()
#         self.zs.clear()
#         self.policys.clear()
        
        
class Residual_CNN:
    def __init__(self,filters=64, conv_kernel_size=3, 
                 res_kernel_size=3,res_block_size=8, 
                 c_reg=0.0001,momentum=0.9, lr=0.001
                ):
        self.filters = filters
        self.conv_kernel_size = conv_kernel_size
        self.res_kernel_size = res_kernel_size
        self.res_block_size = res_block_size
        self.c_reg = c_reg
        self.momentum = momentum
        self.lr = lr
        
    def batchNormalizedConv2D(self,x,filters,kernel_size,c_reg):
        x = tf.keras.layers.Conv2D(filters=filters, kernel_size=kernel_size, 
                                   data_format="channels_first", padding='same', use_bias=False, 
                                   kernel_initializer='he_normal', 
                                   kernel_regularizer=tf.keras.regularizers.l2(c_reg)
                                  )(x)
        x = tf.keras.layers.BatchNormalization(axis=1)(x)
        return x
        
    def conv_layer(self, x):
        x = self.batchNormalizedConv2D(x,self.filters,self.conv_kernel_size,self.c_reg)
        x = tf.keras.layers.LeakyReLU()(x)
        return x
    
    def res_layer(self,x):
        y = self.batchNormalizedConv2D(x,self.filters,self.res_kernel_size,self.c_reg)
        y = tf.keras.layers.LeakyReLU()(y)
        y = self.batchNormalizedConv2D(y,self.filters,self.res_kernel_size,self.c_reg)
        x = tf.keras.layers.add([x,y])
        x = tf.keras.layers.LeakyReLU()(x)
        return x
    
    def value_head(self,x):
        x = self.batchNormalizedConv2D(x,1,1,self.c_reg)
        x = tf.keras.layers.LeakyReLU()(x)
        x = tf.keras.layers.Flatten()(x)
        x = tf.keras.layers.Dense(self.filters, use_bias=False,
                                  kernel_initializer='he_normal', 
                                  kernel_regularizer=tf.keras.regularizers.l2(self.c_reg)
                                 )(x)
        x = tf.keras.layers.LeakyReLU()(x)
        x = tf.keras.layers.Dense(1, activation="tanh", use_bias=False, 
                                  kernel_regularizer=tf.keras.regularizers.l2(self.c_reg),
                                  name='value_head'
                                 )(x)
        return x
    
    def policy_head(self,x):
        x = self.batchNormalizedConv2D(x,2,1,self.c_reg)
        x = tf.keras.layers.LeakyReLU()(x)
        x = tf.keras.layers.Flatten()(x)
        x = tf.keras.layers.Dense(_A, use_bias=False, 
                                  kernel_regularizer=tf.keras.regularizers.l2(self.c_reg),
                                 )(x)
        x=tf.keras.layers.Softmax(name='policy_head')(x)
        return x
        
    def build_model(self):
        x=tf.keras.layers.Input(shape = (_CB+_CO,_V,_H))
        y=self.conv_layer(x)
        for i in range(self.res_block_size):
            y=self.res_layer(y)
        vh=self.value_head(y)
        ph=self.policy_head(y)
        model = tf.keras.models.Model(x, [vh,ph])
        model.compile(loss={'value_head':'mean_squared_error','policy_head':'categorical_crossentropy'}, 
                      #optimizer=tf.keras.optimizers.SGD(lr=self.lr, momentum=self.momentum)
                      optimizer=tf.keras.optimizers.Adam(lr=self.lr, beta_1=self.momentum),
                      loss_weights={'value_head': 0.5, 'policy_head': 0.5}
                     )
        return model