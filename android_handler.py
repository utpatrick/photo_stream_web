# [START imports]
import os
import model
import json
import time

import jinja2
import webapp2

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

IMAGE_COUNT = 16


class GetAllStreams(webapp2.RequestHandler):
    def get(self):
        orig_streams = model.get_all_stream()
        streams = sorted(orig_streams, key=lambda x: x.last_update, reverse=True)
        response_content = [{'stream_name': s.stream_name, 'cover_image': s.cover_image} for s in streams]
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response_content))


class SearchStreams(webapp2.RequestHandler):
    def get(self):
        keyword = self.request.get('keyword')
        streams = []
        stream_all = model.get_all_stream()
        for i in stream_all:
            if i.stream_name.find(keyword) != -1:
                streams.append(i)
                print(i)

        response_content = [{'stream_name': s.stream_name, 'cover_image': s.cover_image} for s in streams]
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response_content))


class GetAllImages(webapp2.RequestHandler):
    def get(self):
        stream_name = self.request.get('stream_name')
        start = int(self.request.get('start'))
        owner_email = model.get_stream_owner_by_name(stream_name)
        if not start:
            start = 0
        if not stream_name:
            img_key = self.request.get('img_key')
            stream_name = model.get_stream_name_by_image_key(img_key)

        photos = model.get_photo_by_stream(stream_name)
        photos = photos[start:start + IMAGE_COUNT]
        content = [{'title': photo.title,
                    'key': str(photo.blob_key),
                    'stream_name': photo.up_stream.get().stream_name} for photo in photos]
        response_content = {'start': start,
                            'content': content,
                            'owner_email': owner_email}
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response_content))


class GetNearbyImages(webapp2.RequestHandler):
    def get(self):
        latitude = self.request.get('latitude')
        longitude = self.request.get('longitude')
        start = int(self.request.get('start'))
        if not start:
            start = 0

        if not latitude or (not longitude):
            self.response.set_status(404)
        else:
            images = model.get_nearby_image(float(latitude), float(longitude), start, IMAGE_COUNT)
            images = images[start:start + IMAGE_COUNT]
            content = [{'title': img.title,
                        'key': str(img.blob_key),
                        'stream_name': img.up_stream.get().stream_name} for img in images]
            response_content = {'start': start,
                                'content': content}
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps(response_content))


class GetSubImages(webapp2.RequestHandler):
    def get(self):
        user_email = self.request.get('user_email')
        start = int(self.request.get('start'))
        if not start:
            start = 0
        user_id = model.user_email_to_user_id(user_email)
        photos_list = model.get_sub_images(user_id)
        photos_list = photos_list[start:start + IMAGE_COUNT]
        content = [{'title': photo.title,
                    'key': str(photo.blob_key),
                    'stream_name': photo.up_stream.get().stream_name} for photo in photos_list]
        response_content = {'start': start,
                            'content': content}
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response_content))


class PhotoUploadImageUrl(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/android/upload_image')
        self.response.headers['Content-Type'] = 'application/json'
        response_content = {'uploadURL': upload_url}
        self.response.out.write(json.dumps(response_content))


class PhotoUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        stream_name = self.request.get('stream')
        user_email = self.request.get('user_email')
        user_id = model.user_email_to_user_id(user_email)
        title = self.request.get('title')
        content = self.get_uploads()[0]
        model.add_photo(user_id, stream_name, title, content.key())


# [START app]
app = webapp2.WSGIApplication([
    ('/android/view_all_streams', GetAllStreams),
    ('/android/view_all_images', GetAllImages),
    ('/android/view_nearby_images', GetNearbyImages),
    ('/android/view_sub_images', GetSubImages),
    ('/android/search', SearchStreams),
    ('/android/upload_image', PhotoUploadHandler),
    ('/android/upload_image_url', PhotoUploadImageUrl)
], debug=True)
# [END app]
