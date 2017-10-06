#!/usr/bin/env python

# [START imports]
import os
import urllib
import model
import time
import re

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail
from google.appengine.api import search

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

# [START mainlogin page]
DEFAULT_STREAM_NAME = 'new_stream'
DEFAULT_IMAGE_URL = '/static/default_product.gif'

class MainLoginPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        url_dict = model.check_if_login(self, user)
        template_values = url_dict
        template = JINJA_ENVIRONMENT.get_template('templates/page_template.html')
        self.response.write(template.render(template_values))
# [END mainlogin page]


# [START manage page]
class ManagePage(webapp2.RequestHandler):

    def post(self):
        user = users.get_current_user()
        status = self.request.get('submit_btn')
        if status == "delete_stream":
            stream_names = self.request.get_all('delete_status')
            model.delete_stream(stream_names, user.user_id())
        elif status == "unsubscribe_stream":
            stream_names = self.request.get_all('unsubscribe_status')
            model.unsubscribe_to_stream(stream_names, user.user_id())
        time.sleep(1)
        self.redirect('/manage')

    def get(self):
        user = users.get_current_user()
        url_dict = model.check_if_login(self, user)
        streams = model.get_stream_list_by_user(user.user_id())
        sub_streams = model.get_subscribed_stream(user.user_id())
        template_input = {
            'streams': streams,
            'sub_streams': sub_streams,
        }
        template_values = model.merge_two_dicts(template_input, url_dict)
        template = JINJA_ENVIRONMENT.get_template('templates/manage_page.html')
        self.response.write(template.render(template_values))
# [END manage page]


# [START create page]
class CreatePage(webapp2.RequestHandler):

    def post(self):
        user = users.get_current_user()
        stream_name = self.request.get('stream_name')
        sub = self.request.get('sub', default_value='')
        r = re.compile(r"[\w\.-]+@[\w\.-]+")
        email_list = r.findall(sub)
        tag = self.request.get('tag', default_value='').split("[\s#]")
        cover_image_url = self.request.get('cover_image_url')
        if cover_image_url == '':
            cover_image_url = DEFAULT_IMAGE_URL
        model.create_stream(stream_name, cover_image_url, tag, user.user_id())

        email_content = self.request.get('email_content')
        for subscriber in email_list:
            mail.send_mail(sender="xs2948@connex-xiaocheng.appspotmail.com", to=subscriber,
                           subject="Welcome to Connexus!", body=email_content)

        template_value = {
            'greeting': 'this is the create page'
        }
        template = JINJA_ENVIRONMENT.get_template('templates/create_page.html')
        self.response.write(template.render(template_value))
        time.sleep(1)
        self.redirect('/manage')

    def get(self):
        user = users.get_current_user()
        url_dict = model.check_if_login(self, user)
        template_input = {
            'greeting': 'this is the the create page'
        }
        template_values = model.merge_two_dicts(template_input, url_dict)
        template = JINJA_ENVIRONMENT.get_template('templates/create_page.html')
        self.response.write(template.render(template_values))
# [END create page]


# [START view all page]
class ViewPage(webapp2.RequestHandler):

    def post(self):
        user = users.get_current_user()
        stream_name = self.request.get('stream_id')
        self.redirect('/view_one?stream=' + stream_name)

    def get(self):
        user = users.get_current_user()
        url_dict = model.check_if_login(self, user)
        streams = model.get_all_stream()
        template_input = {
            'greeting': 'this is the view page',
            'streams': streams
        }
        template_values = model.merge_two_dicts(template_input, url_dict)
        template = JINJA_ENVIRONMENT.get_template('templates/view_all_page.html')
        self.response.write(template.render(template_values))
# [END view all page]


