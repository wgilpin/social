import unittest
from test import test_support
from google.appengine.api import apiproxy_stub_map
from canvas_models import User
from dataloader import Loader

from test_data import test_users

class TestCaseUsers(unittest.TestCase):

    # Only use setUp() and tearDown() if necessary

    def setUp(self):
        #Wipe DB
        apiproxy_stub_map.apiproxy.GetStub('datastore_v3').Clear()
        #load default data
        l = Loader()
        l.loadDatabase()
        
    #def tearDown(self):
    #    ... code to execute to clean up after tests ...

    def test_get_users(self):
        # Test create users.
        u1_name=test_users[0]['key_name']
        u1 = User().get_by_key_name(u1_name)
        assert(u1.email == test_users[0]['email'])
        
    def test_create_users(self):
        # Test create users.
        u1_name="mary"
        u1 = User(key_name=u1_name)
        u1.email="mary@mail.com"
        u1.display_name = u1_name
        u1.pwdHash = ''
        u1.put()
        u2=User().get_by_key_name(u1_name)
        assert(u2.email == u1.email)

    def test_request_buddy(self):
        requester = User().get_by_key_name(test_users[0]['key_name'])
        #User1 requests User2 be a buddy
        requester.add_buddy_request(to_user_key_name=test_users[1]['key_name'])
        target = User().get_by_key_name(test_users[1]['key_name'])
        #Check User1 is on User1's list
        target_buddy_req_list  = target.get_buddy_requests(False)
        found=False
        for x in target_buddy_req_list:
            if(x.key()==requester.key()):
                found=True
                break
        assert(found)
        
        target = User().get_by_key_name(test_users[1]['key_name'])
        requester = User().get_by_key_name(test_users[0]['key_name'])
        
        assert(requester.key()  in target.buddies_asked_me)
        assert(requester.key() not in target.buddies)
        assert(target.key() not in requester.buddies)
        assert(target.key()  in requester.buddies_I_asked)
        target.accept_buddy_request(from_user_key_name=test_users[0]['key_name'])
        target = User().get_by_key_name(test_users[1]['key_name'])
        requester = User().get_by_key_name(test_users[0]['key_name'])
        assert(requester.key() not in target.buddies_asked_me)
        assert(requester.key() in target.buddies)
        assert(target.key() in requester.buddies)
        assert(target.key() not in requester.buddies_I_asked)

        



def test_main():
    test_support.run_unittest(MyTestCase1,
                             )

if __name__ == '__main__':
    test_main()
