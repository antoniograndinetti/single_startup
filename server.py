#!/usr/bin/env python

import os
import urllib
import json

from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext import ndb

import jinja2
import webapp2
# import sendgrid
# from sendgrid.helpers.mail import *

# make a secure connection to SendGrid
#sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Startup(ndb.Model):
    nome = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty()
    startup_name = ndb.StringProperty(indexed=False)
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
            if self.request.get('fbID') != "":
                fbuser_add = FBUser()
                fbuser_add.fbid = self.request.get('fbID')
                fbuser_add.nome = self.request.get('name')
                fbuser_add.put()


# class AdminPage(webapp2.RequestHandler):
#     def get(self):
#         send_message("antoniograndinetti91@gmail.com")
#         client = sendgrid.SendGridClient(SENDGRID_API_KEY)
#         message = sendgrid.Mail()

#         message.add_to("antoniograndinetti91@gmail.com")
#         message.set_from("noreply@singlestartupmarket.eu")
#         message.set_subject("Sending with SendGrid is Fun")
#         message.set_html("and easy to do anywhere, even with Python")

#         client.send(message)
#         template = JINJA_ENVIRONMENT.get_template('admin.html')
#         self.response.write(template.render())
    
#     def post(self):
#         username = self.request.get('username')
#         password = self.request.get('password')
#         if username != "":
#             self.response.write("non vuoto")
#         else:
#             self.response.write("vuoto")

        # if (username == 'admin' and password == 'password'):
        #     self.redirect('/confirm', {'user_param': username})
        # else:
        #     self.redirect('/admin')
        


class ConfirmPage(webapp2.RequestHandler):

    def get(self):
        #user_param = self.request.get('user_param')

        #if (user_param == 'admin'):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                logout_url = users.create_logout_url(self.request.uri)
                logout = 'Welcome! (<a href="{}">sign out</a>)'.format(logout_url)

                to_confirm = Startup.query(Startup.accettato == 0)
                to_confirm_list = to_confirm.fetch()
                confirm_param = {
                    'to_confirm_list': to_confirm_list,
                    'logout': logout,
                }
                template = JINJA_ENVIRONMENT.get_template('confirm.html')
                out = template.render(confirm_param)
            else:
                login_url = users.create_login_url(self.request.uri)
                out = '<html><body><a style="color: #428bca; text-decoration: none;" href="{}">SIGN IN</a></body></html>'.format(login_url)

        else:
            login_url = users.create_login_url(self.request.uri)
            out = '<html><body><a style="color: #428bca; text-decoration: none;" href="{}">SIGN IN</a></body></html>'.format(login_url)
        
        self.response.write(out)

        

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
        startup_add.startup_name = self.request.get('startup_name')
        startup_add.website = self.request.get('website')
        avatar = self.request.get('avatar')
        avatar = images.resize(avatar, 70, 70)
        startup_add.avatar = avatar
        startup_add.put()

        # # invio delle mail
        # (status, msg) = send_message(self.request.get('email'))
        # inserire contatto admin
        # (status, msg) = send_message("antoniograndinetti91@gmail.com")

        template = JINJA_ENVIRONMENT.get_template('redirect.html')
        self.response.write(template.render())


# funzione per inviare la mail
# def send_message(destinatario):
# #     # [START sendgrid-send]
# #     message = sendgrid.Mail()
# #     message.set_subject('message subject')
# #     message.set_html('<strong>HTML message body</strong>')
# #     message.set_text('plaintext message body')
# #     message.set_from('Example App Engine Sender <noreply@{}>'.format(
# #         SENDGRID_DOMAIN))
# #     message.add_to(destinatario)
# #     status, msg = sg.send(message)
# #     return (status, msg)
#     from_email = Email("noreply@singlestartupmarket.eu")
#     subject = "Hello World from the SendGrid Python Library"
#     to_email = Email(destinatario)
#     content = Content("text/plain", "some text here")
#     mail = Mail(from_email, subject, to_email, content)
#     response = sg.client.mail.send.post(request_body=mail.get())


class Image(webapp2.RequestHandler):
    def get(self):
        startup_key = ndb.Key(urlsafe=self.request.get('img_id'))
        startup = startup_key.get()
        if startup.avatar:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(startup.avatar)
        else:
            self.response.out.write('No image')

class Quote1Page(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('quote1.html')
        self.response.write(template.render())

class Quote2Page(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('quote2.html')
        self.response.write(template.render())

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/firma', FirmaStartup),
    ('/image', Image),
#    ('/admin', AdminPage),
    ('/confirm', ConfirmPage),
    ('/quote1', Quote1Page),
    ('/quote2', Quote2Page)
], debug=True)
# [END app]