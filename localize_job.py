#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import sys,os,time
import code
import argparse
import re, datetime
import inspect

# sys.path.append(os.path.realpath('/TiledViz/TVConnections/'))
# from connect import sock

import json
    
if (os.path.exists("config.tar")):
    os.system("tar xf config.tar")

SITE_config='./site_config.ini'
CASE_config="./case_config.ini"

actions_file=open("/home/myuser/actions.json",'r')
tiles_actions=json.load(actions_file)
#launch_actions()

config = configparser.ConfigParser()
config.optionxform = str

config.read(SITE_config)

TILEDOCKERS_path=config['SITE']['TILEDOCKER_DIR']
DOCKERSPACE_DIR=config['SITE']['DOCKERSPACE_DIR']
DOMAIN=config['SITE']['DOMAIN']
#NOVNC_URL=config['SITE']['NOVNC_URL']
GPU_FILE=config['SITE']['GPU_FILE']

SSH_FRONTEND=config['SITE']['SSH_FRONTEND']
SSH_LOGIN=config['SITE']['SSH_LOGIN']
SSH_IP=config['SITE']['SSH_IP']
init_IP=config['SITE']['init_IP']

config.read(CASE_config)

CASE=config['CASE']['CASE_NAME']
NUM_DOCKERS=int(config['CASE']['NUM_DOCKERS'])

CASE_DOCKER_PATH=config['CASE']['CASE_DOCKER_PATH']

network=config['CASE']['network']
nethost=config['CASE']['nethost']
domain=config['CASE']['domain']

OPTIONssh=config['CASE']['OPTIONssh']
SOCKETdomain=config['CASE']['SOCKETdomain']

DOCKER_NAME=config['CASE']['DOCKER_NAME']

DATA_PATH=config['CASE']['DATA_PATH']
DATA_MOUNT_DOCKER=config['CASE']['DATA_MOUNT_DOCKER']
DATA_PATH_DOCKER=config['CASE']['DATA_PATH_DOCKER']

OPTIONS=config['CASE']['OPTIONS'].replace("$","").replace('"','')
print("\nOPTIONS from CASE_CONFIG : "+OPTIONS)
def replaceconf(x):
    if (re.search('}',x)):
        varname=x.replace("{","").replace("}","")
        return config['CASE'][varname]
    else:
        return x
OPTIONS=OPTIONS.replace("JOBPath",JOBPath)
OPTIONS=OPTIONS.replace('{','|{').replace('}','}|').split('|')
OPTIONS="".join(list(map( replaceconf,OPTIONS)))


CreateTS='create TS='+TileSet+' Nb='+str(NUM_DOCKERS)

client.send_server(CreateTS)

# # get TiledAstrochem package from Github
# COMMAND_GIT="git clone https://github.com/mmancip/TiledAstrochem.git"
# print("command_git : "+COMMAND_GIT)
# os.system(COMMAND_GIT)

# # get TiledAstrochem package from Github
# COMMAND_TAG="bash -c 'cd TiledAstrochem; git checkout SSL'"
# print("command_git : "+COMMAND_TAG)
# os.system(COMMAND_TAG)

# Global commands
# Execute on each/a set of tiles
ExecuteTS='execute TS='+TileSet+" "
# Launch a command on the frontend
LaunchTS='launch TS='+TileSet+" "+JOBPath+' '

# Build VMD dir
# client.send_server(LaunchTS+" mkdir "+CASE)
# print("Out of mkdir %s : %s" % (CASE, str(client.get_OK())))

# Send CASE and SITE files
try:
    client.send_server(LaunchTS+' chmod og-rxw '+JOBPath)
    print("Out of chmod JOBPath : "+ str(client.get_OK()))
    
    send_file_server(client,TileSet,".", CASE_config, JOBPath)
    CASE_config=os.path.join(JOBPath,CASE_config)
    send_file_server(client,TileSet,".", SITE_config, JOBPath)
    SITE_config=os.path.join(JOBPath,os.path.basename(SITE_config))
    send_file_server(client,TileSet,".", "tiledset.json", JOBPath)
    send_file_server(client,TileSet,".", "list_hostsgpu", JOBPath)

