#-*- coding: utf-8 -*-
import re, urllib, json
import oauth2 as oauth


class APIError(StandardError):
    def __init__(self, msg, response=None):
        StandardError.__init__(self, msg)


class Pynientos:
    def __init__(self, key, secret):
        self.site = "https://api.500px.com"
        if key is None or secret is None:
            raise ValueError("Key and secret must be set.")

        self.client = self.set_oauth_client(key, secret)
        self.set_methods()

    def api_key(self):
        return {"api_key": self.client.consumer.key}

    def set_oauth_client(self, key, secret):
#        consumer = oauth.Consumer(key=key, secret=secret)
        return oauth.Client(oauth.Consumer(key=key, secret=secret))

    def api_setting(self):
        api_str = """
          photos_popular         /v1/photos?feature=popular         oauth  get
          photos_upcoming        /v1/photos?feature=upcoming        oauth  get
          photos_editors         /v1/photos?feature=editors         oauth  get
          photos_fresh_today     /v1/photos?feature=fresh_today     oauth  get
          photos_fresh_yesterday /v1/photos?feature=fresh_yesterday oauth  get
          photos_fresh_week      /v1/photos?feature=fresh_week      oauth  get
          photos_user            /v1/photos?feature=user            oauth  get
          photos_user_friends    /v1/photos?feature=user_friends    oauth  get
          photos_search          /v1/photos/search                  oauth  get
          photo_detail           /v1/photos/                        oauth  get
        """
        return map(lambda x: re.split("\s+", x.strip()),
                             re.split("\n", api_str.strip()))

    def set_methods(self):
        for api_list in self.api_setting():
            api = {}
            api["method_name"], api["path"], api["auth"], api["http_method"] = api_list

            def _method(api=api, id="", **params):
                if id:
                    return getattr(self, api["http_method"])(str.join('',(api["path"],id)), params)
                else:
                    return getattr(self, api["http_method"])(api["path"], params)
            setattr(self, api["method_name"], _method)

    def get(self, path, params=""):
        return self.parse_response(self.client.request(
                   self.site + path + self.parse_params(params),
                   "GET",
                   ))

    def post(self, path, params={}):
        return self.parse_response(self.client.request(
                   self.site + path,
                   "POST",
                   self.parse_params(params)
                   ))

    def parse_params(self, params=""):
        strparam = ''
        for key in params:
            strparam += "&" + str.join("=", (key, params[key]))
        return strparam

    def parse_response(self, result):
        resp, content = result
        content = json.loads(content)
        if 400 <= int(resp['status']) <= 600:
            raise APIError(resp['status'], result)
        return content
