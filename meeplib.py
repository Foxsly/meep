import pickle
import MySQLdb
import _mysql
import sys

"""
meeplib - A simple message board back-end implementation.

Functions and classes:

 * u = User(username, password) - creates & saves a User object.  u.id
     is a guaranteed unique integer reference.

 * m = Message(title, post, author) - creates & saves a Message object.
     'author' must be a User object.  'm.id' guaranteed unique integer.

 * get_all_messages() - returns a list of all Message objects.

 * get_all_users() - returns a list of all User objects.

 * delete_message(m) - deletes Message object 'm' from internal lists.

 * delete_user(u) - deletes User object 'u' from internal lists.

 * get_user(username) - retrieves User object for user 'username'.

 * get_message(msg_id) - retrieves Message object for message with id msg_id.

"""

__all__ = ['Message', 'get_all_messages', 'get_message', 'delete_message',
           'User', 'get_user', 'get_all_users', 'delete_user']

###
# internal data structures & functions; please don't access these
# directly from outside the module.  Note, I'm not responsible for
# what happens to you if you do access them directly.  CTB

# a string, stores the current user that is logged on
_curr_user = []

# a dictionary, storing all messages by a (unique, int) ID -> Message object.
_messages = {}

# a dictionary, storing all users by a (unique, int) ID -> User object.
_user_ids = {}

# a dictionary, storing all users by username
_users = {}

# a dictionary, storing all topics by a (unique, int) ID -> Topic object.
_topics = {}

def _get_next_message_id():
    if _messages:
        return max(_messages.keys()) + 1
    return 0

def _get_next_user_id():
    if _users:
        return int(max(_user_ids.keys())) + 1
    return 0
    
def _get_next_topic_id():
    if _topics:
        return max(_topics.keys()) + 1
    return 0

def _reset():
    """
    Clean out all persistent data structures, for testing purposes.
    """
    global _messages, _users, _user_ids, _topics, _curr_user
    _messages = {}
    _users = {}
    _user_ids = {}
    _topics = {}
    _curr_user = []

###

###
# MySQL implementation
###
_conn = None

###
# Loads the data
###
def _load_data():
    pass

###
# Creates the tables
###
def _create_tables(conn):
    def _create_user_table(conn):
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS user (\
            id INT NOT NULL PRIMARY KEY,\
            username VARCHAR(25) NOT NULL,\
            password VARCHAR(25) NOT NULL\
        );")
    def _create_topic_table(conn):
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS topic (\
            id INT NOT NULL PRIMARY KEY,\
            title VARCHAR(255) NOT NULL,\
            author_id INT NOT NULL REFERENCES user (id)\
        );")
    def _create_message_table(conn):
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS message (\
            id INT NOT NULL PRIMARY KEY,\
            post VARCHAR(255) NOT NULL,\
            author_id INT NOT NULL REFERENCES user (id),\
            msg_topic_id INT NOT NULL REFERENCES topic (id),\
            title VARCHAR(255) NOT NULL,\
            topic_msg_id INT NOT NULL\
            )")
    _create_user_table(conn)
    _create_topic_table(conn)
    _create_message_table(conn)

###
# Loads data from the tables
###
def _load_data():
    print ('in load data')
    def load_users(conn):
        cur=conn.cursor()
        cur.execute("SELECT * FROM user")
        rows = cur.fetchall()
        for row in rows:
            #0=id, 1=username, 2=password
            User(row[1], row[2], row[0])
    def load_topics(conn):
        cur=conn.cursor()
        cur.execute("SELECT * FROM topic")
        rows = cur.fetchall()
        for row in rows:
            #0=id, 1=title, 2=author
            topicuser = _user_ids[row[0]]
            Topic(row[1], row[2], topicuser)
    def load_messages(conn):
        cur=conn.cursor()
        cur.execute("SELECT * FROM message")
        rows = cur.fetchall()
        for row in rows:
            #0=id, 1=post, 2=author, 3=topic, 4=title
            author = _user_ids[row[2]]
            topic = _topics[row[3]]
            message = Message(row[4], row[1], author, row[0])
            topic.add_message(message, row[5])
    #global _conn
    conn = None
    try:
        try:
            conn = MySQLdb.connect(db='meepdb')
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0],e.args[1])
            sys.exit(1)

        _create_tables(conn)
        print('tables created')
        load_users(conn)
        load_topics(conn)
        load_messages(conn)

    finally:
        if conn:
            conn.close()

def _get_db_conn():
    try:
        conn = MySQLdb.connect(db='meepdb')
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    return conn