except:
    print("Error sending files !")
    traceback.print_exc(file=sys.stdout)
    try:
        code.interact(banner="Try sending files by yourself :",local=dict(globals(), **locals()))
    except SystemExit:
        pass



# COMMAND_TiledAstrochem=LaunchTS+COMMAND_GIT
# client.send_server(COMMAND_TiledAstrochem)
# print("Out of git clone TiledAstrochem : "+ str(client.get_OK()))

# COMMAND_TiledAstrochem=LaunchTS+COMMAND_TAG
# client.send_server(COMMAND_TiledAstrochem)
# print("Out of git tag SSL : "+ str(client.get_OK()))

# COMMAND_copy=LaunchTS+"cp -rp TiledAstrochem/labelImg_client "+\
#               "TiledAstrochem/kill_labelImg "+\
#               "TiledAstrochem/build_nodes_file "+\
#               "TiledAstrochem/label.py "+\
#                 "./"

# client.send_server(COMMAND_copy)
# print("Out of copy scripts from TiledCourse : "+ str(client.get_OK()))

try:
    send_file_server(client,TileSet,".", "labelImg_client", JOBPath)
    send_file_server(client,TileSet,".", "kill_labelImg", JOBPath)
    send_file_server(client,TileSet,".", "build_nodes_file", JOBPath)
    send_file_server(client,TileSet,".", "label.py", JOBPath)
    send_file_server(client,TileSet,".", "classes.txt", JOBPath)
    
except:
    print("Error sending files !")
    traceback.print_exc(file=sys.stdout)

# Launch containers HERE
REF_CAS=str(NUM_DOCKERS)+" "+DATE+" "+DOCKERSPACE_DIR+" "+DOCKER_NAME
TiledSet=list(range(NUM_DOCKERS))

print("\nREF_CAS : "+REF_CAS)

COMMANDStop=os.path.join(TILEDOCKERS_path,"stop_dockers")+" "+REF_CAS+" "+os.path.join(JOBPath,GPU_FILE)
print("\n"+COMMANDStop)
sys.stdout.flush()

# Launch dockers
stateVM=True
def Run_dockers():
    global stateVM
    COMMAND="bash -c \""+os.path.join(TILEDOCKERS_path,"launch_dockers")+" "+REF_CAS+" "+GPU_FILE+" "+SSH_FRONTEND+":"+SSH_IP+\
             " "+network+" "+nethost+" "+domain+" "+init_IP+" TileSetPort "+UserFront+"@"+Frontend+" "+OPTIONS+\
             " > "+os.path.join(JOBPath,"output_launch")+" 2>&1 \"" 

    print("\nCommand dockers : "+COMMAND)

    client.send_server(LaunchTS+' '+COMMAND)
    state=client.get_OK()
    stateVM=stateVM and (state == 0)
    print("Out of launch docker : "+ str(state))
    sys.stdout.flush()

Run_dockers()
sys.stdout.flush()

with open("tiledset.json") as nodes_json:
    tilednodes   = json.load(nodes_json)["nodes"]


# Build nodes.json file from new dockers list
def build_nodes_file():
    global stateVM
    print("Build nodes.json file from new dockers list.")
    # COMMAND=LaunchTS+' chmod u+x build_nodes_file '
    # client.send_server(COMMAND)
    # print("Out of chmod build_nodes_file : "+ str(client.get_OK()))

    COMMAND=LaunchTS+' ./build_nodes_file '+os.path.join(JOBPath,CASE_config)+' '+os.path.join(JOBPath,SITE_config)+' '+TileSet
    print("\nCommand dockers : "+COMMAND)

    client.send_server(COMMAND)
    state=client.get_OK()
    stateVM=stateVM and (state == 0)
    print("Out of build_nodes_file : "+ str(state))
    time.sleep(2)

