#-*- coding: utf-8 -*-
import re
import urllib
import json
import oauth2 as oauth
import urllib2
import poster
import certifi

opener = poster.streaminghttp.register_openers()


class APIError(StandardError):
    def __init__(self, msg, response=None):
        StandardError.__init__(self, msg)


class Pynientos:
    def __init__(self, **kwargs):
        self.site = "https://api.500px.com"

    def auth(self, **kwargs):
        """ Set the oauth client with the given key and secret """
        if not 'key'in kwargs or not 'secret' in kwargs:
            raise ValueError("Key and secret must be set.")

        if len(kwargs) == 4:
            if 'token' in kwargs and 'token_secret' in kwargs:
                self.client = oauth.Client(
                  oauth.Consumer(
                    key=kwargs['key'], secret=kwargs['secret']
                  ),
                  oauth.Token(
                    key=kwargs['token'], secret=kwargs['token_secret']
                  )
                )
            else:
                raise ValueError("Wrong parameters")
        else:
            self.client = oauth.Client(
                oauth.Consumer(key=kwargs['key'],
                secret=kwargs['secret']
            ))
        self.client.ca_certs = certifi.where()
        self.set_methods()

    def api_setting(self):
        """ A list of name, url, auth type and http method for the API usage """
        api_str = """
          get_photos_popular         /v1/photos?feature=popular         get
          get_photos_upcoming        /v1/photos?feature=upcoming        get
          get_photos_editors         /v1/photos?feature=editors         get
          get_photos_fresh_today     /v1/photos?feature=fresh_today     get
          get_photos_fresh_yesterday /v1/photos?feature=fresh_yesterday get
          get_photos_fresh_week      /v1/photos?feature=fresh_week      get
          get_photos_user            /v1/photos?feature=user            get
          get_photos_user_friends    /v1/photos?feature=user_friends    get
          get_photos_user_favorites  /v1/photos?feature=user_favorites  get
          get_photos_search          /v1/photos/search?                 get
          get_photo_detail           /v1/photos/                        get
          get_user                   /v1/users                          get
          get_user_show              /v1/users/show                     get
          get_blogs_fresh            /v1/blogs?feature=fresh            get
          get_blogs_user             /v1/blogs?feature=user             get
          get_blog_detail            /v1/blogs/                         get
          post_blog                  /v1/blogs/                         post
          delete_blog_post           /v1/blogs/                         delete
          post_photo                 /v1/photos/                        post
          upload_photo               /v1/upload/                        upload
        """
        return map(lambda x: re.split("\s+", x.strip()),
                             re.split("\n", api_str.strip()))

    def set_methods(self):
        """ Set the API methods with the api_settings list """
        for api_list in self.api_setting():
            api = {}
            api["method_name"], api["path"], api["http_method"] = api_list

            def _method(api=api, id="", **params):
                """ Check if the parameters include an ID
                This change the url construction
                """
                if id:
                    return getattr(self,
                        api["http_method"])(str.join('', (api["path"], id)),
                        params
                        )
                else:
                    return getattr(self,
                        api["http_method"])(api["path"],
                        params
                        )

            setattr(self, api["method_name"], _method)

    def get(self, path, params=""):
        """ construct the complete GET url and returns the JSON response """
        if params:
            return self.parse_response(self.client.request(
                str.join('', (self.site, path, self.encode_params(params))),
                "GET",
                ))

        else:
            return self.parse_response(self.client.request(
                str.join('', (self.site, path)),
                "GET",
                ))

    def post(self, path, params={}):
        return self.parse_response(self.client.request(
            str.join('', (self.site, path)),
            "POST", body=urllib.urlencode(params)
            ))

    def upload(self, path, params={}):

        if 'file' in params and 'photo_id' in params and "upload_key" in params:
            try:
                params = {'file': open(params['file'], "rb"),
                    'upload_key': params['upload_key'],
                    'photo_id': params['photo_id'],
                    'consumer_key': self.client.consumer.key,
                    'access_key': self.client.token.key}

                datagen, headers = poster.encode.multipart_encode(params)
                request = urllib2.Request(
                    str.join('', (self.site, path)),
                    datagen, headers)
                print urllib2.urlopen(request).read()

            except IOError:
                print "File %s does not exist!" % params['file']

        else:
            print "invalid parameters, see documentation"
        return

    def delete(self, path, params={}):
            return self.parse_response(self.client.request(
                str.join('', (self.site, path, self.encode_params(params))),
                "DELETE",
                ))

    def encode_params(self, params={}):
        return str.join('', ('&', urllib.urlencode(params)))

    def parse_response(self, result):
        """ Parse the response from the server to check for errors """
        resp, content = result
        if 400 <= int(resp['status']) <= 600:
            raise APIError(content)

        content = json.loads(content)
        return content
