#!/usr/bin/env python

# [START imports]
import os
import model
import time
import re
import json
import datetime

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from dateutil.relativedelta import relativedelta

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

# [START mainlogin page]
DEFAULT_STREAM_NAME = 'new_stream'
DEFAULT_IMAGE_URL = '/static/images/default_product.gif'


class MainLoginPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url_dict = model.check_if_login(self, user)
        stream_names = []
        for stream in model.search_stream(""):
            stream_names.append(str(stream.stream_name))
        template_input = {
            'stream_names': stream_names
        }
        template_values = model.merge_two_dicts(template_input, url_dict)
        template = JINJA_ENVIRONMENT.get_template('templates/main_login_page.html')
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
        print(user.user_id)
        url_dict = model.check_if_login(self, user)
        streams = model.get_stream_list_by_user(user.user_id())
        sub_streams = model.get_subscribed_stream(user.user_id())
        stream_names = []
        for stream in model.search_stream(""):
            stream_names.append(str(stream.stream_name))

        template_input = {
            'streams': streams,
            'sub_streams': sub_streams,
            'stream_names': stream_names
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
        subject = "Welcome to Connexus!"
        email_content = self.request.get('email_content')
        model.send_email(subject, email_list, email_content)

        tag = self.request.get('tag', default_value='').split("[\s#,]")
        cover_image_url = self.request.get('cover_image_url')
        if cover_image_url == '':
            cover_image_url = DEFAULT_IMAGE_URL
        result = model.create_stream(stream_name, cover_image_url, tag, user.user_id())
        if result:
            self.redirect('/error?stream=' + stream_name)
            return

        template_value = {

        }
        template = JINJA_ENVIRONMENT.get_template('templates/create_page.html')
        self.response.write(template.render(template_value))
        time.sleep(0.5)
        self.redirect('/manage')

    def get(self):
        user = users.get_current_user()
        url_dict = model.check_if_login(self, user)
        stream_names = []
        for stream in model.search_stream(""):
            stream_names.append(str(stream.stream_name))
        template_input = {
            'stream_names': stream_names
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
        stream_names = []
        for stream in model.search_stream(""):
            stream_names.append(str(stream.stream_name))
        template_input = {
            'streams': streams,
            'stream_names': stream_names
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
        action = self.request.get('action', '')
        loaded_photo = self.request.get('loaded', default_value='9')
        loaded_photo = int(loaded_photo)

        if action == 'upload':
            counts = self.request.get('counts')
            for i in range(int(counts)):
                title = self.request.get('title[' + str(i) + ']')
                content = self.request.get('image[' + str(i) + ']')
                result = model.add_photo(user.user_id(), stream_name, title, comment, content)
                if result:
                    self.redirect('/error?photo=invalid')
                    return
        elif action == 'subscribe':
            model.subscribe_to_stream(stream_name, user.user_id())
        elif action == 'more':
            loaded_photo += 3
        elif action == "geoview":
            self.redirect('/geo_view?stream=' + stream_name)
            return
        # should use ancestor query, will change it later
        time.sleep(0.25)
        self.redirect('/view_one?stream=' + stream_name + '&loaded=' + str(loaded_photo))

    def get(self):
        user = users.get_current_user()
        url_dict = model.check_if_login(self, user)
        stream_name = self.request.get('stream')
        loaded_photo = self.request.get('loaded', default_value='9')

        photos = model.get_photo_by_stream(stream_name)

        # adding fake gps information
        model.shuffle_stream_geo_info(stream_name)
        time.sleep(0.1)

        photos = sorted(photos, key=lambda x: x.last_update, reverse=True)

        current_date = datetime.datetime.utcnow().date()
        a_year_before = current_date + relativedelta(years=-1)
        more = loaded_photo < len(photos)
        photo_key = []
        for i in range(min(loaded_photo, len(photos))):
            photo_key.append(photos[i].blob_key)

        if user:
            is_owner = model.get_stream_by_name(stream_name).owner == model.get_user(user.user_id()).key
        else:
            is_owner = False
        model.add_view_counts(stream_name)

        stream_names = []
        for stream in model.search_stream(""):
            stream_names.append(str(stream.stream_name))

        upload_url = blobstore.create_upload_url('/upload_image')
        template_input = {
            'is_owner': is_owner,
            'img_ids': photo_key,
            'upload_url': upload_url,
            'more': more,
            'stream_name': stream_name,
            'loaded': loaded_photo,
            'stream_names': stream_names,
            'current_date': current_date.strftime("%Y, %m, %d"),
            'a_year_before': a_year_before.strftime("%Y, %m, %d")
        }

        template_values = model.merge_two_dicts(template_input, url_dict)
        template = JINJA_ENVIRONMENT.get_template('templates/view_one_page.html')
        self.response.write(template.render(template_values))


# [END view one page]


# [START geo view page]
class GeoViewPage(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        stream_name = self.request.get('stream')
        action = self.request.get('action', '')

        if action == "subscribe":
            if user:
                model.subscribe_to_stream(stream_name, user.user_id())
            else:
                self.redirect('/')
                return

        # should use ancestor query, will change it later
        time.sleep(0.1)
        self.redirect('/geo_view?stream=' + stream_name)

    def get(self):
        user = users.get_current_user()
        url_dict = model.check_if_login(self, user)
        stream_name = self.request.get('stream')

        photos = model.get_photo_by_stream(stream_name)
        geo_photo = photos

        # adding fake gps information
        model.shuffle_stream_geo_info(stream_name)
        time.sleep(0.1)

        current_date = datetime.datetime.utcnow().date()
        a_year_before = current_date + relativedelta(years=-1)

        if user:
            is_owner = model.get_stream_by_name(stream_name).owner == model.get_user(user.user_id()).key
        else:
            is_owner = False

        geo_info = []
        for photo in geo_photo:
            temp = {'geo_info': (photo.geo_info.lat, photo.geo_info.lon),
                    'last_update': photo.last_update.strftime("%Y, %m, %d"),
                    'key_url': photo.key.urlsafe(),
                    'key': photo.key.id()}
            geo_info.append(temp)

        model.add_view_counts(stream_name)
        template_input = {
            'is_owner': is_owner,
            'stream_name': stream_name,
            'geo_photo': json.dumps(geo_info),
            'current_date': current_date.strftime("%Y, %m, %d"),
            'a_year_before': a_year_before.strftime("%Y, %m, %d")
        }
        template_values = model.merge_two_dicts(template_input, url_dict)
        template = JINJA_ENVIRONMENT.get_template('templates/geo_view.html')
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

        streams = model.search_stream("")
        stream_names = []
        for stream in streams:
            stream_names.append(str(stream.stream_name))
        template_input = {
            'stream_list': stream_found,
            'stream_names': stream_names
        }
        template_values = model.merge_two_dicts(template_input, url_dict)
        template = JINJA_ENVIRONMENT.get_template('templates/search_page.html')
        self.response.write(template.render(template_values))


# [END search page]


# [START trending page]
class TrendingPage(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        stream_name = self.request.get('stream_id')
        if stream_name:
            self.redirect('/view_one?stream=' + stream_name)
        else:
            new_trending_setting = self.request.get('new_trending_setting')
            model.update_user_trending_setting(user.user_id(), new_trending_setting)
            time.sleep(0.1)
            self.redirect('/trending')

    def get(self):
        user = users.get_current_user()
        url_dict = model.check_if_login(self, user)

        # model.update_views_in_past_hour() will run by cron.yaml every 5 min

        streams = model.get_all_recent_stream()
        sorted_streams = sorted(streams, key=lambda x: x.views_in_last_hour, reverse=True)
        num_of_streams = len(sorted_streams)
        if num_of_streams >= 3:
            num_of_streams = 3
            sorted_streams = sorted_streams[:3]

        streams = model.search_stream("")
        stream_names = []
        for stream in streams:
            stream_names.append(str(stream.stream_name))

        if user:
            trending_setting = model.get_trending_setting(user.user_id())
            logged_in = True
        else:
            trending_setting = "no"
            logged_in = False

        template_input = {
            'logged_in': logged_in,
            'trending_setting': trending_setting,
            'trending_streams': sorted_streams,
            'num_of_streams': num_of_streams,
            'stream_names': stream_names

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

        streams = model.search_stream("")
        stream_names = []
        for stream in streams:
            stream_names.append(str(stream.stream_name))
        template_input = {
            'stream_names': stream_names
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
        stream_name = self.request.get('stream')
        photo = self.request.get('photo')

        streams = model.search_stream("")
        stream_names = []
        for stream in streams:
            stream_names.append(str(stream.stream_name))
        template_input = {
            'error_message': 'stream name: ' + stream_name + ' is already occupied!',
            'stream_names': stream_names
        }
        if photo:
            template_input['error_message'] = 'photo ' + photo
        template_values = model.merge_two_dicts(template_input, url_dict)
        template = JINJA_ENVIRONMENT.get_template('templates/error_page.html')
        self.response.write(template.render(template_values))


# [END error page]


class PhotoUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        counts = self.request.get('counts')
        user = users.get_current_user()
        stream_name = self.request.get('stream')
        loaded_photo = self.request.get('loaded_photo')
        if counts:
            for i in range(int(counts)):
                title = self.request.get('title[' + str(i) + ']')
                content = self.get_uploads('image[' + str(i) + ']')[0]
                print(content.key())
                result = model.add_photo(user.user_id(), stream_name, title, content.key())
                if result:
                    self.redirect('/error?photo=invalid')
                    return
        time.sleep(0.25)
        self.redirect('/view_one?stream=' + stream_name + '&loaded=' + str(loaded_photo))


class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        image_id = self.request.get('img_id')
        if image_id:
            self.send_blob(image_id)
        else:
            self.redirect('error?photo=invalid')


class UpdateTrendingPage(webapp2.RequestHandler):
    def get(self):
        model.update_views_in_past_hour()


class SendDigest5Min(webapp2.RequestHandler):
    def get(self):
        model.send_digest_5_min()


class SendDigest1Hr(webapp2.RequestHandler):
    def get(self):
        model.send_digest_1_hr()


class SendDigest24Hr(webapp2.RequestHandler):
    def get(self):
        model.send_digest_24_hr()


# [START app]
app = webapp2.WSGIApplication([
    ('/', MainLoginPage),
    ('/manage', ManagePage),
    ('/create', CreatePage),
    ('/view', ViewPage),
    ('/view_one', ViewOnePage),
    ('/geo_view', GeoViewPage),
    ('/search', SearchPage),
    ('/trending', TrendingPage),
    ('/social', SocialPage),
    ('/error', ErrorPage),
    ('/updatetrending', UpdateTrendingPage),
    ('/digest5min', SendDigest5Min),
    ('/digest1hr', SendDigest1Hr),
    ('/digest24hr', SendDigest24Hr),
    ('/upload_image', PhotoUploadHandler),
    ('/view_image', ViewPhotoHandler)
], debug=True)
# [END app]
