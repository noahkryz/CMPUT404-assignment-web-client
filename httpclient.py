#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = str(data.split("\r\n")).split(" ")[1]
        return code

    def get_headers(self,data):
        headers = str(data.split("\r\n\r\n")[0])
        return headers

    def get_body(self, data):
        body = str(data.split("\r\n\r\n")[1])
        return body
    
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
        return buffer.decode('utf-8')

    def parse_url(self, url):
        parse_result = urllib.parse.urlparse(url)
        host_name = parse_result.hostname
        port_num = parse_result.port
        path = parse_result.path

        scheme = parse_result.scheme

        # No port number given, manually set it based on protocol
        if not port_num:
            # https protocol, set to 443
            if scheme == "https":
                port_num = '443'
            # http protocol, set to 80
            else:
                port_num = '80'

        # No path given, manually set it to /
        if not path:
            path = '/'

        return host_name, port_num, path

    def GET(self, url, args=None):
        # Obtain the components from the url, using the parse function
        host_name, port_num, path = self.parse_url(url)

        # Build up the GET request
        method_line = "GET " + path + " HTTP/1.1\r\n"
        host_line = "Host: " + host_name + ":" + str(port_num) + "\r\n"
        connection_line = "Connection: close\r\n"
        get_request = method_line + host_line + connection_line + "\r\n"
        # print("Request\n", get_request)

        # Connect to the host name with the port (default already handled)
        self.connect(host_name, int(port_num))

        # Send the GET request
        self.sendall(get_request)

        # Get the response from the server
        response = self.recvall(self.socket)
        
        headers = self.get_headers(response)
        code = int(self.get_code(response))
        body = self.get_body(response)
        print(body)

        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # Construct a string of arguments to pass in the body
        argument_line = ''
        counter = 1
        # Only construct the string if arguments are provided
        if args:
            for item in args:
                if counter != len(args):
                    argument_line += str(item) + '=' + str(args[item]) + "&"
                    counter += 1
                else:
                    argument_line += str(item) + '=' + str(args[item])

        # Obtain the components from the url, using the parse function
        host_name, port_num, path = self.parse_url(url)

        # Build up the POST request
        method_line = "POST " + path + " HTTP/1.1\r\n"
        host_line = "Host: " + host_name + ":" + str(port_num) + "\r\n"
        content_line = "Content-Type: application/x-www-form-urlencoded" + "\r\n"
        length_line = "Content-Length: " + str(len(argument_line)) + "\r\n"
        connection_line = "Connection: close\r\n\r\n"
        post_line = argument_line + "\r\n"

        get_request = method_line + host_line + content_line + length_line + connection_line + post_line + "\r\n"

        # Connect to the host name with the port (default already handled)
        self.connect(host_name, int(port_num))

        # Send the POST request
        self.sendall(get_request)

        # Get the response from the server
        response = self.recvall(self.socket)
        
        headers = self.get_headers(response)
        code = int(self.get_code(response))
        body = self.get_body(response)
        print(body)

        self.close()
        
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