if (stateVM):
    build_nodes_file()
sys.stdout.flush()
#get_file_client(client,TileSet,JOBPath,"nodes.json",".")

time.sleep(2)
# Launch docker tools
def launch_resize(RESOL="1280x800"): #"1440x900"
    client.send_server(ExecuteTS+' bash -c "export DISPLAY=:1; xrandr --fb '+RESOL+'"')
    state=client.get_OK()
    print("Out of xrandr : "+ str(state))

if (stateVM):
    launch_resize()

def launch_tunnel():
    global stateVM
    # Call tunnel for VNC
    client.send_server(ExecuteTS+' /opt/tunnel_ssh '+SSH_FRONTEND+' '+SSH_LOGIN)
    state=client.get_OK()
    stateVM=stateVM and (state == 0)
    print("Out of tunnel_ssh : "+ str(state))
    if (not stateVM):
        return

    commandTestFreePort="ssh "+SSH_LOGIN+"@"+SSH_FRONTEND+''' \'bash -c "echo \\$(python -c \\\"import socket; s=socket.socket(); s.bind((\\\\\\"\\\\\\", 0)); print(s.getsockname()[1]); s.close();\\\" )"\' > .vnc/port_wss'''
    client.send_server(ExecuteTS+commandTestFreePort)
    state=client.get_OK()
    stateVM=stateVM and (state == 0)
    print("Out of get WSS PORT : "+ str(state))
    if (not stateVM):
        return

    # Get back PORT
    for i in range(NUM_DOCKERS):
        i0="%0.3d" % (i+1)
        TILEi=ExecuteTS+' Tiles=('+containerId(i+1)+') '
        SSH_JobPath=SSH_LOGIN+"@"+SSH_FRONTEND+":"+JOBPath
        COMMANDi="bash -c \"while ( [ ! -f .vnc/port_wss ] ); do sleep 2; ls -la .vnc; done;"+\
                  " export PORT=\$(cat .vnc/port); "+\
                  " export PORTWSS=\$(cat .vnc/port_wss); "+\
                  " scp "+SSH_JobPath+"/nodes.json CASE/ ;"+\
                  " sed -e 's#port="+SOCKETdomain+i0+"#port='\$PORTWSS'#' -i CASE/nodes.json; "+\
                  " scp CASE/nodes.json "+SSH_JobPath+"/ ;"+\
                  " ssh "+SSH_LOGIN+"@"+SSH_FRONTEND+''' \' bash -c \\\" cd '''+TILEDOCKERS_path+"/..; "+\
                  "    ./wss_websockify /etc/letsencrypt/archive/mdls.fr/fullchain2.pem /etc/letsencrypt/archive/mdls.fr/privkey2.pem "+''' \'\$PORTWSS\' \'\$PORT\' '''+TILEDOCKERS_path+"/../../TVWeb &"+\
                  ''' \\\"\' & ''' +\
                  "\""
        #"    LOG=/tmp/websockify_"+i0+"_\\\$(date +%F_%H-%M-%S).log; pwd > \\\\\$LOG;"+\
        #'''  pgrep -f \\\\\".*websockify.*\'\$PORTWSS\'\\\\\" >> \\\\\$LOG'''+\
        # TODO : DOC install noVNC on web server
        # pushd TILEDOCKERS_path+"/../../TVWeb
        # git clone https://github.com/novnc/noVNC.git noVNC
        # cd noVNC
        # git checkout 33e1462

        print("%s | %s" % (TILEi, COMMANDi)) 
        sys.stdout.flush()
        client.send_server(TILEi+COMMANDi)
        state=client.get_OK()
        stateVM=stateVM and (state == 0)
        print("Out of change port %s : %s" % (i0,state))
        sys.stdout.flush()
        if (state != 0):
            break

    if (not stateVM):
        return

    sys.stdout.flush()
    if (not stateVM):
        return
    launch_nodes_json()

