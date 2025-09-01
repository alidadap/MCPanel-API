import subprocess
import os
from flask import jsonify 
from mcstatus.server import JavaServer
from .config import storage
from .Decorators import token_check, access_required, set_body


minecraft_server = None

def make_server(script, directory):
        return subprocess.Popen(args=script, cwd=directory, stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.PIPE,shell=True)


target = JavaServer.lookup('127.0.0.1')

@token_check
@access_required(1)
def start():
    global minecraft_server
    
    
    #If minecraft server is start
    if minecraft_server == None:
        # Try to start server 
        try:
            minecraft_server = make_server(storage['script'],storage['root_folder'])
            return jsonify({"message": 'Server Successfully Started'})
        
        # If have a error run this
        except Exception as error:
            print(error)
            return jsonify({"message": 'Failed! Check the Console on Backend'})
        
    # if not is start 
    else:
        return jsonify({"message": 'Server Already is Started'})


@token_check
@access_required(1)
def stop():
    global minecraft_server
    
    
    #If minecraft server is start
    if minecraft_server == None:
        os.system("pkill java")
        return jsonify({"message": 'Server Already is Stopped'})
    
    # if not is start
    else:
        try:
            minecraft_server.stdin.write("stop".encode()+b'\n')  # type: ignore
            minecraft_server.stdin.flush()  # type: ignore
            minecraft_server= None
            f = open(storage['root_folder']+'dlog/lastlog.log','w')
            f.write(storage['logs'])
            storage['logs']=''
        except:
            minecraft_server= None
        return jsonify({"message": "Server Successfully Stopped"})

@set_body
@token_check
@access_required(2)
def command():
    minecraft_server.stdin.write(storage['body'].get('cmd').encode()+b'\n')  # type: ignore
    minecraft_server.stdin.flush()  # type: ignore
    return jsonify({"message":"Command used"})


def load_status():

        try:
            
            return {           
                "playersName":target.query().players.list,
                "maxPlayers":target.status().players.max,
                "onlinePlayers":target.status().players.online,
                "status":'online'
            }
            
        except Exception as e:
            
            print(e)
            return {
                "playersName":None,
                "maxPlayers":0,
                "onlinePlayers":0,
                "status":'offline'                
            }
