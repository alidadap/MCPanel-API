# ===== Import Liberys ===== #
from curses import wrapper
from mcstatus.server import JavaServer
from flask import Flask, request, jsonify ,send_file
from jwt import ExpiredSignatureError, decode, InvalidTokenError, encode 
from datetime import datetime, timedelta 
from functools import wraps 
from flask_cors import CORS 
from flask_socketio import SocketIO, emit
import subprocess
import time
import psutil
import os
import shutil
from shutil import rmtree, make_archive
import bcrypt
from sqlalchemy import Column, Integer, String, create_engine, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from zipfile import ZipFile
# debug



Base = declarative_base()

class PanelUser(Base):
    __tablename__ = 'panel_users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))  
    access = Column(String(255))  
    email = Column(String(255))  


engine = create_engine("sqlite:///minecraft-site.db",connect_args={"check_same_thread": False}, echo=True)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# ===== Class for Manage Minecraft Server ===== #
 

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

        self.is_start.stdin.write(command.encode()+b'\n')
        self.is_start.stdin.flush()


# ===== Set Default Variables ===== #
storage = {
    'key': b'$2b$12$OSIMaXAxIKzSv/uRJAQDK.',
    'root_folder' : 'server/',
    'current_folder' : 'server/',
    'stack_last_folder' : [],
    'folder_list' : [],
    'script' : '/bin/bash start_server_script.sh',
    'logs':''
}
# ===== Init App ===== #
app = Flask(__name__) # Define object app for route and socketIO 
app.config['SECRET_KEY'] = "kpJ-kwp;MbHJ<^d!" # Define secret key for security
CORS(app, supports_credentials=True)  # Enable CORS with support for credentials

socketio = SocketIO(app, cors_allowed_origins="*") # Define socketio object for handle events and emit data
minecraft_server = MCServer(storage['script'],storage['root_folder']) # Define minecratServer object for on/off or manage server


