import cgi
import wsgiref.handlers
import os
import logging

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.db import GqlQuery 
from google.appengine.api import memcache

from appengine_django.models import BaseModel

class Page(db.Model):  #0.2
    #TODO: pages have title - default is Home
    title = db.StringProperty()
    room = db.StringProperty()
    
class Room(db.Model):
    main_page = db.StringProperty()  #0.2
    public_read = db.BooleanProperty()
    public_readwrite = db.BooleanProperty()
    group_write = db.BooleanProperty()
    owner = db.StringProperty()
    
    def roomy_list(self):
        list = []
        try:
            logger = logging.getLogger("canvasLogger")
            #roomuser has string key for users in it, convert to obj list of users
            roomyQ = GqlQuery("SELECT * FROM RoomUser WHERE room = :room_key", room_key=str(self.key()))
            for ru in roomyQ:
                roomy = User().get(ru.user)
                list.append(roomy)
        except:
            if logger:
                logger.error("Room.roomy_list: exception")
        
        return list
    
    def get_lastMsgId(self):
        """get_lastMsgId()
      
        Checks the cache to see if there are cached highest seq no.
        If not, set the cache
    
        Returns:
            Highest req no
        """
        logger = logging.getLogger("canvasLogger")
        try:
            #msgId = memcache.get("lastMsg:"+self.key().name())
            if False: #msgId is not None:
                return msgId
            else:
                q = db.GqlQuery("SELECT * FROM ChatMsg " + 
                    "WHERE roomName = :1 " +
                    "ORDER BY seq DESC",
                    self.key().name()) 
    
                # The query is not executed until results are accessed.
                result = q.get()
                if result:
                    msgId = result.seq
                else:
                    msgId = 0
                    
                logger = logging.getLogger("canvasLogger")
                if not memcache.set("lastMsg:"+self.key().name(), msgId, 3600):
                    logger.error("get_lastMsgId - Memcache set failed.")
                dbStr = str(memcache.get("lastMsg:"+self.key().name()))
                logger.debug("get_lastMsgId - "+dbStr)
            return int(msgId)
        except:
            logger.error("get_lastMsgId - EXCEPTION")
            return -2
            
    def has_read_access(self, user):
        try:
            if self.public_read:
                return True
            if user == None:
                return False
            user_key = str(user.key())
            if self.owner == user_key:
                return True
            
            room_k = str(self.key())
            roomyQ = GqlQuery("SELECT * FROM RoomUser WHERE room = :room_key AND user =:p_user_key ", 
                              room_key=room_k,
                              p_user_key=user_key) 
            if roomyQ.get():
                return True
            else:
                return False
        except:
            return False
        
    def has_write_access(self, user_key):
        try:
            if self.owner == user_key:
                return True
            if self.public_readwrite:
                return True
            if self.group_write:
                #group_write means you need to be abuddy
                room_k = str(self.key())
                roomyQ = GqlQuery("SELECT * FROM RoomUser WHERE room = :room_key AND user =:p_user_key ", 
                                  room_key=room_k,
                                  p_user_key=user_key) 
                if roomyQ.get():
                    return True
            return False
        except:
            return False
    
