# ===== Import Liberys ===== #
import json
from flask import Flask
from flask_cors import CORS 
from flask_socketio import SocketIO
import psutil
import os
import time
from view.Auth import login
from view.Dashboard import start, stop, command
from view.Decorators import socketio_token_check
from view.FileManager import (
    get_files,
    change_dir,
    upload,
    download,
    url_download,
    zip,
    remove,
    rename,
    edit,
    create,
    move
)
from view.Account import get_users, add_user, update_user, remove_user

# load config
conf_file = open("config.json","r")
storage = dict(json.load(conf_file))
conf_file.close()

# ===== Init App ===== #
app = Flask(__name__) # Define object app for route and socketIO 
app.config['SECRET_KEY'] = storage["key"] # Define secret key for security
CORS(app, supports_credentials=True)  # Enable CORS with support for credentials
socketio = SocketIO(app, cors_allowed_origins="*") # Define socketio object for handle events and emit data







# new_user = PanelUser(username='ozi', password=bcrypt.hashpw("11223344".encode(),storage['key']).decode(),access='1234',email='ozi@gmail.com')
# session.add(new_user)
# session.commit()
print('user creater stop')

####========login=========####

app.add_url_rule("/login", view_func=login, methods=['POST']) 


####======= Dashboard Routes =======####

app.add_url_rule('/dashboard/start', view_func=start, methods=['POST'])
app.add_url_rule('/dashboard/stop', view_func=stop, methods=['POST'])
app.add_url_rule('/dashboard/command', view_func=command, methods=['POST'])


####======= File Manager Routes =======####

app.add_url_rule('/fmgr/cd', view_func=change_dir, methods=['POST']) 

app.add_url_rule('/fmgr/net/upload', view_func=upload, methods=['POST']) 
app.add_url_rule('/fmgr/net/download', view_func=download, methods=['POST']) 
app.add_url_rule('/fmgr/net/url-download', view_func=url_download, methods=['POST']) 

app.add_url_rule('/fmgr/file/zip', view_func=zip, methods=['POST']) 
app.add_url_rule('/fmgr/file/remove', view_func=remove, methods=['POST']) 
app.add_url_rule('/fmgr/file/rename', view_func=rename, methods=['POST']) 
app.add_url_rule('/fmgr/file/edit', view_func=edit, methods=['POST']) 
app.add_url_rule('/fmgr/file/create', view_func=create, methods=['POST']) 
app.add_url_rule('/fmgr/file/move', view_func=move, methods=['POST']) 


####======= Account Manager Routes =======####

app.add_url_rule('/acmgr/get', view_func=get_users, methods=['POST']) 
app.add_url_rule('/acmgr/add', view_func=add_user, methods=['POST']) 
app.add_url_rule('/acmgr/update', view_func=update_user, methods=['POST']) 
app.add_url_rule('/acmgr/remove', view_func=remove_user, methods=['POST']) 


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






@app.route("/api/file",methods=['POST','GET']) #--->> /api/file
@token_check
@access_required(3)
def file():

        elif body.get('run') == 'create':

            # If file in the body
           

        # If run is move
        elif body.get('run') == 'move':   

            

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