# ===== Defind Functions for Auth ===== #
def socketio_token_check(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.args.get('token')  # Get token from query parameters
        if not token:
            emit('auth', {'alert': 'Token is required'}) # Send error to client
            return False  # Disconnect the client

        try:
            payload = decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            user = payload.get('user')  # Assuming 'user' is in payload
            if not user:
                emit('auth', {'alert': 'Invalid token payload'})
                return False

            # Store the user in the storage for later use
            request.sid = request.sid  # Store storage ID
            request.user = user  # Store user

        except ExpiredSignatureError:
            emit('auth', {'alert': 'Token has expired'})
            return False
        except InvalidTokenError:
            emit('auth', {'alert': 'Token is invalid'})
            return False
        except Exception as e:
            emit('auth', {'alert': f'Token decoding failed: {e}'})
            return False
        return f(*args, **kwargs)
    return wrapped


# Token checker
def token_check(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        # Get token from cookies or JSON request
        
        token = request.cookies.get('token')
        if not token:
            token = request.form.get('token')
            if not token:
                token = dict(request.json).get('token')
                if not token:
                    return jsonify({'alert': 'Token is required'})
        try:
            # Decode token using the secret key
            payload = decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            print(payload)
        except ExpiredSignatureError:
            return jsonify({'alert': 'Token has expired'})
        except InvalidTokenError:
            return jsonify({'alert': 'Token is invalid'})
        return func(*args, **kwargs)
    return decorated

def socket_access_required(required_access):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                token = request.args.get('token')
                if not token:
                    print('token req')
                    return False
                
                payload = decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                user_access = payload.get('access')
                
                print(required_access,' : ',user_access)
                if required_access not in user_access:
                    print('access deny')
                    return False
                
                return f(*args, **kwargs)
                
            except Exception as e:
                print(e)
                return False
        return wrapped
    return decorator

def access_required(required_access):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.cookies.get('token') or request.form.get('token') or (request.json and request.json.get('token'))
            if not token:
                return jsonify({'alert': 'Token is required'}), 401
            
            try:
                payload = decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                user_access = payload.get('access')
                
                if str(required_access) not in user_access:
                    return jsonify({'alert': 'Access denied'}), 403
                    
            except Exception as e:
                return jsonify({'alert': str(e)}), 401
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# new_user = PanelUser(username='ozi', password=bcrypt.hashpw("11223344".encode(),storage['key']).decode(),access='1234',email='ozi@gmail.com')
# session.add(new_user)
# session.commit()
print('user creater stop')

####========login=========####

@app.route("/api/login", methods=['POST']) #--->> /api/login
def check_login():

    # Try to get body from frount
    try:
        body = dict(request.json)
        password = bcrypt.hashpw(body['pass'].encode(),storage['key']).decode()
        user = session.query(PanelUser).filter_by(username=body['user']).first()
        print(user)
    except Exception as error:
        print(error)
        return jsonify({"alert": 'Failed! Check the Console on Backend'})
        
    # Check username and password validity
    if user.password == password:

        # Generate JWT token
        token = encode({
            "user": body['user'],
            "access": user.access,
            "exp": datetime.utcnow() + timedelta(minutes=30)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
        # Create response with HttpOnly cookie
        resp = jsonify({'alert': 'Login successful', 'token': token,'access': user.access})
        return resp
    # If user not in the database
    else:

        return jsonify({'alert': 'Invalid username or password', 'token': None})



####======= Dashboard Routes =======####

@app.route('/api/script',methods=['POST'])
@token_check
@access_required(1)
def script():
    try:
        body = dict(request.json)
    except Exception as error:
        print(error)
    if body.get('script'):
        storage['script'] = body.get('script')
        return jsonify({"alert":"Successfuly Saved","script":storage['script']})
    else:
        return jsonify({"alert":"Get the Script!","script":storage['script']})

# Start and stop minecraft_server
@app.route('/api/button', methods=['POST']) # --->> /api/button

# Check the user token is valid
@token_check
@access_required(1)
def handle_button():
    
    # Try to define body of request
    try:
        body = dict(request.json)
    except Exception as error:
        print(error)
        
    # If btn exist in body
    if body.get('btn'):
        
        #If btn is start 
        if body.get('btn') == "start":
            
            #If minecraft server is start
            if minecraft_server.is_start == None:
                # Try to start server 
                try:
                    minecraft_server.start()
                    return jsonify({"alert": 'Server Successfully Started'})
                
                # If have a error run this
                except Exception as error:
                    print(error)
                    return jsonify({"alert": 'Failed! Check the Console on Backend'})
                
            # if not is start 
            else:
                return jsonify({"alert": 'Server Already is Started'})
        
        #if btn is stop 
        elif body.get('btn') == "stop":
            
            #If minecraft server is start
            if minecraft_server.is_start == None:
                os.system("pkill java")
                return jsonify({"alert": 'Server Already is Stopped'})
            
            # if not is start
            else:
                try:
                    minecraft_server.command('stop')
                    minecraft_server.is_start = None
                    f = open(storage['root_folder']+'dlog/lastlog.log','w')
                    f.write(storage['logs'])
                    storage['logs']=''
                except:
                    minecraft_server.is_start = None
                return jsonify({"alert": "Server Successfully Stopped"})
            
        # if something else
        else:
            return jsonify({"alert": "invalid btn"})
    else:
        return jsonify({"alert": "you forgoute somthing"})
        

@app.route("/api/command",methods=['POST']) #--->> /api/command

# chek the token user valid
@token_check
@access_required(1)
def run_command():
    
    # Try to get body
    try:
        body = dict(request.json)
    except Exception as error:
        print(error)
    
    # If cmd in the body
    if body.get('cmd'):
        if body.get('cmd') != 'stop' or body.get('cmd') != 'reload' or body.get('cmd') != 'reload confirm':
            minecraft_server.command(body.get('cmd'))
            return jsonify({"alert":"ok"})
    else:
        return jsonify({"alert": "you forgoute somthing"})
        
        


# ==== # Dashboard SocketIO # ==== #


# Handle the connect event ( if user connected )
@socketio.on('connect')

@socketio_token_check
# @socket_access_required('1')
def handle_connect():
    
    #Define send_status function for send status of minecraft_server
    def send_status():
        while True:
            minecraft_server.load_status() # Call load_status method for load status of minecraft_server and define emit data
            data = {
                'status': minecraft_server.status,
                'ram': psutil.virtual_memory().percent,
                "cpu": psutil.cpu_percent(),
                "onlinePlayers": minecraft_server.online_players,
                "maxPlayers": minecraft_server.max_players,
                'playersName':minecraft_server.players_name,
                "address": "skyvers.xyz:25565"
            }

            # emiting data on status 
            socketio.emit("status", data)
            time.sleep(0.2)
    

    #Define send_log function for send log of minecraft_server
    def send_log():
        socketio.emit('log',storage['logs'])
        while True:

            try:
                # Define log_data variable and emit
                log_data = minecraft_server.is_start.stdout.readline().decode('utf-8').strip()+'\n'
                if log_data == '\n':
                    continue
                storage['logs'] = storage['logs']+log_data
                socketio.emit('log',storage['logs'])
            except:
                pass
            time.sleep(0.2)


    socketio.start_background_task(send_log)
    socketio.start_background_task(send_status)



####======= File Manager Routes =======####


@app.route("/api/file",methods=['POST','GET']) #--->> /api/file
@token_check
@access_required(3)
def file():

    # If run is upload
    if request.form.get('run') == 'upload':
        print('upl')
        if "file" not in request.files:
            return jsonify({"alert": "No file part in request"})

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"alert": "No selected file"})
    
        file_path = os.path.join(request.form.get('cwd'), file.filename)
        file.save(file_path)

        return jsonify({"alert": "File uploaded successfully", "file_path": file_path})
    
    # Try to get the body
    try:
        body = dict(request.json)
        print(body)
    except:
        body={}

    # If run in the body
    if body.get('run'):
        if body.get('run') == 'zip':
            if body.get('ac') == 'unzip':
                zip_file = ZipFile(storage['current_folder']+body.get('file'),'r')
                zip_file.extractall(storage['current_folder']+body.get('file').replace('.zip',''))
                return 'suc'
        if body.get('run') == 'zip':
            if body.get('ac') == 'zip':
                make_archive(storage['current_folder']+body.get('dir'), 'zip', storage['current_folder']+body.get('dir'))
                return 'suc'
        # If run is delete
        if body.get('run') == 'delete':
            
            # If file in the body
            if body.get('file'):
                
                # Try remove file
                try:
                    os.remove(storage['current_folder']+body.get('file'))
                    return jsonify({'alert':'successfull'})
                except FileNotFoundError:
                    return jsonify({'alert':'file not found'})
                
            # If dir in the body    
            elif body.get('dir'):
                
                # Try remove folder
                try:
                    rmtree(storage['current_folder']+body.get('dir')+'/')
                    return jsonify({'alert':'successfull'})
                except FileNotFoundError:
                    return jsonify({'alert':'dir not found'})
            
            # Somethings else
            else:
                return jsonify({'alert':'please get "file" or "dir" key on body!'})
        
        # If run is download
        elif body.get('run') == 'download':
            if body.get('file'):
                safe_path = os.path.join(storage['current_folder'],body.get('file'))
                return send_file(
                safe_path,
                as_attachment=True,
                download_name=body.get('file'),
                mimetype='application/octet-stream')
        
        elif body.get('run') == 'rename':
            if body.get('name') and body.get('file'):
                os.rename(storage['current_folder']+body.get('file'),storage['current_folder']+body.get('name'))
                return jsonify({"alert":"suc"})
            else:
                return jsonify({"alert":"fal"})
                
        elif body.get('run') == 'edit':
            
            if body.get('ac'):
                
                if body.get('ac') == 'read':
                    
                    if body.get('file'):
                        file = open(storage['current_folder']+body.get('file'),'r')
                        content = file.read()
                        return jsonify({'content' : content, 'alert' : 'ok'})
                    else:
                        return 'oh n f1'
                
                elif body.get('ac') == 'write':
            
                    if body.get('file'):
                    
                        if body.get('content'):
                        
                            file = open(storage['current_folder']+body.get('file'),'w')
                            content = file.write(body.get('content'))
                            return jsonify({'alert' : 'File successfully Saved'})
                        else:
                            return 'oh n c'
                    else:
                        return 'oh n f2'
                else:
                    return 'w or r'
            else:
                return 'oh1'
        # If run is create
        elif body.get('run') == 'create':

            # If file in the body
            if body.get('file'):
                
                # Try to create file
                try:
                    f = open(storage['current_folder']+body.get('file'), "w")
                    f.close()
                    return jsonify({'alert':'successfull'})
                except Exception as error:
                    print(error)
                    return jsonify({'alert':'faild'})
                    
            # If dir in the body
            elif body.get('dir'):
                
                # Try to create folder
                try:
                    os.mkdir(storage['current_folder']+body.get('dir'))
                    return jsonify({'alert':'successfull'})
                except Exception as error :
                    print(error)
                    return jsonify({'alert':'faild'})
            else:
                return jsonify({'alert':'you forgoute somthing'})
        
        # If run is go
        elif body.get('run') == 'go':
            
            # If dir in the body
            if body.get('dir'):
                
                # If for back folder
                if body.get('dir') in storage['folder_list'] or body.get('dir') == '..':
                    
                    # If current folder equals root directory do not go back
                    if body.get('dir') == '..' and storage['current_folder'] != storage['root_folder']:
                        print(storage['stack_last_folder'])
                        storage['current_folder'] = storage['current_folder'].replace(storage['stack_last_folder'][-1], '')
                        print("after replase :"+storage['current_folder'])
                        storage['stack_last_folder'].pop(-1)
                        print(storage['stack_last_folder'])
                        
                    # Else go back
                    else:
                        if body.get('dir') != '..':
                            gdir= body.get('dir')+'/'
                            storage['stack_last_folder'].append(gdir)
                            storage['current_folder'] = storage['current_folder']+storage['stack_last_folder'][-1]
                        else:
                            return jsonify({'alert':'you in the root dir','cwd':storage['current_folder']})
                    
                    return jsonify({'alert':'successfull','cwd':storage['current_folder']})
                else:
                    return jsonify({'alert':'folder not found','cwd':storage['current_folder']})
            else:
                return jsonify({'alert':'you forgoute somthing'})

        # If run is move
        elif body.get('run') == 'move':   

            if body.get('dir') == '..' and storage['current_folder'] != storage['root_folder']:
                try:
                    dir = storage['current_folder'].replace(storage['stack_last_folder'][-1], '')
                    print(storage['current_folder']+body.get('dir')+'/')
                    shutil.move(storage['current_folder']+body.get('file'),dir+body.get('file'))
                except Exception as e :
                    print(e)

            # If dir in the body
            if body.get('dir') and body.get('file'):
                try:
                    print(storage['current_folder']+body.get('dir')+'/')
                    shutil.move(storage['current_folder']+body.get('file'),storage['current_folder']+body.get('dir')+'/'+body.get('file'))
                except Exception as e :
                    print(e)
                return body.get('dir')+body.get('file')

        elif body.get('run') == 'wget':
            if body.get('link'):
                os.system(f'wget -P {storage['current_folder']} '+body.get('link'))


            return 'hello'

    # If run is not in the body 
    else:
        files=[] # Define files name list 
        dirs=[] # Define folders name list
        print("on list dir: "+storage['current_folder'])
        list_files = os.listdir(storage['current_folder'])
                  
        # Loop for separation files and folders
        for file in list_files:
            if os.path.isdir(storage['current_folder']+file):
                dirs.append(file)
            else:
                files.append(file)

        storage['folder_list'] = dirs

        return jsonify({'files':files,'dirs':dirs,'cwd':storage['current_folder']})

@app.route("/api/account",methods=['POST']) #--->> /api/file
@token_check
@access_required(4)
def account():
    # Try to get the body
    try:
        body = dict(request.json)
    except:
        body={}
    
    # default page
    if body.get("run") and body.get("run") == "create":
        condition_ok : bool = (
            body.get('user') and
            body.get('pass') and
            body.get('confirm') and
            body.get('access') and
            body.get('email') and
            not session.query(PanelUser).filter_by(username=body.get('user'), password=body.get('pass'),access=body.get('access'),email=body.get('email')).first() and
            body.get('pass') == body.get('confirm')
        )
        if condition_ok:    
            hashed_password = bcrypt.hashpw(body.get('pass').encode(), storage['key']).decode()
            new_user = PanelUser(username=body.get('user'), password=hashed_password,access=body.get('access'),email=body.get('email'))
            session.add(new_user)
            session.commit()
            return jsonify({"alert":"successful!"})
        else:
            return jsonify({"alert":"somethings is wrong!"})
    elif body.get("run") and body.get("run") == "delete":
        if body.get('id'):
            q = delete(PanelUser).where(PanelUser.id == int(body.get('id')))
            session.execute(q)
            session.commit()
            return jsonify({"alert":"user deleted!"})
    else:    
        users = session.query(PanelUser).all()
        users_dict = []
        for user in users:
            users_dict.append({
                "id" : user.id,
                "username" : user.username,
                "email" : user.email,
                "access" : user.access
            })
        return jsonify({"users":users_dict})

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5834, host="0.0.0.0")
