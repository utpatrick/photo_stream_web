#!/usr/bin/env python

# [START imports]
import os
import urllib
import model

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail


import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

# [START mainlogin page]
DEFAULT_STREAM_NAME = 'new stream'



class MainLoginPage(webapp2.RequestHandler):

    def get(self):

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('templates/page_template.html')
        self.response.write(template.render(template_values))
# [END mainlogin page]


# [START manage page]
class ManagePage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        streams = model.get_stream_by_user(user.user_id())
        sub_streams = model.get_subscribed_stream(user.user_id())

        template_value = {
            'streams': streams,
            'sub_streams': sub_streams,
        }
        template = JINJA_ENVIRONMENT.get_template('templates/manage_page.html')
        self.response.write(template.render(template_value))
# [END manage page]


# [START create page]
class CreatePage(webapp2.RequestHandler):

    def post(self):
        user = users.get_current_user()
        stream_name = self.request.get('streamname', DEFAULT_STREAM_NAME)
        sub = self.request.get('sub', '')
        tag = self.request.get('tag', '')
        model.create_stream(stream_name, sub, tag, user.user_id())

        template_value = {
            'greeting': 'this is the create page'
        }
        template = JINJA_ENVIRONMENT.get_template('templates/page_template.html')
        self.response.write(template.render(template_value))

    def get(self):
        template_value = {
            'greeting': 'this is the the create page'
        }
        template = JINJA_ENVIRONMENT.get_template('templates/create_page.html')
        self.response.write(template.render(template_value))
# [END create page]


# [START view page]
class ViewPage(webapp2.RequestHandler):

    def post(self):
        user = users.get_current_user()
        stream_name = self.request.get('steamname', DEFAULT_STREAM_NAME)
        comment = self.request.get('comment')
        title = self.request.get('title')
        content = self.request.get('img')
        model.add_photo(user.user_id(), stream_name, title, comment, content)
        photo_ids = model.get_photo_id_for_user(user.user_id())
        template_value = {
            'greeting': 'this is the view page',
            'img_ids': photo_ids
        }
        template = JINJA_ENVIRONMENT.get_template('templates/view_page.html')
        self.response.write(template.render(template_value))

    def get(self):
        user = users.get_current_user()
        photo_ids = model.get_photo_id_for_user(user.user_id())
        template_value = {
            'greeting': 'this is the view page',
            'img_ids': photo_ids
        }
        template = JINJA_ENVIRONMENT.get_template('templates/view_page.html')
        self.response.write(template.render(template_value))
# [END view page]


# [START search page]
class SearchPage(webapp2.RequestHandler):

    def get(self):
        template_value = {
            'greeting': 'this is the search page'
        }
        template = JINJA_ENVIRONMENT.get_template('templates/page_template.html')
        self.response.write(template.render(template_value))

# [END search page]


# [START trending page]
class TrendingPage(webapp2.RequestHandler):

    def get(self):
        template_value = {
            'greeting': 'this is the trending page'
        }
        template = JINJA_ENVIRONMENT.get_template('templates/page_template.html')
        self.response.write(template.render(template_value))
# [END trending page]


# [START social page]
class SocialPage(webapp2.RequestHandler):

    def get(self):
        template_value = {
            'greeting': 'this is the social page'
        }
        template = JINJA_ENVIRONMENT.get_template('templates/page_template.html')
        self.response.write(template.render(template_value))
# [END social page]


# [START error page]
class ErrorPage(webapp2.RequestHandler):

    def get(self):
        template_value = {
            'greeting': 'this is the error page'
        }
        template = JINJA_ENVIRONMENT.get_template('templates/page_template.html')
        self.response.write(template.render(template_value))
# [END error page]


class Image(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        img_id = self.request.get('img_id')
        if img_id:
            print(img_id)
            photo = model.get_photo(user.user_id(), img_id)
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(photo.content)
        else:
            self.response.out.write('No image')


# [START app]
app = webapp2.WSGIApplication([
    ('/', MainLoginPage),
    ('/manage', ManagePage),
    ('/create', CreatePage),
    ('/view', ViewPage),
    ('/search', SearchPage),
    ('/trending', TrendingPage),
    ('/social', SocialPage),
    ('/error', ErrorPage),
    ('/image', Image)
], debug=True)
# [END app]