import cgi
import wsgiref.handlers
import os
import pickle
import sys
import hashlib
import datetime
import logging
import random
from types import *
        

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from sessions import Session
#
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.conf import settings
from django.utils import simplejson
from django.shortcuts import render_to_response

import canvas_models
from canvas_models import *

######################################################################################
#
#  AUTHENTICATION
#
######################################################################################
def logged_in():
    try:
        session = Session()
        if 'username' in session:
            return True
        else:
            Audit().log("ACCESS", "None", "Login required for "+f.__name__)
            return False
    except:
        Audit().log("EXCEPTION", "unknown", "Login required for "+f.__name__)
        return False
    return True

def requires_login(f):
    def decorator(request, *args, **kwargs): 
        if logged_in():
            return f(request, *args, **kwargs)
        else:
            return render_response_with_context("login.html", ({}))
        
    return decorator

def requires_post(f):
    def decorator(request, *args, **kwargs): 
        if request.method == "GET":
            return HttpResponseForbidden('Access Denied')
        else:
            return f(request, *args, **kwargs)
        
    return decorator


def renderLogin():
    try:
        message = Session()["message"]
    except KeyError:
        message = ''
        
    if (message != None) and (message != ""):
        #str_message = pickle.loads(message)
        template_values = Context({
           'error': message})
    else:
        template_values = Context()
        
    t = get_template('login.html')
    
    res = HttpResponse(t.render(template_values))
    return res
#    except Error:
#        self.error(500)
@requires_post
def goodLogin(request):
    logger = logging.getLogger("canvasLogger")
    # its a POST, so credentials should have been supplied
    username = request.POST.get('username','')
    pwd = request.POST.get('password','')
      
    try:
        me = User.get_by_key_name(username)
    except Exception:
        logger.error('login: Exception - Username or Password Error')
        try:
            logger.error('login: Exception:'+sys.exc_type+sys.exc_value)
        except:
            pass
        me = None
            
    if me == None:
        #FAILED LOGIN
        Session()['message'] = "User Name and/or Password do not match"
        logger.info('login failed: '+username)
        return False
    else:
        #good login
        Session()['username'] = username
        Session()['message'] = ""
        logger.info('login good: '+username)
        #redirect to the page requestes, if there is one
        redir = request.POST.get('page',username)
        return True
    assert(False)
    
def loginSilent(request):
    if goodLogin(request):
        return HttpResponse('ok', mimetype='application/javascript')
    else:
        return HttpResponse('denied', mimetype='application/javascript')
            
def login(request):
    if goodLogin(request):
        redir = request.POST.get('page',request.POST.get('username',''))
        return HttpResponseRedirect('/'+redir+'/')
    else:
        return renderLogin()
    
def logoff(request):
    try:
        room = Session()['room'] if 'room' in Session() else None
        Session().delete()
        if room:
            return HttpResponseRedirect('/'+room+'/')
        return HttpResponseRedirect('/login/')
    except Error:
            self.error(500)

class LoginException(BaseException):
    def __init__(self):
        BaseException.__init__()
        
def register(request):
    def hash (str):
        m = hashlib.md5()
        m.update(settings.SECRET_KEY)
        m.update(str)
        return m.hexdigest()

    if request.method == "GET":
        t = get_template('login.html')
        return HttpResponse(t.render([]))
    else:
        #add new user
        username = request.POST.get("reg-username",'')
        pwd = request.POST.get("reg-password1","")
        email = request.POST.get("reg-email","")
        if username != '':
            newUser = User(key_name = username)
            newUser.email = email
            newUser.display_name = username
            #newUser.key name = username
            newUser.pwdHash = hash (pwd)
            newUser.put()
            Session()['username'] = username
            #add a room for the user
            #TODO: this is not the key
            new_room = Room().get_by_key_name(username)
            if new_room == None:
                RoomUser().create_room(owner=newUser, room_name=username, is_public_read=False, is_public_write=False)
                
            
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/register/')        
     
