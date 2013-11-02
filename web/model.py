import sqlalchemy
from sqlalchemy import *
from sqlalchemy.dialects.mysql import *
from sqlalchemy.orm import sessionmaker , relationship , scoped_session
from sqlalchemy.ext.declarative import declarative_base
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('database.conf')

db_user = config.get('DB' , 'user')
db_password = config.get('DB' ,'password')
db_host = config.get('DB' , 'host')
db_database = config.get('DB' , 'database')

DB_Connect = 'mysql://%s:%s@%s/%s?charset=utf8' % (db_user , db_password , db_host , db_database)
engine = create_engine(DB_Connect)

Declbase = declarative_base()
metadata = Declbase.metadata
Session = scoped_session(sessionmaker(bind = engine))

class Base :
    def save(self, use_session = None):
        if use_session is None:
            use_session = Session()
        use_session.add(self)
        use_session.commit()
        use_session.flush()
        use_session.expunge(self)
    def refresh(self,use_session = None):
    	if use_session is None:
    		use_session = Session()
    	use_session.add(self)
    	use_session.refresh(self)
    	use_session.commit()
    	use_session.expunge(self)
    def delete(self,use_session = None):
    	if use_session is None:
    		use_session = Session()
    	use_session.add(self)
    	use_session.delete(self)
    	use_session.commit()
    	use_session.expunge(self)
    def save_return_id(self , use_session = None):
        if use_session is None :
            use_session = Session()
        use_session.add(self)
        use_session.flush()
        id_ =  self.id
        use_session.commit()
        use_session.flush()
        use_session.expunge(self)
        return id_

script_group = Table('script_group', metadata ,\
        Column('script_id' , INTEGER , ForeignKey('script.id') ,primary_key = True),\
        Column('scriptGroup_id' , INTEGER , ForeignKey('scriptGroup.id') , primary_key = True))

class Script(Declbase,Base):
    __tablename__ = 'script'
    __table_args__ = {'mysql_charset':'utf8'}
    id = Column(INTEGER , primary_key = True)
    name = Column(NVARCHAR(256))
    desc = Column(NVARCHAR(1024))
    location = Column(NVARCHAR(256))
    groups = relationship('ScriptGroup',secondary=script_group,backref='script')
    
    def __getattr__(self,name):
        if name == 'group_ids':
            return [group.id for group in self.groups]
        raise AttributeError , 'AttributeError'
    def __init__(self , p_name , p_location , p_desc) :
        self.name = p_name
        self.location = p_location
        self.desc = p_desc
    def __repr__(self):
        return 'name=%s , location=%s , desc=%s ' % (self.name , self.location , self.desc )

    def dump(self) :
        ret = {}
        ret['id'] = self.id 
        ret['name'] = self.name
        ret['location'] = self.location
        ret['group_ids'] = self.group_ids
        ret['desc'] = self.desc
        return ret

class ScriptGroup(Declbase,Base):
    __tablename__ = 'scriptGroup'
    __table_args__ = {'mysql_charset':'utf8'}
    id = Column(INTEGER , primary_key = True)
    name = Column(NVARCHAR(256))
    scripts = relationship('Script', secondary = script_group , backref = 'scriptGroup')
    def __getattr__(self,name):
        if name == 'script_ids':
            return [script.id for script in self.scripts]
        raise AttributeError , 'AttributeError'
    def __init__(self , p_name ) :
        self.name = p_name
    def __repr__(self):
        return 'name=%s' % (self.name)
    def dump(self) :
        ret = {}
        ret['id'] = self.id
        ret['name'] = self.name
        ret['script_ids'] = self.script_ids
        return ret

class Sorted_Script(Declbase,Base):
    __tablename__ = 'sorted_script'
    __table_args__ = {'mysql_charset':'utf8'}
    id = Column(INTEGER , primary_key = True)
    group_id = Column(INTEGER , ForeignKey('scriptGroup.id'))
    sorted_array = Column(NVARCHAR(4096))
    def __init__(self , p_group_id , p_sorted_array) :
        self.group_id = p_group_id
        self.sorted_array = p_sorted_array

    def dump(self) :
        ret = {}
        ret['id'] = self.id
        ret['group_id'] = self.group_id 
        ret['sorted_array'] = self.sorted_array

