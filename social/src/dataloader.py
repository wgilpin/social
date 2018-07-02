import hashlib
from django.conf import settings
#from google.appengine.api import apiproxy_stub_map

from canvas_models import *
from django.http import HttpResponse

#from test_data import test_users
#from test_data import test_room_users
#from test_data import test_rooms
from test_data import *

def loadData(request):
    def hash (str):
        m = hashlib.md5()
        m.update(settings.SECRET_KEY)
        m.update(str)
        return m.hexdigest()
    
    response = "<h1>Social Canvas</h1><br><br><h2>Database Loaded</h2>"
    
    #apiproxy_stub_map.apiproxy.GetStub('datastore_v3').Clear()
    
  
    for u in User.all():
        u.delete()
    response += "<br><br>test_users:"
    for a_user in test_users:
        u = User(key_name=a_user['key_name'])
        u.email = a_user['email']
        u.pwdHash = hash(a_user['pwd'])
        u.display_name = a_user['key_name'] #same as key name 
        u.put()
        response += "<br>" + a_user['key_name']
      
    
    for r in Room.all():
        r.delete()
    response += "<br><br>test_rooms:"
    for a_room in test_rooms:
        homePage = Page(title="Home")
        homePage.put()
        r = Room(key_name=a_room[0])
        r.main_page = str(homePage.key())
        #r.content = a_room[1]
        r.public_read = a_room[2]
        r.public_readwrite = a_room[3]
        user = User().get_by_key_name(a_room[4])
        r.owner = str(user.key())
        r.group_write = a_room[5]
        r.put()
        homePage.room = str(r.key())
        homePage.put()
        response += "<br>" + a_room[1]
        
    
    for r in RoomUser.all():
        r.delete()
    response += "<br><br>Room test_users:"
    for an_ru in test_room_users:
        ru = RoomUser()
        room = Room().get_by_key_name(an_ru[0])
        user = User().get_by_key_name(an_ru[1])
        ru.room = str(room.key())
        ru.user = str(user.key())
        ru.full_access = an_ru[2]
        ru.put()
        response += "<br>" + an_ru[1] + ' in ' + an_ru[0]
  
     
    response += "<br><br>buddies test_buddies:"
    for buddy_pair in test_buddies:
        left = User().get_by_key_name(buddy_pair[0])
        right = User().get_by_key_name(buddy_pair[1])
        left.add_buddy(right.key())
        left.put()
        right.add_buddy(left.key())
        right.put()
        response += "<br>" + buddy_pair[0] + ' 4 ' + buddy_pair[1]

  
    return HttpResponse("<html><body>" + response + "<p><a href='/index'>Home Page</a></body></html>")
      
class Loader():
    def loadDatabase(self):
        loadData(None)
        

