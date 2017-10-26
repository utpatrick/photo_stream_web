# [START imports]
import os
import model
import json

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

IMAGE_COUNT = 16


class GetAllStreams(webapp2.RequestHandler):
    def get(self):
        user_email = self.request.get('user_email')
        user_id = model.user_email_to_user_id(user_email)
        streams = model.get_stream_list_by_user(user_id)
        response_content = [{'stream_name': s.stream_name, 'cover_image': s.cover_image} for s in streams]
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response_content))


class GetAllImages(webapp2.RequestHandler):
    def get(self):
        stream_name = self.request.get('stream_name')
        start = int(self.request.get('start'))
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
                            'content': content}
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
            images = images[start:start+IMAGE_COUNT]
            content = [{'title': img.title,
                        'key': str(img.blob_key),
                        'stream_name': img.up_stream.get().stream_name} for img in images]
            response_content = {'start': start,
                                'content': content}
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps(response_content))


class UploadImage(webapp2.RequestHandler):
    #TODO for upload
    pass


# [START app]
app = webapp2.WSGIApplication([
    ('/android/view_all_streams', GetAllStreams),
    ('/android/view_all_images', GetAllImages),
    ('/android/view_nearby_images', GetNearbyImages),
    ('/android/upload_image', UploadImage)
], debug=True)
# [END app]