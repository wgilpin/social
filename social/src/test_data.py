#'key_name','email','pwd'
test_users = ({'key_name':'will', 'email':'will@mail.com', 'pwd':'will'},
              {'key_name':'matt', 'email':'matt@mail.com', 'pwd':'matt'},
       )

#'key_name','content','public_read','public_readwrite','owner','group_write'
test_rooms = (('will', 'this is wills room', True, False,'will', True),
         ('matt', "this is Matt's room", True, False,'matt', True),
         )

#room, user, full_access
test_room_users = (('will', 'will', True),
             ('will', 'matt', False),
             ('matt', 'matt', True),
             )

test_buddies = (('will','matt'),
                )