######################################################################################
#
#  MAIN
#
######################################################################################   
def main (request):
    logger = logging.getLogger("canvasLogger")
    try:
        room = Session()['room'] if 'room' in Session() else None
        if room:
            return HttpResponseRedirect('/'+room+'/')
        t = get_template('index.html')
        logger.debug("main: got_template")
        return HttpResponse(t.render(main_context()))    
    except Exception:
        #not logged in
        logger.info("main: not logged in")
        try:
            logger.error("main: "+sys.exc_type)
            Session()["message"] = 'Login Error:'+sys.exc_type+sys.exc_value
        except:
            try:
                logger.error("main: exception logging in")
                logger.error("main: username: "+Session()['username'])
                del Session()['username']
            except:
                pass
        return renderLogin()
    
def allowed_read_access(room_name):
    if 'username' in Session():
        me = Session()['username']
    else:
        me = None
    
    #valid login
    #TODO: Check access to this room 
    db_room = Room().get_by_key_name(room_name)
    if me == None:
        user_me = None
    else:
        user_me = User().get_by_key_name(me)
        
    if db_room:
        if db_room.has_read_access(user_me):
            return True
    
    return False

def main_context(room_name = None): 
    logger = logging.getLogger("canvasLogger")
    logger.error("main_context: ")
    
    loggedIn = False
    buddy_list = []
    buddy_out_list = []
    buddy_in_list = []
    me = ""
    logger.debug("main_context: 1")
    if 'username' in Session():
        logger.debug("main_context: 2")
        me = Session()['username'] 
        logger.debug("main_context: 3")
        if (me != None) and (me != ''):
            #logged in
            loggedIn = True
            logger.debug("main_context: 4")
            user_me = User().get_by_key_name(me)
            logger.debug("main_context: 5")
            buddy_list = user_me.get_buddy_list()
            logger.debug("main_context: 6")
            buddy_out_list = user_me.get_buddy_requests(fromUser=True)
            buddy_in_list = user_me.get_buddy_requests(fromUser=False)
    if 'page' in Session():
        logger.debug("main_context: 7")
        page = Session()['page']
    else:
        page = ""
    if page == None:
        page=""
    try: 
        if room_name == None:
            room_name = ""
            
        if room_name == "":
            if 'room' in Session():
                logger.debug("main_context: 8")
                room_name = Session()['room']
                logger.debug("main_context: 9")
            else:
                if me:
                    room_name = me
                else:
                    #not logged in, no room, go to main page
                    logger.debug("main_context: 10")
                    raise Exception, "RoomNotAvailable"
        room = Room().get_by_key_name(room_name)
        roomy_list = room.roomy_list() 
        rooms_list = user_me.get_room_list() if loggedIn else [] 
        content_list = Content.gql("WHERE room = :room_key", room_key=str(room.key()) )
    except:
        logger.debug("main_context: exception A")
        roomy_list = []
        rooms_list = []
    if room_name == "Home":
        logger.error('HOME HOME HOME')
    logger.debug('***************room_name: '+room_name)
    return Context({
      'showPrivate': loggedIn, 
      'buddy_count': len(buddy_list),
      'out_count': len(buddy_out_list),
      'in_count': len(buddy_in_list),
      'buddies': buddy_list,
      'buddies_outstanding': buddy_out_list,
      'buddies_received': buddy_in_list,
      'username': me,
      'room_name': room_name,
      'page': page,
      'roomy_count': len(roomy_list),
      'roomies': roomy_list,
      'myrooms': rooms_list,
      'contents': content_list,
      'public_rd' : room.public_read,
      'public_wr': room.public_readwrite,
      'group_wr': room.group_write
      })
    