if (stateVM):
    launch_tunnel()
sys.stdout.flush()

nodesf=open("nodes.json",'r')
nodes=json.load(nodesf)
nodesf.close()    

def launch_vnc():
    global stateVM
    client.send_server(ExecuteTS+' /opt/vnccommand')
    state=client.get_OK()
    stateVM=stateVM and (state == 0)
    print("Out of vnccommand : "+ str(state))

if (stateVM):
    launch_vnc()

def get_old_YOLO(tile,nodeRead,TilesStr):
    file_name=os.path.basename(tile["url"])
    try:
        if (len(tile["comment"].split("YOLO"))>1):
            tileyolo=eval(tile["comment"].split("YOLO=")[1])
            OUT_YOLO=file_name.split('png')[0]+'txt'

            #TODO : test and change for multiple box on one image cf l437
            with open("classes_"+OUT_YOLO,'w') as classef:
                with open(OUT_YOLO,'w') as out_yolof:
                    for i in range(len(tileyolo)):
                        if (i<len(tileyolo)/2):
                            classef.write(f"{tileyolo[i]}"+"\n")
                        else:
                            out_yolof.write(f"{tileyolo[i]}"+"\n")
            
            send_file_server(client,TileSet,".", "classes_"+OUT_YOLO, JOBPath)
            send_file_server(client,TileSet,".", OUT_YOLO, JOBPath)
            COMMANDi=ExecuteTS+TilesStr+" mv -f "+os.path.join("CASE","classes_"+OUT_YOLO)+" ./.vnc/classes.txt"
            print("%s move old classes command : %s" % (TilesStr,COMMANDi))
            client.send_server(COMMANDi)
            client.get_OK()
            COMMANDi=ExecuteTS+TilesStr+" mv -f "+os.path.join("CASE",OUT_YOLO)+" .vnc/"
            print("%s move old labels command : %s" % (TilesStr,COMMANDi))
            client.send_server(COMMANDi)
            client.get_OK()
    except:
        print("Error get_old_YOLO(tile %s,nodeRead %d) !" % (tile["title"],nodeRead))
        traceback.print_exc(file=sys.stdout)

    
nodeRead=0
def launch_one_client(script='labelImg_client',tileNum=-1,tileId='001'):
    global nodeRead
    tile=tilednodes[nodeRead]
    if ( tileNum > -1 ):
        TilesStr=' Tiles=('+containerId(tileNum+1)+') '            
    else:
        TilesStr=' Tiles=('+tileId+') '

    get_old_YOLO(tile,nodeRead,TilesStr)
        
    file_name=os.path.basename(tile["url"])
    dir_name=os.path.basename(os.path.dirname(tile["url"]))
    
    COMMANDi=ExecuteTS+TilesStr+" cp "+os.path.join("/datas/"+dir_name,file_name)+" "+os.path.join("/home/myuser/.vnc/",file_name)
    print("%s copy input file command : %s" % (TilesStr,COMMANDi))
    client.send_server(COMMANDi)
    client.get_OK()

    COMMAND=' '+os.path.join(CASE_DOCKER_PATH,script)+" "+os.path.join("/home/myuser/.vnc/",file_name)

    print("%s labelImg command : %s" % (TilesStr,COMMAND))
    CommandTS=ExecuteTS+TilesStr+COMMAND
    client.send_server(CommandTS)
    client.get_OK()
    nodeRead=nodeRead+1
    
# TODO : give a list of lines !
def Run_clients():
    for i in range(NUM_DOCKERS):
        launch_one_client(tileNum=i)
    Last_Elt=NUM_DOCKERS-1

if (stateVM):
    Run_clients()
sys.stdout.flush()

