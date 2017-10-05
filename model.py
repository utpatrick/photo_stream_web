from google.appengine.api import images
from google.appengine.ext import ndb
import os
import webapp2
import time

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
    owner = ndb.StringProperty()
    stream_name = ndb.StringProperty()
    last_update = ndb.DateTimeProperty(auto_now=True)
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
        user.put()
    return user


def get_stream_by_user(id):
    user = get_user(id)
    stream = Stream.query(Stream.owner == user.user_id)
    return stream.fetch()

def get_stream_name_by_user(id):
    user = get_user(id)
    user_stream_list = get_stream_by_user(user.user_id)
    stream_name_list = []
    for stream in user_stream_list:
        stream_name_list.append(stream.stream_name)
    return stream_name_list

def get_subscribed_stream(id):
    user = get_user(id)
    list = []
    for sub_id in user.subscribe_list:
        sub = get_user(sub_id)
        list.append(sub.stream_list)
    return list


# search function
def search_stream(stream_name):
    streams = Stream.query(Stream.stream_name == stream_name)
    stream_list = streams.fetch()
    stream_list.sort(key=lambda x: x.photo_counts)
    stream_top5 = []
    for i in range(0,5):
        stream_top5.append(stream_list[i])
    return stream_top5


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
    new_stream.owner = user_id
    new_stream.stream_name = stream_name
    new_stream.photo_counts = 0
    user_data.stream_list.append(new_stream)
    user_data.subscribe_list.append(sub)
    user_data.put()
    new_stream.put()


def add_photo(user_id, stream_name, title, comment, content):
    user_data = get_user(user_id)
    stream_name_list = get_stream_name_by_user(user_data.user_id)
    if stream_name not in stream_name_list:
        create_stream(stream_name, '', '', user_id)
    img_id = user_data.photo_counts
    new_photo = Photo()
    new_photo.owner = user_id
    new_photo.stream_name = stream_name

    # should use ancestor query, will change it later
    time.sleep(1)
    stream = Stream.query(Stream.stream_name == stream_name)
    user_stream = stream.get()
    user_stream.photo_counts += 1

    new_photo.title = title
    new_photo.comment = comment
    new_photo.content = content
    new_photo.img_id = img_id + 1
    user_data.photo_counts += 1

    user_stream.put()
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