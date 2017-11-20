from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import mail
from math import radians, cos, sin, asin, sqrt
from faker import Faker

import datetime




class User(ndb.Model):
    user_id = ndb.StringProperty()
    user_email = ndb.StringProperty()
    subscribes_list = ndb.StringProperty(repeated=True)
    photo_counts = ndb.IntegerProperty()
    trending_setting = ndb.StringProperty(choices=('no', 'per_5min', 'per_1hr', 'per_24hr'))


class Stream(ndb.Model):
    # stream_name is unique meaning (among all users)
    owner = ndb.KeyProperty(kind=User)
    stream_name = ndb.StringProperty()
    last_update = ndb.DateTimeProperty(auto_now=True)
    photo_counts = ndb.IntegerProperty()
    cover_image = ndb.StringProperty()
    total_views = ndb.IntegerProperty()
    tags = ndb.StringProperty(repeated=True)
    views_in_last_hour = ndb.IntegerProperty()


class Photo(ndb.Model):
    up_stream = ndb.KeyProperty(kind=Stream)
    title = ndb.StringProperty()
    last_update = ndb.DateTimeProperty(auto_now_add=True)
    # content = ndb.BlobProperty()
    comments = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()
    geo_info = ndb.GeoPtProperty()


class View(ndb.Model):
    time_stamp = ndb.DateTimeProperty(auto_now_add=True)
    up_stream = ndb.KeyProperty(kind=Stream)


def create_user(id):
    curr_user = users.get_current_user()
    user = User(user_id=id, user_email=curr_user.email(), photo_counts=0, trending_setting='no')
    user.put()
    return user


def get_user(user_id):
    curr_user = User.query(User.user_id == user_id)
    user = curr_user.get()
    if not user:
        user = create_user(user_id)
    return user


def get_stream_by_name(stream_name):
    stream = Stream.query(Stream.stream_name == stream_name)
    return stream.get()


def get_stream_owner_by_name(stream_name):
    stream = get_stream_by_name(stream_name)
    owner_email = stream.owner.get().user_email
    return owner_email


def get_all_stream():
    stream = Stream.query()
    return stream.fetch()


def send_email(subject, receivers, email_content):
    for receiver in receivers:
        mail.send_mail(sender="sparrows@minitrial-181200.appspotmail.com", to=receiver,
                       subject=subject, body=email_content)


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
    if stream_name not in user.subscribes_list:
        user.subscribes_list.append(stream_name)
    user.put()


def unsubscribe_to_stream(stream_name_list, id):
    user = get_user(id)
    for stream_name in stream_name_list:
        user.subscribes_list.remove(stream_name)
    user.put()


def send_digest_5_min():
    users = User.query(User.trending_setting == 'per_5min')
    email_list = []
    for user in users:
        email_list.append(user.user_email)
    subject = "Stream Recommendation From Connexus - 5 min"
    email_content = "Connexus trending page url: from here!"
    send_email(subject, email_list, email_content)


def send_digest_1_hr():
    users = User.query(User.trending_setting == 'per_1hr')
    email_list = []
    for user in users:
        email_list.append(user.user_email)
    subject = "Stream Recommendation From Connexus - 1 hr"
    email_content = "Connexus trending page url: from here!"
    send_email(subject, email_list, email_content)


def send_digest_24_hr():
    users = User.query(User.trending_setting == 'per_24hr')
    email_list = []
    for user in users:
        email_list.append(user.user_email)
    subject = "Stream Recommendation From Connexus - 24 hr"
    email_content = "Connexus trending page url: from here!"
    send_email(subject, email_list, email_content)


def get_views_in_past_hour(stream_name):
    stream = get_stream_by_name(stream_name)
    views = View.query(Photo.up_stream == stream.key)
    time_1hr_ago = datetime.datetime.utcnow() + datetime.timedelta(hours=-1)
    views_in_last_hour = views.filter(ndb.GenericProperty("time_stamp") > time_1hr_ago)
    stream.views_in_last_hour = views_in_last_hour.count()
    stream.put()


def update_views_in_past_hour():
    stream = Stream.query()
    for s in stream.fetch():
        get_views_in_past_hour(s.stream_name)


def get_all_recent_stream():
    streams = Stream.query()
    recent_streams = streams.filter(ndb.GenericProperty("views_in_last_hour") > 0)
    return recent_streams.fetch()