def next_element(script='labelImg_client',tileNum=-1,tileId='001'):
    global TiledSet,nodeRead
    try:
        tile=tilednodes[nodeRead]
        COMMANDKill=' '+CASE_DOCKER_PATH+"kill_labelImg"
        if ( tileNum > -1 ):
            tileId=containerId(tileNum+1)
        else:
            tileNum=int(tileId)-1 
        TiledSet[tileNum]=nodeRead
        TilesStr=' Tiles=('+tileId+') '

        file_name=os.path.basename(tile["url"])
        dir_name=os.path.basename(os.path.dirname(tile["url"]))
    
        COMMANDi=ExecuteTS+TilesStr+" cp "+os.path.join("/datas/"+dir_name,file_name)+" "+os.path.join("/home/myuser/.vnc/",file_name)
        print("%s copy input file command : %s" % (TilesStr,COMMANDi))
        client.send_server(COMMANDi)
        client.get_OK()

        COMMAND=' '+os.path.join(CASE_DOCKER_PATH,script)+" "+os.path.join("/home/myuser/.vnc/",file_name)
        print("%s labelImg command : %s" % (TilesStr,COMMAND))

        CommandTSK=ExecuteTS+TilesStr+COMMANDKill
        client.send_server(CommandTSK)
        client.get_OK()
    
        get_old_YOLO(tile,nodeRead,TilesStr)

        CommandTS=ExecuteTS+TilesStr+COMMAND
        client.send_server(CommandTS)
        client.get_OK()
        
        nodes["nodes"][tileNum]["title"]=tileId+" "+file_name
        if ("variable" in nodes["nodes"][tileNum]):
            nodes["nodes"][tileNum]["variable"]="ID-"+tileId+"_"+file_name
            nodes["nodes"][tileNum]["comment"]=tile["comment"]
        if ("usersNotes" in nodes["nodes"][tileNum]):
            nodes["nodes"][tileNum]["usersNotes"]=re.sub(r'file .*',"file "+os.path.join(dir_name,file_name),
                                                     nodes["nodes"][tileNum]["usersNotes"])+" tilenum "+str(nodeRead)
        nodes["nodes"][tileNum]["tags"]=tile["tags"]
        nodes["nodes"][tileNum]["tags"].append(TileSet)

        nodesf=open("nodes.json",'w')
        nodesf.write(json.dumps(nodes))
        nodesf.close()
        nodeRead=nodeRead+1
    except:
        print("No more next element for : %d" % (nodeRead))


def re_initialization():
    global nodeRead
    nodeRead=0
    for i in range(NUM_DOCKERS):
        next_element(tileNum=i)
    sys.stdout.flush()

def collect_all_Yolo():
    for i in range(NUM_DOCKERS):
        collect_Yolo(tileNum=i)
    launch_nodes_json()
        
def collect_Yolo(tileNum=-1,tileId='001'):
    if ( tileNum > -1 ):
        DOCKERID=containerId(tileNum+1)
        TilesStr=' Tiles=('+DOCKERID+') '
    else:
        DOCKERID=tileId
        TilesStr=' Tiles=('+tileId+') '
        # FAUX !! après des next ce n'est plus forcément le cas...
        tileNum=int(tileId)-1 
    tile=tilednodes[TiledSet[tileNum]]
    #file_name=tile["comment"].split('png')[0]+'txt'
    file_name=os.path.basename(tile["url"])
    OUT_YOLO=file_name.split('png')[0]+'txt'
    #COMMAND=' cat /home/myuser/.vnc/classes.txt /home/myuser/.vnc/'+OUT_YOLO+' > /home/myuser/CASE/'+DOCKERID+'_'+OUT_YOLO
    COMMAND=' for f in \"/home/myuser/.vnc/classes.txt\" \"/home/myuser/.vnc/'+OUT_YOLO+'\"; do (cat "${f}"; echo); done > /home/myuser/CASE/'+DOCKERID+'_'+OUT_YOLO
    print("%s move YOLO output command : %s" % (TilesStr,COMMAND))
    CommandTS=ExecuteTS+TilesStr+COMMAND
    client.send_server(CommandTS)
    client.get_OK()

    YOLO_local_file=str(TiledSet[tileNum])+'_'+OUT_YOLO
    get_file_client(client,TileSet,JOBPath,DOCKERID+'_'+OUT_YOLO,".")
    os.system("mv "+DOCKERID+'_'+OUT_YOLO+" "+YOLO_local_file)

    out={}
    with open(YOLO_local_file,'r') as yolof:
        lines=yolof.read().split("\n")
        out[str(TiledSet[tileNum])]=list(filter(None,lines))
        
    print("YOLO out :"+str(out))

    # Test if YOLO definition is already in input tiledset 
    # if (len(tile["comment"].split("YOLO="))>1):
    #     tilecomment=eval(tile["comment"].split("YOLO=")[1])
    # else:
    #     tilecomment=[]

    # List of new or old YOLO definitions 
    yololist=out[str(TiledSet[tileNum])]
    tilednodes[TiledSet[tileNum]]["comment"]=tile["comment"].split("YOLO=")[0]+"YOLO="+str(yololist)
    
    with open("nodes.json",'r') as nodesf:
        nodes=json.load(nodesf)
        if ("YOLO" in nodes):
            nodes["YOLO"]=dict(nodes["YOLO"],**out)
        else:
            nodes["YOLO"]=out
        nodes["tiledset"]=tilednodes

    print("New nodes YOLO : "+str(nodes["YOLO"]))

    with open("nodes.json",'w') as nodesf:
        nodesf.write(json.dumps(nodes))

    print("nodes.json saved.")
    
