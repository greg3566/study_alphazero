_Name='6R'
_V=5
_H=10
_A=_V*_H*(_V+_H)

_CB=4
_CO=1

_HB=2
_NPCM=6

# _Name='10R'
# _V=7
# _H=11
# _A=_V*_H*(_V+_H)

# _CB=4
# _CO=1

# _HB=2
# _NPCM=6

_LM=_V*2 #typical legal moves
_GL=(_V-2)*(_H-_HB+_NPCM) #typical game length
_F=(_V+_H)*2+2

def pindex2key(pindex,player):
    dc1=pindex%(_V+_H)
    if dc1<_V:
        d='V'
        c1=dc1
    else:
        d='H'
        c1=dc1-_V
        if player==False:
            c1=_H-1-c1
    v0h0=pindex//(_V+_H)
    v0=v0h0//_H
    h0=v0h0%_H
    if player==False:
        h0=_H-1-h0
    return (v0,h0,d,c1)

def key2pindex(key,player):
    v0,h0,d,c1=key
    if player==False:
        h0=_H-1-h0
    if d=='V':
        dc1=c1
    else:
        if player==False:
            c1=_H-1-c1
        dc1=c1+_V
    return (v0*_H+h0)*(_V+_H)+dc1