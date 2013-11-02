from xml.dom import minidom , Node

def task_parser (task_config_file) :
    try :
        doc = minidom.parse(task_config_file)
        task_list = {}
        server_list = []
        script_list = []
        task = None
        for child in doc.childNodes :
            if child.nodeType == Node.ELEMENT_NODE and child.tagName == 'task' :
                task = child
                break
        for child in task.childNodes :
            if child.nodeType == Node.ELEMENT_NODE :
                if child.tagName == 'servers' :
                    for server in child.childNodes :
                        if server.nodeType == Node.ELEMENT_NODE and server.tagName == 'server' :
                            server_item = {}
                            for item in server.childNodes :
                                if item.nodeType == Node.ELEMENT_NODE :
                                    server_item[str(item.tagName)] = str(item.firstChild.nodeValue
)
                                    if item.tagName == 'remote_port' :
                                        server_item[str(item.tagName)] = int(server_item[str(item.tagName)])
                            server_list.append(server_item)
                elif child.tagName == 'scripts' :
                    for script in child.childNodes :
                        if script.nodeType == Node.ELEMENT_NODE and script.tagName == 'script_path' :
                            script_list.append(str(script.firstChild.nodeValue))

        task_list['servers'] = server_list
        task_list['scripts'] = script_list
        return task_list
    except Exception , msginfo :
        print 'Excption ! ' , msginfo
        return {}
if __name__ == '__main__' : 
    task_list = tasks_parser('tasks.xml')
    print task_list