######################################################################################
class User(db.Model):
  email = db.StringProperty()
  sys_user = db.UserProperty()
  pwdHash = db.StringProperty()
  display_name = db.StringProperty()
  buddies = db.ListProperty(db.Key)
  buddies_I_asked = db.ListProperty(db.Key)
  buddies_asked_me = db.ListProperty(db.Key)
  
  def get_room_list(self):
      q = GqlQuery("SELECT * FROM RoomUser "
                   "WHERE user = :1 ",
                   str(self.key()))
      result = []
      try:
          for room_user in q:
              room_key = room_user.room
              room = Room().get(room_key)
              room_name = room.key().name()
              result.append(room_name)
      finally:
          return result
  
  def add_buddy(self,key):
      if self.buddies.__contains__(key):
          pass
      else:
          self.buddies.append(key)
  
  def add_buddy_request(self,to_user_key_name):
      to_user = User().get_by_key_name(to_user_key_name)
      to_user.buddies_asked_me.append(self.key())
      to_user.put()
      self.buddies_I_asked.append(to_user.key())
      self.put()
      
  def accept_buddy_request(self,from_user_key_name):
      from_user = User().get_by_key_name(from_user_key_name)
      if from_user.key() in self.buddies_asked_me:
          #from user Did request this
          if self.key() not in from_user.buddies:
              #don't add buddy if already there
              from_user.buddies.append(self.key())
              from_user.buddies_I_asked.remove(self.key())
              from_user.put()
          if from_user.key() not in self.buddies:
              self.buddies.append(from_user.key())
              self.buddies_asked_me.remove(from_user.key())
              self.put()
      
  def get_buddy_list(self):
      list = self.buddies
      res = []
      for key in list:
          buddy = User().get(key)
          res.append(buddy)
      return res

  def get_buddy_requests(self,fromUser):
      list = self.buddies_asked_me
      if fromUser:
          list = self.buddies_I_asked
      res = []
      for key in list:
          buddy = User().get(key)
          res.append(buddy)
      return res
  

#####################################################################################

class RoomUser(db.Model):
    #map Rooms to Users
    room = db.StringProperty()
    user = db.StringProperty()
    full_access = db.BooleanProperty()
    
    @staticmethod
    def create_room(owner, room_name, is_public_read, is_public_write):
    #create a new room, owned by this 'owner'
        room_key = owner.key().name()
        if Room().get_by_key_name(room_key) != None:
            #room exists
            raise Exception("User already has Room of that name: "+room_key)
        
        homePage = Page(title="Home")
        homePage.put()
        room = Room(key_name=room_key, 
                    owner=str(owner.key()),  
                    public_read=is_public_read, 
                    public_readwrite=is_public_write, 
                    main_page=str(homePage.key()))
        room.put()
        homePage.room = str(room.key())
        homePage.put()
        
        ru = RoomUser(room=str(room.key()), user=str(owner.key()), full_access=True)
        ru.put()
    
    #TODO: Is this rubbish? Why am I looking at the Room table?
    def has_full_access(self, user_key):
        if Room().all().filter('room=',self.key().name()).filter('user=',user_key).filter('full_access=',True).get() != None:
            #has full access
            return true
        else:
            return false
    
    
        
    def grant_access(room_key, grant_by, grant_to, is_full_access):
        room = Room().get_by_key_name(room_key)    
        if  room == None:
            #room doesnt exist
            raise Exception("Room does not exist: "+room_key)
        if room.public_readwrite:
            #no need for access to public room
            return
        if room.has_full_access(grant_by):
            ru = RoomUser().all().filter('user=',grant_to).filter('room=',room_key).get()
            if ru == none:
                ru = RoomUser(user=grant_to,room=room_key)
            
            ru.full_access=is_full_access
            ru.put()
                         
   
class ChatMsg(db.Model):
    chatRoom = db.ReferenceProperty(Room)
    roomName = db.StringProperty()
    user = db.ReferenceProperty(User)
    text = db.StringProperty()
    time = db.DateTimeProperty()
    seq = db.IntegerProperty()
    
    def setId(self,aRoom):
        lastId = self.chatRoom.get_lastMsgId()
        self.seq = lastId+1
        roomkey = aRoom.key()
        roomName = roomkey.name()
        seqNo = self.seq
        x = memcache.set("lastMsg:"+roomName, seqNo, 3600)
        if not x:
            logging.error("Memcache set failed.")          
                        
class Content(db.Model):
    room = db.StringProperty()   #deprecated in 0.2
    page = db.StringProperty()   #0.2
    data = db.TextProperty()
    x = db.StringProperty()
    y = db.StringProperty()
    z = db.StringProperty()
    width = db.StringProperty()
    height = db.StringProperty()
    #title = db.StringProperty()
    type = db.StringProperty()
    deleted = db.BooleanProperty() #marked for deletion - manual transaction
    
#####################################################################################
class DbImage(db.Model):
    user = db.StringProperty()
    room = db.StringProperty()
    picture = db.BlobProperty()
    title = db.StringProperty()      
    
    