######################################################################################
#
#  PAGE
#
######################################################################################   
def page(request, room, page=None):
    #open a page
    logger = logging.getLogger("canvasLogger")
    if page == '#':
        page=None
        
    try:
        me = Session()['username']
    except:
        me = None
    
    if (me == None) or (me == ''):
        logger.info("page: not logged in ["+room+"]")
    #valid login
    #TODO: Check access to this room 
    if room:
        db_room = Room().get_by_key_name(room)
        if db_room:
            if me == None:
                user_me = None
            else:
                user_me = User().get_by_key_name(me)
                
            if db_room.has_read_access(user_me):
                logger.info("page: Access ok ["+room+"]")
                Session()['room'] = room
                if page:
                    Session()['page'] = page
                else:
                    Session()['page'] = ""
                #TODO: Exception here, need to render static welcome page
                return render_to_response('index.html',main_context(room_name=room)) 
            else:
                #no access to room
                #TODO: error message
                if 'room' in Session():
                    del Session()['room']
                return HttpResponseRedirect("/")
        
    #no room
    if 'room' in Session():
        del Session()['room']
    return HttpResponseRedirect("/")
    
def newPage(request, room):
    #add a page
    if request.method == "GET":
        logger.error('newPage: GET was not expected')
        return HttpResponseBadRequest
    
    try:
        #Save Content of RTF editor
        me = Session()['username']
        if (me == None) or (me == ''):
            #not logged in
            logger.debug('saveContent: /')  
            HttpResponseRedirect('/')
            
        #get room
        room_name = request.POST.get('room')
        room = Room().get_by_key_name(room_name) 
        
        user_me = User().get_by_key_name(me)
        if room.has_write_access(str(user_me.key())):
            #get page
            page_name = request.POST.get('page')
            page_key = pageNameToKey(room, page_name)
            if page_key == None:
                #page doesnt exist - create
                newPage = Page()
                newPage.room = str(room.key())
                newPage.title = page_name
                newPage.put()
                resp = {"isOk":True,
                        "pageName":page_name}
                json_contents = simplejson.dumps(resp)
                response = HttpResponse(json_contents, mimetype='application/javascript')
                return response
            else:
                logger.error('newPage: Page Exists')
                return HttpResponseBadRequest
        else:
            logger.error('newPage: Access Denied')
            return HttpResponseBadRequest
    except:
        logger.error('newPage: Exception')
        return HttpResponseBadRequest
    
######################################################################################
#
#  BUDDIES
#
######################################################################################   

def addbuddy(request):
    #add a new buddy
    if not request.POST:
        return HttpResponseBadRequest
    try:
        my_email = Session()['username']
        if (my_email == None) or (my_email == ''):
            #not logged in
            HttpResponseRedirect('/')

        me = User().get_by_key_name(my_email)

        new_buddy_name = request.POST.get('buddyName', '')
        #add outgoing req 
        me.add_buddy_request(new_buddy_name)
        
        t = get_template('buddyreqspane.html');
        return HttpResponse(t.render(main_context()));
    except Exception:
        print 'Exception:'+sys.exc_type+sys.exc_value
        return HttpResponse('Exception:'+sys.exc_type+sys.exc_value)
               
def acceptbuddy(request):
    #accept a buddy request
    if not request.POST:
        return HttpResponseBadRequest
    try:
        my_email = Session()['username']
        if (my_email == None) or (my_email == ''):
            #not logged in
            HttpResponseRedirect('/')
        me = User().get_by_key_name(my_email)
        new_buddy_name = request.POST.get('buddyName', '')
        me.accept_buddy_request(new_buddy_name)
        
        t = get_template('buddiespane.html');
        return HttpResponse(t.render(main_context()));
    except Exception:
        #create logger
        logger = logging.getLogger("canvasLogger")
        logger.error('acceptbuddy Exception:'+sys.exc_type+sys.exc_value)
        #TODO: dont return anything if live
        return HttpResponse('Exception:'+sys.exc_type+sys.exc_value)
    
#for the settings dialog content pane - NOT USED
#TODO: NOT USED?
def buddiesChecklist(request):
    if not request.GET:
        return HttpResponseBadRequest
    try:
        my_email = Session()['username']
        if (my_email == None) or (my_email == ''):
            #not logged in
            return HttpResponse('Not Logged In')
        me = User().get_by_key_name(my_email)
        t = get_template('buddieschecklist.html');
        return HttpResponse(t.render(main_context()));
    except Exception:
        #create logger
        logger = logging.getLogger("canvasLogger")
        logger.error('buddiesChecklist Exception:'+sys.exc_type+sys.exc_value)
        #TODO: dont return anything if live
        return HttpResponse('Exception:'+sys.exc_type+sys.exc_value)
    