def init_wmctrl():
    client.send_server(ExecuteTS+' wmctrl -l -G')
    print("Out of wmctrl : "+ str(client.get_OK()))

if (stateVM):
    init_wmctrl()

def clear_vnc(tileNum=-1,tileId='001'):
    if ( tileNum > -1 ):
        TilesStr=' Tiles=('+containerId(tileNum+1)+') '
    else:
        TilesStr=' Tiles=('+tileId+') '
    client.send_server(ExecuteTS+TilesStr+' x11vnc -R clear-all')
    print("Out of clear-vnc : "+ str(client.get_OK()))

def clear_vnc_all():
    os.system('x11vnc -R clear-all')
    for i in range(NUM_DOCKERS):
        clear_vnc(i)
        #clear_vnc(tileId=containerId(i))

if (stateVM):
    clear_vnc_all()

    
def save_all(tileNum=-1,tileId='001'):
    if ( tileNum > -1 ):
        TilesStr=' Tiles=('+containerId(tileNum+1)+') '
        click_point(tileNum=tileNum,X=64,Y=468)
    else:
        TilesStr=' Tiles=('+tileId+') '
        click_point(tileId=tileId,X=64,Y=468)
    COMMAND=" xdotool key --window $(xdotool search --name label) s "
    client.send_server(ExecuteTS+TilesStr+COMMAND)
    print("Out of save_all %s : %s" % (TilesStr,str(client.get_OK())))
    
def fit_to_window(tileNum=-1,tileId='001'):
    if ( tileNum > -1 ):
        TilesStr=' Tiles=('+containerId(tileNum+1)+') '
    else:
        TilesStr=' Tiles=('+tileId+') '
    COMMAND=" xdotool key --window $(xdotool search --name label) 'ctrl+f' "
    client.send_server(ExecuteTS+TilesStr+COMMAND)
    print("Out of fit_to_window %s : %s" % (TilesStr,str(client.get_OK())))
    
def click_point(tileNum=-1,tileId='001',X=0,Y=0):
    if ( tileNum > -1 ):
        TilesStr=' Tiles=('+containerId(tileNum+1)+') '
    else:
        TilesStr=' Tiles=('+tileId+') '
    COMMAND=" xdotool mousemove "+str(X)+" "+str(Y)+" click 1 mousemove restore"
    # -> xdotool getmouselocation
    client.send_server(ExecuteTS+TilesStr+COMMAND)
    print("Out of click_point : "+ str(client.get_OK()))


