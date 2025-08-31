from zipfile import ZipFile
from flask import request, jsonify ,send_file
import shutil
from shutil import rmtree, make_archive
from Decorators import token_check, access_required, set_body
from ..server import os, storage
# net route
@set_body
def upload():
    
    if "file" not in request.files:
        return jsonify({"alert": "No file part in request"})
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"alert": "No selected file"})
    file_path = os.path.join(storage['current_folder'], file.filename) # type: ignore
    file.save(file_path)
    return jsonify({"alert": "File uploaded successfully", "file_path": file_path})
    

@set_body
def download():
    if storage['body'].get('file'):
        safe_path = os.path.join(storage['current_folder'],storage['body'].get('file'))
        return send_file(
        safe_path,
        as_attachment=True,
        download_name=storage['body'].get('file'),
        mimetype='application/octet-stream')
        

@set_body
def url_download():
    if storage['body'].get('link'):
            os.system(f'wget -P {storage['current_folder']} '+storage['body'].get('link'))


# file route
@set_body
def get_files():
    pass


@set_body
def zip():
    
    if storage['body'].get('ac') == 'unzip':
        zip_file = ZipFile(storage['current_folder']+storage['body'].get('file'),'r')
        zip_file.extractall(storage['current_folder']+storage['body'].get('file').replace('.zip','')) # type: ignore
        return 'suc'
            
    if storage['body'].get('ac') == 'zip':
        make_archive(storage['current_folder']+storage['body'].get('dir'), 'zip', storage['current_folder']+storage['body'].get('dir'))
        return 'suc'
    return ''
    

@set_body
def remove():
    if storage['body'].get('file'):    
        # Try remove file
        try:
            os.remove(storage['current_folder']+storage['body'].get('file'))
            return jsonify({'alert':'successfull'})
        except FileNotFoundError:
            return jsonify({'alert':'file not found'})
        
    # If dir in the storage['body']    
    elif storage['body'].get('dir'):
        
        # Try remove folder
        try:
            rmtree(storage['current_folder']+storage['body'].get('dir')+'/')
            return jsonify({'alert':'successfull'})
        except FileNotFoundError:
            return jsonify({'alert':'dir not found'})
    
    # Somethings else
    else:
        return jsonify({'alert':'please get "file" or "dir" key on body'})


@set_body
def rename():
    if storage['body'].get('name') and storage['body'].get('file'):
        os.rename(storage['current_folder']+storage['body'].get('file'),storage['current_folder']+storage['body'].get('name'))
        return jsonify({"alert":"suc"})
    else:
        return jsonify({"alert":"fal"})


@set_body
def edit():
    if storage['body'].get('ac'):
                
        if storage['body'].get('ac') == 'read':
            
            if storage['body'].get('file'):
                file = open(storage['current_folder']+storage['body'].get('file'),'r')
                content = file.read()
                return jsonify({'content' : content, 'alert' : 'ok'})
            else:
                return 'oh n f1'
        
        elif storage['body'].get('ac') == 'write':

            if storage['body'].get('file'):
        
                if storage['body'].get('content'):
            
                    file = open(storage['current_folder']+storage['body'].get('file'),'w')
                    content = file.write(storage['body'].get('content'))
                    return jsonify({'alert' : 'File successfully Saved'})
                else:
                    return 'oh n c'
            else:
                return 'oh n f2'
        else:
            return 'w or r'
    else:
        return 'oh1'


@set_body
def create():
    if storage['body'].get('file'):
                
        # Try to create file
        try:
            f = open(storage['current_folder']+storage['body'].get('file'), "w")
            f.close()
            return jsonify({'alert':'successfull'})
        except Exception as error:
            print(error)
            return jsonify({'alert':'faild'})
                    
    # If dir in the body
    elif storage['body'].get('dir'):
        
        # Try to create folder
        try:
            os.mkdir(storage['current_folder']+storage['body'].get('dir'))
            return jsonify({'alert':'successfull'})
        except Exception as error :
            print(error)
            return jsonify({'alert':'faild'})
    else:
        return jsonify({'alert':'you forgoute somthing'})


@set_body
def change_dir():
    if storage['body'].get('dir'):
        
        if storage['body'].get('dir') in storage['folder_list'] or storage['body'].get('dir') == '..':
                    
            # If current folder equals root directory do not go back
            if storage['body'].get('dir') == '..' and storage['current_folder'] != storage['root_folder']:
                print(storage['stack_last_folder'])
                storage['current_folder'] = storage['current_folder'].replace(storage['stack_last_folder'][-1], '')
                print("after replase :"+storage['current_folder'])
                storage['stack_last_folder'].pop(-1)
                print(storage['stack_last_folder'])
                
            # Else go back
            else:
                if storage['body'].get('dir') != '..':
                    gdir= storage['body'].get('dir')+'/'
                    storage['stack_last_folder'].append(gdir)
                    storage['current_folder'] = storage['current_folder']+storage['stack_last_folder'][-1]
                else:
                    return jsonify({'alert':'you in the root dir','cwd':storage['current_folder']})
           
            return jsonify({'alert':'successfull','cwd':storage['current_folder']})
        
        else:
            return jsonify({'alert':'folder not found','cwd':storage['current_folder']})
    else:
        return jsonify({'alert':'you forgoute somthing'})


 
@set_body 
def move():
    if storage['body'].get('dir') == '..' and storage['current_folder'] != storage['root_folder']:
        try:
            dir = storage['current_folder'].replace(storage['stack_last_folder'][-1], '')
            print(storage['current_folder']+storage['body'].get('dir')+'/')
            shutil.move(storage['current_folder']+storage['body'].get('file'),dir+storage['body'].get('file'))
            return ''
        except Exception as e :
            print(e)
            return ''
            
    # If dir in the body
    if storage['body'].get('dir') and storage['body'].get('file'):
        try:
            print(storage['current_folder']+storage['body'].get('dir')+'/')
            shutil.move(storage['current_folder']+storage['body'].get('file'),storage['current_folder']+storage['body'].get('dir')+'/'+storage['body'].get('file'))
            return ''

        except Exception as e :
            print(e)
            return ''
    return storage['body'].get('dir')+storage['body'].get('file')
   