server_group = Table('server_group' , metadata , \
        Column('server_id' , INTEGER , ForeignKey('server.id') , primary_key = True),\
        Column('serverGroup_id' , INTEGER , ForeignKey('serverGroup.id'),primary_key = True))

class Server(Declbase , Base) :
    __tablename__ = 'server'
    __table_args__ = {'mysql_charset':'utf8'}
    id = Column(INTEGER , primary_key = True)
    username = Column(NVARCHAR(256))
    password = Column(NVARCHAR(256))
    host_address = Column(NVARCHAR(128))
    host_port = Column(NVARCHAR(16))
    script_location = Column(NVARCHAR(256))
    groups = relationship('ServerGroup' , secondary = server_group , backref = 'server')

    def __getattr__(self , name) :
        if name == 'group_ids':
            return [group.id for group in self.groups]
        raise AttributeError , 'AttributeError'
    def __init__(self , p_username , p_password , p_host_address , p_host_port , p_script_location) :
        self.username = p_username
        self.password = p_password
        self.host_address = p_host_address
        self.host_port = p_host_port
        self.script_location = p_script_location
    def __repr__(self) :
        return "username=%s , password=%s , host_address=%s , host_port=%s , script_location=%s" % (self.username , self.password , self.host_address , self.host_port , self.script_location)
    def dump(self) :
        ret = {}
        ret['id'] = self.id
        ret['remote_user'] = str(self.username)
        ret['password'] = str(self.password)
        ret['remote_host'] = str(self.host_address)
        ret['remote_port'] = int(self.host_port)
        ret['remote_path'] = str(self.script_location)
        return ret

class ServerGroup(Declbase , Base) :
    __tablename__ = 'serverGroup'
    __table_args__ = {'mysql_charset':'utf8'}
    id = Column(INTEGER , primary_key = True)
    name = Column(NVARCHAR(256))
    servers = relationship('Server' , secondary = server_group , backref = 'serverGroup')
    def __getattr__ (self , name ) :
        if name == 'server_ids':
            return [server.id for server in self.servers]
        raise AttributeError , 'AttributeError'
    def __init__(self , p_name) :
        self.name = p_name
    def dump(self) :
        ret = {}
        ret['id'] = self.id
        ret['name'] = self.name
        ret['server_ids'] = self.server_ids
        return ret

class Task (Declbase , Base) :
    __tablename__ = 'task'
    __table_args__ = {'mysql_charset':'utf8'}
    id = Column(INTEGER , primary_key = True)
    name = Column(NVARCHAR(256))
    script_group_id = Column(INTEGER,ForeignKey('scriptGroup.id'))
    server_group_id = Column(INTEGER,ForeignKey('serverGroup.id'))

    def __init__(self , p_script_group_id , p_server_group_id , p_name = "") :
        self.script_group_id = p_script_group_id 
        self.server_group_id = p_server_group_id
        self.name = p_name

    def dump(self) :
        ret = {}
        ret['id'] = self.id 
        ret['script_group_id'] = self.script_group_id
        ret['server_group_id'] = self.server_group_id
        ret['name'] = self.name
        return ret

class TaskStatus (Declbase , Base) :
    __tablename__ = 'taskStatus'
    __table_args__ = {'mysql_charset':'utf8'}
    id = Column(INTEGER , primary_key = True)
    task_id = Column(INTEGER , ForeignKey('task.id'))
    success_array = Column(NVARCHAR(40960))
    key_code_list = Column(NVARCHAR(40960))

    def __init__(self , p_task_id , p_success_array , p_key_code_list) :
        self.task_id = p_task_id
        self.success_array = p_success_array
        self.key_code_list = p_key_code_list

metadata.create_all(engine)

