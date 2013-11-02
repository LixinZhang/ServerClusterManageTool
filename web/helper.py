from model import Session
from model import Script , ScriptGroup , Server , ServerGroup , Sorted_Script , Task , TaskStatus
import json
import hashlib
import datetime
import upload_remotefile

BASE_PATH = "script_files/"
def create_scriptgroup(name) :
    try :
        session = Session()
        group_list = session.query(ScriptGroup).all()
        name_is_unique = True 
        for group in group_list :
            if name == group.name :
                name_is_unique = False
                break
        if name_is_unique == True :
            group = ScriptGroup(name)
            group_id = group.save_return_id(session)
            sa = Sorted_Script(group_id , json.dumps([]))
            sa.save(session)
            return {"status":0 , "val":group_id}
        else :
            return {"status":-1 , "val":"Script group name is not unique!"}
    except Exception , msginfo :
        return {"status":-1 , "val": msginfo}
    finally :
        session.close()

def create_script(name , content , desc ) :
    try :
        session = Session()
        filename = hashlib.md5(str(datetime.datetime.now())).hexdigest()
        newfile = open(BASE_PATH + filename , 'w')
        content = content.replace('\r\n' , '\n')
        newfile.writelines(content)
        newfile.flush()
        newfile.close()
        newscript = Script(name , BASE_PATH + filename , desc)
        script_id = newscript.save_return_id(session)
        return {"status":0 , "val":script_id}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def create_servergroup(name ) :
    try :
        session = Session()
        group_list = session.query(ServerGroup).all()
        name_is_unique = True
        for group in group_list :
            if name == group.name :
                name_is_unique = False
                break
        if name_is_unique == True :
            group = ServerGroup(name)
            group_id = group.save_return_id (session)
            return {"status":0  , "val":group_id}
        else :
            return {"status":-1 , "val":"Server Group name is not unique!"}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def create_server(username , password , host_address , host_port , script_location) :
    try :
        session = Session()
        new_server = Server(username , password , host_address , host_port , script_location)
        server_id = new_server.save_return_id(session)
        return {"status":0 , "val":server_id}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def get_script_group_list() :
    try :
        session = Session()
        group_list = session.query(ScriptGroup).all()
        if group_list == None or len(group_list) == 0 :
            return {"status":-1 , "val":None}
        return {"status":0 , "val":group_list}
    except Exception , msginfo :
        return {"status": -1 , "val":msginfo}
    finally :
        session.close()

def get_script_group_by_id(group_id) :
    try :
        session = Session()
        group = session.query(ScriptGroup).filter(ScriptGroup.id == group_id).first()
        group.scripts = group.scripts
        if group == None :
            return {"status":-1 , "val":None}
        return {"status":0 , "val":group}
    except Exception , msginfo :
        return {"status": -1 , "val":msginfo}
    finally :
        session.close()

def get_all_scripts() :
    try :
        session = Session()
        script_list = session.query(Script).all()
        if script_list == None or len(script_list) == 0 :
            return {"status":-1 , "val":None}
        for script in script_list :
            script.groups = script.groups #delay query , so get values before session closes
        return {"status":0 , "val":script_list}
    except Exception , msginfo :
        return {"status": -1 , "val":msginfo}
    finally :
        session.close()

def get_script_by_id(script_id) :
    try :
        session = Session()
        script = session.query(Script).filter(Script.id == script_id).first()
        if script == None :
            return {"status":-1 , "val":None}
        return {"status":0 , "val":script}
    except Exception , msginfo :
        return {"status": -1 , "val":msginfo}
    finally :
        session.close()

def get_script_content_by_id(script_id) :
    try :
        session = Session()
        script = session.query(Script).filter(Script.id == script_id).first()
        if script == None :
            return {"status":-1 , "val":None}
        ori_script_file = open(script.location,"r");
        content = ori_script_file.read()
        ori_script_file.close()
        return {"status":0 , "val":content}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def update_script(script_id , name , content , desc) :
    try :
        session = Session()
        ori_script = session.query(Script).filter(Script.id == script_id).first()
        if ori_script == None :
            return {"status":-1 , "val":None}
        ori_script.name = name 
        ori_script.desc = desc
        tmpfile = open(ori_script.location , "w")
        content = str(content)
        content = content.replace('\r\n' , '\n')
        tmpfile.writelines(content)
        tmpfile.flush()
        tmpfile.close()
        ori_script.save(session)
        return {"status":0 , "val":script_id}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def update_server(server_id , username , password , host_address , host_port , script_location) :
    try :
        session = Session()
        ori_server = session.query(Server).filter(Server.id == server_id).first()
        if ori_server == None :
            return {"status":-1 , "val":None}
        ori_server.username = username
        ori_server.password = password
        ori_server.host_address = host_address
        ori_server.host_port = host_port
        ori_server.script_location = script_location
        ori_server.save(session)
        return {"status":0 , "val":server_id}

    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def get_scripts_by_group_id (group_id) :
    try :
        session = Session()
        group = session.query(ScriptGroup).filter(ScriptGroup.id == group_id).first()
        ss = session.query(Sorted_Script).filter(Sorted_Script.group_id == group_id).first()
        if group == None or ss == None:
            return {"status":-1 , "val":None}
        sa = json.loads(ss.sorted_array)
        sorted_array = []
        tmp_dict = {}
        for script in group.scripts :
            script.groups = script.groups
            tmp_dict[script.id] = script
        for script_id in sa :
            sorted_array.append(tmp_dict[script_id])
        return {"status":0 , "val":sorted_array}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def get_server_group_list() :
    try :
        session = Session()
        group_list = session.query(ServerGroup).all()
        if group_list == None or len(group_list) == 0 :
            return {"status":-1 , "val":None}
        return {"status":0 , "val":group_list}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()
