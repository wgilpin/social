from google.appengine.ext.db import GqlQuery 
from canvas_models import *
from django.http import HttpResponse

def migrate_to_0_2(request):
    #added:
    #  page
    #  room.main_page
    #  content.page
    
    # 1. Add a main page to each room
    roomsQ = GqlQuery("SELECT * FROM Room")
    for room in roomsQ:
        mp = Page()
        mp.room = str(room.key())
        mp.title = "Home"
        mp.put()
        room.main_page = str(mp.key())
        room.put()
        # 2. set all content for that room to the page
        contentsQ = GqlQuery("SELECT * FROM Content WHERE ANCESTOR is :room_key", room_key=room.key())
        for c in contentsQ:
            c.parent = room.main_page
            c.page = room.main_page
            c.room = None
            c.put()
    return HttpResponse('Migration to 0.2 Successful')
            