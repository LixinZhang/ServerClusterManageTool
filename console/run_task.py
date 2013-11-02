import pexpect
from LogUtil import Logging
import pxssh
import hashlib
import datetime
import time
import threading
import Queue
import task_parser 
import sys

timeout_ = 100
max_work_threads = 10
def upload_file(file_path_list , remote_user , remote_host ,remote_path , password , remote_port = 22) :
    '''
    Copy a file to remote machine. return 0 if success
    '''
    logger = Logging.getLogger(log_file='run_task.log')
    try :
        file_path = ' '# multi files
        for path_item in file_path_list :
            file_path += path_item
            file_path += ' '
        if not file_path or not remote_user or not remote_host or not remote_path :
            logger.error('Empty parameter given')
            raise Excpetion , 'Empty parameter given'
        cmd_text = 'scp -P %d %s %s@%s:%s' % \
            (remote_port , file_path, remote_user, remote_host, remote_path)
        
        print cmd_text
        logger.info(cmd_text)
        global timeout_
        cmd = pexpect.spawn(cmd_text,timeout=timeout_)
        expect_res = cmd.expect(['(yes/no)','password',pexpect.EOF,pexpect.TIMEOUT])
        if expect_res == 0 :
            logger.info('pexpect expects (yes/no)')
            cmd.sendline('yes')
            cmd.expect('password')
            cmd.sendline(password)
        elif expect_res == 1 :
            logger.info('pexpect expects (password)')
            cmd.sendline(password)
        elif expect_res == 2 :
            logger.info('pexpect expects (EOF)')
        else:
            logger.info('pexpect expects (TIMEOUT)')
            raise Exception , 'TIMEOUT'
        expect_res = cmd.expect(['Permission denied',pexpect.EOF])
        if expect_res == 0 :
            logger.info('Permission denied')
            cmd.close()
            cmd.kill(0)
        else :
            cmd.close()
        return cmd.exitstatus
    except Exception ,e :
        cmd.close()
        logger.error(e)
        return 1

def do_remotecommand(file_path_list, server_array) :
    '''
    copy a script file list to server_array and execute the script files at remote machines
    Each file has a unique key_code.
    The standard output and standard error output of all files are written to a log file named 'log_code.log'
    return a Queue object which contains [exitstatus, key_code_list, log_code, machine]
    '''   
    '''
    if not file_path_list or type(file_path_list) is not list \
            or not server_array or type(server_array) is not list :
                return None
    '''
    file_list = []
    key_code_list = []
    log_code = hashlib.md5(str(datetime.datetime.now())).hexdigest()
    log_code = log_code[len(log_code)/2:]
    log_name = log_code + '.log'

    for file_path in file_path_list :
        if file_path.rfind('/') != 0:
            file_name = file_path[file_path.rfind('/')+1:]
        else : 
            file_name = file_path
        file_code = hashlib.md5(str(datetime.datetime.now())).hexdigest()
        file_code = file_code[len(file_code)/2:]
        newfile_name = log_code + file_code + file_name
        file_list.append((file_name , newfile_name))
        key_code_list.append(log_code + file_code)
    result = Queue.Queue()
    def work(machine):
        upload_res =  upload_file(file_path_list,machine['remote_user'], machine['remote_host'], machine['remote_path'],\
                machine['password'], machine.get('remote_port',22))
        if upload_res == 0 :
            try:
                s = pxssh.pxssh()
                is_login = s.login(server = machine['remote_host'], username = machine['remote_user'], password = machine['password'] , login_timeout = 100)
                if is_login == False :
                    raise Exception , 'Permission denied'
                else: 
                    print 'login %s success' % machine["remote_host"]

                if machine['remote_path'].endswith('/') == False:
                    machine['remote_path'] += '/'
                s.sendline('cd '+ machine['remote_path'])
                s.prompt()
                for file_name , newfile_name in file_list :
                    s.sendline('mv '+ file_name  + ' ' + newfile_name)
                    s.prompt()
                    s.sendline('chmod u+x ' + newfile_name)
                    s.prompt()
                s.sendline('cd ~')
                s.prompt()
                cmd_text = ''
                for file_name , newfile_name in file_list :
                    newfile_name_ = machine['remote_path'] + newfile_name
                    log_name_ = machine['remote_path'] + log_name
                    cmd_text += newfile_name_ + ' >> ' + log_name_ + ' 2>&1 && '
                cmd_text += 'echo ' + log_code + '#' +' >> ' + log_name_ + ' &'
                s.sendline(cmd_text)
                s.prompt()
                s.logout()
                result.put([s.exitstatus,key_code_list,log_code,machine])#success
            except Exception, e: 
                print e
                result.put([-1,[],'',machine])#fail
    
    machine_queue = Queue.Queue()
    for machine in server_array :
        machine_queue.put(machine)
    def minithreadworker (queue) :
        try :
            while queue.empty() == False :
                work(queue.get(True , 10))
        except Queue.Empty :
            pass
    thread_num = min( max_work_threads , machine_queue.qsize() )
    work_threads = [] 
    for i in range(thread_num) :
        new_thread = threading.Thread(target = minithreadworker , args = [machine_queue ,])
        work_threads.append(new_thread)
        new_thread.start()
    for thread in work_threads :
        thread.join() #just wait
    return result