#set the access level
#TODO: SECURITY HOLE        
def roomSettings(request):
    if not request.POST:
        return HttpResponseBadRequest
    try:
        my_email = Session()['username']
        if (my_email == None) or (my_email == ''):
            #not logged in
            return HttpResponse('Not Logged In')
        me = User().get_by_key_name(my_email)
        
        #check I have permission to set this
        roomName = request.POST.get("chatRoom")
        room = Room.get_by_key_name(roomName)
        if room:
            if room.owner == str(me.key()):
                #i am allowed - set it
                #reset all initially
                room.group_write = False
                room.public_read = False
                room.public_write = False
            
                #READ ACCESS
                #roomys can see if they exist
                access_rd = request.POST.get("access-rd")
                if access_rd=="world":
                    room.public_read = True
                
                #WRITE ACCESS
                #if there is a roomy, they can see it, but can only write if group_write set
                access_wr = request.POST.get("access-wr")
                if access_wr=="world":
                    room.public_write = True
                    
                if access_wr=="group":
                    room.group_write = True
                    
                #SAVE
                room.put()
                return HttpResponse(request.POST.get('label'))
        
        return HttpResponse('error');
    except Exception:
        #create logger
        logger = logging.getLogger("canvasLogger")
        logger.error('roomSettings Exception:'+sys.exc_type+sys.exc_value)
        #TODO: dont return anything if live
        return HttpResponse('Exception:'+sys.exc_type+sys.exc_value)
######################################################################################
#
#  CONTENT
#
######################################################################################
def startTransaction(page_key):
    #mark all room content for delete
    old_contents = Content.gql("WHERE page = :1", page_key)
    for content in old_contents:
        content.deleted = True
        content.put()
        
def commitTransaction(page_key):
    #mark all room content for delete
    old_contents = Content.gql("WHERE page = :1 and deleted = True", page_key)
    for content in old_contents:
        content.delete()

def rollbackTransaction(page_key):
    #restore all room content for delete
    new_contents = Content.gql("WHERE page = :1 and deleted = False", page_key)
    for content in new_contents:
        content.delete()
    old_contents = Content.gql("WHERE page = :1 and deleted = True", page_key)
    for content in old_contents:
        content.deleted = False
        content.put()
        
@requires_post       
@requires_login
def saveItem(request):
    try:
        room_name = request.POST.get('room')
        room = Room().get_by_key_name(room_name) 
        me = Session()['username']
        user_me = User().get_by_key_name(me)
        if room.has_write_access(str(user_me.key())):
            #get page
            page_name = request.POST.get('page')
            page_key = pageNameToKey(room, page_name)
            if page_key == None:
                logger.error('SaveContent: NO PAGE: room:'+room_name+' page:'+page_name)
                return HttpResponseServerError
            #good page, and we have access
            item = simplejson.loads(request.POST.get('item'))
            try:
                content = Content.get(item["key"])
            except:
                content = Content(parent=Page().get(page_key))
                
            if content:
                content.page = page_key 
                content.data = item['data']
                content.x = "10px" if (item['x'] == "") else item['x']
                content.y = "10px" if (item['y'] == "") else item['y']
                content.width = item['width']
                content.height = item['height']
                content.type = item['type']
                content.deleted = False #for the transaction, mark as new
                #content.title = contents[str(item_no)]['title']
                content.put()
                return HttpResponse('ok', mimetype='application/javascript')
            else:
                return HttpResponseServerError
    except:
        pass
    
    return HttpResponseServerError
        