def new_rect(tileNum=-1,tileId='001'):
    x=525
    y=360 
    if ( tileNum > -1 ):
        #fullscreenApp(windowname="labelImg",tileNum=-1)
        click_point(tileNum=tileNum,X=x,Y=y)
        TilesStr=' Tiles=('+containerId(tileNum+1)+') '
    else:
        click_point(tileId=tileId,X=x,Y=y)
        TilesStr=' Tiles=('+tileId+') '
    COMMAND=" xdotool key --window $(xdotool search --name label) W "
    client.send_server(ExecuteTS+TilesStr+COMMAND)
    print("Out of new_rect %s : %s" % (TilesStr,str(client.get_OK())))


def toggle_fullscr():
    for i in range(NUM_DOCKERS):
        fullscreenApp(windowname="labelImg",tileNum=i)

def launch_changesize(RESOL="1920x1080",tileNum=-1,tileId='001'):
    if ( tileNum > -1 ):
        TilesStr=' Tiles=('+containerId(tileNum+1)+') '
    else:
        TilesStr=' Tiles=('+tileId+') '
    COMMAND=ExecuteTS+TilesStr+' xrandr --fb '+RESOL
    print("call server with : "+COMMAND)
    client.send_server(COMMAND)
    print("server answer is "+str(client.get_OK()))

def launch_smallsize(tileNum=-1):
    print("Launch launch_changesize smallsize for tile "+str(tileNum))
    launch_changesize(tileNum=tileNum,RESOL="950x420")

def launch_bigsize(tileNum=-1):
    print("Launch launch_changesize bigsize for tile "+str(tileNum))
    launch_changesize(tileNum=tileNum,RESOL="1920x1200")

def fullscreenApp(windowname="labelImg",tileNum=-1,tileId='001'):
    if ( tileNum > -1 ):
        movewindows(windowname=windowname,wmctrl_option='toggle,fullscreen',tileNum=tileNum)
    else:
        movewindows(windowname=windowname,wmctrl_option='toggle,fullscreen',tileId=tileId)
    
def movewindows(windowname="labelImg",wmctrl_option='toggle,fullscreen',tileNum=-1,tileId='001'):
    COMMAND='/opt/movewindows '+windowname+' -b '+wmctrl_option
    #remove,maximized_vert,maximized_horz
    #toggle,above
    if ( tileNum > -1 ):
        TilesStr=' Tiles=('+containerId(tileNum+1)+') '
    else:
        TilesStr=' Tiles=('+tileId+') '
    client.send_server(ExecuteTS+TilesStr+COMMAND)
    client.get_OK()


def kill_all_containers():
    global stateVM
    # Get back PORTWSS and kill websockify servers
    for i in range(NUM_DOCKERS):
        i0="%0.3d" % (i+1)
        TILEi=ExecuteTS+' Tiles=('+containerId(i+1)+') '
        COMMANDi="bash -c \" "+\
                  " export PORTWSS=\$(cat .vnc/port_wss); "+\
                  " ssh "+SSH_LOGIN+"@"+SSH_FRONTEND+''' \' bash -c \\\" '''+\
                  '''      pgrep -f \\\\\".*websockify.*\'\$PORTWSS\'\\\\\" |xargs kill '''+\
                  ''' \\\"\' ''' +\
                  "\""
        print("%s | %s" % (TILEi, COMMANDi)) 
        sys.stdout.flush()
        client.send_server(TILEi+COMMANDi)
        state=client.get_OK()
        stateVM=stateVM and (state == 0)
        print("Out of kill websockify %s : %s" % (i0,state))
        sys.stdout.flush()
        if (state != 0):
            break
    client.send_server(ExecuteTS+' killall Xvnc')
    print("Out of killall command : "+ str(client.get_OK()))
    client.send_server(LaunchTS+" "+COMMANDStop)
    client.close()


launch_actions_and_interact()

try:
    print("isActions: "+str(isActions))
except:
    print("isActions not defined.")

kill_all_containers()

sys.exit(0)

