#!/usr/bin/env python

# Copyright 2016 Google Inc.
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

# [START imports]
import os
import urllib

from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'


# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)


class Startup(ndb.Model):
    """Sub model for representing an author."""
    nome = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    website = ndb.StringProperty(indexed=False)
    accettato = ndb.IntegerProperty()
    #avatar = ndb.BlobProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class FBUser(ndb.Model):
    """Sub model for representing an author."""
    fbid = ndb.StringProperty()
    nome = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


# [START main_page]
# class MainPage(webapp2.RequestHandler):

#     def get(self):
#         guestbook_name = self.request.get('guestbook_name',
#                                           DEFAULT_GUESTBOOK_NAME)
#         greetings_query = Greeting.query(
#             ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
#         greetings = greetings_query.fetch(10)

#         user = users.get_current_user()
#         if user:
#             url = users.create_logout_url(self.request.uri)
#             url_linktext = 'Logout'
#         else:
#             url = users.create_login_url(self.request.uri)
#             url_linktext = 'Login'

#         template_values = {
#             'user': user,
#             'greetings': greetings,
#             'guestbook_name': urllib.quote_plus(guestbook_name),
#             'url': url,
#             'url_linktext': url_linktext,
#         }

#         template = JINJA_ENVIRONMENT.get_template('index.html')
#         self.response.write(template.render(template_values))
# # [END main_page]

class MainPage(webapp2.RequestHandler):
    def get(self):
        startups = Startup.query().order(-Startup.date)
        startup_da_visualizzare = startups.fetch(2)
        params_value = {
            'startup_da_visualizzare': startup_da_visualizzare
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(params_value))
    def post(self):
        result = FBUser.query(FBUser.fbid == self.request.get('fbID'))

        if result.fetch() == []:
            fbuser_add = FBUser()
            fbuser_add.fbid = self.request.get('fbID')
            fbuser_add.nome = self.request.get('name')
            fbuser_add.put()

        

class AdminPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                template = JINJA_ENVIRONMENT.get_template('admin.html')
                self.response.write(template.render())
            else:
                self.response.write('You are not an administrator.')
        else:
            self.response.write('You are not logged in.')


class FirmaStartup(webapp2.RequestHandler):
    def post(self):
        #if users.get_current_user():
        startup_add = Startup(accettato=1)
        startup_add.nome = self.request.get('name')
        startup_add.email = self.request.get('email')
        startup_add.website = self.request.get('website')
        startup_add.put()

        #query_params = {'guestbook_name': guestbook_name}
        #self.redirect('/?' + urllib.urlencode(query_params))
        self.response.write("Richiesta aggiunta! Torna alla pagina precedente")


# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/firma', FirmaStartup),
    ('/admin', AdminPage),
], debug=True)
# [END app]