@requires_post      
def saveContent(request):
    #save content of Editor
    def saveContentTrans(old, page, count):
        #clear old data
        #TODO: this deletes it all, but we were only sent one item, so you lose all but last
        for old_item in canvas_models.Content().get(old):
            old_item.delete()
        
        
            
    logger = logging.getLogger("canvasLogger")
    logger.debug('saveContent: '+request.method)
    
    try:
        #Save Content of RTF editor
        me = Session()['username']
        if (me == None) or (me == ''):
            #not logged in
            logger.debug('saveContent: /')  
            HttpResponseRedirect('/')
            
        #get room
        room_name = request.POST.get('room')
        room = Room().get_by_key_name(room_name) 
        
        user_me = User().get_by_key_name(me)
        if room.has_write_access(str(user_me.key())):
            #get page
            page_name = request.POST.get('page')
            page_key = pageNameToKey(room, page_name)
            if page_key == None:
                logger.error('SaveContent: NO PAGE: room:'+room_name+' page:'+page_name)
                return HttpResponseBadRequest
            #good page, and we have access
            contents = simplejson.loads(request.POST.get('items'))
            startTransaction(page_key)
            try:
                item_no = 0;
                while item_no < contents['count']:
                    content = Content(parent=Page().get(page_key)) 
                    content.page = page_key 
                    content.data = contents[str(item_no)]['data']
                    content.x = "10px" if (contents[str(item_no)]['x'] == "") else contents[str(item_no)]['x']
                    content.y = "10px" if (contents[str(item_no)]['y'] == "") else contents[str(item_no)]['y']
                    content.width = contents[str(item_no)]['width']
                    content.height = contents[str(item_no)]['height']
                    content.type = contents[str(item_no)]['type']
                    content.deleted = False #for the transaction, mark as new
                    #content.title = contents[str(item_no)]['title']
                    content.put()
                    item_no = item_no+1
                commitTransaction(page_key)
            except:
                rollbackTransaction(page_key)
                
            logger.debug('saveContent: Put ')
            return HttpResponse('ok', mimetype='application/javascript')
        else:
            return HttpResponse('access denied', mimetype='application/javascript')
    except Exception: 
        logger.error('saveContent: Exception')
        return HttpResponse('Exception:'+sys.exc_type+sys.exc_value, mimetype='application/javascript')
 
def pageNameToKey(room, pageName):
    #Get page_key
    if pageName == "":
        return room.main_page
    else: #named page
        page = Page().all().filter("room = ",str(room.key())).filter("title = ",pageName).get()
        if page:
            return str(page.key())
        else:
            return None
""" 
Load all content items for a page
Returns JSON from a GET for AJAX
"""   
def loadContent(request):
    if not request.POST:
        return HttpResponseBadRequest
    try:
        #its a POST to stop IE caching it
        roomName = request.POST.get("chatRoom")
        if allowed_read_access(roomName):
            pageName = request.POST.get("page")
            room = Room().get_by_key_name(roomName) 
            logger = logging.getLogger("canvasLogger")
            if (pageName == None) or (pageName == ""):
                #main page
                page_key = room.main_page
            else:
                page_key = pageNameToKey(room, pageName)
                if page_key == None:
                    logger.error('loadContent: NO PAGE: room:'+roomName+' page:'+pageName)
                    return HttpResponseBadRequest
                
            #use page_key to find content
            content_list = Content.gql("WHERE page = :page", page=page_key)  
            contents ={}
            contents["count"] = content_list.count()
            content_items = []
            for item in content_list:
                content_item = {}
                content_item["data"] = item.data
                content_item["x"] = "10px" if item.x=="" else item.x
                content_item["y"] = "10px" if item.y=="" else item.y
                content_item["width"] = "150px" if item.width=="" else item.width
                content_item["height"] = "150px" if item.height=="" else item.height
                content_item["type"] = item.type
                #content_item["title"] = item.title
                content_items.append(content_item)
            contents["items"] = content_items
            json_contents = simplejson.dumps(contents)
            response = HttpResponse(json_contents, mimetype='application/javascript')
            response["If-Modified-Since"]="Sat, 1 Jan 2000 00:00:00 GMT" 
            response['public_rd'] = room.public_read,
            response['public_wr'] = room.public_readwrite,
            response['group_wr'] = room.group_write
            page = Page.get(page_key)
            response['main'] = page.title

            return response 
        else:
            #not allowed read

            return HttpResponse('{error:"authentication-error"}', mimetype='application/javascript')
        
    except Exception:
        try:
            resp = sys.exc_type+sys.exc_value 
        except:
            resp ="exception in loadContent"
        
        return HttpResponse('Exception in loadContent:'+resp, mimetype='application/javascript')
 
