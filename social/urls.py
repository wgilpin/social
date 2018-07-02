# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^foo/', include('foo.urls')),

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
    (r"^$", "src.views.main"), 
    (r"^login/$","src.views.login"),
    (r"^loginSilent/$","src.views.loginSilent"),
    (r"^register/$","src.views.register"),
    (r"^logoff/$","src.views.logoff"),
    (r'^addBuddy/$','src.views.addbuddy'),
    (r'^acceptBuddy/$','src.views.acceptbuddy'),
    (r'^wipedb/$','src.views.wipedb'),
    (r'^saveContent/$','src.views.saveContent'),
    (r'^saveItem/$','src.views.saveItem'),
    (r'^loadContent/$','src.views.loadContent'),
    (r'^loadData/$','src.dataloader.loadData'),
    (r'^sendChat/$','src.views.sendChat'),
    (r'^poll/$','src.views.poll'),
    (r"^index/$","src.views.main"),
    (r"^uploadImage/$","src.views.uploadImg"),
    (r"^img/$","src.views.image"),  #img/abCDef -> image("abCDef")
    (r"^buddieschecklist/$","src.views.buddiesChecklist"),
    (r"^roomSettings/$","src.views.roomSettings"),
    (r'^migrate_0_2/$','src.migrate.migrate_to_0_2'),
    (r"^(.*)/pages/$","src.views.getPageList"),  #.../will/pages -> getPageList("will"),
    (r"^pagesPane/$","src.views.pagesPane"),
    (r"^pageLinksPane/$","src.views.pageLinksPane"),

    (r"^(.*)/newPage/$","src.views.newPage"),  #.../will/newPage -> newPage("will"),
    #THIS ONE LAST
    (r"^(.*)/(.*)/$","src.views.page"),  #.../will/page2/ -> page("will","page2"),
    (r"^(.*)/$","src.views.page"),  #.../will -> room("will"),
    
    
)
