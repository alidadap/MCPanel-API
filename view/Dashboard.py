import subprocess
from mcstatus.server import JavaServer
from ..server import storage
from Decorators import token_check, access_required

class MCServer:
    def __init__(self, script: str, directory: str = './') -> None:
        self.target = JavaServer.lookup('127.0.0.1')
        self.server_start_bat = script
        self.directory = directory
        self.is_start = None 

    def start(self) -> None:
        self.is_start = subprocess.Popen(
            args=self.server_start_bat, cwd=self.directory, stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.PIPE,shell=True)

    def load_status(self):

        try:           
            self.max_players=self.target.status().players.max
            self.online_players=self.target.status().players.online
            self.status='online'
        except Exception as e:
            self.players_name = None
            self.max_players=0
            self.online_players=0
            self.status='offline'

    def command(self, command: str) -> None:

        self.is_start.stdin.write(command.encode()+b'\n') # type: ignore
        self.is_start.stdin.flush() # type: ignore

minecraft_server = MCServer(storage['script'],storage['root_folder']) # Define minecratServer object for on/off or manage server


def start():
    pass


def stop():
    pass


def command():
    pass




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
            
#             #If minecraft server is start
#             if minecraft_server.is_start == None:
#                 # Try to start server 
#                 try:
#                     minecraft_server.start()
#                     return jsonify({"alert": 'Server Successfully Started'})
                
#                 # If have a error run this
#                 except Exception as error:
#                     print(error)
#                     return jsonify({"alert": 'Failed! Check the Console on Backend'})
                
#             # if not is start 
#             else:
#                 return jsonify({"alert": 'Server Already is Started'})
        
#         #if btn is stop 
#         elif body.get('btn') == "stop":
            
#             #If minecraft server is start
#             if minecraft_server.is_start == None:
#                 os.system("pkill java")
#                 return jsonify({"alert": 'Server Already is Stopped'})
            
#             # if not is start
#             else:
#                 try:
#                     minecraft_server.command('stop')
#                     minecraft_server.is_start = None
#                     f = open(storage['root_folder']+'dlog/lastlog.log','w')
#                     f.write(storage['logs'])
#                     storage['logs']=''
#                 except:
#                     minecraft_server.is_start = None
#                 return jsonify({"alert": "Server Successfully Stopped"})
            
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
        
        

