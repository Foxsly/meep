import meeplib
import traceback
import cgi
import meepcookie
import os
from Cookie import SimpleCookie
from jinja2 import Environment, FileSystemLoader

def initialize():
    try:
        meeplib._load_data()
    except IOError:  # file does not exist/cannot be opened
        # initialize data from scratch
        # create a default user with username: test, password: test
        u = meeplib.User('test', 'test')

        # create a single message and topic
        meeplib.Topic('First Topic', meeplib.Message('my title', 'This is my message!', u), u)

#Check if tests are running - if so, load the proper templates.
if 'test' in os.getcwd():
    env = Environment(loader=FileSystemLoader('../templates'))
else:
    env = Environment(loader=FileSystemLoader('templates'))

def render_page(filename, **variables):
    template = env.get_template(filename)
    x = template.render(**variables)
    return str(x)        
        
class MeepExampleApp(object):
    """
    WSGI app object.
    """
    def index(self, environ, start_response):
        #start_response("200 OK", [('Content-type', 'text/html')])
        username = ''
        # If a cookie exists, get it
        try:
            cookie_str = environ.get('HTTP_COOKIE', '')
            cookie = SimpleCookie(cookie_str)
            username = cookie["username"].value
            print "Login: Username = %s" % username
        except:
            #TODO change this from a broad exception
            print "session cookie not set! defaulting username"
            username = ''
        
        #If the cookie was found, redirect to main page, and set current user
        if username is not '':
            meeplib.set_curr_user(username)
            headers = [('Content-type', 'text/html')]
            headers.append(('Location','/main_page'))
            start_response("302 Found", headers)
            return "Cookie found, redirecting"
        #If the cookie wasn't found, prompt the user to login
        else:
            start_response("200 OK", [('Content-type', 'text/html')])
            return [ render_page('index.html') ]

    ###
    #   MAIN PAGE
    ###
    def main_page(self, environ, start_response):
        headers = [('Content-type', 'text/html')]

        if(meeplib.get_curr_user() is None):
            headers.append(('Location', '/'))
            start_response("401 Unauthorized", headers)
            return ["""<a href='/'>Click to login</a>"""]

        start_response("200 OK", headers)
        username = meeplib.get_curr_user()

        return [ render_page('main_page.html', username=username) ]

    ###
    #   CREATE USER
    ###
    def create_user(self, environ, start_response):
        headers = [('Content-type', 'text/html')]
        
        start_response("200 OK", headers)
        return [ render_page('create_user.html') ]

    def create_user_action(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        #TODO Error Checking on Creating a User
        returnStatement = "user added"
       
        username = form['username'].value
        password = form['password'].value
  
        new_user = meeplib.User(username, password)

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/'))
        start_response("302 Found", headers)

        return [returnStatement]

    ###
    #   LOGIN
    ###
    def login(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        username = form['username'].value
        password = form['password'].value

        # set content-type
        headers = [('Content-type', 'text/html')]

        k = 'Location'
        v = '/'

        # Test whether variable is defined to be None
        # No idea why these tests don't work... the None value from the form is viewed as a string
        if username != "None":
             if password != "None":
                 if meeplib.check_user(username, password) is False:
                     returnStatement = """Invalid login"""
           
                 else:
                     meeplib.set_curr_user(username)
                     k = 'Location'
                     v = '/main_page'
                     # Create and set the cookie
                     cookie_name, cookie_val = meepcookie.make_set_cookie_header('username', username)
                     headers.append((cookie_name, cookie_val))
                     print cookie_name, cookie_val
                     returnStatement = """Login successful"""
             else:      
                 returnStatement = """password none"""
        else:
            returnStatement = """username none"""

        headers.append((k, v))
        start_response('302 Found', headers)
        
        return returnStatement

    ###
    #   LOGOUT
    ###
    def logout(self, environ, start_response):
        headers = [('Content-type', 'text/html')]
        #Clear the cookie
        #TODO: remove try block here, need to test that it still works properly
        try:
            #cookie_str = environ.get('HTTP_COOKIE', '')
            #cookie = SimpleCookie(cookie_str)
            cookie_name, cookie_val = meepcookie.make_set_cookie_header('username', '')
            headers.append((cookie_name, cookie_val))
        except:
            print "No cookie exists (this probably shouldn't happen)"

        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers.append((k, v))
        start_response('302 Found', headers)
        
        return "Logged out"

    ###
    #   LIST TOPICS
    ###
    def list_topics(self, environ, start_response):
        topics = meeplib.get_all_topics()   
        
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)

        return [ render_page('view_topics.html', topics = topics) ]        
        
    ###
    #   VIEW TOPIC
    ###
    def view_topic(self, environ, start_response):
        qString = cgi.parse_qs(environ['QUERY_STRING'])
        tId = qString.get('id', [''])[0]
        topic = meeplib.get_topic(int(tId))
        messages = topic.get_messages()
        
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)
        
        return [ render_page('view_topic.html', messages=messages, topic=topic) ]
    
    ###
    #   ADD TOPIC
    ###
    def add_topic(self, environ, start_response):
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)

        return [ render_page('add_topic.html') ]
        
    def add_topic_action(self, environ, start_response):
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        #Get values off form
        title = form['title'].value
        msgtitle = form['msgtitle'].value
        message = form['message'].value
        
        #Get the current user
        username = meeplib.get_curr_user()
        user = meeplib.get_user(username)
        
        #Create new message and topic
        new_message = meeplib.Message(msgtitle, message, user)
        new_topic = meeplib.Topic(title, new_message, user)

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list_topics'))
        start_response("302 Found", headers)
        return ["topic added"]

    ###
    #   ADD MESSAGE TO TOPIC
    ###
    def add_message_topic_action(self, environ, start_response):
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        #Get values off the form
        topicId = form['topicid'].value        
        title = form['title'].value
        message = form['message'].value
        
        #Get the topic and user
        topic = meeplib.get_topic(int(topicId))
        username = meeplib.get_curr_user()
        user = meeplib.get_user(username)
        
        #Add the message to the topic
        new_message = meeplib.Message(title, message, user)
        topic.add_message(new_message)
        
        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/topics/view?id=%d' % (topic.id)))
        start_response("302 Found", headers)
        return ["message added to topic"]
        
    ###
    #   DELETE MESSAGE
    ###
    def delete_message_action(self, environ, start_response):
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        #Get the message
        messageId = form['mid'].value
        message = meeplib.get_message(int(messageId))
        
        #Delete the message from the topic
        topicId = form['tid'].value
        topic = meeplib.get_topic(int(topicId))
        topic.delete_message_from_topic(message)
        
        #Delete the message altogether
        meeplib.delete_message(message)
        
        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list_topics'))
        start_response("302 Found", headers)
        return ["message deleted"]
        
    ###
    #   DELETE TOPIC
    ###
    def delete_topic_action(self, environ, start_response):
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        topicId = form['tid'].value
        topic = meeplib.get_topic(int(topicId))
        meeplib.delete_topic(topic)
        
        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list_topics'))
        start_response("302 Found", headers)
        return ["topic deleted"]

    ###
    #   CALL HANDLER
    ###
    def __call__(self, environ, start_response):
        # store url/function matches in call_dict
        call_dict = { '/': self.index,
                      '/main_page': self.main_page,
                      '/login': self.login,
                      '/logout': self.logout,
                      '/create_user': self.create_user,
                      '/create_user_action':self.create_user_action,
                      '/m/list_topics': self.list_topics,
                      '/m/topics/view': self.view_topic,
                      '/m/add_message_topic_action': self.add_message_topic_action,
                      '/m/add_topic': self.add_topic,
                      '/m/add_topic_action': self.add_topic_action,
					  '/m/delete_action': self.delete_message_action,
                      '/m/delete_topic_action': self.delete_topic_action
                      }

        # see if the URL is in 'call_dict'; if it is, call that function.
        url = environ['PATH_INFO']
        fn = call_dict.get(url)

        if fn is None:
            start_response("404 Not Found", [('Content-type', 'text/html')])
            return ["Page not found."]

        try:
            return fn(environ, start_response)
        except:
            tb = traceback.format_exc()
            print tb
            x = "<h1>Error!</h1><pre>%s</pre>" % (tb,)
            
            status = '500 Internal Server Error'
            start_response(status, [('Content-type', 'text/html')])
            return [x]