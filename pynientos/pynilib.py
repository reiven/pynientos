#-*- coding: utf-8 -*-
import re
import json
import oauth2 as oauth


class APIError(StandardError):
    def __init__(self, msg, response=None):
        StandardError.__init__(self, msg)


class Pynientos:
    def __init__(self, **kwargs):
        self.site = "https://api.500px.com"

        if not 'key'in kwargs or not 'secret' in kwargs:
            raise ValueError("Key and secret must be set.")
        self.client = self.set_oauth_client(kwargs)
        self.set_methods()

    def set_oauth_client(self, kwargs):
        """ Set the oauth client with the given key and secret """
        if len(kwargs) == 4:
            if 'token' in kwargs and 'token_secret' in kwargs:
                return oauth.Client(
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
            return oauth.Client(
                oauth.Consumer(key=kwargs['key'],
                secret=kwargs['secret']
            ))

    def api_setting(self):
        """ A list of name, url, auth type and http method for the API usage """
        api_str = """
          photos_popular         /v1/photos?feature=popular         get
          photos_upcoming        /v1/photos?feature=upcoming        get
          photos_editors         /v1/photos?feature=editors         get
          photos_fresh_today     /v1/photos?feature=fresh_today     get
          photos_fresh_yesterday /v1/photos?feature=fresh_yesterday get
          photos_fresh_week      /v1/photos?feature=fresh_week      get
          photos_user            /v1/photos?feature=user            get
          photos_user_friends    /v1/photos?feature=user_friends    get
          photos_search          /v1/photos/search                  get
          photo_detail           /v1/photos/                        get
          user                   /v1/users                          get
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
        """ Parse the params and returns a string for the url construction """
        strparam = ''
        for key in params:
            strparam += "&" + str.join("=", (key, params[key]))
        return strparam

    def parse_response(self, result):
        """ Parse the response from the server to check for errors """
        resp, content = result
        if 400 <= int(resp['status']) <= 600:
            raise APIError(content)

        content = json.loads(content)
        return content
