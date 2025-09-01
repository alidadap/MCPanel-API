import subprocess
from flask import jsonify 
from mcstatus.server import JavaServer
from ..server import storage, os
from Decorators import token_check, access_required, set_body


minecraft_server = None

def make_server(script, directory):
        return subprocess.Popen(args=script, cwd=directory, stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.PIPE,shell=True)


target = JavaServer.lookup('127.0.0.1')

def start():
    global minecraft_server
    
    
    #If minecraft server is start
    if minecraft_server == None:
        # Try to start server 
        try:
            minecraft_server = make_server(storage['script'],storage['root_folder'])
            return jsonify({"alert": 'Server Successfully Started'})
        
        # If have a error run this
        except Exception as error:
            print(error)
            return jsonify({"alert": 'Failed! Check the Console on Backend'})
        
    # if not is start 
    else:
        return jsonify({"alert": 'Server Already is Started'})


def stop():
    global minecraft_server
    
    
    #If minecraft server is start
    if minecraft_server == None:
        os.system("pkill java")
        return jsonify({"alert": 'Server Already is Stopped'})
    
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
        return jsonify({"alert": "Server Successfully Stopped"})


def command():
    minecraft_server.stdin.write(storage['body'].get('cmd').encode()+b'\n')  # type: ignore
    minecraft_server.stdin.flush()  # type: ignore
    return jsonify({"data":None, "message":"Command used"})


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




# # Check the user token is valid
# @token_check
# @access_required(1)
# def handle_button():
    
#     # Try to define body of request
#     try:
#         body = dict(request.json)
#     except Exception as error:
#         print(error)
        
#     # If btn exist in body
#     if body.get('btn'):
        
#         #If btn is start 
#         if body.get('btn') == "start":
            
            
        
#         #if btn is stop 
#         elif body.get('btn') == "stop":
            
           
            
#         # if something else
#         else:
#             return jsonify({"alert": "invalid btn"})
#     else:
#         return jsonify({"alert": "you forgoute somthing"})
        
        
        
        
        
        
        
        
        
        
#         @token_check
# @access_required(1)
# def run_command():
    
#     # Try to get body
#     try:
#         body = dict(request.json)
#     except Exception as error:
#         print(error)
    
#     # If cmd in the body
#     if body.get('cmd'):
#         if body.get('cmd') != 'stop' or body.get('cmd') != 'reload' or body.get('cmd') != 'reload confirm':
#             minecraft_server.command(body.get('cmd'))
#             return jsonify({"alert":"ok"})
#     else:
#         return jsonify({"alert": "you forgoute somthing"})
        
        

