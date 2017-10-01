from google.appengine.api import images
from google.appengine.ext import ndb
import os
import lib.cloudstorage as gcs
import webapp2

from google.appengine.api import app_identity

class Photo(ndb.Model):
    stream_name = ndb.StringProperty()
    title = ndb.StringProperty()
    comment = ndb.StringProperty()
    last_update = ndb.DateTimeProperty(auto_now_add=True)

    # calls the save_photo_to_cs method
    def get_photo(self):
        pass  # TODO

    # calls the get_photo_from_cs method
    def save_photo(self):
        pass  # TODO

    def get_comment(self):
        pass  # TODO

    def get_title(self):
        pass  # TODO

    def get_last_update(self):
        pass  # TODO

    def stream_name(self):
        pass  # TODO

    #internal method dealing with connection to data store
    def save_photo_to_cs(self):
        pass  # TODO

    # internal method dealing with connection to data store
    def get_photo_from_cs(self):
        pass  # TODO


class Stream(ndb.Model):
    user_id = ndb.StringProperty()
    # stream_name is unique meaning
    stream_name = ndb.StringProperty()
    image_count = ndb.IntegerProperty()
    last_update = ndb.DateTimeProperty(auto_now_add=True)
    tag = ndb.StringProperty()
    photo_list = ndb.StructureProperty(Photo, repeated=True)

    def get_user_id(self):
        pass  # TODO

    def get_stream_name(self):
        pass  # TODO

    def get_image_count(self):
        pass  # TODO

    def get_last_update(self):
        pass  # TODO

    def get_tag(self):
        pass  # TODO

    #saves photo to this stream, calls the save_photo method of Photo
    def save_photo_to_stream(self):
        pass  # TODO

    # gets photo from this stream, calls the get_photo method of Photo
    def get_photo_from_stream(self):
        pass  # TODO

    #should return a list of photo object for display
    def get_all_photo(self):
        pass  # TODO
