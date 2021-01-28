_N=3

_Name='Tictactoe'
_V=_N
_H=_N
_A=_V*_H

_Gravity=False

_LM=_N if _Gravity else _N*_N #typical legal moves
_GL=_N*_N #typical game length
_F=2*_N+2 #number of filters for neural network

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