"""
image returns an image given an Event Key - matched URL img/(.*)$
"""    
def image(request): 
    if "img_id" in request.GET:
        #event image
        key = request.GET["img_id"]
        img = DbImage.get(key)
        if img:
            return HttpResponse(img.picture, mimetype="image/png")
        return("No Photo")
    
def uploadImg(request):
    #create logger
    logger = logging.getLogger("canvasLogger")
    
    file = request.FILES.get("imgUp", None)
    if file: 
        page_name = request.POST.get('page') 
        Session()['page'] = page_name
        room = Room().get_by_key_name(Session()['room'])
        page = Page.gql('WHERE room = :room_key AND title = :title', 
                        room_key=str(room.key()),
                        title=page_name).get()    
        if page:
            pic = file.read()  
            dbpic = DbImage() 
            dbpic.picture = pic 
            dbpic.user =Session()['username']
            dbpic.put()
            
            #save the image to the content so its there when we reload (we are about to)
            content = Content(parent=page) 
            content.page = str(page.key()) 
            content.data = str(dbpic.key())
            content.x = str(100+random.randint(0,100))
            content.y = str(100+random.randint(0,100))
            #TODO: set aspect ratio correctly
            content.width = str(150)
            content.height = str(150)
            content.type = 'img'
            content.deleted = False #for the transaction, mark as new
            #content.title = contents[str(item_no)]['title']
            content.put()
            return HttpResponseRedirect('/'+room.key().name()+'/'+page.title)
        else:
            return HttpResponse('<textarea>{error:"no page" }</textarea>', mimetype='text/html')
    else:
        return HttpResponse('<textarea>{error:"no file" }</textarea>', mimetype='text/html')
 

    
def commonPagesList(request, room):
    #get the page list for a room
    logger = logging.getLogger("canvasLogger")
    if allowed_read_access(room):
        #valid login
        #TODO: Check access to this room
        if room:
            db_room = Room().get_by_key_name(room)
            resp = {}
            pageList = []
            try:
                mainPage = Page.get(db_room.main_page)  
                if mainPage:
                    pageList.append(mainPage.title)
                    
                else:
                    logger.error('commonPagesList: No main page for '+room)
            except:
                raise Exception,  "commonPagesList mainPage Exception "+room
             
            try:   
                pageQ = GqlQuery('SELECT * FROM Page WHERE room = :r', r=str(db_room.key()))
                for page in pageQ: 
                    if page.title != "Home": #cos we added already
                        pageList.append(page.title)
            except:
                raise Exception,  "getPageList pageQ Exception "+room
            #TODO: Sort this list alpha before adding Home, so order is Home,a,b,c,d...
            
            return pageList
            
        #no room
        raise Exception, "commonPagesList: Which Room"
    else:
        raise Exception, "Access Denied"
   
    
def getPageList(request, room):
    try:
        pageList = commonPagesList(request, room)
    except Exception, e:
        return HttpResponse('{error:"access denied"}')
    resp = {}
    resp["count"] = len(pageList) 
    resp["pages"] = pageList
    if len(pageList)>0:
        resp['main'] = pageList[0] # passed back so we can set the page button label (it shows what page we're on)
    json_contents = simplejson.dumps(resp)
    response = HttpResponse(json_contents, mimetype='application/javascript')
    return response
    
def pagesPane(request):
    try:
        pageList = commonPagesList(request, Session()['room'])
    except Exception, e:
        return HttpResponse(str(e))
    
    context = Context({})
    context['pages']=pageList 
    context['room_name'] = Session()['room']
    context['page_count'] = len(pageList)
    return render_to_response("pagespane.html",context)

