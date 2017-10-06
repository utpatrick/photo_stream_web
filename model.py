from google.appengine.api import images
from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.api import app_identity
from google.appengine.api import users

import os
import webapp2
import time
import datetime


class User(ndb.Model):
    user_id = ndb.StringProperty()
    subscribes_list = ndb.StringProperty(repeated=True)
    photo_counts = ndb.IntegerProperty()
    trending_setting = ndb.StringProperty(choices=('no', 'per_5min', 'per_1hr', 'per_1day'))


class Stream(ndb.Model):
    # stream_name is unique meaning (among all users)
    owner = ndb.KeyProperty(kind=User)
    stream_name = ndb.StringProperty()
    last_update = ndb.DateTimeProperty(auto_now=True)
    photo_counts = ndb.IntegerProperty()
    cover_image = ndb.StringProperty()
    views = ndb.IntegerProperty()
    tags = ndb.StringProperty(repeated=True)


class Photo(ndb.Model):
    up_stream = ndb.KeyProperty(kind=Stream)
    title = ndb.StringProperty()
    comment = ndb.StringProperty()
    last_update = ndb.DateTimeProperty(auto_now_add=True)
    content = ndb.BlobProperty()


class View(ndb.Model):
    time_stamp = ndb.DateTimeProperty(auto_now_add=True)
    up_stream = ndb.KeyProperty(kind=Stream)


def create_user(id):
    user = User(user_id=id, photo_counts=0, trending_setting='no')
    user.put()
    return user


def get_user(id):
    curr_user = User.query(User.user_id == id)
    user = curr_user.get()
    if not user:
        user = create_user(id)
    return user


def get_stream_by_name(stream_name):
    stream = Stream.query(Stream.stream_name == stream_name)
    return stream.get()


def get_all_stream():
    stream = Stream.query()
    return stream.fetch()


def get_stream_list_by_user(id):
    user = get_user(id)
    stream = Stream.query(Stream.owner == user.key)
    return stream.fetch()


def get_subscribed_stream(id):
    user = get_user(id)
    subscribed_stream_list = []
    for s in user.subscribes_list:
        subscribed_stream_list.append(get_stream_by_name(s))
    return subscribed_stream_list


def subscribe_to_stream(stream_name, id):
    user = get_user(id)
    user.subscribes_list.append(stream_name)
    user.put()


def unsubscribe_to_stream(stream_name_list, id):
    user = get_user(id)
    for stream_name in stream_name_list:
        user.subscribes_list.remove(stream_name)
    user.put()


def get_views_in_past_hour(stream_name):
    stream = get_stream_by_name(stream_name)
    views = View.query(Photo.up_stream == stream.key)
    time_1hr_ago = datetime.datetime.utcnow() + datetime.timedelta(hours=-1)
    views.filter(ndb.GenericProperty("time_stamp") > time_1hr_ago)
    view_count = views.count()
    return view_count


def add_view_counts(stream_name):
    stream = get_stream_by_name(stream_name)
    stream.views += 1
    new_view = View(up_stream=stream.key)
    stream.put()
    new_view.put()


# search function
def search_stream(keyword):
    streams = Stream.query(ndb.OR(Stream.stream_name == keyword, Stream.tags == keyword))
    stream_list = streams.fetch()
    return stream_list


def check_if_login(get, user):
    if user:
        url = users.create_logout_url(get.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(get.request.uri)
        url_linktext = 'Login'
    template_values = {
        'user': user,
        'url': url,
        'url_linktext': url_linktext,
    }
    return template_values


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


def get_photo_by_stream(stream_name, id):
    user = get_user(id)
    stream = get_stream_by_name(stream_name)
    photos = Photo.query(Photo.up_stream == stream.key)
    photo_list = []
    for photo in photos.fetch():
        photo_list.append(photo)
    return photo_list


def create_stream(stream_name, cover_image_url, tag, id):
    user = get_user(id)
    new_stream = Stream(owner=user.key, tags=tag, stream_name=stream_name,
                        photo_counts=0, views=0, cover_image=cover_image_url)
    print("this: {}".format(cover_image_url))
    user.put()
    new_stream.put()


def add_photo(id, stream_name, title, comment, content):
    user = get_user(id)
    stream = get_stream_by_name(stream_name)
    stream.photo_counts += 1
    user.photo_counts += 1
    new_photo = Photo(up_stream=stream.key, title=title, comment=comment, content=content)
    new_photo.put()
    stream.put()
    user.put()


def get_photo(img_key):
    photo = img_key.get()
    return photo


def get_photo_id_for_user(user_id):
    user = get_user(id)
    photos = Photo.query(Photo.owner == user.key)
    photo_id_list = []
    for photo in photos.fetch(6):
        photo_id_list.append(photo.img_id)
    return photo_id_list


def delete_photo_by_stream(stream_name, id):
    user = get_user(id)
    stream = get_stream_by_name(stream_name)
    tbdPhotoQ = Photo.query(Photo.up_stream == stream.key)
    tbdPhotoKey = tbdPhotoQ.get().key
    tbdPhotoKey.delete()


def delete_stream(stream_name_list, id):
    user = get_user(id)
    count = 0
    for stream_name in stream_name_list:
        tbdStreamQ = Stream.query(Stream.stream_name == stream_name, Stream.owner == user.key)
        tbdStreamKey = tbdStreamQ.get().key
        photo_counts = tbdStreamQ.get().photo_counts
        if photo_counts != 0:
            delete_photo_by_stream(stream_name, user.user_id)
            count += photo_counts
        tbdStreamKey.delete()
    user.photo_counts -= count
    user.put()


def get_cover_image_url(stream_name):
    stream = get_stream_by_name(stream_name)
    return stream.cover_image