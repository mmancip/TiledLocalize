#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

with open("nodes.json",'r') as nodesf:
    nodes=json.load(nodesf)

with open("tiledset.json") as nodes_json:
    tiles   = json.load(nodes_json)
    
i=0
for tile in tiles["nodes"]:
    if (str(i) in nodes["YOLO"]):
        tile["comment"]=tile["comment"]+" YOLO="+str(nodes["YOLO"][str(i)])
    i=i+1 


with open("tiledset_.json",'w') as tiledset_f:
        tiledset_f.write(json.dumps(tiles))
