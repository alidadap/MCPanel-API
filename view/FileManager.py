import shutil
import os
from zipfile import ZipFile
from flask import request, jsonify ,send_file
from shutil import rmtree, make_archive
from .Decorators import token_check, access_required, set_body
from .config import storage

# net route
@token_check
@access_required(3)
def upload():
    
    if "file" not in request.files:
        return jsonify({"message": "No file part in request"})
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No selected file"})
    file_path = os.path.join(storage['current_folder'], file.filename) # type: ignore
    file.save(file_path)
    return jsonify({"message": "File uploaded successfully", "data": {"filePath" : file_path}})
    

@set_body
@token_check
@access_required(3)
def download():
    if storage['body'].get('file'):
        safe_path = os.path.join(storage['current_folder'],storage['body'].get('file'))
        return send_file(
        safe_path,
        as_attachment=True,
        download_name=storage['body'].get('file'),
        mimetype='application/octet-stream')
    else:
        return jsonify({"message":"Error"})

@set_body
@token_check
@access_required(3)
def url_download():
    if storage['body'].get('link'):
            os.system(f'wget -P {storage['current_folder']} '+storage['body'].get('link'))
            return jsonify({"message":"Downloaded!"})
    else:
        return jsonify({ "message":"Error"})

# file route
@token_check
@access_required(3)
def get_files():
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
    return jsonify({"data":{'files':files,'dirs':dirs,'cwd':storage['current_folder']}})


@set_body
@token_check
@access_required(3)
def zip():
    
    if storage['body'].get('ac') == 'unzip':
        zip_file = ZipFile(storage['current_folder']+storage['body'].get('file'),'r')
        zip_file.extractall(storage['current_folder']+storage['body'].get('file').replace('.zip','')) # type: ignore
        return jsonify({"message":"Unzipd!"})
            
    elif storage['body'].get('ac') == 'zip':
        make_archive(storage['current_folder']+storage['body'].get('dir'), 'zip', storage['current_folder']+storage['body'].get('dir'))
        return jsonify({"message":"Zipd!"})

    else:
        return jsonify({"message":"Please send valid data in body"})
    

@set_body
@token_check
@access_required(3)
def remove():
    if storage['body'].get('file'):    
        # Try remove file
        try:
            os.remove(storage['current_folder']+storage['body'].get('file'))
            return jsonify({'message':'Successfull'})
        except FileNotFoundError:
            return jsonify({'message':'File not found'})
        
    # If dir in the storage['body']    
    elif storage['body'].get('dir'):
        
        # Try remove folder
        try:
            rmtree(storage['current_folder']+storage['body'].get('dir')+'/')
            return jsonify({'message':'Successfull'})
        except FileNotFoundError:
            return jsonify({'message':'Dir not found'})
    
    # Somethings else
    else:
        return jsonify({'message':'Please send valid data in body'})


@set_body
@token_check
@access_required(3)
def rename():
    if storage['body'].get('name') and storage['body'].get('file'):
        os.rename(storage['current_folder']+storage['body'].get('file'),storage['current_folder']+storage['body'].get('name'))
        return jsonify({'message':'Successfull'})
    else:
        return jsonify({'message':'Faild'})


@set_body
@token_check
@access_required(3)
def edit():
    if storage['body'].get('action') == 'read': 
        if storage['body'].get('file'):
            
            file = open(storage['current_folder']+storage['body'].get('file'),'r')
            content = file.read()
            return jsonify({"data": {"content": content}})
        
        else:
            
            return jsonify({'message':'Please send valid data in body'})
    
    elif storage['body'].get('action') == 'write':
        if storage['body'].get('file'):
    
            if storage['body'].get('content'):
        
                file = open(storage['current_folder']+storage['body'].get('file'),'w')
                content = file.write(storage['body'].get('content'))
                return jsonify({'message' : 'File successfully Saved'})
            
            else:
                return jsonify({'message':'Please send valid data in body'})
        else:
            return jsonify({'message':'Please send valid data in body'})
    else:
        return jsonify({'message':'Please send valid data in body'})


@set_body
@token_check
@access_required(3)
def create():
    if storage['body'].get('file'):
                
        # Try to create file
        try:
            f = open(storage['current_folder']+storage['body'].get('file'), "w")
            f.close()
            return jsonify({'message':'Successfull'})
        except Exception as error:
            print(error)
            return jsonify({'message':'Faild'})
                    
    # If dir in the body
    elif storage['body'].get('dir'):
        
        # Try to create folder
        try:
            os.mkdir(storage['current_folder']+storage['body'].get('dir'))
            return jsonify({'message':'Successfull'})
        except Exception as error :
            print(error)
            return jsonify({'message':'Faild'})
    else:
        return jsonify({'message':'Please send valid data in body'})


@set_body
@token_check
@access_required(3)
def change_dir():
    if storage['body'].get('dir'):
        
        if storage['body'].get('dir') in storage['folder_list'] or storage['body'].get('dir') == '..':
                    
            # If current folder equals root directory do not go back
            if storage['body'].get('dir') == '..' and storage['current_folder'] != storage['root_folder']:
                storage['current_folder'] = storage['current_folder'].replace(storage['stack_last_folder'][-1], '')
                storage['stack_last_folder'].pop(-1)
                
            # Else go back
            else:
                if storage['body'].get('dir') != '..':
                    gdir= storage['body'].get('dir')+'/'
                    storage['stack_last_folder'].append(gdir)
                    storage['current_folder'] = storage['current_folder']+storage['stack_last_folder'][-1]
                else:
                    return jsonify({'message':'You in the root directory',"data":{'cwd':storage['current_folder']}})
           
            return jsonify({'message':'Successfull',"data":{'cwd':storage['current_folder']}})
        
        else:
            return jsonify({'message':'Folder not found',"data":{'cwd':storage['current_folder']}})
    else:
        return jsonify({'message':'Please send valid data in body'})


 
@set_body
@token_check
@access_required(3)
def move():
    if storage['body'].get('dir') == '..' and storage['current_folder'] != storage['root_folder']:
        try:
            dir = storage['current_folder'].replace(storage['stack_last_folder'][-1], '')
            shutil.move(storage['current_folder']+storage['body'].get('file'),dir+storage['body'].get('file'))
            return jsonify({'message':'File moved'})
        
        except Exception as e :
            print(e)
            return jsonify({'message':'Faild'})
            
    # If dir in the body
    if storage['body'].get('dir') and storage['body'].get('file'):
        try:
            shutil.move(storage['current_folder']+storage['body'].get('file'),storage['current_folder']+storage['body'].get('dir')+'/'+storage['body'].get('file'))
            return jsonify({'message':'File moved'})

        except Exception as e :
            print(e)
            return jsonify({'message':'Faild'})
        
    return jsonify({"data":{"path":storage['body'].get('dir')+storage['body'].get('file')}})
   

