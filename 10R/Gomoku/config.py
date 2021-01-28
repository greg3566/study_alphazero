_Name='Gomoku'
_V=6
_H=7
_A=_V*_H

_N=4
_Gravity=True

_LM=_H if _Gravity else _V*_H #typical legal moves
_GL=_V*_H #typical game length
_F=(_V+_H)*2+2 #number of filters for neural network

_CB=2
_CO=0

def pindex2key(pindex,player):
    v0=pindex//_H
    h0=pindex%_H
    if player==False:
        h0=_H-1-h0
    return (v0,h0)

def key2pindex(key,player):
    v0,h0=key
    if player==False:
        h0=_H-1-h0
    return v0*_H+h0