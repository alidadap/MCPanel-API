# ===== Import Liberys ===== #
from flask import Flask
from flask_cors import CORS 
from flask_socketio import SocketIO
import psutil
import time
from view.config import storage
from view.Auth import login
from view.Dashboard import start, stop, command, load_status, minecraft_server
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

app.add_url_rule('/fmgr', view_func=get_files, methods=['POST']) 
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
             # Call load_status method for load status of minecraft_server and define emit data
            data = {
                'ram': psutil.virtual_memory().percent,
                "cpu": psutil.cpu_percent(),
                "address": "skyvers.xyz:25565",
                **load_status()
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
                log_data = minecraft_server.stdout.readline().decode('utf-8').strip()+'\n' # type: ignore
                if log_data == '\n':
                    continue
                storage['logs'] = storage['logs']+log_data
                socketio.emit('log',storage['logs'])
            except:
                pass
            time.sleep(0.2)


    socketio.start_background_task(send_log)
    socketio.start_background_task(send_status)


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5834, host="0.0.0.0")