def get_server_group_by_id(group_id) :
    try :
        session = Session()
        group = session.query(ServerGroup).filter(ServerGroup.id == group_id).first()
        group.servers = group.servers
        if group == None :
            return {"status":-1 , "val":None}
        return {"status":0 , "val":group}
    except Exception , msginfo :
        return {"status": -1 , "val":msginfo}
    finally :
        session.close()

def get_all_servers() :
    try :
        session = Session()
        server_list = session.query(Server).all()
        if server_list == None or len(server_list) == 0 :
            return {"status":-1 , "val":None}
        for server in server_list :
            server.groups = server.groups
        return {"status":0 , "val":server_list}
    except Exception , msginfo :
        return {"status": -1 , "val":msginfo}
    finally :
        session.close()

def get_server_by_id(server_id) :
    try :
        session = Session()
        server = session.query(Server).filter(Server.id == server_id).first()
        if server == None :
            return {"status":-1 , "val":None}
        return {"status":0 , "val":server}
    except Exception , msginfo :
        return {"status": -1 , "val":msginfo}
    finally :
        session.close()

def get_servers_by_group_id (group_id) :
    try :
        session = Session()
        group = session.query(ServerGroup).filter(ServerGroup.id == group_id).first()
        if group == None :
            return {"status":-1 , "val":None}
        for server in group.servers :
            server.groups = server.groups
        return {"status":-1 , "val":group.servers}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def create_task(name , script_group_id , server_group_id) :
    try :
        session = Session()
        new_task = Task(script_group_id , server_group_id , name)
        task_id = new_task.save_return_id()
        if task_id <= 0 :
            return {"status":-1 , "val":None }
        return {"status":0 , "val":task_id}
    except Exception ,msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def delete_task(task_id) :
    try :
        session = Session()
        task = session.query(Task).filter(Task.id == task_id).first()
        if task == None :
            return {"status":-1 , "val":None}
        task.delete(session)
        return {"status":0 , "val":None}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def get_all_tasks() :
    try :
        session = Session()
        task_list = session.query(Task).all()
        if task_list == None or len(task_list) <= 0 :
            return {"status":-1 , "val":None}
        all_tasks_result = []
        for task in task_list :
            script_group = get_script_group_by_id(task.script_group_id)
            if script_group["status"] != 0 :
                return {"status":-1 , "val":None}
            server_group = get_server_group_by_id(task.server_group_id)
            if server_group["status"] != 0 :
                return {"status":-1 , "val":None}
            all_tasks_result.append({"task":task.dump() , "script_group":script_group["val"] , "server_group":server_group["val"]})
        return {"status":0 , "val":all_tasks_result}
    except Exception , msginfo :
        return {"status":-1 , "val":None}
    finally :
        session.close()

def get_task_by_id (task_id) :
    try :
        session = Session()
        task = session.query(Task).filter(Task.id == task_id).first()
        if task == None :
            return {"status":-1 , "val":None}
        script_group = get_script_group_by_id(task.script_group_id)
        if script_group["status"] != 0 :
            return {"status":-1 , "val":None}
        server_group = get_server_group_by_id(task.server_group_id)
        if server_group["status"] != 0 :
            return {"status":-1 , "val":None}
        return {"status":0 , "val":{"task":task.dump() , "script_group":script_group["val"] , "server_group":server_group["val"]}}
    except Exception , msginfo :
        return {"status":-1 , "val":None}
    finally :
        session.close()

