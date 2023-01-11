#!/usr/bin/env python3
import os,sys,socket

NUM_DOCKERS=int(sys.argv[1])

listwss="list_wss";
with open(listwss,'w') as fwss:
    for d in range(NUM_DOCKERS):
        s=socket.socket();
        s.bind(("", 0));
        WSS_PORT=s.getsockname()[1];
        s.close();
        fwss.write(str(WSS_PORT)+"\n")