def update_user_trending_setting(id, setting):
    user = get_user(id)
    user.trending_setting = setting
    user.put()


def get_trending_setting(id):
    user = get_user(id)
    setting = user.trending_setting
    return setting


def add_view_counts(stream_name):
    stream = get_stream_by_name(stream_name)
    stream.total_views += 1
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


def get_photo_by_stream(stream_name):
    stream = get_stream_by_name(stream_name)
    photos = Photo.query(Photo.up_stream == stream.key)
    photo_list = []
    for photo in photos.fetch():
        photo_list.append(photo)
    return photo_list


def create_stream(stream_name, cover_image_url, tag, id):
    user = get_user(id)
    check_existing = get_stream_by_name(stream_name)
    if check_existing:
        return 1
    else:
        new_stream = Stream(owner=user.key, tags=tag, stream_name=stream_name,
                        photo_counts=0, total_views=0, views_in_last_hour=0,
                        cover_image=cover_image_url)
        new_stream.put()
        return 0


def add_photo(user_id, stream_name, title, key):
    user = get_user(user_id)

    if not title or not key or not stream_name:
        return 1
    else:
        stream = get_stream_by_name(stream_name)
        stream.photo_counts += 1
        user.photo_counts += 1
        new_photo = Photo(up_stream=stream.key, title=title, blob_key=key)
        new_photo.put()
        stream.put()
        user.put()
        return 0


def add_photo_geo(user_id, stream_name, title, key, geo, tags):
    user = get_user(user_id)

    if not title or not key or not stream_name:
        return 1
    else:
        stream = get_stream_by_name(stream_name)
        stream.photo_counts += 1
        user.photo_counts += 1
        new_photo = Photo(up_stream=stream.key, title=title, blob_key=key, geo_info=geo, comments=tags)
        new_photo.put()
        stream.put()
        user.put()
        return 0


def get_photo(img_key):
    photo = img_key.get()
    return photo


def get_photo_id_for_user(user_id):
    user = get_user(user_id)
    photos = Photo.query(Photo.owner == user.key)
    photo_id_list = []
    for photo in photos.fetch(6):
        photo_id_list.append(photo.img_id)
    return photo_id_list


def delete_photo_by_stream(stream_name, user_id):
    user = get_user(user_id)
    stream = get_stream_by_name(stream_name)
    tbd_photo_q = Photo.query(Photo.up_stream == stream.key)
    tbd_photo_key = tbd_photo_q.get().key
    tbd_photo_key.delete()


def delete_stream(stream_name_list, user_id):
    user = get_user(user_id)
    count = 0
    for stream_name in stream_name_list:
        tbd_stream_q = Stream.query(Stream.stream_name == stream_name, Stream.owner == user.key)
        if tbd_stream_q.get():
            tbd_stream_key = tbd_stream_q.get().key
            photo_counts = tbd_stream_q.get().photo_counts
            if photo_counts != 0:
                delete_photo_by_stream(stream_name, user_id)
                count += photo_counts
            tbd_stream_key.delete()
    if count:
        user.photo_counts -= count
        user.put()


def get_cover_image_url(stream_name):
    stream = get_stream_by_name(stream_name)
    return stream.cover_image


def shuffle_stream_geo_info(stream_name):
    fake_gps = Faker()
    photos = get_photo_by_stream(stream_name)
    for photo in photos:
        if photo.geo_info:
            continue
        else:
            photo.geo_info = ndb.GeoPt(fake_gps.latitude(), fake_gps.longitude())
        photo.put()


def get_stream_name_by_image_key(key):
    photo = Photo.query(Photo.blob_key == key)
    if photo:
        return photo.get().up_stream.stream_name


def get_nearby_image(latitude, longitude, start, count):
    photos = Photo.query().fetch()
    sorted_photos = sorted(photos, key=lambda x: get_distance(longitude, latitude, x.geo_info.lon, x.geo_info.lat))
    return sorted_photos[start:(start + count)]


def user_email_to_user_id(email):
    user = User.query(User.user_email == email)
    if user and user.get():
        return user.get().user_id


def get_sub_images(user_id):
    stream_list = get_subscribed_stream(user_id)
    photo_list = []
    if stream_list:
        for stream in stream_list:
            photo_list.extend(get_photo_by_stream(stream.stream_name))
        return photo_list


def get_distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km
