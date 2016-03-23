"""
    This module handles cookie content encapsulation

"""

class Cookie(object):

    """ Encapsulates the values of an HTTP Cookie """
    def __init__(self, name, value, domain, path, **kwargs):
        self.name = name
        self.value = value
        self.path = path
        self.domain = domain
        self.attributes = self.assign_attributes(kwargs)
        self.cookie_str = self.set_cookie_str()

    def __str__(self):

        return self.cookie_str

    def set_cookie_str(self):

        """ Creates HTTP valid cookie string """
        return "%s=%s;" % (self.name, self.value)

    def assign_attributes(self, attrs):

        """ Assign additional cookie attributes to dictionary """
        attr_dict = {"Expires": attrs.get('Expires'),
                     "Max-Age": attrs.get('Max-Age'),
                     "Secure": attrs.get('Secure', False),
                     "HttpOnly": attrs.get('HttpOnly', False),
                     "Raw-String": attrs.get('Raw-String')}
        return attr_dict
