"""
    This module handles HTTP requests. It currently only supports basic
    GET and POST behavior

"""

import sys

from HTTPRequests.connection import WebSocket
from HTTPRequests.message import HttpRequestMessage, HttpResponseMessage

class HttpRequest(object):

    """ HTTP Request to server for some resource """

    def __init__(self, host):

        self.host = host
        self.port = self.check_port()
        self.request = None
        self.history = []
        self.redirect_count = 0

    def get(self, page='/', headers=None, cookies=None):

        """ Perform a GET request to host """
        self.request = HttpRequestMessage('GET', page, self.host,
                                          headers, cookies=cookies)
        self.history.append(self.request)
        return self.do_request()

    def post(self, page='/', headers=None, data="", cookies=None):

        """ Perform a POST request to host """
        data = encode_data(data)
        self.request = HttpRequestMessage('POST', page, self.host, headers,
                                          body=data, cookies=cookies)
        self.history.append(self.request)
        return self.do_request()

    def head(self, page='/', headers=None):

        """ Perform a HEAD request to host """
        self.request = HttpRequestMessage('HEAD', page, self.host,
                                          headers=headers)
        self.history.append(self.request)
        return self.do_request()

    def do_request(self):

        """ Send request message to destination server """
        s = WebSocket(self.host, self.port)
        s.send(self.request.message)
        status, headers, body = self.receive_response(s)
        response = HttpResponseMessage(status, headers, body)
        if self.redirect_count > 3: #Caught in possible redirect loop
            print "Error: Redirect loop detected. Exiting."
            sys.exit(1)
        if response.get_status_code() in (301, 302):
            self.redirect_count += 1
            page = self.parse_location(headers.get('Location', ''))
            self.get(page)
        return response

    def check_protocol(self):

        """ Strips protocol from hostname and stores it as a variable """
        split_data = self.host.split('://')
        self.host = '://'.join(split_data[1:]) # Handle possibility of multiple ://
        return split_data[0]

    def check_port(self):

        """ Checks to see if port is attached to host """
        if ':' in self.host:
            self.host, port = self.host.split(':')
            s = port.find('/')
            q = port.find('?')
            if s != -1:
                port = port[:s]
            elif q != -1:
                port = port[:q]
            elif len(port) > 0:
                return int(port)
        return 80

    def parse_location(self, loc):

        """ Splits location header value into host and page """
        loc = loc.replace('http:', '').replace('https:', '').replace('//', '')
        s = loc.find('/')
        self.host = loc[:s]
        return loc[s:]

    def receive_response(self, sock):

        """ Parse server HTTP response """
        status = sock.readline()
        headers = parse_headers(sock.recv(until='\r\n'))

        size, body = -1, ""
        if 'Content-Length' in headers:
            size = int(headers['Content-Length'])
            body = sock.recv(size=size)
        elif headers.get('Transfer-Encoding') == "chunked":
            while size != 0:
                size = int(sock.readline(), 16)
                body += sock.recv(size=size)
                sock.readline() # pass over \r\n
        else:
            print "ERROR: No length specified in headers"

        return (status, headers, body)

def parse_headers(header_data):

    """ Converts header string into dictionary """
    headers = [k.split(':') for k in header_data.split('\r\n') if k]
    return {k[0].strip().title():':'.join(k[1:]).strip() for k in headers}

def encode_data(data):

    """ Converts data dictionary into urlencoded string """

    strlist = ["%s=%s" % (k, url_encode(v)) for k, v in data.iteritems()]
    return '&'.join(strlist)

def url_encode(string):

    """ Replaces problem characters with appropriate percent encoding """
    percent_map = {' ':'%20',
                   '!':'%21',
                   '\"':'%22',
                   '#':'%23',
                   '$':'%24',
                   '&':'%26',
                   '\'':'%27',
                   '(':'%28',
                   ')':'%29',
                   '*':'%2A',
                   '+':'%2B',
                   ',':'%2C',
                   '-':'%2D',
                   '.':'%2E',
                   '/':'%2F',
                   ':':'%3A',
                   ';':'%3B',
                   '<':'%3C',
                   '=':'%3D',
                   '>':'%3E',
                   '?':'%3F',
                   '@':'%40',
                   '[':'%5B',
                   '\\':'%5C',
                   ']':'%5D',
                   '^':'%5E',
                   '_':'%5F'}

    string = string.replace('%', '%25')
    for k, v in percent_map.iteritems():
        string = string.replace(k, v)
    return string
