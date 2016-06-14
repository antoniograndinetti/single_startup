#!/usr/bin/env python

import os
import urllib
import json

from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Startup(ndb.Model):
    nome = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty()
    website = ndb.StringProperty(indexed=False)
    accettato = ndb.IntegerProperty()
    avatar = ndb.BlobProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class FBUser(ndb.Model):
    fbid = ndb.StringProperty()
    nome = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        startups = Startup.query(Startup.accettato == 1).order(-Startup.date)
        startup_da_visualizzare = startups.fetch()
        startups_number = Startup.query().count()

        fbusers = FBUser.query().order(-Startup.date)
        fbusers_da_visualizzare = fbusers.fetch(10)
        fbusers_number = FBUser.query().count()

        params_value = {
            'startup_da_visualizzare': startup_da_visualizzare,
            'fbusers_da_visualizzare': fbusers_da_visualizzare,
            'startups_number': startups_number,
            'fbusers_number': fbusers_number
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(params_value))
    def post(self):
        result = FBUser.query(FBUser.fbid == self.request.get('fbID'))

        if result.fetch() == []:
            if self.request.get('fbID') != None:
                fbuser_add = FBUser()
                fbuser_add.fbid = self.request.get('fbID')
                fbuser_add.nome = self.request.get('name')
                fbuser_add.put()


class AdminPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('admin.html')
        self.response.write(template.render())
    
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        if (username == 'admin' and password == 'password'):
            self.redirect('/confirm', {'user_param': username})
        else:
            self.redirect('/admin')
        


class ConfirmPage(webapp2.RequestHandler):

    def get(self):
        user_param = self.request.get('user_param')

        #if (user_param == 'admin'):
        to_confirm = Startup.query(Startup.accettato == 0)
        to_confirm_list = to_confirm.fetch()
        confirm_param = {
            'to_confirm_list': to_confirm_list,
        }
        template = JINJA_ENVIRONMENT.get_template('confirm.html')
        self.response.write(template.render(confirm_param))

    def post(self):
        start_id = self.request.get('id')
        start_type = self.request.get('type')

        if start_type == 'ok':
            startup_key = Startup.query(Startup.email == start_id)
            startup_conf = startup_key.fetch()[0]
            startup_conf.accettato = 1
            ret = startup_conf.key.id()
            startup_conf.put()
            self.response.out.write(ret)
        elif start_type == 'ko':
            startup_key = Startup.query(Startup.email == start_id)
            startup_conf = startup_key.fetch()[0]
            ret = startup_conf.key.id()
            startup_conf.key.delete()
            self.response.out.write(ret)



class FirmaStartup(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('submit_backers.html')
        self.response.write(template.render())

    def post(self):
        #if users.get_current_user():
        startup_add = Startup(accettato=0)
        startup_add.nome = self.request.get('name')
        startup_add.email = self.request.get('email')
        startup_add.website = self.request.get('website')
        avatar = self.request.get('avatar')
        avatar = images.resize(avatar, 70, 70)
        startup_add.avatar = avatar
        startup_add.put()

        template = JINJA_ENVIRONMENT.get_template('redirect.html')
        self.response.write(template.render())

class Image(webapp2.RequestHandler):
    def get(self):
        startup_key = ndb.Key(urlsafe=self.request.get('img_id'))
        startup = startup_key.get()
        if startup.avatar:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(startup.avatar)
        else:
            self.response.out.write('No image')

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/firma', FirmaStartup),
    ('/image', Image),
    ('/admin', AdminPage),
    ('/confirm', ConfirmPage)
], debug=True)
# [END app]