def _save_data(tablename, *args):
    try:
        try:
            conn = MySQLdb.connect(db='meepdb')
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0],e.args[1])
            sys.exit(1)

        cur = conn.cursor()
        query = "INSERT INTO " + tablename + "VALUES ("
        for arg in args:
            query += arg
        cur.execute(query)
    finally:
        if conn:
            conn.close()

def _delete_data(tablename, id):
    try:
        try:
            conn = MySQLdb.connect(db='meepdb')
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0],e.args[1])
            sys.exit(1)

        cur = conn.cursor()
        query = "DELETE FROM " + tablename + "WHERE id=" + str(id)
        cur.execute(query)
    finally:
        if conn:
            conn.close()


###

class Message(object):
    """
    Simple "Message" object, containing title/post/author.

    'author' must be an object of type 'User'.
    
    """
    def __init__(self, title, post, author, id=None):
        if id:
            self.title = title
            self.post = post
            self.author = author
            self.id = id
            _messages[self.id] = self
        else:
            self.title = title
            self.post = post
            assert isinstance(author, User)
            self.author = author
            self._save_message()

    def _save_message(self):
        self.id = _get_next_message_id()
        # register this new message with the messages list:
        _messages[self.id] = self
        

def get_all_messages(sort_by='id'):
    return _messages.values()

def get_message(id):
    return _messages[id]

def delete_message(msg):
    assert isinstance(msg, Message)
    _delete_data('message', msg.id)
    del _messages[msg.id]

###

class Topic(object):
    """
    Simple "Topic" object, containing a title, author, and messages.
    
    author must be an object of type 'User', and messages contains objects of type 'Message'
    """
    def __init__(self, title, message, author, id=None):
        if id:
            self.title = title
            self.author = author
            self.id = id
            self.messages = {}
            _topics[self.id] = self
        else:
            self.title = title
            assert isinstance(message, Message)
            self.messages = {message.id : message}
            assert isinstance(author, User)
            self.author = author
            self._save_topic()

    def _save_topic(self):
        self.id = _get_next_topic_id()
        _topics[self.id] = self
        _save_data('topic', self.id, self.title, self.author.id)
        
    def _get_next_msg_id(self):
        if self.messages:
            return max(self.messages.keys()) + 1
        return 0
        
    def get_messages(self):
        return self.messages.values()
        
    def add_message(self, message, id=None):
        assert isinstance(message, Message)
        if id:
            self.messages[id] = message
        else:
            id=self._get_next_msg_id()
            self.messages[id] = message
            _save_data('message', message.id, message.post, message.author.id, self.id, message.title, id)

    def delete_message_from_topic(self, msg):
        assert isinstance(msg, Message)
        _delete_data('message', msg.id)
        del self.messages[msg.id]

def get_all_topics():
    return _topics.values()

def get_topic(id):
    return _topics[id]
        
def delete_topic(topic):
    del _topics[topic.id]
    _save_topic_data()

###

class User(object):
    #This is for new users through the frontend
    def __init__(self, username, password, id=None):
        if id:
            self.username = username
            self.password = password
            self.id = id
            _users[self.username] = self
            _user_ids[self.id] = self
        else:
            self.username = username
            self.password = password
            self._save_user()

    def _save_user(self):
        self.id = _get_next_user_id()
        # register new user ID with the users list:
        _user_ids[self.id] = self
        _users[self.username] = self
        _save_data('user', self.id, self.username, self.password)

def set_curr_user(username):
    _curr_user.insert(0, username)

def get_curr_user():
    if(len(_curr_user) > 0):
        return _curr_user[0]
    else:
        return None

def delete_curr_user():
    if(get_curr_user() != None):
        _curr_user.pop(0)
    """
    if(len(_curr_user) > 0):
        print get_curr_user()
        _curr_user.remove(_curr_user.index(0))
    """

def get_user(username):
    return _users.get(username)

def get_all_users():
    return _users.values()

def delete_user(user):
    _delete_data('user', user.id)
    del _users[user.username]
    del _user_ids[user.id]

def check_user(username, password):
    aUser = get_user(username)
    if aUser == None:
        return False

    if aUser.password == password:
        return True
    else:
        return False

###

###
# Debugging functions
###

def _print_topics():
    for x in _topics.values():
        print 'Topic ID: ', x.id, 'Title: ', x.title

def _print_messages():
    for x in _messages.values():
        print 'Message ID: ', x.id, 'Title: ', x.title, 'Message: ', x.post

def _print_users():
    for x in _users.values():
        print 'Username: ', x.username, 'Password: ', x.password
    
def _print_user_ids():
    pass
