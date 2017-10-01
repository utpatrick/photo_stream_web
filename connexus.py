#!/usr/bin/env python

# [START imports]
import os
import urllib
import model

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

# [START mainlogin page]

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
        template_value = {
            'greeting': 'this is the manage page'
        }
        template = JINJA_ENVIRONMENT.get_template('templates/page_template.html')
        self.response.write(template.render(template_value))
# [END manage page]

# [START create page]
class CreatePage(webapp2.RequestHandler):

    def get(self):
        template_value = {
            'greeting': 'this is the create page'
        }
        template = JINJA_ENVIRONMENT.get_template('templates/page_template.html')
        self.response.write(template.render(template_value))
# [END create page]


# [START view page]
class ViewPage(webapp2.RequestHandler):

    def get(self):
        template_value = {
            'greeting': 'this is the view page'
        }
        template = JINJA_ENVIRONMENT.get_template('templates/page_template.html')
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

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainLoginPage),
    ('/manage', ManagePage),
    ('/create', CreatePage),
    ('/view', ViewPage),
    ('/search', SearchPage),
    ('/trending', TrendingPage),
    ('/social', SocialPage),
    ('/error', ErrorPage)
], debug=True)
# [END app]