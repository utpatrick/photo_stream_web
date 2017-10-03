from google.appengine.api import images
from google.appengine.ext import ndb
import os
import webapp2

from google.appengine.api import app_identity

class Photo(ndb.Model):
    owner = ndb.StringProperty()
    img_id = ndb.IntegerProperty()
    stream_name = ndb.StringProperty()
    title = ndb.StringProperty()
    comment = ndb.StringProperty()
    last_update = ndb.DateTimeProperty(auto_now_add=True)
    content = ndb.BlobProperty()


class Stream(ndb.Model):
    # stream_name is unique meaning
    stream_name = ndb.StringProperty()
    last_update = ndb.DateTimeProperty(auto_now_add=True)
    tag = ndb.StringProperty()
    photo_counts = ndb.IntegerProperty()


class User(ndb.Model):
    user_id = ndb.StringProperty()
    stream_list = ndb.StructuredProperty(Stream, repeated=True)
    subscribe_list = ndb.StringProperty(repeated=True)
    photo_counts = ndb.IntegerProperty()


def get_user(id):
    curr_user = User.query(User.user_id == id)
    user = curr_user.get()
    if not user:
        user = User()
        user.user_id=id
        user.subscribe_list = []
        user.stream_list = []
        user.photo_counts = 0
    return user


def get_stream_by_user(id):
    user = get_user(id)
    return user.stream_list


def get_subscribed_stream(id):
    user = get_user(id)
    list = []
    for sub_id in user.subscribe_list:
        sub = get_user(sub_id)
        list.append(sub.stream_list)
    return list


def get_photo_by_stream(stream_name, user_id):
    photos = Photo.query(Photo.stream_name == stream_name, Photo.owner == user_id)
    photo_list = []
    for photo in photos.fetch():
        photo_list.append(photo.content)
    return photo_list


def create_stream(stream_name, sub, tag, user_id):
    user_data = get_user(user_id)
    new_stream = Stream()
    new_stream.tag = tag
    new_stream.user_id = user_id
    new_stream.stream_name = stream_name
    user_data.stream_list.append(new_stream)
    user_data.subscribe_list.append(sub)
    user_data.put()


def add_photo(user_id, stream_name, title, comment, content):
    user_data = get_user(user_id)
    img_id = user_data.photo_counts
    new_photo = Photo()
    new_photo.owner = user_id
    new_photo.stream_name = stream_name
    new_photo.title = title
    new_photo.comment = comment
    new_photo.content = content
    new_photo.img_id = img_id + 1
    user_data.photo_counts = img_id + 1
    user_data.put()
    new_photo.put()


def get_photo(user_id, img_id):
    photo = Photo.query(Photo.img_id == int(img_id), Photo.owner == user_id)
    return photo.get()


def get_photo_id_for_user(user_id):
    photos = Photo.query(Photo.owner == user_id)
    photo_id_list = []
    for photo in photos.fetch(6):
        photo_id_list.append(photo.img_id)
    return photo_id_list