def add_script2group(script_id , group_id):
    try :
        session = Session()
        script = session.query(Script).filter(Script.id == script_id).first()
        group = session.query(ScriptGroup).filter(ScriptGroup.id == group_id).first()
        if script == None or group == None :
            return {"status":-1 , "val" : None}
        if script not in group.scripts :
            group.scripts.append(script)
            group.save(session)
            sa = session.query(Sorted_Script).filter(Sorted_Script.group_id == group_id).first()
            sorted_array = json.loads(sa.sorted_array)
            sorted_array.append(int(script_id))
            sa.sorted_array = json.dumps(sorted_array)
            sa.save(session)
            return {"status":0 , "val" : None}
        return {"status":-1 , "val":None}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def add_server2group(server_id , group_id):
    try :
        session = Session()
        server = session.query(Server).filter(Server.id == server_id).first()
        group = session.query(ServerGroup).filter(ServerGroup.id == group_id).first()
        if server == None or group == None :
            return {"status":-1 , "val" : None}
        if server not in group.servers :
            group.servers.append(server)
            group.save(session)
            return {"status":0 , "val" : None}
        return {"status":-1 , "val":None}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def delete_script(script_id) :
    try :
        session = Session()
        script = session.query(Script).filter(Script.id == script_id).first()
        if script == None :
            return {"status":-1 , "val": None}
        for group in script.groups :
            ss = session.query(Sorted_Script).filter(Sorted_Script.group_id == group.id).first()
            sorted_array = json.loads(ss.sorted_array)
            sorted_array.remove(int(script_id))
            ss.sorted_array = json.dumps(sorted_array)
            ss.save(session)
        while(len(script.groups)>0) :
            script.groups.pop()
        script.save(session)
        script.delete(session)
        return {"status":0 , "val":script_id}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def delete_server(server_id) :
    try :
        session = Session()
        server = session.query(Server).filter(Server.id == server_id).first()
        if server == None :
            return {"status":-1 , "val":None}
        while(len(server.groups)>0) :
            server.groups.pop()
        server.save(session)
        server.delete(session)
        return {"status":0 , "val":server_id}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def remove_script(script_id , group_id):
    try :
        session = Session()
        script = session.query(Script).filter(Script.id == script_id).first()
        group = session.query(ScriptGroup).filter(ScriptGroup.id == group_id).first()
        if script == None or group == None :
            return {"status":-1 , "val":None}
        if script in group.scripts :
            group.scripts.remove(script)
            group.save(session)            
            ss = session.query(Sorted_Script).filter(Sorted_Script.group_id == group_id).first()
            sorted_array = json.loads(ss.sorted_array)
            sorted_array.remove(int(script_id))
            ss.sorted_array = json.dumps(sorted_array)
            ss.save(session)
            return {"status":0 , "val":None}
        return {"status":-1 , "val":None}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()
def remove_server(server_id , group_id):
    try :
        session = Session()
        server = session.query(Server).filter(Server.id == server_id).first()
        group = session.query(ServerGroup).filter(ServerGroup.id == group_id).first()
        if server == None or group == None :
            return {"status":-1 , "val":None}
        if server in group.servers :
            group.servers.remove(server)
            group.save(session)
        return {"status":0 , "val":None}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def update_position(group_id , json_str) :
    try :
        session = Session()
        position_list = json_str.split('|')
        position_list.remove(position_list[len(position_list)-1])
        for i in range(len(position_list)) :
            position_list[i] = int(str(position_list[i]))
        sorted_script = session.query(Sorted_Script).filter(Sorted_Script.group_id == group_id).first()
        sorted_array = json.loads(sorted_script.sorted_array)
        check = True
        for item in position_list :
            if item not in sorted_array :
                check = False
                break
        if len(position_list) != len(sorted_array) :
            check = False
        if check == True :
            sorted_script.sorted_array = json.dumps(position_list)
            sorted_script.save(session)
            return {"status":0 , "val":None}
        else :
            return {"status":-1 , "val":None}
   
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}
    finally :
        session.close()

def do_command (task_id) :
    try :
        task_res = get_task_by_id(task_id)
        if task_res["status"] != 0 :
            return {"status":-1 , "val":None}
        task = task_res["val"]["task"]
        group_id = script_group = task_res["val"]["script_group"].id
        server_group = task_res["val"]["server_group"]
        scripts = get_scripts_by_group_id(group_id)["val"]
        script_list = []
        for script in scripts :
            script_list.append(str(script.location))
        server_list = []
        for server in server_group.servers :
            server_list.append(server.dump())
        if script_list == [] or server_list == [] :
            return {"status":-1 , "val":None}
        task_to_do = {"scripts":script_list , "servers":server_list}
        success_array , key_code_list = upload_remotefile.do_task(task_to_do)
        session = Session()
        taskStatus = session.query(TaskStatus).filter(TaskStatus.task_id == task_id).first()
        if taskStatus == None :
            taskStatus = TaskStatus(task_id , json.dumps(success_array) , json.dumps(key_code_list))
            taskStatus_id = taskStatus.save_return_id(session)
        else :
            taskStatus.success_array = json.dumps(success_array)
            taskStatus.key_code_list = json.dumps(key_code_list)
            taskStatus_id = taskStatus.id
            taskStatus.save(session)
        session.close()
        return {"status":0 , "val":taskStatus_id}
    except Exception , msginfo :
        return {"status":-1 , "val":msginfo}

def do_request(task_id) :
    try:
        session = Session()
        status = session.query(TaskStatus).filter(TaskStatus.task_id == task_id).first()
        if status == None :
            return {"status":-1 , "val":None}
        success_array = json.loads(status.success_array)
        key_code_list = json.loads(status.key_code_list)
        result = upload_remotefile.get_request_result(success_array , key_code_list)
        return {"status":0 , "val":result}
    except Exception , msginfo :
        return {"Status":-1 , "val":None}
    finally :
        session.close()
if __name__ == '__main__' :
    print do_command(1)
    print do_request(1)