# [START view one page]
class ViewOnePage(webapp2.RequestHandler):

    def post(self):
        user = users.get_current_user()
        stream_name = self.request.get('stream')
        comment = self.request.get('comment')
        title = self.request.get('title')
        content = self.request.get('img')
        status = self.request.get('submit_btn')
        if status == "Upload this photo":
            model.add_photo(user.user_id(), stream_name, title, comment, content)
        elif status == "Subscribe this stream":
            model.subscribe_to_stream(stream_name, user.user_id())
            print("subscription success!")
        # should use ancestor query, will change it later
        time.sleep(1)
        self.redirect('/view_one?stream=' + stream_name)

    def get(self):
        user = users.get_current_user()
        url_dict = model.check_if_login(self, user)
        stream_name = self.request.get('stream')
        photo_ids = model.get_photo_by_stream(stream_name, user.user_id())
        is_owner = model.get_stream_by_name(stream_name).owner == model.get_user(user.user_id()).key
        model.add_view_counts(stream_name)
        template_input = {
            'is_owner': is_owner,
            'greeting': 'this is the view page',
            'img_ids': photo_ids,
            'stream_name': stream_name
        }
        template_values = model.merge_two_dicts(template_input, url_dict)
        template = JINJA_ENVIRONMENT.get_template('templates/view_one_page.html')
        self.response.write(template.render(template_values))
# [END view one page]


# [START search page]
class SearchPage(webapp2.RequestHandler):

    def post(self):
        user = users.get_current_user()
        stream_name = self.request.get('stream_id')
        status = self.request.get('submit_btn')
        if status == "go_search":
            keyword = self.request.get('search_str')
            self.redirect('/search?keyword=' + keyword)
        else:
            self.redirect('/view_one?stream=' + stream_name)


    def get(self):
        user = users.get_current_user()
        url_dict = model.check_if_login(self, user)
        keyword = self.request.get('keyword')

        if keyword:
            stream_found = model.search_stream(keyword)
        else:
            stream_found = []
        template_input = {
            'greeting': 'this is the search page',
            'stream_list': stream_found
        }
        template_values = model.merge_two_dicts(template_input, url_dict)
        template = JINJA_ENVIRONMENT.get_template('templates/search_page.html')
        self.response.write(template.render(template_values))

# [END search page]


# [START trending page]
class TrendingPage(webapp2.RequestHandler):

    def post(self):
        status = self.request.get('submit_btn')
        if status == "trial":
            view_count = model.get_views_in_past_hour("fffff")
            print(view_count)
            self.redirect('/trending')

    def get(self):
        user = users.get_current_user()
        url_dict = model.check_if_login(self, user)
        template_input = {
            'greeting': 'this is the trending page'
        }
        template_values = model.merge_two_dicts(template_input, url_dict)
        template = JINJA_ENVIRONMENT.get_template('templates/trending_page.html')
        self.response.write(template.render(template_values))
# [END trending page]


# [START social page]
class SocialPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        url_dict = model.check_if_login(self, user)
        template_input = {
            'greeting': 'this is the social page'
        }
        template_values = model.merge_two_dicts(template_input, url_dict)
        template = JINJA_ENVIRONMENT.get_template('templates/social_page.html')
        self.response.write(template.render(template_values))
# [END social page]


# [START error page]
class ErrorPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        url_dict = model.check_if_login(self, user)
        template_input = {
            'greeting': 'this is the error page'
        }
        template_values = model.merge_two_dicts(template_input, url_dict)
        template = JINJA_ENVIRONMENT.get_template('templates/error_page.html')
        self.response.write(template.render(template_values))
# [END error page]


class Image(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        img_id_url_safe = self.request.get('img_id')
        if img_id_url_safe:
            photo = ndb.Key(urlsafe=img_id_url_safe)
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(photo.get().content)
        else:
            self.response.out.write('No image')

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainLoginPage),
    ('/manage', ManagePage),
    ('/create', CreatePage),
    ('/view', ViewPage),
    ('/view_one', ViewOnePage),
    ('/search', SearchPage),
    ('/trending', TrendingPage),
    ('/social', SocialPage),
    ('/error', ErrorPage),
    ('/image', Image)
], debug=True)
# [END app]