def pageLinksPane(request):
    try:
        pageList = commonPagesList(request, Session()['room'])
    except Exception, e:
        return HttpResponse(str(e))
    
    context = Context({})
    context['pages']=pageList 
    context['room_name'] = Session()['room']
    context['page_count'] = len(pageList)
    return render_to_response("pageLinkDialogPane.html",context)
    
######################################################################################
#
#  CHAT
#
######################################################################################       
    
def sendChat(request):
    #create logger
    logger = logging.getLogger("canvasLogger")
    
    if not request.POST:
        return HttpResponseBadRequest
    
    try:
        me = Session()['username']
        if (me == None) or (me == ''):
            #not logged in
            HttpResponseRedirect('/')
            
        msg = ChatMsg()
        roomName = request.POST.get('chatRoom')
        room = Room.get_by_key_name(roomName)
        if room:
            msg.chatRoom = room
            msg.roomName = room.key().name() #needed cos you cant GQL query a key value!!!!!!
            userMe = User.get_by_key_name(me)
            if userMe:
                msg.user = userMe
                msg.text = request.POST.get('chatMsg')
                msg.time = datetime.datetime.now()
                msg.setId(room)
                msg.put()
                respTxt = '<br><b>'+me+': </b>'+request.POST.get('chatMsg')
                #lastId = room.get_lastMsgId()
                resp = '{"msg":"'+respTxt+'", "lastMsgSeq": "'+str(msg.seq)+'"}'
                logger.debug("sendChat - "+resp)
                return HttpResponse(resp, mimetype='application/javascript')
        
        return HttpResponse('Exception: Room not found '+roomName, mimetype='application/javascript')
    except Exception:
        return HttpResponse('Exception:'+sys.exc_value, mimetype='application/javascript')
    
def poll(request):
    resp = '{"error": "Exception in Poll()"}'
    if not request.GET:
        return HttpResponseBadRequest
    
    try:
        #create logger
        logger = logging.getLogger("canvasLogger")
        
        me = Session()['username']
        if (me == None) or (me == ''):
            #not logged in
            HttpResponseRedirect('/')
            
        chatRoomName = request.GET.get('chatRoom')
        lastStr = request.GET.get('lastMsg')
        logger.debug('poll? - '+chatRoomName+'/'+str(lastStr))
        lastMsgSent = int(lastStr)
        #TODO: Query msgs to see if any new (from anyone else)
        #Check memcache for room's last ID
        chatRoom = Room.get_by_key_name(chatRoomName)
        lastId = chatRoom.get_lastMsgId()
        logger.debug('poll? - Id:'+str(lastId))
        msgs=""
        if lastMsgSent != lastId:
            #a new msg
            #return all msgs from lastMsg to lastId
            q = db.GqlQuery("SELECT * FROM ChatMsg " + 
                "WHERE roomName = :1 AND seq > :2 " +
                "ORDER BY seq",
                chatRoomName,lastMsgSent)
                #, lastMsgSent)
            logger.debug('poll? - querying')
            msgs = ""
            for msg in q:
                msgs += "<br><b>"
                msgs += msg.user.key().name()
                msgs +=": </b>"
                msgs += msg.text
                
            logger.debug('poll? - msgs:'+msgs)
        resp = '{"msg": "'+msgs+'", "lastMsgSeq": "'+str(lastId)+'"}'
        #resp = HttpResponse('{"msg": "", "lastMsgSeq": "0"}', mimetype='application/javascript')
        logger.debug("poll - "+e+'/'+chatRoomName+'/'+resp)                     
        return HttpResponse('{"msg": "'+msgs+'", "lastMsgSeq": "'+str(lastId)+'"}', mimetype='application/javascript')

    except Exception:
        try:
            resp = '{"error":"'+sys.exc_type+sys.exc_value+'"}'
        finally:
            return HttpResponse(resp, mimetype='application/javascript')

     
   