def do_multi_query(key_code_list , server_array) : 
    '''
    Query for running status of script files.
    return a Queue object which contains [PID,executing_id,exitstatus,content,machine]
    PID : process number of a still running script file
    exectuing_id : which file is running
    exitstatus : ssh exit status , 0 if success
    content : the last 10 lines of the log file 
    machine : for which machine
    '''
    log_code = key_code_list[0][:len(key_code_list[0])/2]
    result = Queue.Queue()
    def do_query(key_code_list,machine) :
        try:
            s = pxssh.pxssh()
            is_login = s.login(machine['remote_host'], machine['remote_user'], machine['password'])
            if is_login == False:
                raise Exception , 'Permission denied'
            s.sendline('ps -aux | grep --color=never ' + log_code)
            s.prompt()
            words = s.before.split()
            index = 0
            PID = -1
            executing_id = 0
            FIND = False
            if machine['remote_path'].endswith('/') == False :
                machine['remote_path'] += '/'
            for item in words :
                if item.find(machine['remote_path'] + log_code) >= 0 :
                    PID = int(words[index-10])
                    for code in key_code_list :
                        if item.find(code) >= 0 :
                            FIND = True
                            break
                        executing_id += 1
                    break
                index+=1
            if FIND == False :
                executing_id = -1
            s.sendline('cd ' + machine['remote_path'])
            s.prompt()
            s.sendline('tail -10 ' + log_code + '.log')
            s.prompt()
            content = s.before
            end_index = content.find(log_code+'#')
            exitstatus = -1
            if end_index >= 0 :
                exitstatus = 0
            content = content[content.find('\r\n')+2:end_index]
            result.put([PID , executing_id , exitstatus , content , machine])
        except Exception , e :
            result.put([-1,-1,-1,'',machine])
    work_threads = [] 
    for machine in server_array :
        work_thread = threading.Thread(target = do_query ,args = (key_code_list,machine,))
        work_threads.append(work_thread)
        work_thread.start()
    for t in work_threads :
        t.join()
    return result

if __name__ == '__main__':
    if len(sys.argv)<2 :
        print 'Error! Please input the task xml file'
        exit()
    tasks = task_parser.task_parser(sys.argv[1])
    server_array = tasks['servers']
    file_path_list = tasks['scripts']
    command_result = do_remotecommand(file_path_list,server_array)
    success_array = []
    key_code_list = []
    while command_result.empty() == False :
        res = command_result.get()
        do_res = res[0]
        key_code_list = res[1]
        log_code = res[2]
        machine = res[3]
        if do_res == 0 :
            success_array.append(machine)
    while 1:         
        query_result = do_multi_query(key_code_list ,success_array)
        while query_result.empty() == False :
            PID , executing_id , exitstatus , content ,machine = query_result.get()
            print '#'*10 , machine['remote_host'] , '#'*10
            if PID > 0 :
                print 'Remote process is alive ! , PID : ' , PID 
                print 'script file ' + file_path_list[executing_id] + ' is running!'
            else :
                print 'Remote process is dead !'
            if exitstatus == 0 :
                print 'Done!'
            else :
                if PID < 0 :
                   print 'something wrong happened !'
            print content
