#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Andrew Culberson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
import json
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, ParseResult, urlencode


def help():
    print("httpclient.py [GET/POST] [URL]\r\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = int(code)
        self.body = body

    def __str__(self):

        return self.body


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return data.split("\n")[0].split(" ")[1]

    def get_headers(self, data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('latin-1')

    def GET(self, url, args=None):
        code = 500
        body = ""
        url_parsed = urlparse(url, scheme="http")

        # set defaults in case user did not include. determine path string with query included
        port = url_parsed.port if url_parsed.port else 80
        path = url_parsed.path if url_parsed.path else "/"
        query = "?" + url_parsed.query if url_parsed.query else ""
        path_with_query = path + query

        # format request
        request = f"GET {path_with_query} HTTP/1.1\r\nHost: {url_parsed.netloc}\r\nAccept: */*\r\nConnection: close\r\n\r\n"

        # connect, send request, and wait for response
        self.connect(url_parsed.hostname, port)
        self.sendall(request)
        resp = self.recvall(self.socket)

        # parse response
        code = self.get_code(resp)
        body = self.get_body(resp)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        url_parsed = urlparse(url, scheme="http")

        # set defaults in case user did not include. determine path string with query included
        port = url_parsed.port if url_parsed.port else 80
        path = url_parsed.path if url_parsed.path else "/"
        query = "?" + url_parsed.query if url_parsed.query else ""
        path_with_query = path + query

        # url encode post args
        content = urlencode(args) if args else ""
        content_length = len(content)

        # format request. long string
        request = f"POST {path_with_query} HTTP/1.1\r\nHost: {url_parsed.netloc}\r\nAccept: */*\r\nConnection: close\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {content_length}\r\n\r\n{content}\rn\r\n"

        # connect, send request, and wait for response
        self.connect(url_parsed.hostname, port)
        self.sendall(request)
        resp = self.recvall(self.socket)

        # parse response
        code = self.get_code(resp)
        body = self.get_body(resp)
        print("BODY: ",body)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
